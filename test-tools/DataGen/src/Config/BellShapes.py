import random
from enum import auto, Enum


class BellShapes(Enum):
    NORMAL = auto()
    FAT = auto()
    TIGHT = auto()


def scale(g: float, min_g: float, max_g: float, low: float, high: float) -> float:
    return round((high - low) * ((g - min_g) / (max_g - min_g)) + low)


def fit_range_to_half_bel(min_val: int, max_val: int, shape: BellShapes = BellShapes.NORMAL) -> int:
    mean = 0
    sigma = 1
    match shape:
        case BellShapes.FAT:
            sigma = 5
        case BellShapes.TIGHT:
            sigma = .2
    g = abs(random.gauss(mean, sigma))
    g = min(g, 10)  # no higher than 10

    scaled = scale(g, 0, 10, min_val, max_val)
    return scaled
