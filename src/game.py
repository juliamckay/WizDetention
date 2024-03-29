import arcade
import time
import threading
from abc import abstractmethod
import arcade.gui
from src.constants import *
from src.env_interaction import *
from src.quit_screen import QuitScreen


class GameScreen(arcade.View):
    def __init__(self):
        """Create the Window here and Declare game variables"""
        # Create the ViewPort
        super().__init__()
        arcade.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)

        #Next scene to load
        self.next_level = None

        # Set up reset fade
        self.fading = False

        # Create the manager
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Variable Declarations
        self.ih = None
        self.interacting = False
        self.in_place = False

        # Game screen
        self.tile_map = None
        self.layer_options = None
        self.scene = None

        # Player Sprites
        self.wizard = None
        # self.wizard_sprite = None
        self.familiar = None
        # self.familiar_sprite = None

        # Interactable Object Sprites

        # Used for spell
        self.target: SpecialSprite = None

        self.target_anim_sprite: arcade.Sprite = None
        self.target_anim = []
        self.curr_targ_anim_count = 0
        self.cooldown = 0

        self.box_pe_list = []
        # self.stop_interact_area = None
        # self.new_box = None

        # Acid Hazards
        self.acid_hazard_list = None
        self.acid_textures = []
        self.cur_texture = 0

        # Levers
        self.current_lever = None
        self.current_plat = None
        self.flipped_right = None
        self.flipped_left = None
        self.lever_left = False

        # Moving Platform Info
        self.lever_count = 0
        self.button_count = 0
        self.button_plats = []
        self.lever_plats = []
        self.player_on_lever = 0
        self.moving_vel = 2

        # Physics Engine
        self.pe1 = None
        self.pe2 = None
        self.ty = None

        # Game Audio
        self.main_theme = arcade.load_sound("Assets/Audio/8bit-harmony.wav", False)
        self.main_player = None
        self.death_noise = arcade.load_sound("Assets/Audio/noise-hit-1.mp3", False)
        self.level_transition = arcade.load_sound("Assets/Audio/door-close.wav", False)

        # set up fade
        self.fade_val = 255

        # fade state: 1 = fade_out, -1 = fade_in
        self.fade_state = -1
        self.fading = True

        self.dying = False
        self.nl = False

    def setup_layer_options(self, lever_count=1, button_count=1):
        self.layer_options = {
            "Platforms": {
                "use_spatial_hash": True,
            },
            "Dont Touch": {
                "use_spatial_hash": True,
            },
            "Door": {
                "use_spatial_hash": True,
            },
        }
        for i in range(1, lever_count + 1):
            self.layer_options[f"Lever {i}"] = {"use_spatial_hash": True, }
        for i in range(1, button_count + 1):
            self.layer_options[f"Button {i}"] = {"use_spatial_hash": True, }

    def setup(self):
        # Make all players alive
        if self.wizard:
            self.wizard.alive()
        if self.familiar:
            self.familiar.alive()

        # play background music
        if not self.main_player:
            self.main_player = arcade.play_sound(self.main_theme, 1.0, 0.0, True, 1.0)

        self.button_plats.clear()
        self.lever_plats.clear()
        self.player_on_lever = False

        # Lever animation setup
        self.flipped_right = arcade.load_texture("Assets/Sprites/Levers/lever_0.png")
        self.flipped_left = arcade.load_texture("Assets/Sprites/Levers/lever_1.png")

        # Acid animation setup
        self.acid_hazard_list = self.tile_map.sprite_lists.get("Dont Touch")
        for i in range(4):
            texture = arcade.load_texture(f"Assets/Sprites/Acid/acid_{i}.png")
            self.acid_textures.append(texture)

        # Player Sprite Setup
        self.scene.add_sprite_list("Interacts")
        self.scene.add_sprite_list("Targeting")
        self.scene.add_sprite_list("Wiz")
        self.scene.add_sprite_list("Cat")
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)

        # self.wizard_sprite = arcade.Sprite("Assets/Sprites/Wizard/wizard_idle.png", WIZARD_SCALING)
        self.wizard = PlayerCharacter("Assets/Sprites/Wizard/wizard", WIZARD_SCALING)
        self.wizard.position = (SPAWN_X, SPAWN_Y)
        self.scene.add_sprite("Wiz", self.wizard)

        # self.familiar_sprite = arcade.Sprite("Assets/Sprites/Familiar/familiar_idle.png", FAMILIAR_SCALING)
        self.familiar = PlayerCharacter("Assets/Sprites/Familiar/familiar", FAMILIAR_SCALING)
        self.familiar.position = (SPAWN_X + 30, SPAWN_Y - 10)
        self.scene.add_sprite("Cat", self.familiar)

        self.dying = False
        self.nl = False

        self.toggle_movements(True)

    def on_show_view(self):
        arcade.play_sound(self.level_transition, 1.0, 0.0, False, 1.0)
        self.setup()
        arcade.set_background_color(arcade.color.GRAY)

    def on_draw(self):
        self.clear()
        self.manager.draw()
        self.scene.draw()

        self.handle_fade()

    def on_key_press(self, key, mods):
        """Delegated to the input handler"""
        command = self.ih.handle_input(key)
        if command:
            command()

    def on_key_release(self, key, mods):
        """Delegated to the input handler"""
        command = self.ih.handle_input(key)
        if command:
            command.undo()

    def on_update(self, delta_time):

        self.update_fade()

        # Update the players animation
        self.wizard.update_animation()
        self.familiar.update_animation()

        # Go through acid animation frames
        self.cur_texture += 1
        if self.cur_texture > 3 * ACID_UPDATES_PER_FRAME:
            self.cur_texture = 0
        frame = self.cur_texture // ACID_UPDATES_PER_FRAME
        for acid in self.acid_hazard_list:
            acid.texture = self.acid_textures[frame]

        self.pe1.update()
        if self.pe1.can_jump():
            self.wizard.jumping = False
        else:
            self.wizard.jumping = True

        self.pe2.update()
        if self.pe2.can_jump():
            self.familiar.jumping = False
        else:
            self.familiar.jumping = True

        self.handle_special_object_physics_engines()

        # Check for if target is within vision of player character
        # For now, a simple within-range check around the wizard for potential targets
        if self.target:
            self.target_anim_sprite.position = self.target.position
            if(arcade.get_distance(self.wizard.center_x, self.wizard.center_y,
                                   self.target.center_x, self.target.center_y) > 200):
                # Halt it's movement
                self.target.change_x = 0
                self.target.change_y = 0
                self.cancel_spell()

                # Deselect the target
                self.target_anim_sprite.alpha = 0
                self.target = None
            else:
                self.play_target_animation(delta_time)
        else:
            # Select the target
            for target in self.scene["Interacts"]:
                if self.in_target_range(target):
                    self.target = target
                    self.target_anim_sprite.position = self.target.position
                    self.target_anim_sprite.alpha = 255
                    break

        # check for collision with buttons
        for i in range(1, self.button_count + 1):
            current_plat = self.button_plats[i-1]
            end = current_plat[1]
            start = current_plat[2]
            layer_name = "Button " + str(i)
            current_plat[0] = button_platform(self.scene, self.wizard, self.familiar, layer_name, current_plat[0],
                                              end, start, self.moving_vel, current_plat[3])

        # check for collision with levers
        if not self.player_on_lever:
            for i in range(0, self.lever_count):
                layer_name = f"Lever {i + 1}"
                self.player_on_lever, self.current_lever = levers_check_col(self.scene, layer_name,
                                                                            self.wizard, self.familiar)

                if self.player_on_lever:
                    self.lever_plats[i][1] = not self.lever_plats[i][1]
                    self.lever_plats[i][2] = not self.lever_plats[i][2]
                    self.lever_left = not self.lever_left

                    if self.lever_left:
                        self.current_lever[0].texture = self.flipped_left
                    else:
                        self.current_lever[0].texture = self.flipped_right
                    break

        # This means someone is currently pressing a lever
        else:
            if self.player_on_lever == 1:
                player = self.wizard
            else:
                player = self.familiar

            self.player_on_lever = levers_check_remaining_col(self.current_lever[0], player, self.player_on_lever)

        # move all platforms accordingly
        for i in range(0, self.lever_count):
            current_plat = self.lever_plats[i]
            current_plat[0] = lever_platform(current_plat[0], current_plat[1], current_plat[2],
                                             current_plat[3], current_plat[4], self.moving_vel,
                                             current_plat[5])

        # See if player has collided w anything from the Don't Touch layer
        if (arcade.check_for_collision_with_list(self.wizard, self.scene["Dont Touch"]) or
                arcade.check_for_collision_with_list(self.familiar, self.scene["Dont Touch"])) and not self.dying:
            self.reset()
            self.dying = True

        # check if BOTH players have collided with door, advance to next level
        # for now it just goes to quit screen since there is no level 2 yet
        if arcade.check_for_collision_with_list(self.wizard, self.scene["Door"]) and \
                arcade.check_for_collision_with_list(self.familiar, self.scene["Door"]):
            self.next_level_prep()

    # region helpers

    def get_target_sprite(self):
        return self.target

    def play_target_animation(self, delta_time):
        self.cooldown += delta_time
        if self.cooldown > 0.1:
            self.target_anim_sprite.texture = self.target_anim[self.curr_targ_anim_count]
            self.curr_targ_anim_count = (self.curr_targ_anim_count + 1) % 4
            self.cooldown = 0

    def setup_physics(self):
        # Physics Engines
        self.pe1 = arcade.PhysicsEnginePlatformer(self.wizard, gravity_constant=GRAVITY,
                                                  walls=(self.scene["Platforms"], self.scene["Interacts"]))
        self.pe2 = arcade.PhysicsEnginePlatformer(self.familiar, gravity_constant=GRAVITY,
                                                  walls=(self.scene["Platforms"], self.scene["Interacts"]))

        # Box Physics
        self.box_pe_list.clear()
        for sprite in self.scene["Interacts"]:
            self.box_pe_list.append(arcade.PhysicsEnginePlatformer(sprite, gravity_constant=0))

    def handle_special_object_physics_engines(self):
        for pe in self.box_pe_list:
            pe.update()

    def setup_target_sprites(self):
        # Load textures for when targeting is occurring
        for i in range(4):
            texture = arcade.load_texture(f"Assets/Sprites/Targets/TargetT1_{i}.png")
            self.target_anim.append(texture)
        self.target_anim_sprite = arcade.Sprite("Assets/Sprites/Targets/TargetT1_0.png")
        self.target_anim_sprite.alpha = 0
        self.scene.add_sprite("Targeting", self.target_anim_sprite)

    def cancel_spell(self):
        if not self.wizard.can_move:
            self.ih.bind(arcade.key.W, JumpCommand(self.wizard))
            self.ih.bind(arcade.key.A, MoveLeftCommand(self.wizard))
            self.ih.bind(arcade.key.D, MoveRightCommand(self.wizard))

    def reset(self):
        if self.fading:
            return
        self.wizard.die()
        self.familiar.die()

        arcade.play_sound(self.death_noise, 1.0, 0.0, False, 1.0)

        self.toggle_movements(False)
        # Fade view
        self.fading = True

    def reset_target(self):
        self.setup()

    def toggle_fade(self):
        self.fade_state *= -1

    def draw_fading(self):
        if 255 >= self.fade_val >= 0:
            arcade.draw_rectangle_filled(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                                         SCREEN_WIDTH, SCREEN_HEIGHT,
                                         (0, 0, 0, self.fade_val))

    def update_fade(self):
        if 255 >= self.fade_val >= 0 and self.fading:
            self.fade_val += FADE_RATE * self.fade_state
            if self.fade_val > 255:
                self.fade_val = 255
            elif self.fade_val < 0:
                self.fade_val = 0

    def toggle_movements(self, boolean):
        # Wizard
        self.wizard.can_move = boolean
        self.wizard.change_x = 0
        self.wizard.change_y = 0

        # Familiar
        self.familiar.can_move = boolean
        self.familiar.change_x = 0
        self.familiar.change_y = 0

        # Interact Objects
        for obj in self.scene["Interacts"]:
            obj.can_move = boolean
            obj.change_x = 0
            obj.change_y = 0

    def next_level_prep(self):
        if isinstance(self.next_level, QuitScreen):
            self.main_theme.stop(self.main_player)
        else:
            self.next_level.main_player = self.main_player

        self.fading = True
        self.nl = True
        self.toggle_movements(False)

    def handle_fade(self):
        if self.fading and self.fade_state == -1 and self.fade_val <= 0:
            # reset up fade after setup is done
            self.fade_state = 1
            self.fading = False

        if self.fading:
            # 1st, fade out until fade val is 255
            self.draw_fading()
            if self.fade_state == 1 and self.fade_val >= 255:
                # Then, setup() or next_level() while no one can see
                if self.nl:
                    self.window.show_view(self.next_level)
                else:
                    self.setup()
                # Finally, fade in
                self.fade_state = -1

    def in_target_range(self, target):
        return arcade.get_distance(self.wizard.center_x, self.wizard.center_y, target.center_x, target.center_y) < 100

    # endregion


