# application for task 3
from lstm_recognizer import Recognizer
from pyglet import window
from pyglet import shapes
import pyglet
import math
import keras
from pyglet.window import mouse
import random


class RockPaperScissorsGame:
    def __init__(self):
        self.player_action = "no action"
        self.computer_action = "no action"
        self.game_result = "not played"

    def set_player_action(self, gesture):
        if gesture is None:
            self.player_action = None
        elif gesture == "rectangle":
            self.player_action = "paper"
        elif gesture == "circle":
            self.player_action = "rock"
        elif gesture == "delete_mark":
            self.player_action = "scissors"

    def set_computer_action(self):
        random_selection = random.random() * 3
        if random_selection <= 1:
            self.computer_action = "paper"
        elif random_selection <= 2:
            self.computer_action = "rock"
        else:
            self.computer_action = "scissors"

    def calculate_game_result(self):
        if self.player_action is None or self.computer_action is None:
            self.game_result = "defeat"
        if self.player_action == self.computer_action:
            self.game_result = "tie"
        elif self.player_action == "rock" and self.computer_action == "scissors":
            self.game_result = "victory"
        elif self.player_action == "paper" and self.computer_action == "rock":
            self.game_result = "victory"
        elif self.player_action == "scissors" and self.computer_action == "paper":
            self.game_result = "victory"
        else:
            self.game_result = "defeat"


class GestureInput:
    def __init__(self, x, y, size, window, game, recognizer, batch=pyglet.graphics.Batch()):
        self.batch = batch
        self.field = shapes.Rectangle(
            x, y, size, size, color=(200, 200, 200), batch=batch)
        self.window = window
        self.window.on_mouse_drag = self.handle_mouse_drag
        self.window.on_mouse_release = self.handle_mouse_release
        self.window.on_mouse_press = self.handle_mouse_press
        self.drawn_points = []
        self.rec_points = []
        self.line_width = size // 75
        self.predicted_gesture = "No result"
        self.recognizer = recognizer

    def convert_to_field_coordinates(self, x, y):
        x -= self.field.x
        y -= self.field.y
        y = -y # transform recog space
        return x, y

    def check_field_hit(self, x, y):
        left = self.field.x
        right = left + self.field.width
        bottom = self.field.y
        top = bottom + self.field.height

        if x >= left and x <= right and y <= top and y >= bottom:
            return True
        return False

    def handle_mouse_drag(self, x, y, dx, dy, buttons, modifiers):

        if self.check_field_hit(x, y):
            if buttons & mouse.LEFT:
                self.drawn_points.append(shapes.Circle(
                    x, y, radius=self.line_width, color=(255, 0, 0), batch=self.batch))
                local_x, local_y = self.convert_to_field_coordinates(x, y)
                self.rec_points.append([local_x, local_y])

    def handle_mouse_press(self, x, y, button, modifiers):

        if self.check_field_hit(x, y):
            if button == mouse.LEFT:
                for point in self.drawn_points:
                    point.delete()
                self.drawn_points.clear()
                self.rec_points.clear()

                self.drawn_points.append(shapes.Circle(
                    x, y, radius=self.line_width, color=(255, 0, 0), batch=self.batch))
                local_x, local_y = self.convert_to_field_coordinates(x, y)
                self.rec_points.append([local_x, local_y])

    def on_finished_drawing(self):
        prediction = recognizer.recognize(self.rec_points)
        self.predicted_gesture = prediction
        game.set_player_action(self.predicted_gesture)
        game.set_computer_action()
        game.calculate_game_result()

    def handle_mouse_release(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            if len(self.rec_points) > 1:
                self.on_finished_drawing()
            else:
                print("No prediction possible. More points needed")


WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 1200

win = window.Window(WINDOW_WIDTH, WINDOW_HEIGHT, "Gesture Input")
batch = pyglet.graphics.Batch()
game = RockPaperScissorsGame()
recognizer = Recognizer()

gesture_input = GestureInput(
    50, 300, WINDOW_HEIGHT-600, win, game, recognizer,  batch=batch)


heading_text = pyglet.text.Label(
    'Draw here!',
    font_size=30,
    x=50,
    y=win.height-200,
    anchor_x='left',
    anchor_y='top',
    batch=batch,
    color=(255, 255, 255),
)
footer = pyglet.text.Label(
    'rectangle = paper, circle = rock, delete = scissors',
    font_size=30,
    x=win.width//2,
    y=int(win.height * 0.05),
    anchor_x='center',
    anchor_y='bottom',
    batch=batch,
    color=(255, 255, 255),
)
player_action_text = pyglet.text.Label(
    'player: ' + game.player_action,
    font_size=30,
    x=50,
    y=250,
    anchor_x='left',
    anchor_y='top',
    batch=batch,
    color=(255, 255, 255),
)
computer_action_text = pyglet.text.Label(
    'computer: ' + game.computer_action,
    font_size=30,
    x=win.width-50,
    y=250,
    anchor_x='right',
    anchor_y='top',
    batch=batch,
    color=(255, 255, 255),
)

result_text = pyglet.text.Label(
    'Result: ' + game.game_result,
    font_size=50,
    x=win.width//2,
    y=int(win.height * 0.9),
    anchor_x='center',
    anchor_y='top',
    batch=batch,
    color=(255, 255, 255),
)


@win.event
def on_draw():
    win.clear()
    player_action_text.text = 'player: ' + game.player_action
    computer_action_text.text = 'computer: ' + game.computer_action
    result_text.text = 'Result: ' + game.game_result

    batch.draw()


pyglet.app.run()
