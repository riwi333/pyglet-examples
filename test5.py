import pyglet
from math import sqrt, radians, sin, cos

# PURPOSE:  1) add the option of filling in shapes with color and
#           2) draw lines with adjustable thickness
#
# pyglet seems to support neither of these options by default (using GL_POLYGONS
# is discouraged), but maybe I'm just bad at reading OpenGL documentation

WINDOW_WIDTH = 960          # width of the main window
WINDOW_HEIGHT = 540         # height of the main window

# generate the vertex list needed to draw a filled rectangle
#
# @param origin     :   tuple of x- and y-coordinates for the bottom left corner of rectangle
# @param length     :   length of rectangle
# @param width      :   width of rectangle
# @param color      :   3-tuple of the RGB value to color the rectangle
#                       (optional)
# @param batch      :   batch to add vertex list to (optional)
#
def generateFilledRectangle(origin, width, height, color=(255, 255, 255), batch=None):
    # if no batch is specified, just return the vertex list used to make the rectangle (should
    # be drawn in GL_TRIANGLES mode)
    if batch is None:
        # note that the rectangle vertices are listed in counter-clockwise order, with the
        # first vertex being at the bottom left corner of the rectangle
        return  pyglet.graphics.vertex_list_indexed(4,
                [0, 1, 2, 2, 3, 0],
                ('v2f', (   origin[0], origin[1],
                            origin[0] + width, origin[1],
                            origin[0] + width, origin[1] + height,
                            origin[0], origin[1] + height )),
                ('c3B', color * 4))

    # otherwise, add the vertex list to the given batch and return it
    else:
        return  batch.add_indexed   (4, pyglet.gl.GL_TRIANGLES, None,
                                    [0, 1, 2, 2, 3, 0],
                                    ('v2f', (   origin[0], origin[1],
                                                origin[0] + width, origin[1],
                                                origin[0] + width, origin[1] + height,
                                                origin[0], origin[1] + height   )),
                                    ('c3B', color * 4))

# generate the vertex list needed to draw a filled circle (basically a disk)
#
# @param center     :   tuple of x- and y-coordinates for the center of the circle
# @param radius     :   radius of the circle
# @param num_points :   number of vertices used to draw the circle
#                       (more vertices make the circle smoother, but more
#                       computationally expensive)
# @param color      :   3-tuple of the RGB value to color the circle with
#                       (optional)
# @param batch      :   batch to add vertex list to (optional)
#
def generateFilledCircle(center, radius, num_points, color=(255, 255, 255), batch=None):
    # note: this function is pretty much the same as the one for circles in test3.py, but we'll
    # order the vertices of list differently at the end to use GL_TRIANGLES instead of
    # GL_LINE_STRIP (fewer comments as a result)

    vertices = [ center[0], center[1] + radius ]

    angle = radians(360.0 / num_points)
    cosine = cos(angle)
    sine = sin(angle)

    current_x, current_y = 0, radius

    for i in range(num_points):
        new_x = current_x * cosine - current_y * sine
        new_y = current_x * sine + current_y * cosine
        vertices += [ new_x + center[0], new_y + center[1]]
        current_x, current_y = new_x, new_y

    # we will add the center of the circle to the list of vertices (as vertex 0); each
    # triangle will be made up of two adjacent vertices on the circle and the center vertex
    order = []
    for i in range(1, num_points + 1):
        order += [ 0, i, i+1 ]

    # if a batch is not specified, return the vertex list for the circle (needs to be drawn
    # in GL_TRIANGLES mode)
    if batch is None:
        # we have 'num_points' + 2 vertices in total in the list: the center, the
        # 'num_points' vertices around the circle, and the first vertex (at the top
        # of the circle) repeated (so the circle closes)
        return  pyglet.graphics.vertex_list_indexed(num_points + 2, order,
                ('v2f', center + vertices),
                ('c3B', color * (num_points + 2)))

    # if a batch is specified, add the circle to the batch and return its vertex list
    else:
        return  batch.add_indexed(num_points + 2, pyglet.gl.GL_TRIANGLES, None, order,
                ('v2f', center + vertices),
                ('c3B', color * (num_points + 2)))

