"""
Connessioni di connessione:
   Pulsante gira la capa tra GND e GPIO4
   Led Rosso (570 ohm) GPIO 13
   Led Verde (570 ohm) GPIO 19
   Led Blu (570 ohm) GPIO 26
   Retroilluminazione ST7735 (330 ohm) GPIO 06
   Display ST7735:
      Pin 1 = GND
      Pin 2 = 3.3V
      Pin 3  (SCK) = SCLK
      Pin 4  (SDA) = MOSI
      Pin 5  (RES) =  GPIO24
      Pin 6  (RS) =  GPIO25
      Pin 7  (CS) = CE0
      Pin 8   3.3V

   Strip MAX7219:
      Pin 1  (VCC) = 3.3V
      Pin 2  (GND) = GND
      Pin 3  (DIN) = MOSI
      Pin 4  (CS) =  CE1
      Pin 1  (CLK) = SCLK
"""

import RPi.GPIO as GPIO
import enum
import os
import time
import random
from PIL import Image, ImageDraw
from luma.lcd.device import st7735
from luma.core.interface.serial import spi, noop
from luma.led_matrix.device      import max7219
from luma.core.legacy import text
from luma.core.render            import canvas
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT, LCD_FONT
from luma.core.virtual import viewport

KEYSTATE = enum.Enum('KEYSTATE', 'NO_KEY KEY_PRESSED BLANK_KEY POWER_KEY')
LEDCOLOR = enum.Enum('LEDCOLOR', 'NO RED GREEN BLU')
DICE_PIN = 4
LED_BLU = 26
LED_VERDE = 19
LED_ROSSO = 13
RETROILLUMINAZIONE = 21

