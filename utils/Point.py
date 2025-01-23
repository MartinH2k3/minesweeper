class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"({self.x}, {self.y})"

    # override math operators
    def __add__(self, other):
        if not isinstance(other, Point):
            return NotImplemented
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        if not isinstance(other, Point):
            return NotImplemented
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        if isinstance(other, Point):
            return Point(self.x * other.x, self.y * other.y)
        if isinstance(other, (int, float)):
            return Point(self.x * other, self.y * other)
        return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, Point):
            return Point(self.x / other.x, self.y / other.y)
        if isinstance(other, (int, float)):
            return Point(self.x / other, self.y / other)
        return NotImplemented

    def __floordiv__(self, other):
        if isinstance(other, Point):
            return Point(self.x // other.x, self.y // other.y)
        if isinstance(other, (int, float)):
            return Point(self.x // other, self.y // other)
        return NotImplemented

    def __mod__(self, other):
        if isinstance(other, Point):
            return Point(self.x % other.x, self.y % other.y)
        if isinstance(other, (int, float)):
            return Point(self.x % other, self.y % other)
        return NotImplemented

    def __eq__(self, other):
        if not isinstance(other, Point):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def within(self, other: list[list]):
        if not isinstance(other, list):
            return NotImplemented
        if not isinstance(other[0], list):
            return NotImplemented
        if not len(other) or not len(other[0]):
            return False
        return 0 <= self.x < len(other) and 0 <= self.y < len(other[0])

    def within_bounds(self, lower_x: int, upper_x: int, lower_y: int, upper_y: int):
        return lower_x <= self.x < upper_x and lower_y <= self.y < upper_y

    def neighbors(self, diagonal=False):
        if diagonal:
            return [Point(self.x + 1, self.y), Point(self.x - 1, self.y), Point(self.x, self.y + 1), Point(self.x, self.y - 1), Point(self.x + 1, self.y + 1), Point(self.x - 1, self.y - 1), Point(self.x + 1, self.y - 1), Point(self.x - 1, self.y + 1)]
        return [Point(self.x + 1, self.y), Point(self.x - 1, self.y), Point(self.x, self.y + 1), Point(self.x, self.y - 1)]