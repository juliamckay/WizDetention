import arcade
import arcade.gui
from Assets.Maps import *
from Assets.Sprites import *
from constants import *
from typing import get_type_hints


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

        # Game screen
        self.tile_map = None
        self.scene = None

        # Player Sprites
        self.wizard_sprite = None
        self.familiar_sprite = None

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
        }

        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

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
        # Wizard keys are WASD
        if key == arcade.key.W:
            if self.pe1.can_jump():
                self.wizard_sprite.change_y = PLAYER_JS
        elif key == arcade.key.A:
            self.wizard_sprite.change_x = -PLAYER_MS
        elif key == arcade.key.D:
            self.wizard_sprite.change_x = PLAYER_MS

        # Familiar keys are Arrow Keys
        elif key == arcade.key.UP:
            if self.pe2.can_jump():
                self.familiar_sprite.change_y = PLAYER_JS
        elif key == arcade.key.LEFT:
            self.familiar_sprite.change_x = -PLAYER_MS
        elif key == arcade.key.RIGHT:
            self.familiar_sprite.change_x = PLAYER_MS

    def on_key_release(self, key, mods):
        # Wizard keys are WASD
        if key == arcade.key.W:
            if self.pe1.can_jump():
                self.wizard_sprite.change_y = 0
        elif key == arcade.key.A or key == arcade.key.D:
            self.wizard_sprite.change_x = 0

        # Familiar keys are Arrow Keys
        elif key == arcade.key.UP:
            if self.pe2.can_jump():
                self.familiar_sprite.change_y = 0
        elif key == arcade.key.LEFT or arcade.key.RIGHT:
            self.familiar_sprite.change_x = 0

    def on_update(self, delta_time):
        self.pe1.update()
        self.pe2.update()
