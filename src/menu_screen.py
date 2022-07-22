import arcade
import arcade.gui
from src.game import LevelZero, LevelOne
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT


class QuitButton(arcade.gui.UIFlatButton):
    def on_click(self, event: arcade.gui.UIOnClickEvent):
        arcade.exit()


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

    def on_show_view(self):
        # Title
        game_title = arcade.gui.UITextArea(text="Wizard Detention",
                                           width=500,
                                           height=40,
                                           font_size=30,
                                           font_name="Kenney Future")
        self.v_box.add(game_title.with_space_around(bottom=50))

        # Start button
        start_button = arcade.gui.UIFlatButton(text="Start", width=200)
        self.h_box.add(start_button.with_space_around(right=20))
        start_button.on_click = self.on_click_start

        # Quit button
        quit_button = QuitButton(text="Quit", width=200)
        self.h_box.add(quit_button.with_space_around(left=20))

        self.v_box.add(self.h_box.with_space_around(bottom=20))

        # Credits button
        credits_button = arcade.gui.UIFlatButton(text="Credits", width=100)
        self.v_box.add(credits_button.with_space_around(bottom=20))
        credits_button.on_click = self.on_click_credits

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
        )

    def on_click_start(self, event):
        game_screen = LevelOne()
        self.window.show_view(game_screen)

    def on_click_credits(self, event):
        message_box = arcade.gui.UIMessageBox(
            width=SCREEN_WIDTH / 2,
            height=SCREEN_HEIGHT / 2,
            message_text=(
                "Credits Screen\n"
                "Game made by Julia McKay, Chandler Fox, and Audrey DeHoog"
            ),
            callback=self.on_message_box_close,
            buttons=["Back"]
        )
        self.manager.add(message_box)

    @staticmethod
    def on_message_box_close(button_text):
        print(f"User pressed {button_text}.")

    def on_draw(self):
        self.clear()
        self.manager.draw()