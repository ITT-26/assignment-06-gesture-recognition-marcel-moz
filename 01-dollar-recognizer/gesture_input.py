# gesture input program for first task
import pyglet
from recognizer import DollarRegcognizer
from pyglet import window
from pyglet import shapes
from pyglet.window import mouse
from geometry import Point


class GestureInput:
    def __init__(self, x, y, size, window, batch=pyglet.graphics.Batch()):
        self.recognizer = DollarRegcognizer(size)
        self.recognizer.add_assignment_gestures()
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

    def convert_to_field_coordinates(self, x, y):
        x -= self.field.x
        y -= self.field.y
        x = - x  # flip x coordinate
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
                self.rec_points.append(Point(local_x, local_y))

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
                self.rec_points.append(Point(local_x, local_y))

    def handle_mouse_release(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            if len(self.rec_points) > 1:
                result = self.recognizer.recognize(self.rec_points)
                print(
                    f"Result: {result.name} ({result.score}) in {result.time} s")

                self.predicted_gesture = result.name
            else:
                print("No prediction possible. More points needed")


WINDOW_SIZE = 600
win = window.Window(WINDOW_SIZE, WINDOW_SIZE, "Gesture Input")
batch = pyglet.graphics.Batch()
gesture_input = GestureInput(50, 50, WINDOW_SIZE-100, window=win, batch=batch)

heading_text = pyglet.text.Label(
    'Draw a gesture in the gray area:',
    font_size=20,
    x=5,
    y=win.height-5,
    anchor_x='left',
    anchor_y='top',
    batch=batch,
    color=(255, 255, 255),
)
result_text = pyglet.text.Label(
    'prediction: ' + gesture_input.predicted_gesture,
    font_size=20,
    x=5,
    y=5,
    anchor_x='left',
    anchor_y='bottom',
    batch=batch,
    color=(255, 255, 255),
)


@win.event
def on_draw():
    win.clear()
    result_text.text = 'prediction: ' + gesture_input.predicted_gesture
    gesture_input.batch.draw()


pyglet.app.run()
