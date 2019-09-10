import pyglet

# PURPOSE: another "Hello, world" program

# create the main window
window = pyglet.window.Window()

# create a "Hello, world" label in the middle of the screen
label = pyglet.text.Label(  'Hello, world',
                            font_name = 'Times New Roman',
                            font_size = 36,
                            x = window.width / 2,
                            anchor_x = 'center',
                            y = window.height / 2,
                            anchor_y = 'center' )

# attach an 'on_draw' function to the window to define what to do
# when window refreshes
@window.event
def on_draw():
    window.clear()  # clear the window
    label.draw()    # draw the label

# run the application (enter the event loop)
pyglet.app.run()
