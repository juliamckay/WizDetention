import arcade
from menu_screen import MenuScreen
from constants import SCREEN_WIDTH, SCREEN_HEIGHT


def main():
    """Main function"""
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Wizard Detention")
    start_view = MenuScreen()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()
