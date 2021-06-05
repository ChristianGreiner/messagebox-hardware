# Messagebox Hardware

The hardware of the messagebox. Inspired by [Lovebox](https://en.lovebox.love/).

## Used Hardware

- Raspberry Pi Zero
- SPI TFT Display 1,8" (128 x 160) ([Amazon](https://www.amazon.de/AZDelivery-Pixeln-Display-Arduino-Raspberry/dp/B078J5TS2G)): Show the message
- SG90 9g Micro Servo: Notify about a new message 
- Reed contact / or switch: Read the sate, if box is open or closed

## Screenshots

![photo_2021-06-05_22-12-38](https://user-images.githubusercontent.com/6233308/120904809-79508180-c64e-11eb-8324-5eecb48c8d8a.jpg)
![photo_2021-06-05_22-12-49](https://user-images.githubusercontent.com/6233308/120904810-79e91800-c64e-11eb-8326-12bbda7a14c6.jpg)
![photo_2021-06-05_22-12-55](https://user-images.githubusercontent.com/6233308/120904811-79e91800-c64e-11eb-8abf-fdcd00a137d0.jpg)


## Installation

### Quickstart (WIP)
If you have a fresh installation if your system, you can use the [install script](https://github.com/ChristianGreiner/messagebox-hardware/blob/master/scripts/messagebox_install.sh).
Check it out to see, what it does. 

### Manual installation

**Requirements**
- Enable SPI (with `raspi-config`)
- Pacakges: `$> sudo apt install ttf-dejavu libopenjp2-7 libtiff5 virtuelenv`

1. Clone repo
2. Create virtual env: `$> virtualenv venv`
3. Activate the venv: `$>  source mypython/bin/activate`
4. Install pip requirements: `$>  pip install -r requirements.txt`

## First Use 

1. First start: `$> python main.py`. The app should exist immediately with exception: `No Endpoint found.`
2. Open the newly created config file `config.ini` and add the endpoint of your [messagebox-backend](https://github.com/ChristianGreiner/messagebox-backend)
```
[SETTINGS]
endpoint = https://yourdomain.net <- dont add "/" and the end
token = 
hardwareid = 
setup = False
```
3. Restart the app again: `$> python main.py`
4. Now the display should show the message "Device ID: 123456". Login in your messagebox account, open the "device"-page and register your device.
5. If the code was correct, the device should be registered and is ready to use.

## Setup the hardware

Everything can be connected to the Raspberry Pi Zero GPIOs directly, so you dont need to solder.
To change the Pins or even the display type, just edit the main.py

```
...

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

...
```

## Used Libraries
- https://github.com/python-pillow/Pillow
- https://github.com/adafruit/Adafruit_CircuitPython_RGB_Display
- https://github.com/gpiozero/gpiozero




