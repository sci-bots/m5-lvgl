import gc

import lvgl as lv
import lvesp32
import ILI9341 as ili
import machine
import utime


__all__ = ['ButtonsInputEncoder', 'EncoderInputDriver',
           'general_event_handler', 'init_ili9341']

class ButtonsInputEncoder:
    def __init__(self, left=39, right=38, press=37):
        self.encoder_state = {'left': 0, 'right': 0, 'pressed': False}

        def on_press_left(*args):
            self.encoder_state['left_time'] = utime.ticks_ms()
            self.encoder_state['left'] += 1

        def on_press_right(*args):
            self.encoder_state['right_time'] = utime.ticks_ms()
            self.encoder_state['right'] += 1

        def on_toggle_press(pin):
            self.encoder_state['press_time'] = utime.ticks_ms()
            self.encoder_state['pressed'] = not pin.value()

        btn_left = machine.Pin(left, machine.Pin.IN, machine.Pin.PULL_UP)
        btn_left.irq(trigger=machine.Pin.IRQ_FALLING, handler=on_press_left)
        btn_right = machine.Pin(right, machine.Pin.IN, machine.Pin.PULL_UP)
        btn_right.irq(trigger=machine.Pin.IRQ_FALLING, handler=on_press_right)
        btn_press = machine.Pin(press, machine.Pin.IN, machine.Pin.PULL_UP)
        btn_press.irq(trigger=machine.Pin.IRQ_FALLING | machine.Pin.IRQ_RISING,
                      handler=on_toggle_press)

    @property
    def diff_peek(self):
        return self.encoder_state['right'] - self.encoder_state['left']

    @property
    def diff(self):
        diff = self.encoder_state['right'] - self.encoder_state['left']
        self.encoder_state['left'] = 0
        self.encoder_state['right'] = 0
        return diff

    @property
    def pressed(self):
        return self.encoder_state['pressed']


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


def init_ili9341():
    '''Configure LittlevGL to use M5Stack ILI9341.'''
    disp = ili.display(mosi=23, miso=19, clk=18, cs=14, dc=27, rst=33,
                       backlight=32)
    disp.init()

    # Register display driver
    disp_buf1 = lv.disp_buf_t()
    buf1_1 = bytearray(480*10)

    lv.disp_buf_init(disp_buf1,buf1_1, None, len(buf1_1)//4)
    disp_drv = lv.disp_drv_t()
    lv.disp_drv_init(disp_drv)
    disp_drv.buffer = disp_buf1
    disp_drv.flush_cb = disp.flush
    disp_drv.hor_res = 320
    disp_drv.ver_res = 240
    lv.disp_drv_register(disp_drv)

    return {'disp': disp, 'disp_drv': disp_drv}
