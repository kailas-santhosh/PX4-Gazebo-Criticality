import math


class TriggerZone:

    def __init__(
        self,
        x,
        y,
        z,
        radius,
    ):

        self.x = x
        self.y = y
        self.z = z
        self.radius = radius

    def contains(
        self,
        px,
        py,
        pz,
    ):

        distance = math.sqrt(
            (px - self.x) ** 2
            + (py - self.y) ** 2
            + (pz - self.z) ** 2
        )

        return distance <= self.radius

    def distance(
        self,
        px,
        py,
        pz,
    ):

        return math.sqrt(
            (px - self.x) ** 2
            + (py - self.y) ** 2
            + (pz - self.z) ** 2
        )
