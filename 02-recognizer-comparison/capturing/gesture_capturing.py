
import pyglet
from pyglet import window
from pyglet import shapes
from pyglet.window import mouse
from geometry import Point
import xml.etree.ElementTree as ET
import time
from pathlib import Path


class GestureInput:
    def __init__(self, x, y, size, window, batch=pyglet.graphics.Batch()):
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
        self.times = []
        self.gesture_start_time = time.time()
        self.gestures = ["arrow", "caret", "check", "circle", "delete_mark", "left_curly_brace",
                         "left_sq_bracket", "pigtail", "rectangle",
                         "right_curly_brace", "right_sq_bracket", "star", "triangle", "v", "x"]
        # exlclude question mark because its not on dollar recognizer website, also exclude zigziag from website bc not in logs
        # in the xml logs delete_mark is used instead of delete (this differs from the assignment sheet)
        self.acitive_gesture = self.gestures.pop(0)
        self.gesture_counter = 1
        print(self.acitive_gesture)

    def convert_to_field_coordinates(self, x, y):
        x -= self.field.x
        y -= self.field.y
        y = -y
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

                # time since starting gesture in ms
                self.times.append(
                    int((time.time() - self.gesture_start_time) * 1000))

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

    def save_gesture_to_xml(self):
        dir = Path("./datasets/")
        dir.mkdir(parents=True, exist_ok=True)

        root = ET.Element("Gesture")
        str_number = f"{self.gesture_counter:02}"
        name = self.acitive_gesture + str_number
        root.set("Name", name)
        root.set("Subject", "0")
        root.set("Number", str(self.gesture_counter))
        root.set("NumPts", str(len(self.rec_points)))
        duration = self.times[len(self.times)-1] - self.times[0]
        root.set("Millseconds", str(duration))  # sic

        for point, t in zip(self.rec_points, self.times):
            point_element = ET.SubElement(root, "Point")
            point_element.set("X", str(point.x))
            point_element.set("Y", str(point.y))
            point_element.set("T", str(t))

        tree = ET.ElementTree(root)
        tree.write(str(dir) + "/" + name + ".xml", encoding="utf-8",
                   xml_declaration=True)

        self.times.clear()
        self.rec_points.clear()

        FILES_PER_GESTURE = 10

        if self.gesture_counter < FILES_PER_GESTURE:
            self.gesture_counter += 1
            print(self.acitive_gesture)
            print(self.gesture_counter)
        else:
            self.gesture_counter = 1
            if len(self.gestures) >= 1:
                self.acitive_gesture = self.gestures.pop(0)
                print(self.acitive_gesture)
                print(self.gesture_counter)
                self.gesture_start_time = time.time()
            else:
                print("finished")
                pyglet.app.exit()

    def handle_mouse_release(self, x, y, button, modifiers):

        if button == mouse.LEFT:
            if len(self.rec_points) > 1:
                self.save_gesture_to_xml()


WINDOW_SIZE = 600
win = window.Window(WINDOW_SIZE, WINDOW_SIZE, "Gesture Input")
batch = pyglet.graphics.Batch()
gesture_input = GestureInput(50, 50, WINDOW_SIZE-100, window=win, batch=batch)


@win.event
def on_draw():
    win.clear()
    gesture_input.batch.draw()


pyglet.app.run()
