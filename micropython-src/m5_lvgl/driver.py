import gc
import struct

import lvgl as lv
import lvesp32
import machine
import uasyncio as asyncio
import utime

from ili9341 import ili9341, COLOR_MODE_BGR, MADCTL_ML


DEFAULT_ENCODER_ADDR = 0x5E  # (94)


__all__ = ['ButtonsInputEncoder', 'FacesEncoderInputEncoder',
           'EncoderInputDriver', 'general_event_handler', 'init_ili9341']


class ButtonsInputEncoder:
    def __init__(self, left=39, right=38, press=37):
        self._left = 0
        self._right = 0
        self._pressed = False

        def on_press_left(*args):
            self._left_time = utime.ticks_ms()
            self._left += 1

        def on_press_right(*args):
            self._right_time = utime.ticks_ms()
            self._right += 1

        def on_toggle_press(pin):
            self._press_time = utime.ticks_ms()
            self._pressed = not pin.value()

        btn_left = machine.Pin(left, machine.Pin.IN, machine.Pin.PULL_UP)
        btn_left.irq(trigger=machine.Pin.IRQ_FALLING, handler=on_press_left)
        btn_right = machine.Pin(right, machine.Pin.IN, machine.Pin.PULL_UP)
        btn_right.irq(trigger=machine.Pin.IRQ_FALLING, handler=on_press_right)
        btn_press = machine.Pin(press, machine.Pin.IN, machine.Pin.PULL_UP)
        btn_press.irq(trigger=machine.Pin.IRQ_FALLING | machine.Pin.IRQ_RISING,
                      handler=on_toggle_press)

    @property
    def diff_peek(self):
        return self._right - self._left

    @property
    def diff(self):
        diff = self._right - self._left
        self._left = 0
        self._right = 0
        return diff

    @property
    def pressed(self):
        return self._pressed


class FacesEncoderInputEncoder:
    def __init__(self, i2c, addr=DEFAULT_ENCODER_ADDR, update_period_ms=10,
                 loop=None):
        self.i2c = i2c
        self.addr = addr
        self._buffer = bytearray(3)
        self._diff = 0
        self._pressed = False
        self.update_period_ms = update_period_ms
        self._last_updated = 0
        self._led_settings = bytearray(4)
        if loop is None:
            loop = asyncio.get_event_loop()

    def update(self):
        self.i2c.readfrom_into(self.addr, self._buffer)
        diff, not_pressed, _ = struct.unpack('bBB', bytes(self._buffer))
        self._diff += diff
        self._pressed = not not_pressed
        self._last_updated = utime.ticks_ms()
        gc.collect()

    @property
    def diff(self):
        value = self._diff
        self._diff = 0
        return value

    @property
    def diff_peek(self):
        return self._diff

    @property
    def pressed(self):
        return self._pressed

    def set_led(self, id, colour):
        self._led_settings[0] = id
        r, g, b = colour
        self._led_settings[1] = r
        self._led_settings[2] = g
        self._led_settings[3] = b
        self.i2c.writeto(self.addr, self._led_settings)


class EncoderInputDriver:
    def __init__(self, encoder, group=None):
        def input_callback(drv, data):
            data.enc_diff = encoder.diff
            if encoder.pressed:
                data.state = lv.INDEV_STATE.PR
            else:
                data.state = lv.INDEV_STATE.REL
            gc.collect()
            return False

        self.drv = lv.indev_drv_t()
        self.encoder = encoder
        lv.indev_drv_init(self.drv)
        self.drv.type = lv.INDEV_TYPE.ENCODER
        self.drv.read_cb = input_callback
        self.win_drv = lv.indev_drv_register(self.drv)
        self.group = group

    @property
    def group(self):
        return self._group

    @group.setter
    def group(self, value):
        self._group = value
        if self._group is not None:
            lv.indev_set_group(self.win_drv, self._group)


def general_event_handler(obj, event):
    if event == lv.EVENT.PRESSED:
        print("Pressed\n")
    elif event == lv.EVENT.SHORT_CLICKED:
        print("Short clicked\n")
    elif event == lv.EVENT.CLICKED:
        print("Clicked\n")
    elif event == lv.EVENT.LONG_PRESSED:
        print("Long press\n")
    elif event == lv.EVENT.LONG_PRESSED_REPEAT:
        print("Long press repeat\n")
#     elif event == lv.EVENT.VALUE_CHANGED:
#         print("Value changed: %s\n", lv_event_get_data() ? (const char *)lv_event_get_data() : "")
    elif event == lv.EVENT.RELEASED:
        print("Released\n")
    elif event == lv.EVENT.DRAG_BEGIN:
        print("Drag begin\n")
    elif event == lv.EVENT.DRAG_END:
        print("Drag end\n")
    elif event == lv.EVENT.DRAG_THROW_BEGIN:
        print("Drag throw begin\n")
    elif event == lv.EVENT.FOCUSED:
        print("Focused\n")
    elif event == lv.EVENT.DEFOCUSED:
        print("Defocused\n")


class M5ili9341(ili9341):
    def __init__(
            self, mosi=23, miso=19, clk=18, cs=14, dc=27, rst=33, backlight=32,
            backlight_on=1, hybrid=True, width=320, height=240,
            colormode=COLOR_MODE_BGR, rot=MADCTL_ML, invert=True, **kwargs):
        super().__init__(
            mosi=mosi, miso=miso, clk=clk, cs=cs, dc=dc, rst=rst,
            backlight=backlight, backlight_on=backlight_on, hybrid=hybrid,
            width=width, height=height, colormode=colormode, rot=rot,
            invert=False, **kwargs)
        if invert:
            # Invert colors (work around issue with `invert` kwarg in stock
            # class).
            self.send_cmd(0x21)
