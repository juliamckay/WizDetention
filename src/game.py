import arcade
from abc import abstractmethod
import arcade.gui
from src.constants import *
from src.env_interaction import *
from src.quit_screen import QuitScreen
from src.constants import ACID_UPDATES_PER_FRAME


class GameScreen(arcade.View):
    def __init__(self):
        """Create the Window here and Declare game variables"""
        # Create the ViewPort
        super().__init__()
        arcade.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)

        #Next scene to load
        next_level = None

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
        self.flipped_right = None
        self.flipped_left = None
        self.lever_right = True
        self.lever_left = False

        # Moving Platform Info
        self.lever_count = 0
        self.button_count = 0
        self.button_plats = []
        self.lever_plats = []
        self.player_on_lever = False
        self.moving_vel = 2

        # Physics Engine
        self.pe1 = None
        self.pe2 = None
        self.pe3 = None
        self.ty = None

    def on_show_view(self):
        self.setup()
        arcade.set_background_color(arcade.color.GRAY)

    def on_draw(self):
        self.clear()
        arcade.draw_text("Hey Wizard! Hold S when close to move the box!", 150, 650, arcade.color.PURPLE, 12, 80)
        arcade.draw_text("Only the cat can fit through that...", 800, 100, arcade.color.ANDROID_GREEN, 12, 80)
        arcade.draw_text("Press R to reset the level", 100, 200, arcade.color.PURPLE, 12, 80)
        arcade.draw_text("Press Esc to quit the game", 100, 180, arcade.color.PURPLE, 12, 80)
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
            max_y = current_plat[1]
            min_y = current_plat[2]
            layer_name = "Button " + str(i)
            current_plat[0] = button_platform(self.scene, self.wizard, self.familiar,
                                                 layer_name, current_plat[0],
                                                 max_y, min_y, self.moving_vel)

        # check for collision with levers
        for i in range(1, self.lever_count + 1):
            current_plat = self.lever_plats[i-1]
            layer_name = "Lever " + str(i)
            self.player_on_lever, current_plat[1], current_plat[2], self.lever_left, self.lever_right, self.current_lever= \
                levers_check_col(self.scene, layer_name, self.wizard, self.familiar,
                                 current_plat[1], current_plat[2], self.player_on_lever, self.lever_left, self.lever_right)
            if self.lever_left and self.player_on_lever:
                self.current_lever[0].texture = self.flipped_left
            if self.lever_right and self.player_on_lever:
                self.current_lever[0].texture = self.flipped_right
            #move platform accordingly
            current_plat[0] = lever_platform(current_plat[0], current_plat[1],
                                                current_plat[2], current_plat[3], current_plat[4], self.moving_vel)

        # See if player has collided w anything from the Don't Touch layer
        if arcade.check_for_collision_with_list(self.wizard, self.scene["Dont Touch"]):
            self.wizard.position = (SPAWN_X, SPAWN_Y)
        if arcade.check_for_collision_with_list(self.familiar, self.scene["Dont Touch"]):
            self.familiar.position = (SPAWN_X + 30, SPAWN_Y - 10)

        # check if BOTH players have collided with door, advance to next level
        # for now it just goes to quit screen since there is no level 2 yet
        if arcade.check_for_collision_with_list(self.wizard, self.scene["Door"]) and \
                arcade.check_for_collision_with_list(self.familiar, self.scene["Door"]):
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
    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        self.next_level = LevelOne()

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
        self.levers_list = self.tile_map.sprite_lists.get("Lever 1")
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

        self.moving_platform_1 = arcade.Sprite("Assets/Sprites/moving_platform_01.png", PLATFORM_SCALING)
        self.moving_platform_1.center_x = 1175
        self.moving_platform_1.center_y = 380
        self.move_plat_1_up = True
        self.move_plat_1_down = False
        self.moving_platform_1.change_x = 0
        self.moving_platform_1.change_y = 0
        self.lever_plats.append([self.moving_platform_1, True, False, 380, 250])
        self.scene.add_sprite("Platforms", self.moving_platform_1)

        self.moving_platform_2 = arcade.Sprite("Assets/Sprites/moving_platform_02_v.png", PLATFORM_SCALING_V)
        self.moving_platform_2.center_x = 600
        self.moving_platform_2.center_y = 455
        self.moving_platform_2.change_x = 0
        self.moving_platform_2.center_y = 0
        self.button_plats.append([self.moving_platform_2, 555, 455])
        self.scene.add_sprite("Platforms", self.moving_platform_2)

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
        self.interact_box = MagicObject("Assets/Sprites/blue_square.png", 0.15)
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

class LevelOne(GameScreen):
    def setup(self):
        """Set up the game here. Call this function to restart the game."""
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

        #Add in moving platforms
        #Lever platforms here

        #Button platforms here

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
        self.interact_box = MagicObject("Assets/Sprites/blue_square.png", 0.15)
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

        # Load simple texture pairs
        self.idle_texture_pair = load_texture_pair(f"{main_path}_idle.png")
        # self.jump_texture_pair = load_texture_pair(f"{main_path}_jump.png")
        # self.fall_texture_pair = load_texture_pair(f"{main_path}_fall.png")

        # Set current texture and hitbox
        self.texture = self.idle_texture_pair[0]
        self.hit_box = self.texture.hit_box_points


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

    def __call__(self):
        """Locks wizard movement and Calls a function back in game.py that returns the target sprite to move instead"""
        # First, unbind wizard movements and halt all movement
        self.sprite.change_x = 0
        self.sprite.change_y = 0
        self.sprite.can_move = False

        # Find Target
        target = self.view.get_target_sprite()
        if not target:
            return

        # Adjust Movement Commands when target exists
        self.ih.bind(arcade.key.A, MoveLeftCommand(target))
        self.ih.bind(arcade.key.D, MoveRightCommand(target))

    def undo(self):
        self.ih.bind(arcade.key.W, JumpCommand(self.sprite))
        self.ih.bind(arcade.key.A, MoveLeftCommand(self.sprite))
        self.ih.bind(arcade.key.D, MoveRightCommand(self.sprite))
        self.sprite.can_move = True


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
