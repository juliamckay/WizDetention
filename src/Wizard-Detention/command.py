from abc import abstractmethod
import arcade
from constants import PLAYER_JS, PLAYER_MS


class InputHandler:
    """Handles Input based off a given key press"""
    def __init__(self, wiz: arcade.Sprite, cat: arcade.Sprite):
        """To add a command, add the key to press to the list as well and assign the correct object constructor"""
        self.commands = \
            {
                arcade.key.A: MoveLeftCommand(wiz),
                arcade.key.D: MoveRightCommand(wiz),
                arcade.key.W: JumpCommand(wiz),
                arcade.key.LEFT: MoveLeftCommand(cat),
                arcade.key.RIGHT: MoveRightCommand(cat),
                arcade.key.UP: JumpCommand(cat)
            }

    def handle_input(self, key_pressed):
        """Simply picks the command"""
        if key_pressed in self.commands:
            return self.commands[key_pressed]
        return None


class Command:
    """An abstract class used for all command classes"""
    def __init__(self, sprite: arcade.Sprite):
        self.sprite = sprite

    @abstractmethod
    def __call__(self):
        pass

    @abstractmethod
    def undo(self):
        pass


class JumpCommand(Command):
    """Makes the character sprite jump"""
    def __init__(self, sprite: arcade.Sprite):
        self.sprite = sprite

    def __call__(self):
        self.sprite.change_y = PLAYER_JS

    def undo(self):
        self.sprite.change_y = 0


class MoveLeftCommand(Command):
    """Makes the character sprite move left"""
    def __init__(self, sprite: arcade.Sprite):
        self.sprite = sprite

    def __call__(self):
        self.sprite.change_x = -PLAYER_MS

    def undo(self):
        self.sprite.change_x = 0


class MoveRightCommand(Command):
    """Makes the character sprite move right"""
    def __init__(self, sprite: arcade.Sprite):
        self.sprite = sprite

    def __call__(self):
        self.sprite.change_x = PLAYER_MS

    def undo(self):
        self.sprite.change_x = 0
