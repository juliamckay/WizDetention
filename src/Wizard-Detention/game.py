import arcade
import arcade.gui
from command import *
from constants import *
from env_interaction import *

class GameScreen(arcade.View):
    def __init__(self):
        """Create the Window here and Declare game variables"""
        # Create the ViewPort
        super().__init__()
        arcade.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)

        # Create the manager
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Variable Declarations
        self.ih = None

        # Game screen
        self.tile_map = None
        self.scene = None

        # Player Sprites
        self.wizard_sprite = None
        self.familiar_sprite = None

        #Moving Platform Sprites
        self.moving_platform_1 = None
        self.moving_vel = 2
        self.move_plat_1_up = True
        self.move_plat_1_down = False

        self.moving_platform_2 = None
        self.move_plat_2_up = True
        self.move_plat_2_down = False

        # Physics Engine
        self.pe1 = None
        self.pe2 = None
        self.ty = None

    def setup(self):
        """Set up the game here. Call this function to restart the game."""
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
        }

        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        #Adding Moving Platform Sprite
        self.moving_platform_1 = arcade.Sprite("Assets\\Sprites\\moving_platform_01.png", PLATFORM_SCALING)
        self.moving_platform_1.center_x = 1175
        self.moving_platform_1.center_y = 380
        self.scene.add_sprite("Platforms", self.moving_platform_1)

        self.moving_platform_2 = arcade.Sprite("Assets\\Sprites\\moving_platform_02_v.png", PLATFORM_SCALING_V)
        self.moving_platform_2.center_x = 600
        self.moving_platform_2.center_y = 455
        self.scene.add_sprite("Platforms", self.moving_platform_2)

        # Player Sprite Setup
        self.scene.add_sprite_list("Wiz")
        self.scene.add_sprite_list("Cat")
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)

        self.wizard_sprite = arcade.Sprite("Assets\\Sprites\\R_witch_stationary.png", WIZARD_SCALING)
        self.wizard_sprite.position = (SPAWN_X, SPAWN_Y)
        self.scene.add_sprite("Wiz", self.wizard_sprite)

        self.familiar_sprite = arcade.Sprite("Assets\\Sprites\\cat05.png", FAMILIAR_SCALING)
        self.familiar_sprite.position = (SPAWN_X + 30, SPAWN_Y - 10)
        self.scene.add_sprite("Cat", self.familiar_sprite)

        self.ih = InputHandler(self.wizard_sprite, self.familiar_sprite)

        self.pe1 = arcade.PhysicsEnginePlatformer(self.wizard_sprite, gravity_constant=GRAVITY,
                                                  walls=self.scene["Platforms"])
        self.pe2 = arcade.PhysicsEnginePlatformer(self.familiar_sprite, gravity_constant=GRAVITY,
                                                  walls=self.scene["Platforms"])

    def on_show_view(self):
        self.setup()
        arcade.set_background_color(arcade.color.GRAY)

    def on_draw(self):
        self.clear()
        self.manager.draw()
        self.scene.draw()

    def on_key_press(self, key, mods):
        # Check command.py for commands
        command = self.ih.handle_input(key)
        if command:
            command()

    def on_key_release(self, key, mods):
        command = self.ih.handle_input(key)
        if command:
            command.undo()

    def on_update(self, delta_time):
        self.pe1.update()
        self.pe2.update()


        self.moving_platform_2 = button_platform(self.scene, self.wizard_sprite, self.familiar_sprite,
                                                 "Button 1", self.moving_platform_2,
                                                 555, 455, self.moving_vel)

        self.moving_platform_1, self.move_plat_1_up, self.move_plat_1_down =\
            lever_platform(self.scene, self.familiar_sprite,
                       "Lever 1", self.moving_platform_1, self.move_plat_1_up,
                       self.move_plat_1_down, 380, 250, self.moving_vel)

        self.moving_platform_1, self.move_plat_1_up, self.move_plat_1_down = \
            lever_platform(self.scene, self.wizard_sprite,
                           "Lever 1", self.moving_platform_1, self.move_plat_1_up,
                           self.move_plat_1_down, 380, 250, self.moving_vel)

        #See if player has collided w anything from the Dont Touch layer
        if arcade.check_for_collision_with_list(self.wizard_sprite, self.scene["Dont Touch"]):
            self.wizard_sprite.position = (SPAWN_X, SPAWN_Y)
        if arcade.check_for_collision_with_list(self.familiar_sprite, self.scene["Dont Touch"]):
            self.familiar_sprite.position = (SPAWN_X + 30, SPAWN_Y - 10)