class LevelZero(GameScreen):
    def __init__(self):
        super().__init__()
        self.text_camera = None
        self.next_level = LevelOne()

    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        # text overlay setup
        self.text_camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

        # name of map to load
        map_name = "Assets\\Maps\\Level_0_map.json"

        self.button_count = 1
        self.lever_count = 1

        super().setup_layer_options(self.lever_count, self.button_count)

        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, self.layer_options)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        super().setup()

        # Adding Moving Platform Sprite
        moving_platform_1 = arcade.Sprite("Assets/Sprites/moving_platform_01.png", PLATFORM_SCALING)
        moving_platform_1.center_x = 1175
        moving_platform_1.center_y = 380
        moving_platform_1.change_x = 0
        moving_platform_1.change_y = 0
        self.lever_plats.append([moving_platform_1, True, False, 380, 250, 'v'])    # [plat, move up, move down, max, min, dir]
        self.scene.add_sprite("Platforms", moving_platform_1)

        moving_platform_2 = arcade.Sprite("Assets/Sprites/moving_platform_02_v.png", PLATFORM_SCALING_V)
        moving_platform_2.center_x = 600
        moving_platform_2.center_y = 455
        moving_platform_2.change_x = 0
        moving_platform_2.center_y = 0
        self.button_plats.append([moving_platform_2, 555, 455, 'v'])    #[plat, max, min]
        self.scene.add_sprite("Platforms", moving_platform_2)

        # Adding interactable objects
        interact_box = MagicObject("Assets/Sprites/Interacts/box.png", 0.15)
        interact_box.center_x = 400
        interact_box.center_y = 595
        self.scene.add_sprite("Interacts", interact_box)

        super().setup_physics()

        # Load textures for when targeting is occurring
        super().setup_target_sprites()

        # Input Handler
        self.ih = InputHandler(self.wizard, self.familiar, self)

    def on_draw(self):
        self.clear()
        self.manager.draw()
        self.scene.draw()

        self.text_camera.use()

        arcade.draw_text("Hey Wizard! Hold S when close to possess the box! [No Jumping]", 150, 700,
                         arcade.color.AFRICAN_VIOLET, 12, 80)
        arcade.draw_text("Only the cat can fit through that...", 800, 150, arcade.color.AMBER, 12, 80)
        arcade.draw_text("Press R to reset the level", 40, 270, arcade.color.WHITE, 12, 80)
        arcade.draw_text("Press Esc to quit the game", 40, 250, arcade.color.WHITE, 12, 80)

        super().handle_fade()


