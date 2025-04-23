"""
Connessioni di connessione:
   Pulsante gira la capa tra GND e GPIO4
   Led Rosso (570 ohm) GPIO 13
   Led Verde (570 ohm) GPIO 19
   Led Blu (570 ohm) GPIO 26
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

GPIO.setmode(GPIO.BCM)
st7735spi = spi(port=0, device=0, gpio_DC=25, gpio_RST=24,bus_speed_hz=24000000, transfer_size=4096)
display = st7735(serial_interface=st7735spi, width=160, height=128, rotation=0, bgr=False)

st7219spi = spi(port=0, device=1, gpio=noop())  #device 1 = CE1
d7219 = max7219(st7219spi,  cascaded=4, block_orientation=90, rotate=2, blocks_arranged_in_reverse_order=1)
d7219.contrast(1)

DICE_PIN = 4
LED_BLU = 26
LED_VERDE = 19
LED_ROSSO = 13

GPIO.setup(LED_BLU, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(LED_VERDE, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(LED_ROSSO, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(DICE_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

text_file = open("Oblique/obliqui.txt", "r")
lines = text_file.read().split('\n')
text_file.close()
lines = [line for line in lines if line.strip()]
key_pressed = False
curSentence = curTarot = -1
blankSentence = True
bLed = False
bTime = 0
logo_time = 0
logo0 = False
vr = vg = vb = 0

def coloraLed():
    global bTime,vr,vb,vg
    bTime = 0
    vr = random.randint(0,1)
    vg = random.randint(0,1)
    vb = random.randint(0,1)
    GPIO.output(LED_BLU, GPIO.HIGH if vb == 1 else GPIO.LOW)
    GPIO.output(LED_VERDE, GPIO.HIGH if vg == 1 else GPIO.LOW)
    GPIO.output(LED_ROSSO, GPIO.HIGH if vr == 1 else GPIO.LOW)

def blinkLed():
    global bLed, bTime,vb,vg,vr
    if blankSentence:
       return

    now = time.time()
    if now - bTime >= 1:
       bTime = now
       if bLed:
          bLed = False
          GPIO.output(LED_BLU, GPIO.LOW)
          GPIO.output(LED_VERDE, GPIO.LOW)
          GPIO.output(LED_ROSSO, GPIO.LOW)
       else:
          bLed = True
          GPIO.output(LED_BLU, GPIO.HIGH if vb == 1 else GPIO.LOW)
          GPIO.output(LED_VERDE, GPIO.HIGH if vg == 1 else GPIO.LOW)
          GPIO.output(LED_ROSSO, GPIO.HIGH if vr == 1 else GPIO.LOW)

def showLogo():
    global logo0, logo_time
    now = time.time()
    if now - logo_time >= 5:
       logo_time = now
       if logo0:
          f = "logo0.jpg"
          logo0 = False
       else:
          f = "logo1.jpg"
          logo0 = True
       img = Image.open(f).convert("RGB")
       img = img.rotate(-90, expand=True)
       display.display(img.resize((display.width, display.height), Image.BICUBIC))
    else:
       coloraLed()

def loadimg(n):
    img = Image.open("Tarot/"+str(n)+".jpg").convert("RGB")
    img = img.rotate(-90, expand=True)
    return img.resize((display.width, display.height), Image.BICUBIC)

def checkKey():
    global key_pressed
    blinkLed()
    if GPIO.input(DICE_PIN) == 0:
        key_pressed = True
    return key_pressed

def showSentence(tarot, oblique):
    global curSentence, curTarot, blankSentence

    blankSentence = False
    if tarot != curTarot:
        curTarot = tarot
        img = loadimg(tarot)
        display.display(img)

    if curSentence != oblique:
        curSentence = oblique
        msg = lines[oblique]
        show_message_with_callback(d7219, "       " + msg, callback=checkKey)

def repeatSentence():
    global curSentence, blankSentence
    if blankSentence:
        thexor()
    else:
        show_message_with_callback(d7219, "       " + lines[curSentence], callback=checkKey)

def print_message(device, message, font=proportional(SINCLAIR_FONT), fill="white"):
    with canvas(device) as draw:
        text(draw, (0, 0), message, font=font, fill=fill)

def show_message_with_callback(device, message, font=proportional(SINCLAIR_FONT), fill="white", scroll_delay=0.01, callback=None):
    global key_pressed
    message = message + "              "
    text_width = sum(len(font[ord(c)]) for c in message)
    virt = viewport(device, width=text_width, height=device.height)
    print_message(virt, message, font=font, fill=fill)

    # Scroll
    for x in range(0, text_width-device.width):
        virt.set_position((x, 0))
        if callback:
            callback()
        if key_pressed:
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
            if checkKey():
                return True
            showLogo()

        while curX < 31:
            set_pixel(d7219, buf, draw, curX, curY, False)
            if speed > 0:
                time.sleep(speed)
            curX = curX + 1
            set_pixel(d7219, buf, draw, curX, curY, True)
            if checkKey():
                return True
            showLogo()

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
            if checkKey():
                return True
            showLogo()

        while curY > destY:
            set_pixel(d7219, buf, draw, curX, curY, True)
            if speed > 0:
                time.sleep(speed)
            set_pixel(d7219, buf, draw, curX, curY, False)
            curY = curY - 1
            if checkKey():
                return True
            showLogo()

        set_pixel(d7219, buf, draw, curX, curY, True)
    return False

def set_pixel(device, buf, draw, x, y, on=True):
    draw.point((x, y), fill="white" if on else "black")
    device.display(buf)    # instantly pushes the whole image

def thexor(speed=0.01):
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
        if checkKey():
           return True

    coords.reverse()
    for t in coords:
       if animotion(buf, draw, t[0], t[1], speed, True):
          return True

    return False

try:
    while True:
        if key_pressed:
           key_pressed = False
           if blankSentence:
              blankSentence = False
              random.seed()
              showSentence(random.randint(0, 21), random.randint(0, len(lines)-1))
           else:
              blankSentence = True
        repeatSentence()
        time.sleep(0.2)

finally:
    GPIO.cleanup()
    print("Clean")
