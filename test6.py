import pyglet
from math import floor
from random import random
import test6_functions as graphics

# PURPOSE: draw a grid that the user can move along with the arrow keys
# the user will be represented by a circle of randomized color

WINDOW_WIDTH = 960          # width of the main window
WINDOW_HEIGHT = 540         # height of the main window
GRID_ROWS = 10              # number of rows in the main grid
GRID_COLS = 10              # number of columns in the main grid
CIRCLE_DRAW_POINTS = 30     # number of vertices used to draw circles

# class to represent grid
class Grid:
    # initialize an instance of the Grid object
    def __init__(self, origin, width, height, rows, cols, color=(255, 255, 255), thickness=1.0, label=False, alpha=False, labelColor=(255, 255, 255, 255)):
        self.origin = origin
        self.width = width
        self.height = height
        self.rows = rows
        self.cols = cols
        self.color = color
        self.thickness = thickness

        # get the batch of the grid for drawing
        self.batch = generateGrid(self.origin, self.width, self.height, self.rows, self.cols, self.color, self.thickness)

        # get the batch of grid labels, if requested (otherwise labelBatch is None)
        self.label = label
        self.alpha = alpha
        self.labelBatch = self.generateLabels(labelColor)

    # draw the grid
    def draw(self):
        self.batch.draw()

        # draw the grid's labels, if it has any
        if self.label is True:
            self.labelBatch.draw()

    # get the coordinates of the center of the cell at (row, col)
    def getCellCenter(self, row, col):
        center_x = self.origin[0] + float(self.width) / self.cols * (col + 0.5)
        center_y = self.origin[1] + float(self.height) / self.rows * (row + 0.5)

        return [ center_x, center_y ]

    # get the horizontal and vertical spacing between cells in the grid
    def getSpacing(self):
        return [ float(self.width) / self.cols, float(self.height) / self.rows ]

    # generate a batch of labels for cells along the left and top sides of the grid
    # if self.alpha = True, columns are labelled with capital letters (A, B, C, ...)
    # otherwise, both rows and columns are numbered
    #
    # note that labelColor is RGBA, not RGB
    def generateLabels(self, labelColor):
        if self.label is False:
            return None

        labelBatch = pyglet.graphics.Batch()

        # positioning for column/row labels
        horizontal_space = float(self.width) / self.cols
        vertical_space = float(self.height) / self.rows

        col_pos = self.getCellCenter(self.rows - 1, 0)
        col_pos[1] = col_pos[1] + vertical_space

        row_pos = self.getCellCenter(0, 0)
        row_pos[0] = row_pos[0] - horizontal_space

        # create labels for the columns
        for i in range(self.cols):
            if self.alpha is True:
                text = chr(65 + i)
            else:
                text = str(i + 1)

            pyglet.text.Label(  text,
                                font_name = 'Times New Roman',
                                font_size = 10,     # TODO: this should adjust with grid size
                                x = col_pos[0],
                                anchor_x = 'left',
                                y = col_pos[1],
                                anchor_y = 'bottom',
                                color = labelColor,
                                batch = labelBatch  )

            col_pos[0] = col_pos[0] + horizontal_space

        # create labels for the rows
        for i in range(self.rows):
            text = str(i + 1)

            # TODO: for some reason the row labels aren't completely centered vertically
            pyglet.text.Label(  text,
                                font_name = 'Times New Roman',
                                font_size = 10,     # TODO: this should adjust with grid size
                                x = row_pos[0],
                                anchor_x = 'left',
                                y = row_pos[1],
                                anchor_y = 'bottom',
                                color = labelColor,
                                batch = labelBatch  )

            row_pos[1] = row_pos[1] + vertical_space

        return labelBatch

    # get the text of the label for this cell
    def getCellLabel(self, row, col):
        if self.alpha is True:
            return chr(65 + col) + str(row + 1)
        else:
            return str(col + 1) + "-" + str(row + 1)

# class to represent user's position and circle
class User:
    # initialize an instance of the User object
    def __init__(self, grid, row, col, color=(255, 255, 255)):
        self.grid = grid        # instance of the Grid object the User is contained in
        self.row = row
        self.col = col
        self.color = color

        # create the vertex list needed to draw the user's circle on the grid (the radius is adjusted to fit
        # within the grid cells)
        self.center = self.grid.getCellCenter(self.row, self.col)
        self.radius = 0.25 * min(float(self.grid.width) / self.grid.cols, float(self.grid.height) / self.grid.rows)
        self.circle = graphics.generateCircle(  self.center,
                                                self.radius,
                                                CIRCLE_DRAW_POINTS,
                                                color = self.color,
                                                fill = True )

    # draw the user's circle
    def draw(self):
        self.circle.draw(pyglet.gl.GL_TRIANGLES)

    # moveTo: move the user's circle to a new cell and update its position
    #
    # @param next_row   :   row of cell the user is moving to
    # @param next_col   :   column of cell the user is moving to
    #
    def moveTo(self, next_row, next_col):
        nextCenter = self.grid.getCellCenter(next_row, next_col)
        deltaX = nextCenter[0] - self.center[0]
        deltaY = nextCenter[1] - self.center[1]

        # translate the circle by adding the change in position to each
        # pair of coordinates in the circle's vertex list
        for i in range(len(self.circle.vertices)):
            # even indices in the vertices list are x-coordinate values; odd
            # indices are y-coordinate values
            if i % 2 == 0:
                self.circle.vertices[i] = self.circle.vertices[i] + deltaX
            else:
                self.circle.vertices[i] = self.circle.vertices[i] + deltaY

        # update the user's position in the grid
        self.center = nextCenter
        self.row = next_row
        self.col = next_col