class LevelOne(GameScreen):
    def __init__(self):
        super().__init__()
        self.next_level = LevelTwo()

    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        self.button_plats.clear()
        self.lever_plats.clear()
        self.player_on_lever = False

        # name of map to load
        map_name = "Assets\\Maps\\Level_1_map.json"

        self.button_count = 6
        self.lever_count = 2

        super().setup_layer_options(self.lever_count, self.button_count)

        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, self.layer_options)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        super().setup()

        # Lever animation setup
        self.flipped_right = arcade.load_texture("Assets/Sprites/Levers/lever_0.png")
        self.flipped_left = arcade.load_texture("Assets/Sprites/Levers/lever_1.png")

        # Add in moving platforms

        # Lever platforms here
        lever_plat = arcade.Sprite("Assets/Sprites/moving_platform_01.png", 2)
        lever_plat.center_x = 895
        lever_plat.center_y = 185
        lever_plat.change_x = 0
        lever_plat.change_y = 0
        self.lever_plats.append([lever_plat, False, True, 1065, 895, 'h'])  # [plat, move up, move down, max, min, dir]
        self.scene.add_sprite("Platforms", lever_plat)

        lever_plat_2 = arcade.Sprite("Assets/Sprites/moving_platform_01.png", 2)
        lever_plat_2.center_x = 1195
        lever_plat_2.center_y = 405
        lever_plat_2.change_x = 0
        lever_plat_2.change_y = 0
        self.lever_plats.append([lever_plat_2, True, False, 1195, 1095, 'h'])  # [plat, move up, move down, max, min, dir]
        self.scene.add_sprite("Platforms", lever_plat_2)

        # Button platforms here
        button_plat_1 = arcade.Sprite("Assets/Sprites/moving_platform_02_v.png", 2)
        button_plat_1.center_x = 200
        button_plat_1.center_y = 90
        button_plat_1.change_x = 0
        button_plat_1.center_y = 0
        self.button_plats.append([button_plat_1, 200, 90, 'v'])
        self.scene.add_sprite("Platforms", button_plat_1)

        button_plat_2 = arcade.Sprite("Assets/Sprites/moving_platform_02_v.png", 2)
        button_plat_2.center_x = 550
        button_plat_2.center_y = 90
        button_plat_2.change_x = 0
        button_plat_2.center_y = 0
        self.button_plats.append([button_plat_2, 200, 90, 'v'])
        self.scene.add_sprite("Platforms", button_plat_2)

        button_plat_2 = arcade.Sprite("Assets/Sprites/moving_platform_02_v.png", 1.8)
        button_plat_2.center_x = 1210
        button_plat_2.center_y = 535
        button_plat_2.change_x = 0
        button_plat_2.center_y = 0
        self.button_plats.append([button_plat_2, 590, 535, 'v'])
        self.scene.add_sprite("Platforms", button_plat_2)

        button_plat_2 = arcade.Sprite("Assets/Sprites/moving_platform_02_v.png", 1.8)
        button_plat_2.center_x = 500
        button_plat_2.center_y = 635
        button_plat_2.change_x = 0
        button_plat_2.center_y = 0
        self.button_plats.append([button_plat_2, 735, 635, 'v'])
        self.scene.add_sprite("Platforms", button_plat_2)

        button_plat_2 = arcade.Sprite("Assets/Sprites/moving_platform_02_v.png", 1.8)
        button_plat_2.center_x = 700
        button_plat_2.center_y = 635
        button_plat_2.change_x = 0
        button_plat_2.center_y = 0
        self.button_plats.append([button_plat_2, 735, 635, 'v'])
        self.scene.add_sprite("Platforms", button_plat_2)

        button_plat_2 = arcade.Sprite("Assets/Sprites/moving_platform_02_v.png", 1.8)
        button_plat_2.center_x = 900
        button_plat_2.center_y = 635
        button_plat_2.change_x = 0
        button_plat_2.center_y = 0
        self.button_plats.append([button_plat_2, 735, 635, 'v'])
        self.scene.add_sprite("Platforms", button_plat_2)

        # Adding interactable objects
        interact_box = MagicObject("Assets/Sprites/Interacts/rectangle.png", 0.15)
        interact_box.center_x = 480
        interact_box.center_y = 140
        self.scene.add_sprite("Interacts", interact_box)

        interact_box = MagicObject("Assets/Sprites/Interacts/box.png", 0.15)
        interact_box.center_x = 625
        interact_box.center_y = 372
        self.scene.add_sprite("Interacts", interact_box)

        super().setup_target_sprites()

        # Acid animation setup
        self.acid_hazard_list = self.tile_map.sprite_lists.get("Dont Touch")
        for i in range(4):
            texture = arcade.load_texture(f"Assets/Sprites/Acid/acid_{i}.png")
            self.acid_textures.append(texture)

        # Input Handler
        self.ih = InputHandler(self.wizard, self.familiar, self)

        super().setup_physics()


