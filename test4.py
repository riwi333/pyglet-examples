import pyglet
from random import seed, random, uniform
from math import floor
from datetime import datetime

# PURPOSE: draw a random walk that only moves along the x and y axes in real time

MAX_STEPS = 1024            # maximum number of lines drawn in the walk
WINDOW_WIDTH = 960          # width of the main window
WINDOW_HEIGHT = 540         # height of the main window
MIN_WALK_LENGTH = 30        # minimum number of pixels one step can take
MAX_WALK_LENGTH = 150       # maximum number of pixels one step can take
WALK_COLOR = (255, 0, 0)    # RGB tuple for the color of the walk
STEP_COLOR = (0, 0, 255)    # RGB tuple for color of the current step we're on

# numbered step of the walk we're on
step = 0

# direction that the random walk should NOT go in next (so it doesn't loop
# back on itself)
bad_direction = None

# generate the vertex list needed to draw a rectangle
#
# @param origin_x   :   x-coordinate of bottom left corner of rectangle
# @param origin_y   :   y-coordinate of bottom left corner of rectangle
# @param length     :   length of rectangle
# @param width      :   width of rectangle
# @param color      :   3-tuple of the RGB value to color the rectangle
#                       (optional)
#
def generateRectangle(origin_x, origin_y, width, height, color=(255, 255, 255)):
    # note that since pyglet doesn't support GL_LINE_LOOP, you need to
    # repeat the first vertex at the end to close the shape (this should be
    # drawn in GL_LINE_STRIP mode)
    return pyglet.graphics.vertex_list(5, ('v2f', (
        origin_x, origin_y,
        origin_x + width, origin_y,
        origin_x + width, origin_y + height,
        origin_x, origin_y + height,
        origin_x, origin_y
    )),
        ('c3B', color * 5))

# calculate x and y coordinates for a vertex that doesn't go outside bounds
#
# @param currentVertex  :   tuple of x- and y-coordinates for the current vertex
#
def getNextVertex(currentVertex):
    # functions to add length to current coordinates depending on direction
    add = [     lambda x, l : x - l,
                lambda y, l : y - l,
                lambda x, l : x + l,
                lambda y, l : y + l     ]

    nextVertex = [ currentVertex[0], currentVertex[1] ]

    global bad_direction

    # randomize the direction and length of the next step; if too "long" (would
    # go out of bounds), randomize a new length and direction
    # (eh probably not the best idea, but it's unlikely to hang for long)
    while (True):
        # randomize if the walk is going left (0), down (1), right (2), or up (3)
        direction = floor(random() * 4)

        # randomize length of the next step
        length = uniform(MIN_WALK_LENGTH, MAX_WALK_LENGTH)

        # calculate the new coordinate for the direction we're moving in (this works)
        newCoordinate = add[direction](currentVertex[direction % 2], length)

        # make sure we're not going back in the direction we just went,
        # and that the next step won't take us out of bounds; 'bad_direction' is just
        # the opposite of the direction the last step went in -- if we just went to the
        # left (direction 0), then 'bad_direction' is to the right (direction 2), etc.
        if not direction == bad_direction :
            # conditions to ensure new point is within bounds (depending on whether
            # we need the coordinate to be less than some value or greater than some
            # value to be in bounds)
            inBounds1 = int(direction / 2) == 0 and newCoordinate > bounds[direction]
            inBounds2 = int(direction / 2) == 1 and newCoordinate < bounds[direction]

            # if either condition is true (new vertex is in bounds), set the next vertex
            # coordinates and update 'bad_direction'
            if inBounds1 or inBounds2 :
                nextVertex[direction % 2] = newCoordinate
                bad_direction = (direction + 2) % 4     # this also works
                break

    return nextVertex

# perform one step of the random walk
#
# @param dt     :   argument required by Pyglet to use this as a callback to the
#                   schedule_interval() function (I think it's just the amount
#                   of time between calls? i.e. 0.1 seconds for this program)
#
def walkStep(dt):
    global step, walk, currentVertex, lastLine

    # don't add any more lines than MAX_STEPS to the walk
    if step == MAX_STEPS:
        return

    # get the next randomized vertex
    nextVertex = getNextVertex(currentVertex)

    # re-color the last line of the walk the standard color so we can color
    # this new step a different color
    lastLine.colors = WALK_COLOR * 2

    # add this new step to the walk and save ther vertex list used to draw
    # its line
    lastLine = walk.add (2, pyglet.gl.GL_LINES, None,
                        ('v2f/static', currentVertex + nextVertex),
                        ('c3B/dynamic', WALK_COLOR + STEP_COLOR))

    currentVertex = nextVertex
    step = step + 1


# create a 16:9 aspect ratio window
window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)

# seed the random generator
seed(datetime.now())

# draw a (white) bounding box for the walk
boundingBox = generateRectangle(    0.1 * WINDOW_WIDTH,
                                    0.1 * WINDOW_HEIGHT,
                                    0.8 * WINDOW_WIDTH,
                                    0.8 * WINDOW_HEIGHT     )

# bounds for the left, bottom, right, and top sides of the bounding box
bounds = [ 0.1 * WINDOW_WIDTH, 0.1 * WINDOW_HEIGHT, 0.9 * WINDOW_WIDTH, 0.9 * WINDOW_HEIGHT ]

# create a batch to hold all of the individual lines in the walk; note that NOT
# using a batch for the individual lines (i.e. making one big vertex list for
# all the vertices) and then using GL_LINES or GL_LINE_STRIP mode causes each
# vertex to always have a line drawn to it from the origin for some reason,
# giving the walk a weird vanishing point effect
walk = pyglet.graphics.Batch()

# randomize the walk's starting vertex (the max/min values are adjusted so that the
# first vertex isn't so close to the bounding walls that the walk is hard to see)
currentVertex = [   uniform(0.15 * WINDOW_WIDTH, 0.75 * WINDOW_HEIGHT),
                    uniform(0.15 * WINDOW_WIDTH, 0.75 * WINDOW_HEIGHT)  ]

# we also need to set the second vertex before starting the walk, since we
# draw the walk as a GL_LINES, which needs two vertices to be drawn
nextVertex = getNextVertex(currentVertex)

# we add this first line to the batch and save the vertex list used to draw it
# so we can alter its color later (we color the current step of the walk a different
# color from the previous steps so it's easier to see)
lastLine = walk.add (2, pyglet.gl.GL_LINES, None,
                    ('v2f/static', currentVertex + nextVertex),
                    ('c3B/dynamic', WALK_COLOR + STEP_COLOR))

# update the new current vertex so we know which one we're on and increment the
# step counter
currentVertex = nextVertex
step = step + 1

# schedule each step of the walk to happen 10 times a second
pyglet.clock.schedule_interval(walkStep, .1)

# draw the bounding box and the walk on the main window
@window.event
def on_draw():
    boundingBox.draw(pyglet.gl.GL_LINE_STRIP)
    walk.draw()

pyglet.app.run()
