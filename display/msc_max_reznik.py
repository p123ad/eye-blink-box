import time
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7735 as st7735  # pylint: disable=unused-import
from os import listdir
from os.path import isfile, join

# # Test of writing a class for the display
# class Display:
#     baudrate = 24000000
#     def __init__(self, cs_pin, dc_pin, reset_pin, display_backlight_pin):
#         self.cs_pin = digitalio.DigitalInOut(cs_pin)
#         self.dc_pin = digitalio.DigitalInOut(dc_pin)
#         self.reset_pin = digitalio.DigitalInOut(reset_pin)
#         self.display_backlight_pin = digitalio.DigitalInOut(display_backlight_pin)

#     def begin(self):
#         # Setup SPI bus using hardware SPI:
#         spi = board.SPI()
#         # 1.8" ST7735R
#         disp = st7735.ST7735R(spi, rotation=90,                           
#                         cs=self.cs_pin,
#                         dc=self.dc_pin,
#                         rst=self.reset_pin,
#                         baudrate=self.baudrate)
#         self.display_backlight_pin.switch_to_output()
#         self.display_backlight_pin.value = True






def drawImage(imagePath):
    image = Image.open(imagePath)
    # Scale the image to the smaller screen dimension
    image_ratio = image.width / image.height
    screen_ratio = width / height
    if screen_ratio < image_ratio:
        scaled_width = image.width * height // image.height
        scaled_height = height
    else:
        scaled_width = width
        scaled_height = image.height * width // image.width
    image = image.resize((scaled_width, scaled_height), Image.BICUBIC)

    # Crop and center the image
    x = scaled_width / 2 - width / 2
    y = scaled_height / 2 - height / 2
    image = image.crop((x, y, x + width, y + height-6))

    # Display image.
    disp.image(image)

# function shows a gif
# gifFolderPath includes the folder path to gif frames
# inside the folder the naming for the frames must be "folderName (1).jpg", "folderName (2).jpg", etc.
def showGIF(gifFolderPath, repetitions):
    folderName = gifFolderPath.split("/")
    # find all elements in the folder and count them
    onlyfiles = [f for f in listdir(gifFolderPath) if isfile(join(gifFolderPath, f))]
    numberOfFiles = len(onlyfiles)

    for j in range(repetitions):
        for i in range(1, numberOfFiles):
            drawImage(gifFolderPath + "/" +  folderName[-1] + " (" + str(i) + ").jpg")
            time.sleep(0.05)



#display1 = Display(board.CE0, board.D24, board.D25, board.D22)
#display1.begin()

# Configuration for CS and DC pins (these are PiTFT defaults):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D24)
reset_pin = digitalio.DigitalInOut(board.D25)

# # Display backlight pin
# # The backlight will be turned on
# # after shutdown the backlight will turn off
display_backlight_pin = digitalio.DigitalInOut(board.D22)
display_backlight_pin.switch_to_output()
display_backlight_pin.value = True



# # Config for display baudrate (default max is 24mhz):
BAUDRATE = 24000000

# # Setup SPI bus using hardware SPI:
spi = board.SPI()

# # 1.8" ST7735R
disp = st7735.ST7735R(spi, rotation=270,                           
                        cs=cs_pin,
                        dc=dc_pin,
                        rst=reset_pin,
                        baudrate=BAUDRATE)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
if disp.rotation % 180 == 90:
    height = disp.width  # we swap height/width to rotate it to landscape!
    width = disp.height
else:
    width = disp.width  # we swap height/width to rotate it to landscape!
    height = disp.height
image = Image.new("RGB", (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image)

drawImage("/home/pi/eye-blink/display/msc_gimp.jpg")