GPIO.setmode(GPIO.BCM)
GPIO.setup(RETROILLUMINAZIONE, GPIO.OUT, initial=GPIO.HIGH)  # logica attenuante invertita
GPIO.setup(LED_BLU, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(LED_VERDE, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(LED_ROSSO, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(DICE_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

st7735spi = spi(port=0, device=0, gpio_DC=25, gpio_RST=24,bus_speed_hz=24000000, transfer_size=4096)
display = st7735(serial_interface=st7735spi, width=160, height=128, rotation=0, bgr=False)

st7219spi = spi(port=0, device=1, gpio=noop())  #device 1 = CE1
d7219 = max7219(st7219spi,  cascaded=4, block_orientation=90, rotate=2, blocks_arranged_in_reverse_order=1)
d7219.contrast(1)
d7219.clear()

available_decks = os.listdir('Tarot/')
curFolder = random.randint(0, len(available_decks)-1)
text_file = open("Oblique/obliqui.txt", "r")
lines = text_file.read().split('\n')
text_file.close()
lines = [line for line in lines if line.strip()]

ledTime = 0
key_pressed = KEYSTATE.NO_KEY
curSentence = -1
GPIO.setup(RETROILLUMINAZIONE, GPIO.OUT, initial=GPIO.LOW)

def showImage(name):
    img = Image.open(name).convert("RGB")
    img = img.rotate(-90, expand=True)
    display.display(img.resize((display.width, display.height), Image.BICUBIC))

def borisBlank():
    global blankSentence, TAROT_LIST, curFolder
    blankSentence = True
    ledOff()
    showImage("logo.jpg")
    curFolder = curFolder + 1
    if curFolder >= len(available_decks):
        curFolder = 0
    TAROT_LIST = os.listdir('Tarot/' + available_decks[curFolder])

def coloraLed():
    global ledTime
    if blankSentence == False:
        if time.time() - ledTime > 5:
            ledTime = time.time()
            vr = random.randint(0,1)
            vg = random.randint(0,1)
            vb = random.randint(0,1)
            GPIO.output(LED_BLU, GPIO.HIGH if vb == 1 else GPIO.LOW)
            GPIO.output(LED_VERDE, GPIO.HIGH if vg == 1 else GPIO.LOW)
            GPIO.output(LED_ROSSO, GPIO.HIGH if vr == 1 else GPIO.LOW)

def checkKey():
    global key_pressed
    if GPIO.input(DICE_PIN) == 0:
        ledOff(LEDCOLOR.BLU)
        key_pressed = KEYSTATE.KEY_PRESSED
        starttime = time.time()
        while GPIO.input(DICE_PIN) == 0:
            if time.time() - starttime > 2:
                ledOff(LEDCOLOR.GREEN)
                key_pressed = KEYSTATE.BLANK_KEY

            if time.time() - starttime > 5: # shutdown time
                ledOff(LEDCOLOR.RED)
                key_pressed = KEYSTATE.POWER_KEY
                time.sleep(1)
                break
            pass
    return key_pressed

def showSentence(oblique):
    global curSentence
    if curSentence != oblique:
        curSentence = oblique
        msg = lines[oblique]
        show_message_with_callback(d7219, "       " + msg, callback=checkKey)

def showTarot(tarot):
    t = 'Tarot/' + available_decks[curFolder] + '/' + tarot
    showImage(t)

def repeatSentence():
    if blankSentence:
        thexor(0.003)
    else:
        show_message_with_callback(d7219, "       " + lines[curSentence], callback=checkKey)

def print_message(device, message, font=proportional(SINCLAIR_FONT), fill="white"):
    with canvas(device) as draw:
        text(draw, (0, 0), message, font=font, fill=fill)

def show_message_with_callback(device, message, font=proportional(SINCLAIR_FONT), fill="white", scroll_delay=0.01, callback=None):
    message = message + "              "
    text_width = sum(len(font[ord(c)]) for c in message)
    virt = viewport(device, width=text_width, height=device.height)
    print_message(virt, message, font=font, fill=fill)

    # Scroll
    for x in range(0, text_width-device.width):
        virt.set_position((x, 0))
        if callback:
            if callback() != KEYSTATE.NO_KEY:
                break

        if scroll_delay > 0:
            time.sleep(scroll_delay)

def animotion(buf, draw, destX, destY, speed=0.1, reverse = False):
    if reverse:
        curX = destX
        curY = destY
        while curY < 7:
            set_pixel(d7219, buf, draw, curX, curY, False)
            if speed > 0:
                time.sleep(speed)
            curY = curY + 1
            set_pixel(d7219, buf, draw, curX, curY, True)
            if checkKey() != KEYSTATE.NO_KEY:
                return True

        while curX < 31:
            set_pixel(d7219, buf, draw, curX, curY, False)
            if speed > 0:
                time.sleep(speed)
            curX = curX + 1
            set_pixel(d7219, buf, draw, curX, curY, True)
            if checkKey() != KEYSTATE.NO_KEY:
                return True

        set_pixel(d7219, buf, draw, curX, curY, False)

    else:
        curX = 31
        curY = 7
        while curX > destX:
            set_pixel(d7219, buf, draw, curX, curY, True)
            if speed > 0:
                time.sleep(speed)
            set_pixel(d7219, buf, draw, curX, curY, False)
            curX = curX - 1
            if checkKey() != KEYSTATE.NO_KEY:
                return True

        while curY > destY:
            set_pixel(d7219, buf, draw, curX, curY, True)
            if speed > 0:
                time.sleep(speed)
            set_pixel(d7219, buf, draw, curX, curY, False)
            curY = curY - 1
            if checkKey() != KEYSTATE.NO_KEY:
                return True

        set_pixel(d7219, buf, draw, curX, curY, True)
    return False

def set_pixel(device, buf, draw, x, y, on=True):
    draw.point((x, y), fill="white" if on else "black")
    device.display(buf)    # instantly pushes the whole image

def thexor(speed=0.1):
    buf = Image.new('1', (d7219.width, d7219.height))
    draw = ImageDraw.Draw(buf)

    coords=[ (0,2), (0,3), (0,4), (0,5), (1,3), (1,6), (2,3), (2,6), #t
         (4,2), (4,3), (4,4), (4,5), (4,6), (5,4), (6,4), (7,5), (7,6), #h
         (9,3), (9,4),(9,5), (10,2),(10,4),(10,6),(11,2),(11,4),(11,6),(12,3), #(12,6), #e
         (15,0),(15,1),(15,5),(15,6),(16,2),(16,4),(17,3),(18,2),(18,4),(19,0),(19,1),(19,5),(19,6),  #X
         (21,1),(21,2),(21,3),(21,4),(21,5),(22,0),(22,6),(23,0),(23,6),(24,0),(24,6),(25,1),(25,2),(25,3),(25,4),(25,5), #O
         (27,0),(27,1),(27,2),(27,3),(27,4),(27,5),(27,6),(28,0),(28,3),(29,0),(29,3),(29,4),(30,0),(30,3),(30,5),(31,1),(31,2),(31,6) #R
    ]
    for t in coords:
       if animotion(buf, draw, t[0], t[1], speed, False):
          return True

    now = time.time()
    while time.time() - now < 5:
        if checkKey() != KEYSTATE.NO_KEY:
           return True

    coords.reverse()
    for t in coords:
       if animotion(buf, draw, t[0], t[1], speed, True):
          return True

    return False

def ledOff(clr = LEDCOLOR.NO):
    global ledTime
    ledTime = 0
    GPIO.output(LED_BLU, GPIO.HIGH if clr == LEDCOLOR.BLU  else GPIO.LOW)
    GPIO.output(LED_ROSSO, GPIO.HIGH if clr == LEDCOLOR.RED  else GPIO.LOW)
    GPIO.output(LED_VERDE, GPIO.HIGH if clr == LEDCOLOR.GREEN  else GPIO.LOW)

def spegni():
    d7219.clear()
    GPIO.output(RETROILLUMINAZIONE, GPIO.HIGH)
    ledOff()

borisBlank()
try:
    while key_pressed != KEYSTATE.POWER_KEY:
        if key_pressed == KEYSTATE.KEY_PRESSED:
            blankSentence = False
            showTarot(random.choice(TAROT_LIST))
            showSentence(random.randint(0, len(lines)-1))

        elif key_pressed == KEYSTATE.BLANK_KEY:
            borisBlank()

        key_pressed = KEYSTATE.NO_KEY
        coloraLed()
        repeatSentence()
        time.sleep(0.2)

    spegni()
    os.system("sudo shutdown -h now")

finally:
    spegni()
    GPIO.cleanup()
    print("Clean")
