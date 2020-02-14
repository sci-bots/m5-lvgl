"""
# Learn how to create GUI elements on the screen

The basic building blocks (components or widgets) in LittlevGL are the graphical objects.
For example:
- Buttons
- Labels
- Charts
- Sliders, etc.

In this part you can learn the basics of the objects like creating, positioning, sizing etc.
You will also meet some different object types and their attributes.

## PARENT-CHILD STRUCTURE

A parent can be considered as the container of its children.
Every object has exactly one parent object (except screens).
A parent can have unlimited number of children.
There is no limitation for the type of the parent.

The children are visible only on their parent. The parts outside will be cropped (not displayed)

If the parent is moved the children will be moved with it.

The earlier created object (and its children) will drawn earlier.
Using this layers can be built.

## INHERITANCE

Similarly to object oriented languages some kind of inheritance is used
among the object types. Every object is derived from the 'Basic object'. (lv_obj)
The types are backward compatible therefore to set the basic parameters (size, position etc.)
you can use 'lv_obj_set/get_...()' function.

## LEARN MORE

This Python tutorial is based on the c version available at:
    https://github.com/littlevgl/lv_examples/lv_tutorial
General overview: http://www.gl.littlev.hu/objects
Detailed description of types: http://www.gl.littlev.hu/object-types
"""
import lvgl as lv
from m5_lvgl import M5ili9341, ButtonsInputEncoder, EncoderInputDriver


def btn_event_cb(btn, event):
    """
    Called when a button is released.

    Parameters
    ----------
    btn :
        The Button that triggered the event.
    event :
        The triggering event.
    """
    if event == lv.EVENT.RELEASED:
        # Increase the button width
        width = btn.get_width()
        btn.set_width(width + 20)


def ddlist_event_cb(ddlist, event):
    """
    Called when a new option is chosen in the drop down list.

    Parameters
    ----------
    ddlist :
        The drop down list that triggered the event.
    event :
        The triggering event.
    """
    if event == lv.EVENT.VALUE_CHANGED:
        opt = ddlist.get_selected() # Get the id of selected option

        # Modify the slider value according to the selection
        slider.set_value(round((opt * 100) / 4), True)

"""
INITIALIZE DISPLAY DRIVER
"""
lv.init() # Initialize LittlevGL library
disp = M5ili9341() # Create a display driver

"""
CREATE A SCREEN

Create a new screen and load it
Screen can be created from any type object type
Now a Page is used which is an object with scrollable content
"""
scr = lv.obj()
lv.scr_load(scr)

"""
ADD A TITLE
"""
label = lv.label(scr) #First parameters (scr) is the parent
label.set_text("Object usage demo") # Set the text
label.set_x(50) # Set the x coordinate

"""
CREATE TWO BUTTONS
"""
# Create a button
btn1 = lv.btn(scr) # Create a button on the currently loaded screen
btn1.set_event_cb(btn_event_cb) # Set function to be called when the button is released
btn1.set_size(btn1.get_width(), 30) # Set the size
btn1.align(label, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 20) # Align below the label

# Create a label on the button (the 'label' variable can be reused)
label = lv.label(btn1)
label.set_text("Button 1")

# Create a second button
btn2 = lv.btn(scr) # Create a button on the currently loaded screen
btn2.set_event_cb(btn_event_cb) # Set function to be called when the button is released
btn2.set_size(btn2.get_width(), 30) # Set the size
btn2.align(btn1, lv.ALIGN.OUT_RIGHT_MID, 50, 0) # Align next to the prev. button.

# Create a label on the button
label = lv.label(btn2)
label.set_text("Button 2")

"""
ADD A SLIDER
"""
slider = lv.slider(scr) # Create a slider
slider.set_size(round(scr.get_width() / 3), slider.get_height()) # Set the size
slider.align(btn1, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 20) # Align below the first button
slider.set_value(30, False) # Set the current value

"""
ADD A DROP DOWN LIST
"""
ddlist = lv.ddlist(scr) # Create a drop down list
ddlist.align(slider, lv.ALIGN.OUT_RIGHT_TOP, 50, 0) # Align next to the slider
ddlist.set_top(True) # Enable to be on the top when clicked
ddlist.set_options("None\nLittle\nHalf\nA lot\nAll")# Set the options
ddlist.set_event_cb(ddlist_event_cb) # Set function to call on new option is chosen

"""
CREATE A CHART
"""
chart = lv.chart(scr) # Create the chart
chart.set_size(round(scr.get_width() / 2), round(scr.get_width() / 4)) # Set the size
chart.align(slider, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 20) # Align below the slider
chart.set_series_width(3) # Set the line width

# Add a RED data series and set some points
dl1 = chart.add_series(lv.color_hex(0xFF0000))
chart.set_next(dl1, 10)
chart.set_next(dl1, 25)
chart.set_next(dl1, 45)
chart.set_next(dl1, 80)

# Add a BLUE data series and set some points
dl2 = chart.add_series(lv.color_hex(0x4070C0))
chart.set_next(dl2, 10)
chart.set_next(dl2, 25)
chart.set_next(dl2, 45)
chart.set_next(dl2, 80)
chart.set_next(dl2, 75)
chart.set_next(dl2, 505)

"""
CREATE ENCODER

Emulate an encoder using the 3 buttons on the front of the m5stack. The first
button moves left, the second button moves right, and the third button
selects/deselects.
"""
button_encoder = ButtonsInputEncoder()
button_driver = EncoderInputDriver(button_encoder)

"""
ADD WIDGETS TO A GROUP AND ASSOCIATE WITH DRIVER

Add the "selectable" widgets to a group and associate this group with the
button encoder driver.
"""
group = lv.group_create() # Create a group
lv.group_add_obj(group, btn1)
lv.group_add_obj(group, btn2)
lv.group_add_obj(group, slider)
lv.group_add_obj(group, ddlist)
button_driver.group = group