# generateGrid: generate a batch of GL_LINES to draw a grid
#
# @param origin     :   tuple of x- and y-coordinates of bottom left corner of grid
# @param width      :   total width of grid
# @param height     :   total height of grid
# @param rows       :   number of rows in the grid
# @param cols       :   number of columns in the grid
# @param color      :   3-tuple of the RGB value to color the grid with
#                       (optional)
# @param thickness  :   thickness of grid lines (optional)
#
def generateGrid(origin, width, height, rows, cols, color=(255, 255, 255), thickness=1.0):
    # create the batch of vertex lists used to draw the grid
    grid = pyglet.graphics.Batch()

    # generate all the horizontal lines in the grid
    for i in range(rows + 1):
        # calculate the number of empty pixels between each row's grid line
        # TODO: incorporate thickness into calculation
        vertical_space = float(height) / rows

        graphics.generateLine(  [ origin[0], origin[1] + i * vertical_space ],
                                [ origin[0] + width, origin[1] + i * vertical_space ],
                                color=color, width=thickness, batch=grid    )

    # generate all the vertical lines in the grid
    for i in range(cols + 1):
        # calculate the number of empty pixels between each column's grid line
        # TODO: incorporate thickness into calculation
        horizontal_space = float(width) / cols

        graphics.generateLine(  [ origin[0] + i * horizontal_space, origin[1] ],
                                [ origin[0] + i * horizontal_space, origin[1] + height ],
                                color=color, width=thickness, batch=grid    )

    return grid

# create the main window (16:9 aspect ratio)
window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)

# create the grid
grid = Grid(    [ 0.05 * WINDOW_WIDTH, 0.05 * WINDOW_HEIGHT ],
                0.45 * WINDOW_WIDTH,
                0.85 * WINDOW_HEIGHT,
                GRID_ROWS,
                GRID_COLS,
                color = (188, 188, 188),
                thickness = 3.5,
                label = True,
                alpha = True    )

# choose a random cell to start the user in
start_row = floor(random() * GRID_ROWS)
start_col = floor(random() * GRID_COLS)

# choose a random color for the user's circle
user_color = [ floor(random() * 255), floor(random() * 255), floor(random() * 255) ]

# create the user
user = User(    grid,
                start_row,
                start_col,
                color = user_color  )

# TODO: add labels for the grid and window positions of the user
#cellLabel = pyglet.text.Label(  grid.getCellLabel(user.row, user.col),
#                                font_name = 'Times New Roman',
#                                font_size = 20,
#                                x = (WINDOW_WIDTH - 0.5 * (grid.origin[0] + grid.getSpacing()[0] * grid.cols)) * 0.5,
#                                width = grid.getSpacing()[0] * 4,
#                                anchor_x = 'center',
#                                y = (WINDOW_HEIGHT - (grid.origin[1] + grid.getSpacing()[1] * grid.rows)) * 0.5,
#                                height = grid.getSpacing()[1] * 2,
#                                anchor_y = 'center'    )

# move the user with the arrow keys (within the grid)
@window.event
def on_key_press(symbol, modifiers):
    global cellLabel

    if symbol == pyglet.window.key.LEFT:
        if user.col > 0:
            user.moveTo(user.row, user.col - 1)

    elif symbol == pyglet.window.key.RIGHT:
        if user.col < user.grid.cols - 1:
            user.moveTo(user.row, user.col + 1)

    elif symbol == pyglet.window.key.DOWN:
        if user.row > 0:
            user.moveTo(user.row - 1, user.col)

    elif symbol == pyglet.window.key.UP:
        if user.row < user.grid.rows - 1:
            user.moveTo(user.row + 1, user.col)

    # update the positioning labels
    #cellLabel.text = grid.getCellLabel(user.row, user.col)

# draw the grid and user when the window refreshes
@window.event
def on_draw():
    window.clear()
    grid.draw()
    user.draw()
    #cellLabel.draw()
    #posLabel.draw()

pyglet.app.run()
