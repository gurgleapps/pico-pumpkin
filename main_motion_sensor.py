# 5 minute hack, please don't judge

import machine
import time
import json
import matrix_fonts
from ht16k33_matrix import ht16k33_matrix
from max7219_matrix import max7219_matrix

#i2c config
clock_pin = 5
data_pin = 4
bus = 0
i2c_addr_left = 0x70
i2c_addr_right = 0x72
# spi config
cs_pin = 5
pir_pin =16

use_max7219 = False
use_i2c = True

pir_sensor = machine.Pin(pir_pin, machine.Pin.IN, machine.Pin.PULL_DOWN)

def scan_for_devices():
    i2c = machine.I2C(bus,sda=machine.Pin(data_pin),scl=machine.Pin(clock_pin))
    devices = i2c.scan()
    if devices:
        for d in devices:
            print(hex(d))
    else:
        print('no i2c devices')

def load_anims(file_name):
  data={}
  try:
    with open(file_name) as infile:
      data=json.load(infile)
  except Exception as err:
      print('Oops problem loading JSON! ')
      print (err)
  return data

anims = load_anims('eyes_ani.json')

if use_i2c:
    scan_for_devices()
    left_eye = ht16k33_matrix(data_pin, clock_pin, bus, i2c_addr_left)
    right_eye = ht16k33_matrix(data_pin, clock_pin, bus, i2c_addr_right)

if use_max7219:
    max7219_eyes = max7219_matrix(machine.SPI(0), machine.Pin(cs_pin, machine.Pin.OUT, True))

def show_char(left, right):
    if use_i2c:
        left_eye.show_char(left)
        right_eye.show_char(right)
    if use_max7219:
        max7219_eyes.show_char(left,right)
        
def anim_runner(anim,font):
    for i in anim:
        if "l" in i:
            if use_i2c:
                left_eye.show_char(font[i["l"]])
            if "r" in i:
                if use_max7219:
                    max7219_eyes.show_char(font[i["l"]],font[i["r"]])
        if "r" in i:
            if use_i2c:
                right_eye.show_char(font[i["r"]])
        if "bl" in i:
            if use_i2c:
                left_eye.set_brightness(i["bl"])
            if use_max7219:
                max7219_eyes.set_brightness(i["bl"])
        if "br" in i:
            if use_i2c:
                right_eye.set_brightness(i["br"])
        time.sleep(i["d"])
        
def scroll_message(font,message='hello',delay=0.1):
    left_message = '   ' + message
    right_message = message + '   '
    length=len(right_message)
    char_range=range(length-1)
    for char_pos in char_range:
      right_left_char=font[right_message[char_pos]]
      right_right_char=font[right_message[char_pos+1]]
      left_left_char=font[left_message[char_pos]]
      left_right_char=font[left_message[char_pos+1]]
      for shift in range(8):
        left_bytes=[0,0,0,0,0,0,0,0]
        right_bytes=[0,0,0,0,0,0,0,0]
        for col in range(8):
          left_bytes[col]=left_bytes[col]|left_left_char[col]<<shift
          left_bytes[col]=left_bytes[col]|left_right_char[col]>>8-shift;
          right_bytes[col]=right_bytes[col]|right_left_char[col]<<shift
          right_bytes[col]=right_bytes[col]|right_right_char[col]>>8-shift;
        if use_max7219:
                    max7219_eyes.show_char(left_bytes,right_bytes)
        if use_i2c:
                left_eye.show_char(left_bytes)
                right_eye.show_char(right_bytes)
        time.sleep(delay)
        
show_char([0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0])     
time.sleep(1)
last = pir_sensor.value()
while True:
    if last!=pir_sensor.value():
        last = pir_sensor.value()
        print(last)
        if last == 1:
            anim_runner(anims['growEyes'],matrix_fonts.eyes)
            anim_runner(anims['roll'],matrix_fonts.eyes)
        else:
            show_char([0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0])
    time.sleep(0.2)
        
while True:
    if pir_sensor.value()==1:
        #scroll_message(matrix_fonts.textFont1, ' Spooky ')
        #anim_runner(anims['stareAndBlink'],matrix_fonts.eyes)
        anim_runner(anims['growEyes'],matrix_fonts.eyes)
        anim_runner(anims['roll'],matrix_fonts.eyes)
        #anim_runner(anims['downLeftABit'],matrix_fonts.eyes)
       # anim_runner(anims['stareAndBlink'],matrix_fonts.eyes)
       # anim_runner(anims['downRightABit'],matrix_fonts.eyes)
      #  anim_runner(anims['stareAndBlink'],matrix_fonts.eyes)
#         scroll_message(matrix_fonts.textFont1, ' Trick or Treat ')
#         anim_runner(anims['roll'],matrix_fonts.eyes)
#         anim_runner(anims['stareAndBlink'],matri x_fonts.eyes)
#         anim_runner(anims['stareAndBlink'],matrix_fonts.eyes)
#         anim_runner(anims['growEyes'],matrix_fonts.eyes)
#         anim_runner(anims['roll'],matrix_fonts.eyes)
#         anim_runner(anims['ghosts1'],matrix_fonts.eyes)
#         anim_runner(anims['stareAndBlink'],matrix_fonts.eyes)
#         anim_runner(anims['winkLeft'],matrix_fonts.eyes)
#         anim_runner(anims['winkRight'],matrix_fonts.eyes)
#         anim_runner(anims['stareAndBlink'],matrix_fonts.eyes)
    else:
        show_char([0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0])
    time.sleep(0.1)