# generate vertex list needed to draw a line of arbitrary thickness
#
# @param p1         :   tuple of (x, y) coordinates for first vertex
# @param p2         :   tuple of (x, y) coordinates for second vertex
# @param color      :   3-tuple of the RGB value to color the circle with
#                       (optional)
# @param width      :   width (thickness) of line in pixels (defined as
#                       the shortest perpendicular distance) in the generated
#                       rectangle (optional)
# @param batch      :   batch to add vertex list to (optional)
#
def generateLine(p1, p2, color=(255, 255, 255), width=1.0, batch=None):
    # lines of thickness <= 1.0 are just treated as regular GL_LINES of width 1.0 pixels
    if width <= 1.0:
        # if no batch is specified, just return the vertex list for the line (needs to be
        # drawn in GL_LINES mode)
        if batch is None:
            return pyglet.graphics.vertex_list(2,   ('v2f', (p1[0], p1[1], p2[0], p2[1])),
                                                    ('c3B', color * 2))

        # if a batch is specified, add the line to the batch and return its vertex list
        else:
            return batch.add    (2, pyglet.gl.GL_LINES, None,
                                ('v2f', (p1[0], p1[1], p2[0], p2[1])),
                                ('c3B', color * 2))

    # lines of thickness > 1.0 need to be triangulated, since GL_TRIANGLES are filled with color
    else:
        # a thick line is basically a (rotated) rectangle, so we just find the four
        # corners of the rectangle and triangulate it

        # deal with horizontal and vertical lines by just using generateFilledRectangle()
        if p2[0] == p1[0]:  # vertical line
            # calculate the coordinates for the bottom left corner of the rectangle
            if p1[1] <= p2[1]:
                origin = [ p1[0] - 0.5 * width, p1[1] ]
            else:
                origin = [ p2[0] - 0.5 * width, p2[1] ]

            return generateFilledRectangle(origin, width, abs(p2[1] - p1[1]), color=color, batch=batch)

        elif p2[1] == p1[1]:    # horizontal line
            if p1[0] <= p2[0]:
                origin = [ p1[0], p1[1] - 0.5 * width ]
            else:
                origin = [ p2[0], p2[1] - 0.5 * width ]

            return generateFilledRectangle(origin, abs(p2[0] - p1[0]), width, color=color, batch=batch)

        # deal with lines not parallel to the x or y axes
        else:
            # since the angle the rectangle is rotated (counter-clockwise, about the midpoint of the line)
            # is the arctangent of the slope of the line, multiplying the corner coordinates by the Cartesian
            # rotation matrix involves sin( arctan(x) ) and cos( arctan(x) ) terms, which simplify into
            # expressions only involving square roots
            slope = float((p2[1] - p1[1]) / (p2[0] - p1[0]))
            cosine = 1.0 / sqrt(1 + slope ** 2)
            sine = cosine * slope

            # first, we translate the line's endpoints so its midpoint would be at the origin;
            # then the rectangle's resulting corner points (q1, q2, q3, q4 -- starting at the top
            # left corner and going in counter-clockwise order) are multiplied by the Cartesian
            # rotation matrix to produce the points of the rectangle that represents the thickened
            # line; we then translate the rotated rectangle back so its center point is at the
            # original midpoint of the line
            mid_x = 0.5 * (p1[0] + p2[0])
            mid_y = 0.5 * (p1[1] + p2[1])

            p1[0] = p1[0] - mid_x
            p1[1] = p1[1] - mid_y
            p2[0] = p2[0] - mid_x
            p2[1] = p2[1] - mid_y

            # note: this is a lil ugly; I should probably change the names of the corner coordinates
            # to something other than q1_y, etc.
            q1_x = p1[0] * cosine - (p1[1] + 0.5 * width) * sine + mid_x
            q1_y = p1[0] * sine + (p1[1] + 0.5 * width) * cosine + mid_y
            q2_x = p1[0] * cosine - (p1[1] - 0.5 * width) * sine + mid_x
            q2_y = p1[0] * sine + (p1[1] - 0.5 * width) * cosine + mid_y
            q3_x = p2[0] * cosine - (p2[1] - 0.5 * width) * sine + mid_x
            q3_y = p2[0] * sine + (p2[1] - 0.5 * width) * cosine + mid_y
            q4_x = p2[0] * cosine - (p2[1] + 0.5 * width) * sine + mid_x
            q4_y = p2[0] * sine + (p2[1] + 0.5 * width) * cosine + mid_y

            # if a batch is not specified, return the vertex list for the rectangle (needs to be drawn
            # in GL_TRIANGLES mode)
            if batch is None:
                # use the rectangle 's4 vertices to form the two adjacent triangles; the indices
                # show which vertices we use the make the triangle (the first triangle is made of
                # q1/q2/q4, etc.)
                return  pyglet.graphics.vertex_list_indexed(4,
                        [0, 1, 3, 2, 1, 3],
                        ('v2f', (   q1_x, q1_y,
                                    q2_x, q2_y,
                                    q3_x, q3_y,
                                    q4_x, q4_y  )),
                        ('c3B', color * 4))

            # if a batch is specified, add the rectangle to the batch and return its vertex list
            else:
                return batch.add_indexed(4, pyglet.gl.GL_TRIANGLES, None,
                                        [0, 1, 3, 2, 1, 3],
                                        ('v2f', (   q1_x, q1_y,
                                                    q2_x, q2_y,
                                                    q3_x, q3_y,
                                                    q4_x, q4_y) ),
                                        ('c3B', color * 4))


# create the main 16:9 aspect ratio window
window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)

# draw some lines, rectangles, and circles (all filled with color)
@window.event
def on_draw():
    generateLine([100, 100], [400, 400], color=(66, 90, 245)).draw(pyglet.gl.GL_LINES)
    generateLine([200, 200], [700, 350], width=5.0, color=(245, 66, 66)).draw(pyglet.gl.GL_TRIANGLES)
    generateLine([250, 350], [750, 175], width=10.5).draw(pyglet.gl.GL_TRIANGLES)
    generateLine([400, 50], [400, 300], width=3.5, color=(0, 255, 0)).draw(pyglet.gl.GL_TRIANGLES)
    generateLine([700, 450], [850, 450], width=7.5, color=(194, 245, 66)).draw(pyglet.gl.GL_TRIANGLES)

    generateFilledRectangle([50, 400], 200, 100).draw(pyglet.gl.GL_TRIANGLES)
    generateFilledRectangle([750, 80], 150, 300, color=(245, 158, 66)).draw(pyglet.gl.GL_TRIANGLES)

    generateFilledCircle([100, 100], 50, 15).draw(pyglet.gl.GL_TRIANGLES)
    generateFilledCircle([450, 450], 75, 25, color=(126, 66, 245)).draw(pyglet.gl.GL_TRIANGLES)

pyglet.app.run()
