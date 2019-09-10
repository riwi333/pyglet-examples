import pyglet
from math import radians, sin, cos, sqrt

# PURPOSE: selection of functions developed in previous tests for use in test6

# generateCircle: generate the vertex list needed to draw and color a circle
#
# @param center     :   tuple of x- and y-coordinates for the center of the circle
# @param radius     :   radius of the circle
# @param num_points :   number of vertices used to draw the circle
#                       (more vertices make the circle smoother, but more
#                       computationally expensive)
# @param color      :   3-tuple of the RGB value to color the circle with
#                       (optional)
# @param fill       :   boolean representing if the circle should be filled
#                       in or not (optional)
# @param batch      :   batch to add vertex list to (optional)
#
def generateCircle(center, radius, num_points, color=(255, 255, 255), fill=False, batch=None):
    # initialize the list of vertex coordinates with the top of the circle
    vertices = [ center[0], center[1] + radius ]

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
    currentVertex = [ 0, radius ]

    # calculate the vertices used to draw the circle (the first vertex is
    # repeated at the end to close the circle)
    for i in range(num_points):
        # get the x and y coordinates of the next vertex (which will be the
        # current vertex rotated 'angle' radians around the circle,
        # counter-clockwise)
        nextVertex = [  currentVertex[0] * cosine - currentVertex[1] * sine,
                        currentVertex[0] * sine + currentVertex[1] * cosine ]

        # translate the calculated coordinates so that the circle is
        # centered about ('center_x', 'center_y')
        vertices += [ nextVertex[0] + center[0], nextVertex[1] + center[1] ]

        # update the current vertex coordinates
        currentVertex = nextVertex

    # triangulate the circle to fully color it (use GL_TRIANGLES mode)
    if fill is True:
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

    # if we're not filling in the circle, we can use GL_LINE_STRIP mode to draw the outline
    else:
        if batch is None:
            # we have 'num_points' + 1 total vertices; the last vertex is the first vertex
            # repeated so that the circle closes
            return  pyglet.graphics.vertex_list(num_points + 1,
                    ('v2f', vertices),
                    ('c3B', color * (num_points + 1)))

        else:
            return  batch.add(num_points + 1, pyglet.gl.GL_LINE_STRIP, None,
                    ('v2f', vertices),
                    ('c3B', color * (num_points + 1)))

# generateRectangle: generate the vertex list needed to draw a rectangle
#
# @param origin     :   tuple of x- and y-coordinates for the bottom left corner of rectangle
# @param length     :   length of rectangle
# @param width      :   width of rectangle
# @param color      :   3-tuple of the RGB value to color the rectangle
#                       (optional)
# @param fill       :   boolean representing if the rectangle should be filled
#                       in or not (optional)
# @param batch      :   batch to add vertex list to (optional)
#
def generateRectangle(origin, width, height, color=(255, 255, 255), fill=False, batch=None):
    # calculate the corner vertices' coordinates for the rectangle (in counter-clockwise
    # order, starting with the bottom left corner)
    vertices = [    origin[0], origin[1],
                    origin[0] + width, origin[1],
                    origin[0] + width, origin[1] + height,
                    origin[0], origin[1] + height   ]

    # triangulate the rectangle to color it with GL_TRIANGLES mode
    if fill is True:
        # if no batch is specified, just return the vertex list used to make the rectangle (should
        # be drawn in GL_TRIANGLES mode)
        if batch is None:
            return  pyglet.graphics.vertex_list_indexed(4,
                    [ 0, 1, 2, 2, 3, 0 ],
                    ('v2f', vertices),
                    ('c3B', color * 4))

        # otherwise, add the vertex list to the given batch and return it
        else:
            return  batch.add_indexed(4, pyglet.gl.GL_TRIANGLES, None,
                    [ 0, 1, 2, 2, 3, 0 ],
                    ('v2f', vertices),
                    ('c3B', color * 4))

    # otherwise, if we're not filling in the rectangle, use GL_LINE_STRIP mode
    else:
        if batch is None:
            # add the bottom left corner as a 5th vertex to close the rectangle
            return  pyglet.graphics.vertex_list(5,
                    ('v2f', vertices + origin),
                    ('c3B', color * 5))

        else:
            return  batch.add(5, pyglet.gl.GL_LINE_STRIP, None,
                    ('v2f', vertices + origin),
                    ('c3B', color * 5))

# generateLine: generate vertex list needed to draw a line of arbitrary thickness
#
# @param p1         :   tuple of (x, y) coordinates for first vertex
# @param p2         :   tuple of (x, y) coordinates for second vertex
# @param color      :   3-tuple of the RGB value to color the line with
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
            return pyglet.graphics.vertex_list(2,
                    ('v2f', (p1[0], p1[1], p2[0], p2[1])),
                    ('c3B', color * 2))

        # if a batch is specified, add the line to the batch and return its vertex list
        else:
            return batch.add    (2, pyglet.gl.GL_LINES, None,
                                ('v2f', (p1[0], p1[1], p2[0], p2[1])),
                                ('c3B', color * 2))

    # lines of thickness > 1.0 need to be triangulated, since GL_TRIANGLES are filled with color
    else:
        # a thick line is basically a rectangle (arbitrarily rotated), so we just find the four
        # corners of the rectangle and triangulate it

        # deal with horizontal and vertical lines by just using generateRectangle()
        if p2[0] == p1[0]:  # vertical line
            # calculate the coordinates for the bottom left corner of the rectangle
            if p1[1] <= p2[1]:
                origin = [ p1[0] - 0.5 * width, p1[1] ]
            else:
                origin = [ p2[0] - 0.5 * width, p2[1] ]

            return generateRectangle(origin, width, abs(p2[1] - p1[1]), color=color, fill=True, batch=batch)

        elif p2[1] == p1[1]:    # horizontal line
            if p1[0] <= p2[0]:
                origin = [ p1[0], p1[1] - 0.5 * width ]
            else:
                origin = [ p2[0], p2[1] - 0.5 * width ]

            return generateRectangle(origin, abs(p2[0] - p1[0]), width, color=color, fill=True, batch=batch)

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
            # line; we then translate the rotated rectangle so its center point is at the
            # true midpoint of the line
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