class LevelTwo(GameScreen):
    def __init__(self):
        super().__init__()
        self.next_level = LevelThree()

    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        self.button_plats.clear()
        self.lever_plats.clear()
        self.player_on_lever = False

        # name of map to load
        map_name = "Assets\\Maps\\Level_2_map.json"

        self.button_count = 8
        self.lever_count = 1
        super().setup_layer_options(self.lever_count, self.button_count)

        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, self.layer_options)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        super().setup()

        # Adding Moving Platform Sprite
        # Button platforms here
        button_plat = arcade.Sprite("Assets/Sprites/moving_platform_01.png", 2)
        button_plat.center_x = 80
        button_plat.center_y = 250
        button_plat.change_x = 0
        button_plat.change_y = 0
        self.button_plats.append([button_plat, 200, 80, 'h'])  # [plat, end, start, dir]
        self.scene.add_sprite("Platforms", button_plat)

        button_plat = arcade.Sprite("Assets/Sprites/moving_platform_01.png", 2)
        button_plat.center_x = 80
        button_plat.center_y = 470
        button_plat.change_x = 0
        button_plat.change_y = 0
        self.button_plats.append([button_plat, 200, 80, 'h'])  # [plat, end, start, dir]
        self.scene.add_sprite("Platforms", button_plat)

        button_plat = arcade.Sprite("Assets/Sprites/moving_platform_02_v.png", 2)
        button_plat.center_x = 760
        button_plat.center_y = 385
        button_plat.change_x = 0
        button_plat.change_y = 0
        self.button_plats.append([button_plat, 470, 385, 'v'])  # [plat, end, start, dir]
        self.scene.add_sprite("Platforms", button_plat)

        button_plat = arcade.Sprite("Assets/Sprites/moving_platform_02_v.png", 2)
        button_plat.center_x = 565
        button_plat.center_y = 385
        button_plat.change_x = 0
        button_plat.change_y = 0
        self.button_plats.append([button_plat, 470, 385, 'v'])  # [plat, end, start, dir]
        self.scene.add_sprite("Platforms", button_plat)

        button_plat = arcade.Sprite("Assets/Sprites/moving_platform_02_v.png", 2)
        button_plat.center_x = 950
        button_plat.center_y = 385
        button_plat.change_x = 0
        button_plat.change_y = 0
        self.button_plats.append([button_plat, 470, 385, 'v'])  # [plat, end, start, dir]
        self.scene.add_sprite("Platforms", button_plat)

        button_plat = arcade.Sprite("Assets/Sprites/moving_platform_02_v.png", 2)
        button_plat.center_x = 660
        button_plat.center_y = 385
        button_plat.change_x = 0
        button_plat.change_y = 0
        self.button_plats.append([button_plat, 470, 385, 'v'])  # [plat, end, start, dir]
        self.scene.add_sprite("Platforms", button_plat)

        button_plat = arcade.Sprite("Assets/Sprites/moving_platform_02_v.png", 2)
        button_plat.center_x = 1050
        button_plat.center_y = 385
        button_plat.change_x = 0
        button_plat.change_y = 0
        self.button_plats.append([button_plat, 470, 385, 'v'])  # [plat, end, start, dir]
        self.scene.add_sprite("Platforms", button_plat)

        button_plat = arcade.Sprite("Assets/Sprites/moving_platform_02_v.png", 2)
        button_plat.center_x = 855
        button_plat.center_y = 385
        button_plat.change_x = 0
        button_plat.change_y = 0
        self.button_plats.append([button_plat, 470, 385, 'v'])  # [plat, end, start, dir]
        self.scene.add_sprite("Platforms", button_plat)

        # Lever platforms here
        lever_plat = arcade.Sprite("Assets/Sprites/moving_platform_01.png", 2)
        lever_plat.center_x = 80
        lever_plat.center_y = 350
        lever_plat.change_x = 0
        lever_plat.change_y = 0
        self.lever_plats.append([lever_plat, False, True, 200, 80, 'h'])  # [plat, end, start, dir]
        self.scene.add_sprite("Platforms", lever_plat)

        # Setup Wizard spawn
        self.wizard.position = (SPAWN_X + 130, SPAWN_Y - 40)

        # Setup Familiar spawn
        self.familiar.position = (SPAWN_X + 110, SPAWN_Y - 50)

        # Adding interactable objects
        interact_box = MagicObject("Assets/Sprites/Interacts/box.png", 0.15)
        interact_box.center_x = 455
        interact_box.center_y = 275
        self.scene.add_sprite("Interacts", interact_box)

        # Load textures for when targeting is occurring
        super().setup_target_sprites()

        # Input Handler
        self.ih = InputHandler(self.wizard, self.familiar, self)

        super().setup_physics()


