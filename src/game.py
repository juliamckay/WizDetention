import time

import arcade
from abc import abstractmethod
import arcade.gui
from src.constants import *
from src.env_interaction import *
from src.quit_screen import QuitScreen
from src.constants import ACID_UPDATES_PER_FRAME, PLAYER_UPDATES_PER_FRAME


class GameScreen(arcade.View):
    def __init__(self):
        """Create the Window here and Declare game variables"""
        # Create the ViewPort
        super().__init__()
        arcade.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)

        #Next scene to load
        self.next_level = None

        # Create the manager
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Variable Declarations
        self.ih = None
        self.interacting = False
        self.in_place = False

        # Game screen
        self.tile_map = None
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

        self.interact_box = None
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
        self.pe3 = None
        self.ty = None

        # Game Audio
        self.main_theme = arcade.load_sound("Assets/Audio/8bit-harmony.wav", False)
        self.main_player = None
        self.death_noise = arcade.load_sound("Assets/Audio/noise-hit-1.mp3", False)

    def on_show_view(self):
        self.setup()
        arcade.set_background_color(arcade.color.GRAY)

    def on_draw(self):
        self.clear()
        self.manager.draw()
        self.scene.draw()

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

        self.pe3.update()

        # Check for if target is within vision of player character
        # For now, a simple within-range check around the wizard for potential targets
        if self.target:
            # self.play_target_animation(delta_time)
            self.target_anim_sprite.position = self.target.position
            if(arcade.get_distance(self.wizard.center_x, self.wizard.center_y,
                                   self.target.center_x, self.target.center_y) > 200):
                # Halt it's movement
                self.target.change_x = 0
                self.target.change_y = 0

                # Deselect the target
                self.target_anim_sprite.alpha = 0
                self.target = None
            else:
                self.play_target_animation(delta_time)
        else:
            # Select the target
            for target in self.scene["Interacts"]:
                if(arcade.get_distance(self.wizard.center_x, self.wizard.center_y,
                                       target.center_x, target.center_y) < 100):
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
        if arcade.check_for_collision_with_list(self.wizard, self.scene["Dont Touch"]) or \
                arcade.check_for_collision_with_list(self.familiar, self.scene["Dont Touch"]):
            time.sleep(0.05)
            self.setup()
        """
        if arcade.check_for_collision_with_list(self.wizard, self.scene["Dont Touch"]):
            self.wizard.position = (SPAWN_X, SPAWN_Y)
        if arcade.check_for_collision_with_list(self.familiar, self.scene["Dont Touch"]):
            self.familiar.position = (SPAWN_X + 30, SPAWN_Y - 10)"""

        # check if BOTH players have collided with door, advance to next level
        # for now it just goes to quit screen since there is no level 2 yet
        if arcade.check_for_collision_with_list(self.wizard, self.scene["Door"]) and \
                arcade.check_for_collision_with_list(self.familiar, self.scene["Door"]):
            if isinstance(self.next_level, QuitScreen):
                self.main_theme.stop(self.main_player)
            else:
                self.next_level.main_player = self.main_player
            self.window.show_view(self.next_level)

    # region helpers

    def get_target_sprite(self):
        return self.target

    def play_target_animation(self, delta_time):
        self.cooldown += delta_time
        if self.cooldown > 0.1:
            self.target_anim_sprite.texture = self.target_anim[self.curr_targ_anim_count]
            self.curr_targ_anim_count = (self.curr_targ_anim_count + 1) % 4
            self.cooldown = 0
    # endregion


