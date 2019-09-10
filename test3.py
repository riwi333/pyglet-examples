import pyglet
from math import sin, cos, radians

# PURPOSE: draw circles and rectangles on the screen

# generate the vertex list needed to draw a circle
#
# @param center_x   :   x-coordinate of center of circle
# @param center_y   :   y-coordinate of center of circle
# @param radius     :   radius of the circle
# @param num_points :   number of vertices used to draw the circle
#                       (more vertices make the circle smoother, but more
#                       computationally expensive)
# @param color      :   3-tuple of the RGB value to color the circle with
#                       (optional)
#
def generateCircle(center_x, center_y, radius, num_points, color=(255, 255, 255)):
    # initialize the list of vertex coordinates with the top of the circle
    vertices = [ center_x, center_y + radius ]

    # set the angle to rotate vertices on the circle by (vertices are evenly spaced)
    angle = radians(360.0 / num_points)

    # instead of calculating the sine and cosines needed to find all vertices on
    # the circle (x = r * cos(angle) and y = r * sin(angle)), we can just
    # calculate the sine and cosine for the set angle and then multiply
    # the starting vertex by the Cartesian rotation matrix. Each matrix
    # multiplication will rotate us along the circle by 'angle' radians, so
    # can just mutliply the current vertex we're on by the matrix
    # 'num_points' times to draw the circle
    #
    # the relevant matrix is:   [   cos(angle), -sin(angle)   ]
    #                           [   sin(angle), cos(angle)    ]

    # doing this only once is way faster than doing it 'num_points' times
    cosine = cos(angle)
    sine = sin(angle)

    # we need to start the vertex generating process about the origin to perform
    # the rotation properly (rotation/translation is not communitative)
    current_x, current_y = 0, radius

    # calculate the vertices used to draw the circle (the first vertex is
    # repeated at the end to close the circle)
    for i in range(num_points):
        # get the x and y coordinates of the next vertex (which will be the
        # current vertex rotated 'angle' radians around the circle,
        # counter-clockwise)
        new_x = current_x * cosine - current_y * sine
        new_y = current_x * sine + current_y * cosine

        # translate the calculated coordinates so that the circle is
        # centered about ('center_x', 'center_y')
        vertices += [ new_x + center_x, new_y + center_y]

        # update the current vertex coordinates
        current_x, current_y = new_x, new_y

    return  pyglet.graphics.vertex_list(num_points + 1,  ('v2f', vertices),
            ('c3B', tuple([ color[i % 3] for i in range(3 * (num_points + 1)) ])))

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
    # repeat the first vertex at the end to close the shape
    return pyglet.graphics.vertex_list(5, ('v2f', (
        origin_x, origin_y,
        origin_x + width, origin_y,
        origin_x + width, origin_y + height,
        origin_x, origin_y + height,
        origin_x, origin_y
    )),
        ('c3B', tuple([ color[i % 3] for i in range(3 * 5) ])
    ))

# create a 960 x 540 window (16:9 ratio)
window = pyglet.window.Window(960, 540)

# generate vertex lists for the drawn objects
circle1 = generateCircle(200, 200, 100, 50, color=(255, 0, 0))
circle2 = generateCircle(350, 450, 30, 15, color=(0, 0, 255))
rect1 = generateRectangle(250, 300, 100, 50)
rect2 = generateRectangle(500, 200, 200, 300, color=(255, 51, 255))

# when the window refreshes, re-draw all the objects (putting these all in a
# batch doesn't seem to work, since then the last vertex of one object is
# always connected to the first vertex of the next one)
@window.event
def on_draw():
    circle1.draw(pyglet.gl.GL_LINE_STRIP);
    circle2.draw(pyglet.gl.GL_LINE_STRIP);
    rect1.draw(pyglet.gl.GL_LINE_STRIP);
    rect2.draw(pyglet.gl.GL_LINE_STRIP);

pyglet.app.run()
