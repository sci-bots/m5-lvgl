"""
Create your first object: a "Hello world" label

This Python tutorial is based on the c version available at:
    https://github.com/littlevgl/lv_examples/lv_tutorial
"""
import lvgl as lv
from m5_lvgl import M5ili9341

lv.init()
disp = M5ili9341()
scr = lv.obj()
label = lv.label(scr)
label.set_text("Hello World!")
label.align(lv.scr_act(), lv.ALIGN.CENTER, 0, 0)
lv.scr_load(scr)

