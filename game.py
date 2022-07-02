import arcade
import arcade.gui
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SCALING


class GameScreen(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)

        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        #game screen
        self.tile_map = None
        self.scene = None

    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        # name of map to load
        map_name = "Maps/Level_0_map.json"
        layer_options = {
            "Platforms": {
                "use_spatial_hash": True,
            },
        }

        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

    def on_show_view(self):
        self.setup()
        arcade.set_background_color(arcade.color.GRAY)

    def on_draw(self):
        self.clear()
        self.manager.draw()
        self.scene.draw()