class LevelZero(GameScreen):
    def __init__(self):
        super().__init__()
        self.text_camera = None

    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        self.next_level = LevelOne()
        self.button_plats.clear()
        self.lever_plats.clear()
        self.player_on_lever = False

        #text overlay setup
        self.text_camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

        # play background music
        self.main_player = arcade.play_sound(self.main_theme, 1.0, 0.0, True, 1.0)

        # name of map to load
        map_name = "Assets\\Maps\\Level_0_map.json"
        layer_options = {
            "Platforms": {
                "use_spatial_hash": True,
            },
            "Dont Touch": {
                "use_spatial_hash": True,
            },
            "Lever 1": {
                "use_spatial_hash": True,
            },
            "Button 1": {
                "use_spatial_hash": True,
            },
            "Door": {
                "use_spatial_hash": True,
            },
        }

        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Lever animation setup
        self.flipped_right = arcade.load_texture("Assets/Sprites/Levers/lever_0.png")
        self.flipped_left = arcade.load_texture("Assets/Sprites/Levers/lever_1.png")

        # Acid animation setup
        self.acid_hazard_list = self.tile_map.sprite_lists.get("Dont Touch")
        for i in range(4):
            texture = arcade.load_texture(f"Assets/Sprites/Acid/acid_{i}.png")
            self.acid_textures.append(texture)

        # Adding Moving Platform Sprite
        self.button_count = 1
        self.lever_count = 1

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

        # self.stop_interact_area = arcade.Sprite("Assets\\Sprites\\red_square.png", 0.15)
        # self.stop_interact_area.center_x = 570
        # self.stop_interact_area.center_y = 570

        # self.scene.add_sprite("Interacts", self.stop_interact_area)

        # Player Sprite Setup
        self.scene.add_sprite_list("Interacts")
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

        # Adding interactable objects
        self.interact_box = MagicObject("Assets/Sprites/Interacts/box.png", 0.15)
        self.interact_box.center_x = 400
        self.interact_box.center_y = 595
        self.scene.add_sprite("Interacts", self.interact_box)

        # Load textures for when targeting is occurring
        for i in range(4):
            texture = arcade.load_texture(f"Assets/Sprites/Targets/TargetT1_{i}.png")
            self.target_anim.append(texture)
        self.target_anim_sprite = arcade.Sprite("Assets/Sprites/Targets/TargetT1_0.png")
        self.target_anim_sprite.alpha = 0
        self.scene.add_sprite("Targeting", self.target_anim_sprite)

        # Input Handler
        self.ih = InputHandler(self.wizard, self.familiar, self)

        # Physics Engines
        self.pe1 = arcade.PhysicsEnginePlatformer(self.wizard, gravity_constant=GRAVITY,
                                                  walls=(self.scene["Platforms"], self.scene["Interacts"]))
        self.pe2 = arcade.PhysicsEnginePlatformer(self.familiar, gravity_constant=GRAVITY,
                                                  walls=(self.scene["Platforms"], self.scene["Interacts"]))
        self.pe3 = arcade.PhysicsEnginePlatformer(self.interact_box, gravity_constant=0)

    def on_draw(self):
        super(LevelZero, self).on_draw()

        self.text_camera.use()
        arcade.draw_text("Hey Wizard! Hold S when close to move the box!", 150, 700, arcade.color.AFRICAN_VIOLET, 12, 80)
        arcade.draw_text("Only the cat can fit through that...", 800, 150, arcade.color.AMBER, 12, 80)
        arcade.draw_text("Press R to reset the level", 40, 270, arcade.color.WHITE, 12, 80)
        arcade.draw_text("Press Esc to quit the game", 40, 250, arcade.color.WHITE, 12, 80)
        #self.manager.draw()
        #self.scene.draw()

class LevelOne(GameScreen):
    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        self.button_plats.clear()
        self.lever_plats.clear()
        self.player_on_lever = False
        self.next_level = LevelTwo()

        # name of map to load
        map_name = "Assets\\Maps\\Level_1_map.json"
        layer_options = {
            "Platforms": {
                "use_spatial_hash": True,
            },
            "Dont Touch": {
                "use_spatial_hash": True,
            },
            "Lever 1": {
                "use_spatial_hash": True,
            },
            "Lever 2": {
                "use_spatial_hash": True,
            },
            "Button 1": {
                "use_spatial_hash": True,
            },
            "Button 2": {
                "use_spatial_hash": True,
            },
            "Button 3": {
                "use_spatial_hash": True,
            },
            "Button 4": {
                "use_spatial_hash": True,
            },
            "Button 5": {
                "use_spatial_hash": True,
            },
            "Button 6": {
                "use_spatial_hash": True,
            },
            "Door": {
                "use_spatial_hash": True,
            },
        }

        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Lever animation setup
        self.flipped_right = arcade.load_texture("Assets/Sprites/Levers/lever_0.png")
        self.flipped_left = arcade.load_texture("Assets/Sprites/Levers/lever_1.png")

        # Add in moving platforms
        self.button_count = 6
        self.lever_count = 2

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

        # Player Sprite Setup
        self.scene.add_sprite_list("Interacts")
        self.scene.add_sprite_list("Wiz")
        self.scene.add_sprite_list("Cat")
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)
        #self.scene.add_sprite_list_after("Wiz", "Foreground")

        # self.wizard_sprite = arcade.Sprite("Assets/Sprites/Wizard/wizard_idle.png", WIZARD_SCALING)
        self.wizard = PlayerCharacter("Assets/Sprites/Wizard/wizard", WIZARD_SCALING)
        self.wizard.position = (SPAWN_X, SPAWN_Y)
        self.scene.add_sprite("Wiz", self.wizard)

        # self.familiar_sprite = arcade.Sprite("Assets/Sprites/Familiar/familiar_idle.png", FAMILIAR_SCALING)
        self.familiar = PlayerCharacter("Assets/Sprites/Familiar/familiar", FAMILIAR_SCALING)
        self.familiar.position = (SPAWN_X + 30, SPAWN_Y - 10)
        self.scene.add_sprite("Cat", self.familiar)

        # Adding interactable objects
        self.interact_box = MagicObject("Assets/Sprites/Interacts/rectangle.png", 0.15)
        self.interact_box.center_x = 480
        self.interact_box.center_y = 140
        self.scene.add_sprite("Interacts", self.interact_box)

        # Load textures for when targeting is occurring
        for i in range(4):
            texture = arcade.load_texture(f"Assets/Sprites/Targets/TargetT1_{i}.png")
            self.target_anim.append(texture)
        self.target_anim_sprite = arcade.Sprite("Assets/Sprites/Targets/TargetT1_0.png")
        self.target_anim_sprite.alpha = 0
        self.scene.add_sprite("Targeting", self.target_anim_sprite)

        # Acid animation setup
        self.acid_hazard_list = self.tile_map.sprite_lists.get("Dont Touch")
        for i in range(4):
            texture = arcade.load_texture(f"Assets/Sprites/Acid/acid_{i}.png")
            self.acid_textures.append(texture)

        # Input Handler
        self.ih = InputHandler(self.wizard, self.familiar, self)

        # Physics Engines
        self.pe1 = arcade.PhysicsEnginePlatformer(self.wizard, gravity_constant=GRAVITY,
                                                  walls=(self.scene["Platforms"], self.scene["Interacts"]))
        self.pe2 = arcade.PhysicsEnginePlatformer(self.familiar, gravity_constant=GRAVITY,
                                                  walls=(self.scene["Platforms"], self.scene["Interacts"]))
        self.pe3 = arcade.PhysicsEnginePlatformer(self.interact_box, gravity_constant=0)

