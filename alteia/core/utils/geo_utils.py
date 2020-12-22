from alteia.core.errors import BoundingBoxError


def compute_bbox_as_polygon(coordinates):
    if len(coordinates) == 0:
        raise BoundingBoxError("The coordinate list must not be empty")

    xmin, ymin = float("inf"), float("inf")
    xmax, ymax = float("-inf"), float("-inf")
    for c_coord in coordinates:
        # Set min coords
        if c_coord[0] < xmin:
            xmin = c_coord[0]
        if c_coord[1] < ymin:
            ymin = c_coord[1]
        # Set max coords
        if c_coord[0] > xmax:
            xmax = c_coord[0]
        if c_coord[1] > ymax:
            ymax = c_coord[1]

    return [[xmin, ymin], [xmax, ymin], [xmax, ymax], [xmin, ymax], [xmin, ymin]]


def compute_bbox(coordinates):
    if len(coordinates) == 0:
        raise BoundingBoxError("The coordinate list must not be empty")

    xmin, ymin = float("inf"), float("inf")
    xmax, ymax = float("-inf"), float("-inf")
    for x, y in coordinates:
        # Set min coords
        if x < xmin:
            xmin = x
        if y < ymin:
            ymin = y
        # Set max coords
        if x > xmax:
            xmax = x
        if y > ymax:
            ymax = y

    return [xmin, xmax, ymin, ymax]
