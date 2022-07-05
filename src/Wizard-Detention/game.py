import arcade
import arcade.gui
from Assets.Maps import *
from Assets.Sprites import *
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SCALING, WIZARD_SCALING, FAMILIAR_SCALING, SPAWN_X, SPAWN_Y


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

        # Player Characters
        self.wizard_list = None
        self.familiar_list = None

        self.wizard_sprite = None
        self.familiar_sprite = None

        # Walls
        self.wall_list = None

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

        self.wizard_list = arcade.SpriteList()
        self.familiar_list = arcade.SpriteList()

        self.wizard_sprite = arcade.Sprite("Assets\\Sprites\\R_witch_stationary.png", WIZARD_SCALING)
        self.wizard_sprite.position = (SPAWN_X, SPAWN_Y)
        self.wizard_list.append(self.wizard_sprite)

        self.familiar_sprite = arcade.Sprite("Assets\\Sprites\\cat05.png", FAMILIAR_SCALING)
        self.familiar_sprite.position = (SPAWN_X + 30, SPAWN_Y - 10)
        self.familiar_list.append(self.familiar_sprite)

        # Walls
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)

    def on_show_view(self):
        self.setup()
        arcade.set_background_color(arcade.color.GRAY)

    def on_draw(self):
        self.clear()
        self.manager.draw()
        self.scene.draw()

        self.wizard_list.draw()
        self.familiar_list.draw()