class LevelTwo(GameScreen):
    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        self.next_level = QuitScreen()
        self.button_plats.clear()
        self.lever_plats.clear()
        self.player_on_lever = False

        # name of map to load
        map_name = "Assets\\Maps\\Level_2_map.json"
        layer_options = {
            "Platforms": {
                "use_spatial_hash": True,
            },
            "Dont Touch": {
                "use_spatial_hash": True,
            },
            "Lever 1": {
                "use_spatial_hash": True,
            },
            "Button 1": {
                "use_spatial_hash": True,
            },
            "Door": {
                "use_spatial_hash": True,
            },
        }

        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Lever animation setup
        self.flipped_right = arcade.load_texture("Assets/Sprites/Levers/lever_0.png")
        self.flipped_left = arcade.load_texture("Assets/Sprites/Levers/lever_1.png")

        # Acid animation setup
        self.acid_hazard_list = self.tile_map.sprite_lists.get("Dont Touch")
        for i in range(4):
            texture = arcade.load_texture(f"Assets/Sprites/Acid/acid_{i}.png")
            self.acid_textures.append(texture)

        # Adding Moving Platform Sprite
        self.button_count = 8
        self.lever_count = 1

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

        # Player Sprite Setup
        self.scene.add_sprite_list("Interacts")
        self.scene.add_sprite_list("Wiz")
        self.scene.add_sprite_list("Cat")
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)

        # self.wizard_sprite = arcade.Sprite("Assets/Sprites/Wizard/wizard_idle.png", WIZARD_SCALING)
        self.wizard = PlayerCharacter("Assets/Sprites/Wizard/wizard", WIZARD_SCALING)
        self.wizard.position = (SPAWN_X + 150, SPAWN_Y)
        self.scene.add_sprite("Wiz", self.wizard)

        # self.familiar_sprite = arcade.Sprite("Assets/Sprites/Familiar/familiar_idle.png", FAMILIAR_SCALING)
        self.familiar = PlayerCharacter("Assets/Sprites/Familiar/familiar", FAMILIAR_SCALING)
        self.familiar.position = (SPAWN_X + 30, SPAWN_Y - 10)
        self.scene.add_sprite("Cat", self.familiar)

        # Adding interactable objects
        self.interact_box = MagicObject("Assets/Sprites/Interacts/box.png", 0.15)
        self.interact_box.center_x = 455
        self.interact_box.center_y = 275
        self.scene.add_sprite("Interacts", self.interact_box)

        # Load textures for when targeting is occurring
        for i in range(4):
            texture = arcade.load_texture(f"Assets/Sprites/Targets/TargetT1_{i}.png")
            self.target_anim.append(texture)
        self.target_anim_sprite = arcade.Sprite("Assets/Sprites/Targets/TargetT1_0.png")
        self.target_anim_sprite.alpha = 0
        self.scene.add_sprite("Targeting", self.target_anim_sprite)

        # Input Handler
        self.ih = InputHandler(self.wizard, self.familiar, self)

        # Physics Engines
        self.pe1 = arcade.PhysicsEnginePlatformer(self.wizard, gravity_constant=GRAVITY,
                                                  walls=(self.scene["Platforms"], self.scene["Interacts"]))
        self.pe2 = arcade.PhysicsEnginePlatformer(self.familiar, gravity_constant=GRAVITY,
                                                  walls=(self.scene["Platforms"], self.scene["Interacts"]))
        self.pe3 = arcade.PhysicsEnginePlatformer(self.interact_box, gravity_constant=0)

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
        if self.cur_texture > 7 * PLAYER_UPDATES_PER_FRAME:
            self.cur_texture = 0
        frame = self.cur_texture // PLAYER_UPDATES_PER_FRAME
        direction = self.character_face_direction
        self.texture = self.walk_textures[frame][direction]


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
                arcade.key.ESCAPE: Quit(view)
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

    def __call__(self):
        """Locks wizard movement and Calls a function back in game.py that returns the target sprite to move instead"""
        # First, unbind wizard movements and halt all movement
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
        self.gs.setup()

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
# endregion