class LevelThree(GameScreen):
    def __init__(self):
        super().__init__()
        self.next_level = QuitScreen()
        self.text_camera = None

    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        self.text_camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.button_plats.clear()
        self.lever_plats.clear()
        self.player_on_lever = False

        # name of map to load
        map_name = "Assets\\Maps\\Level_3_map.json"

        self.button_count = 5
        self.lever_count = 6
        super().setup_layer_options(self.lever_count, self.button_count)

        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, self.layer_options)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        super().setup()

        #Add moving platforms
        # Button platforms here
        button_plat = arcade.Sprite("Assets/Sprites/moving_platform_01.png", 2)
        button_plat.center_x = 200
        button_plat.center_y = 58
        button_plat.change_x = 0
        button_plat.change_y = 0
        self.button_plats.append([button_plat, 470, 200, 'h'])  # [plat, end, start, dir]
        self.scene.add_sprite("Platforms", button_plat)

        button_plat = arcade.Sprite("Assets/Sprites/moving_platform_01.png", 2)
        button_plat.center_x = 1120
        button_plat.center_y = 328
        self.button_plats.append([button_plat, 1010, 1120, 'h'])  # [plat, end, start, dir]
        self.scene.add_sprite("Platforms", button_plat)

        button_plat = arcade.Sprite("Assets/Sprites/moving_platform_02_v.png", 1.9)
        button_plat.center_x = 920
        button_plat.center_y = 365
        self.button_plats.append([button_plat, 475, 365, 'v'])  # [plat, end, start, dir]
        self.scene.add_sprite("Platforms", button_plat)

        button_plat = arcade.Sprite("Assets/Sprites/moving_platform_02.png", 2)
        button_plat.center_x = 710
        button_plat.center_y = 420
        self.button_plats.append([button_plat, 370, 420, 'v'])  # [plat, end, start, dir]
        self.scene.add_sprite("Platforms", button_plat)

        button_plat = arcade.Sprite("Assets/Sprites/moving_platform_01.png", 2)
        button_plat.center_x = 570
        button_plat.center_y = 550
        self.button_plats.append([button_plat, 450, 550, 'v'])  # [plat, end, start, dir]
        self.scene.add_sprite("Platforms", button_plat)

        # Lever platforms here
        lever_plat = arcade.Sprite("Assets/Sprites/moving_platform_01.png", 2)
        lever_plat.center_x = 810
        lever_plat.center_y = 58
        lever_plat.change_x = 0
        lever_plat.change_y = 0
        self.lever_plats.append([lever_plat, False, True, 1070, 810, 'h'])  # [plat, end, start, dir]
        self.scene.add_sprite("Platforms", lever_plat)

        lever_plat = arcade.Sprite("Assets/Sprites/moving_platform_02_v.png", 1.9)
        lever_plat.center_x = 740
        lever_plat.center_y = 75
        self.lever_plats.append([lever_plat, False, True, 175, 75, 'v'])  # [plat, end, start, dir]
        self.scene.add_sprite("Platforms", lever_plat)

        lever_plat = arcade.Sprite("Assets/Sprites/moving_platform_02_v.png", 1.9)
        lever_plat.center_x = 103
        lever_plat.center_y = 255
        self.lever_plats.append([lever_plat, False, True, 375, 255, 'v'])  # [plat, end, start, dir]
        self.scene.add_sprite("Platforms", lever_plat)

        lever_plat = arcade.Sprite("Assets/Sprites/moving_platform_02_v.png", 1.9)
        lever_plat.center_x = 1017
        lever_plat.center_y = 370
        self.lever_plats.append([lever_plat, False, True, 475, 370, 'v'])  # [plat, end, start, dir]
        self.scene.add_sprite("Platforms", lever_plat)

        lever_plat = arcade.Sprite("Assets/Sprites/moving_platform_02_v.png", 1.9)
        lever_plat.center_x = 952
        lever_plat.center_y = 340
        self.lever_plats.append([lever_plat, False, True, 445, 340, 'v'])  # [plat, end, start, dir]
        self.scene.add_sprite("Platforms", lever_plat)

        lever_plat = arcade.Sprite("Assets/Sprites/moving_platform_01.png", 1.9)
        lever_plat.center_x = 820
        lever_plat.center_y = 345
        self.lever_plats.append([lever_plat, False, True, 920, 820, 'h'])  # [plat, end, start, dir]
        self.scene.add_sprite("Platforms", lever_plat)

        #Wizard Spawn
        self.wizard.position = (45, SPAWN_Y - 40)
        #self.wizard.position = (45, SPAWN_Y + 100)

        #Familiar Spawn
        self.familiar.position = (1220, SPAWN_Y - 50)
        #self.familiar.position = (1220, SPAWN_Y + 100)

        # Adding interactable objects
        interact_box = MagicObject("Assets/Sprites/Interacts/rectangle.png", 0.16)
        interact_box.center_x = 585
        interact_box.center_y = 440
        self.scene.add_sprite("Interacts", interact_box)

        interact_box = MagicObject("Assets/Sprites/Interacts/box.png", 0.12)
        interact_box.center_x = 120
        interact_box.center_y = 335
        self.scene.add_sprite("Interacts", interact_box)

        # Load textures for when targeting is occurring
        super().setup_target_sprites()

        # Input Handler
        self.ih = InputHandler(self.wizard, self.familiar, self)

        super().setup_physics()

    def on_draw(self):
        self.clear()
        self.manager.draw()
        self.scene.draw()

        self.text_camera.use()

        arcade.draw_text("Hey Wizard! Press E to swap between targets (if in range).", 100, 530,
                         arcade.color.AFRICAN_VIOLET, 12, 80)

        super().handle_fade()



