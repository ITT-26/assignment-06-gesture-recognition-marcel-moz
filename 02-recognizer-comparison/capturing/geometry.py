import math


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Rectangle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height


def get_centroid(points):
    x, y = 0.0, 0.0
    for point in points:
        x += point.x
        y += point.y
    x = x / len(points)
    y = y / len(points)
    return Point(x, y)


def get_bounding_box(points):
    min_x = math.inf
    max_x = -math.inf
    min_y = math.inf
    max_y = -math.inf

    for point in points:
        min_x = min(min_x, point.x)
        min_y = min(min_y, point.y)
        max_x = max(max_x, point.x)
        max_y = max(max_y, point.y)

    width = max_x - min_x
    height = max_y - min_y

    return Rectangle(min_x, min_y, width, height)


def get_point_distance(p1, p2):
    dx = p2.x - p1.x
    dy = p2.y - p1.y

    return math.sqrt(dx * dx + dy * dy)


def get_path_distance(pts1, pts2):
    assert len(pts1) == len(pts2), "// assumes pts1.length == pts2.length"
    d = 0.0
    for p1, p2 in zip(pts1, pts2):
        d += get_point_distance(p1, p2)
    return d / len(pts1)


def get_path_length(points):
    d = 0.0

    for i, point in enumerate(points):
        if i == 0:
            continue
        d += get_point_distance(points[i-1], point)

    return d


def deg2rad(d):
    return d * math.pi / 180.0


def indicative_angle(points):
    center = get_centroid(points)
    return math.atan2(center.y - points[0].y, center.x - points[0].x)


def rotate_by(points, radians):
    center = get_centroid(points)
    cos = math.cos(radians)
    sin = math.sin(radians)
    new_points = []
    for point in points:
        qx = (point.x - center.x) * cos - (point.y - center.y) * sin + center.x
        qy = (point.x - center.x) * sin + (point.y - center.y) * cos + center.y
        new_points.append(Point(qx, qy))
    return new_points


def scale_to(points, size):
    bbox = get_bounding_box(points)
    new_points = []
    for point in points:
        qx = point.x * (size / bbox.width)
        qy = point.y * (size / bbox.height)
        new_points.append(Point(qx, qy))
    return new_points


def translate_to(points, pt):
    center = get_centroid(points)
    new_points = []
    for point in points:
        qx = point.x + pt.x - center.x
        qy = point.y + pt.y - center.y
        new_points.append(Point(qx, qy))
    return new_points


def vectorize(points):
    sum = 0.0
    vector = []
    for point in points:
        vector.append(point.x)
        vector.append(point.y)
        sum += point.x * point.x + point.y * point.y
    magnitude = math.sqrt(sum)
    for i in range(len(vector)):
        vector[i] /= magnitude
    return vector


def get_phi():
    return 0.5 * (-1.0 + math.sqrt(5.0))


def get_distance_at_angle(points, T, radians):
    new_points = rotate_by(points, radians)
    return get_path_distance(new_points, T.points)


def get_distance_at_best_angle(points, T, a, b, threshold):
    phi = get_phi()
    x1 = phi * a + (1.0 - phi) * b
    f1 = get_distance_at_angle(points, T, x1)
    x2 = (1 - phi) * a + phi * b
    f2 = get_distance_at_angle(points, T, x2)
    while abs(b - a) > threshold:
        if f1 < f2:
            b = x2
            x2 = x1
            f2 = f1
            x1 = phi * a + (1.0 - phi) * b
            f1 = get_distance_at_angle(points, T, x1)
        else:
            a = x1
            x1 = x2
            f1 = f2
            x2 = (1.0 - phi) * a + phi * b
            f2 = get_distance_at_angle(points, T, x2)
    return min(f1, f2)


def resample(points, n):
    interval = get_path_length(points) / (n - 1)
    D = 0.0
    new_points = [points[0]]

    i = 1
    while i < len(points):
        d = get_point_distance(points[i-1], points[i])

        if D + d >= interval:
            qx = points[i-1].x + ((interval - D) / d) * \
                (points[i].x - points[i-1].x)
            qy = points[i-1].y + ((interval - D) / d) * \
                (points[i].y - points[i-1].y)
            q = Point(qx, qy)
            new_points.append(q)
            points.insert(i, q)
            D = 0.0
        else:
            D += d
        i += 1

    if len(new_points) == n - 1:  # for rounding error
        new_points.append(
            Point(points[len(points)-1].x, points[len(points)-1].y))
    return new_points


class Unistroke:
    def __init__(self, name, points, num_points, square_size, origin):
        self.name = name
        self.points = resample(points, num_points)
        radians = indicative_angle(self.points)
        self.points = rotate_by(self.points, - radians)
        self.points = scale_to(self.points, square_size)
        self.points = translate_to(self.points, origin)
        # self.vector = vectorize(self.points) # for protactor only (so not needed)
