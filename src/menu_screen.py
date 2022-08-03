import arcade
import arcade.gui
from src.game import LevelZero, LevelThree, LevelOne
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT

from src.quit_screen import QuitScreen


class MenuScreen(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)

        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Set background color
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        # Alignment boxes
        self.v_box = arcade.gui.UIBoxLayout()
        self.h_box = arcade.gui.UIBoxLayout(vertical=False)

        # Load button textures
        self.button_texture = arcade.load_texture("Assets/UI/button_0.png")
        self.pressed_button_texture = arcade.load_texture("Assets/UI/button_1.png")

        # Load title texture
        self.title_texture = arcade.load_texture("Assets/UI/title.png")

        # Load background texture
        self.background = arcade.load_texture("Assets/UI/wiz_det_start_screen.png")

    def on_show_view(self):
        # Title
        game_title = arcade.gui.UITextureButton(texture=self.title_texture, scale=0.3)
        self.v_box.add(game_title.with_space_around(bottom=50))

        # Start button
        start_button = arcade.gui.UITextureButton(texture=self.button_texture,
                                                  texture_pressed=self.pressed_button_texture)
        self.h_box.add(start_button.with_space_around(right=20))
        start_button.on_click = self.on_click_start

        # Quit button
        quit_button = arcade.gui.UITextureButton(texture=self.button_texture,
                                                 texture_pressed=self.pressed_button_texture)
        quit_button.on_click = self.on_click_quit
        self.h_box.add(quit_button.with_space_around(left=20))
        self.v_box.add(self.h_box.with_space_around(bottom=20))

        # Credits button
        credits_button = arcade.gui.UITextureButton(texture=self.button_texture,
                                                    texture_pressed=self.pressed_button_texture,
                                                    scale=0.7)
        credits_button.on_click = self.on_click_credits
        self.v_box.add(credits_button.with_space_around(bottom=20))

        self.manager.add(
            arcade.gui.UITexturePane(
                child=arcade.gui.UIAnchorWidget(
                    anchor_x="center_x",
                    anchor_y="center_y",
                    child=self.v_box),
                tex=self.background,
                padding=(220, 220, 220, 220)
            ),
        )

    def on_click_quit(self, event):
        arcade.exit()

    def on_click_start(self, event):
        game_screen = LevelZero()
        self.window.show_view(game_screen)

    def on_click_credits(self, event):
        message_box = arcade.gui.UIMessageBox(
            width=SCREEN_WIDTH / 2,
            height=SCREEN_HEIGHT / 2,
            message_text=(
                "\n     Credits Screen\n\n"
                "       Game made by Julia McKay, Chandler Fox, and Audrey DeHoog\n"
                "       Audio from freesound.org\n"
                "       Sprites and other game art from itch.io\n"
            ),
            buttons=["Back"]
        )
        self.manager.add(message_box)

    def on_draw(self):
        self.clear()
        self.manager.draw()

        # Start Button Text
        arcade.draw_text("Start",
                         -150,
                         (SCREEN_HEIGHT // 2) - 10,
                         arcade.color.WHITE_SMOKE,
                         25,
                         width=SCREEN_WIDTH,
                         align="center",
                         font_name="Kenney Mini Square")

        # Quit Button Text
        arcade.draw_text("Quit",
                         150,
                         (SCREEN_HEIGHT // 2) - 10,
                         arcade.color.WHITE_SMOKE,
                         25,
                         width=SCREEN_WIDTH,
                         align="center",
                         font_name="Kenney Mini Square")

        # Credits Button Text
        arcade.draw_text("Credits",
                         0,
                         (SCREEN_HEIGHT // 2) - 105,
                         arcade.color.WHITE_SMOKE,
                         15,
                         width=SCREEN_WIDTH,
                         align="center",
                         font_name="Kenney Mini Square")
