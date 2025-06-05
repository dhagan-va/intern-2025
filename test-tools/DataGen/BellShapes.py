import random
from enum import auto, Enum


class BellShapes(Enum):
    NORMAL = auto()
    FAT = auto()
    TIGHT = auto()


def scale(g: int, min_g: int, max_g: int, low: int, high: int) -> int:
    return round((high - low) * ((g - min_g) / (max_g - min_g)) + low)


def fit_range_to_half_bel(low: int, high: int, shape: BellShapes = BellShapes.NORMAL) -> int:
    mean = 0
    sigma = 1  # Normal Dist
    match shape:
        case BellShapes.FAT:
            sigma = 5
        case BellShapes.TIGHT:
            sigma = .2
    g = abs(random.gauss(mean, sigma))
    g = min(max(g,0), 10)  # no higher than 10

    return scale(g, 0, 10, low, high)
