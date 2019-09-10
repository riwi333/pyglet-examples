import pyglet

# PURPOSE: print out whatever key the user presses

# create the main window
window = pyglet.window.Window()

# create an event handler for when a key is pressed
@window.event
def on_key_press(symbol, modifiers):
    print(chr(symbol) + " was pressed")

# create an event handler for when the window is refreshed
@window.event
def on_draw():
    window.clear()  # clear the window

pyglet.app.run()
