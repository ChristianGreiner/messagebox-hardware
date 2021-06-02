import adafruit_rgb_display.st7735 as st7735
import board
import digitalio

from Messagebox import Messagebox

# Pick your Display
# see https://github.com/adafruit/Adafruit_CircuitPython_RGB_Display
display = st7735.ST7735R(
    spi=board.SPI(),
    cs=digitalio.DigitalInOut(board.CE0),
    dc=digitalio.DigitalInOut(board.D24),
    rst=digitalio.DigitalInOut(board.D25),
    baudrate=24000000,
    rotation=90,
)

trigger_pin = 26 # Read state trigger (if box is open or closed)
servo_pin = 17

if __name__ == "__main__":
    msgBox = Messagebox(display, trigger_pin=trigger_pin, servo_pin=servo_pin)
    msgBox.run()