def load_texture_pair(filename):
    """Load a texture pair from the file at filename"""
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True),
    ]


class SpecialSprite(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.can_move = True


class PlayerCharacter(SpecialSprite):
    """Character class for player sprites with additional sprites"""
    def __init__(self, main_path, scaling):
        super().__init__()

        self.death = False
        self.death_ctr = 0
        self.character_face_direction = RIGHT_FACE

        # Used for flipping between image sequences
        self.cur_texture = 0
        self.scale = scaling

        # State variables
        self.jumping = False
        self.can_move = True
        # self.climbing = False
        # self.on_ladder = False

        # --- Load the textures ---

        # Load idle texture
        self.idle_texture_pair = load_texture_pair(f"{main_path}_idle.png")

        # Load walking and death animation textures
        self.walk_textures = []
        self.death_textures = []
        for i in range(8):
            texture = load_texture_pair(f"{main_path}_walk_{i}.png")
            self.walk_textures.append(texture)
            texture = load_texture_pair(f"{main_path}_death_{i}.png")
            self.death_textures.append(texture)

        # Set current texture and hitbox
        self.texture = self.idle_texture_pair[0]
        self.hit_box = self.texture.hit_box_points

    def update_animation(self, delta_time: float = 1 / 60):

        # Death Animation
        if self.death:
            self.death_ctr = (self.death_ctr + 1) % (8 * PLAYER_UPDATES_PER_FRAME)
            frame = self.death_ctr // PLAYER_UPDATES_PER_FRAME
            self.texture = self.death_textures[frame][self.character_face_direction]
            return

        # Figure out if we need to flip face left or right
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACE:
            self.character_face_direction = LEFT_FACE
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACE:
            self.character_face_direction = RIGHT_FACE

        # Idle animation
        if self.change_x == 0 and self.change_y == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        # Walking animation
        self.cur_texture += 1
        if self.cur_texture > (8 * PLAYER_UPDATES_PER_FRAME) - 1:
            self.cur_texture = 0
        frame = self.cur_texture // PLAYER_UPDATES_PER_FRAME
        direction = self.character_face_direction
        self.texture = self.walk_textures[frame][direction]

    def die(self):
        self.death_ctr = 0
        self.death = True
        self.change_x = 0
        self.change_y = 0

    def alive(self):
        self.death_ctr = 0
        self.death = False


class MagicObject(SpecialSprite):
    """Object class for casting spells on an object"""

    def __init__(self, main_path, scaling):
        super().__init__()

        # Used for flipping between image sequences
        self.cur_texture = 0
        self.scale = scaling

        # State variables
        self.can_move = True

        # Set current texture and hitbox
        self.texture = arcade.load_texture(f"{main_path}")
        self.hit_box = self.texture.hit_box_points


# region InputHandler
class InputHandler:
    """Handles Input based off a given key press"""
    def __init__(self, wiz: PlayerCharacter, cat: PlayerCharacter, view: GameScreen):
        """To add a command, add the key to press to the list as well and assign the correct object constructor"""
        self.commands = \
            {
                arcade.key.A: MoveLeftCommand(wiz),
                arcade.key.D: MoveRightCommand(wiz),
                arcade.key.W: JumpCommand(wiz),
                arcade.key.S: SpellCommand(wiz, self, view),
                arcade.key.LEFT: MoveLeftCommand(cat),
                arcade.key.RIGHT: MoveRightCommand(cat),
                arcade.key.UP: JumpCommand(cat),
                arcade.key.R: Reset(view),
                arcade.key.ESCAPE: Quit(view),
                arcade.key.L: SkipLevel(view),
                arcade.key.E: AlternateTargets(view)
            }

    def handle_input(self, key_pressed):
        """Simply picks the command"""
        if key_pressed in self.commands:
            return self.commands[key_pressed]
        return None

    def bind(self, key_pressed, command):
        if key_pressed in self.commands:
            self.commands[key_pressed] = command

    def unbind(self, key_pressed):
        if key_pressed in self.commands:
            self.commands[key_pressed] = None


class Command:
    """An abstract class used for all command classes"""
    def __init__(self, sprite: SpecialSprite):
        self.sprite = sprite

    @abstractmethod
    def __call__(self):
        pass

    @abstractmethod
    def undo(self):
        pass


class JumpCommand(Command):
    """Makes the PlayerCharacter jump"""
    def __init__(self, sprite: PlayerCharacter):
        super().__init__(sprite)
        self.sprite = sprite

    def __call__(self):
        if not self.sprite.jumping and self.sprite.can_move:
            self.sprite.change_y = PLAYER_JS

    def undo(self):
        self.sprite.change_y = 0


class MoveLeftCommand(Command):
    """Makes the SpecialSprite move left"""
    def __init__(self, sprite: SpecialSprite):
        super().__init__(sprite)
        self.called = False

    def __call__(self):
        self.called = self.sprite.can_move
        if self.called:
            self.sprite.change_x -= PLAYER_MS

    def undo(self):
        if self.called and self.sprite.can_move:
            self.sprite.change_x += PLAYER_MS


class MoveRightCommand(Command):
    """Makes the SpecialSprite move right"""
    def __init__(self, sprite: SpecialSprite):
        super().__init__(sprite)
        self.called = False

    def __call__(self):
        self.called = self.sprite.can_move
        if self.called:
            self.sprite.change_x += PLAYER_MS

    def undo(self):
        if self.called and self.sprite.can_move:
            self.sprite.change_x -= PLAYER_MS


class SpellCommand(Command):
    """Finds the target and makes the player stop moving while allowing them to move the target"""
    def __init__(self, sprite: PlayerCharacter, ih: InputHandler, view: GameScreen):
        super().__init__(sprite)
        self.ih = ih
        self.view = view
        self.target = None
        self.called = False

    def __call__(self):
        """Locks wizard movement and Calls a function back in game.py that returns the target sprite to move instead"""
        # First, unbind wizard movements and halt all movement
        if not self.sprite.can_move:
            return

        self.called = True
        self.sprite.change_x = 0
        self.sprite.change_y = 0
        self.sprite.can_move = False

        # Find Target
        self.target = self.view.get_target_sprite()
        if not self.target:
            return

        # Adjust Movement Commands when target exists
        self.ih.bind(arcade.key.A, MoveBoxLeftCommand(self.target))
        self.ih.bind(arcade.key.D, MoveBoxRightCommand(self.target))

    def undo(self):
        if not self.called:
            return

        if self.target:
            self.target.change_x = 0
            self.target.change_y = 0
        self.ih.bind(arcade.key.W, JumpCommand(self.sprite))
        self.ih.bind(arcade.key.A, MoveLeftCommand(self.sprite))
        self.ih.bind(arcade.key.D, MoveRightCommand(self.sprite))
        self.sprite.can_move = True


class MoveBoxRightCommand(MoveRightCommand):
    def __init__(self, sprite: SpecialSprite):
        super().__init__(sprite)

    def __call__(self):
        super().__call__()

    def undo(self):
        if self.called and self.sprite.can_move:
            self.sprite.change_x = 0


class MoveBoxLeftCommand(MoveLeftCommand):
    def __init__(self, sprite: SpecialSprite):
        super().__init__(sprite)

    def __call__(self):
        super().__call__()

    def undo(self):
        if self.called and self.sprite.can_move:
            self.sprite.change_x = 0


class Reset(Command):
    """Reset the level mid-round"""
    def __init__(self, gs: GameScreen):
        super().__init__(None)
        self.gs = gs

    def __call__(self):
        self.gs.reset()

    def undo(self):
        return


class Quit(Command):
    """Quit the game mid-game"""
    def __init__(self, gs: GameScreen):
        super().__init__(None)
        self.gs = gs

    def __call__(self):
        arcade.exit()

    def undo(self):
        return


class SkipLevel(Command):
    """Skip to the next level if one exists"""
    def __init__(self, gs: GameScreen):
        super().__init__(None)
        self.gs = gs

    def __call__(self):
        if self.gs.next_level:
            self.gs.next_level_prep()

    def undo(self):
        return


class AlternateTargets(Command):
    """Swap Targets if a different one is available"""
    def __init__(self, view: GameScreen):
        super().__init__(None)
        self.view = view
        self.target = None

    def __call__(self):
        """Call will find current target, then check to see if any other interactables can be the target"""
        # Find Target
        self.target = self.view.get_target_sprite()
        if not self.target:
            return

        # Loop through all available targets
        # To do: Make loop happen by index so there is no box priority
        index = self.view.scene["Interacts"].index(self.target)
        length = len(self.view.scene["Interacts"])
        for i in range(1, length):
            targetIndex = (index + i) % length
            target = self.view.scene["Interacts"][targetIndex]
            if self.view.in_target_range(target):
                self.view.target = target

    def undo(self):
        return

# endregion