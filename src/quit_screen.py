import arcade
import arcade.gui
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FAMILIAR_SCALING, WIZARD_SCALING


class QuitScreen(arcade.View):
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

        # Load background texture
        self.background = arcade.load_texture("Assets/UI/wiz_det_end_screen.png")

        self.player_list = arcade.SpriteList()
        self.cur_texture = 0

        # Set up familiar sprite
        self.familiar = arcade.Sprite("Assets/Sprites/Familiar/familiar_idle.png", FAMILIAR_SCALING)
        self.cat_bounce0 = arcade.load_texture("Assets/Sprites/Familiar/familiar_bounce_0.png")
        self.cat_bounce1 = arcade.load_texture("Assets/Sprites/Familiar/familiar_bounce_1.png")
        self.familiar.center_x = (SCREEN_WIDTH // 2) + 200
        self.familiar.center_y = (SCREEN_HEIGHT // 2) - 295
        self.player_list.append(self.familiar)

        # Set up familiar sprite
        self.wizard = arcade.Sprite("Assets/Sprites/Wizard/wizard_idle.png", WIZARD_SCALING)
        self.wiz_bounce0 = arcade.load_texture("Assets/Sprites/Wizard/wizard_bounce_0.png")
        self.wiz_bounce1 = arcade.load_texture("Assets/Sprites/Wizard/wizard_bounce_1.png")
        self.wizard.center_x = (SCREEN_WIDTH // 2) + 150
        self.wizard.center_y = (SCREEN_HEIGHT // 2) - 295
        self.player_list.append(self.wizard)

        # Game Audio
        self.victory_music = arcade.load_sound("Assets/Audio/very-lush-and-swag.mp3", False)

    def on_show_view(self):
        arcade.play_sound(self.victory_music, 1.0, 0.0, True, 1.0)

        # Title
        game_title = arcade.gui.UITextArea(text="You escaped the Detention\n"
                                                "                    Dimension!\n"
                                                "        Thanks for playing!",
                                           width=800,
                                           height=200,
                                           font_size=30,
                                           text_color=arcade.color.DARK_BLUE_GRAY,
                                           font_name="Kenney Pixel Square")
        self.v_box.add(game_title.with_space_around(bottom=50, left=150))

        # Quit button
        quit_button = arcade.gui.UITextureButton(texture=self.button_texture,
                                                 texture_pressed=self.pressed_button_texture)
        quit_button.on_click = self.on_click_quit
        self.h_box.add(quit_button.with_space_around(bottom=20))

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
                padding=(165, 165, 165, 165)
            ),
        )

    def on_click_quit(self, event):
        arcade.exit()

    def on_click_credits(self, event):
        message_box = arcade.gui.UIMessageBox(
            width=SCREEN_WIDTH / 2,
            height=SCREEN_HEIGHT / 2,
            message_text=(
                "\n     Credits Screen\n"
                "       Game made by Julia McKay, Chandler Fox, and Audrey DeHoog"
            ),
            buttons=["Back"]
        )
        self.manager.add(message_box)

    @staticmethod
    def on_message_box_close(button_text):
        print(f"User pressed {button_text}.")

    def on_draw(self):
        self.clear()
        self.manager.draw()
        self.player_list.draw()

        # Quit Button Text
        arcade.draw_text("Quit",
                         0,
                         (SCREEN_HEIGHT // 2) - 70,
                         arcade.color.WHITE_SMOKE,
                         25,
                         width=SCREEN_WIDTH,
                         align="center",
                         font_name="Kenney Mini Square")

        # Credits Button Text
        arcade.draw_text("Credits",
                         0,
                         (SCREEN_HEIGHT // 2) - 185,
                         arcade.color.WHITE_SMOKE,
                         15,
                         width=SCREEN_WIDTH,
                         align="center",
                         font_name="Kenney Mini Square")

    def on_update(self, delta_time):
        self.cur_texture += 1
        if self.cur_texture > 20:
            self.cur_texture = 1

        if self.cur_texture % 20 == 0:
            self.wizard.texture = self.wiz_bounce0
            self.familiar.texture = self.cat_bounce0
        if self.cur_texture % 12 == 0:
            self.wizard.texture = self.wiz_bounce1
            self.familiar.texture = self.cat_bounce1
