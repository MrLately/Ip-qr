import socket
from PIL import Image, ImageDraw, ImageFont
import RPi.GPIO as GPIO
from luma.core.interface.serial import spi
from luma.oled.device import sh1106
import qrcode
import time

# Set the GPIO pin numbering mode to BCM
GPIO.setmode(GPIO.BCM)

# Initialize the GPIO interface
gpio_DC = 27
gpio_RST = 17
GPIO.setup(gpio_DC, GPIO.OUT)
GPIO.setup(gpio_RST, GPIO.OUT)

# Initialize the SPI interface and OLED device
serial = spi(port=0, device=0, gpio_DC=gpio_DC, gpio_RST=gpio_RST)
device = sh1106(serial)

def get_ip_address(max_retries=15, retry_delay=5):
    for _ in range(max_retries):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                ip_address = s.getsockname()[0]
            return ip_address
        except:
            # Sleep for the specified retry delay (in seconds) before the next attempt
            time.sleep(retry_delay)

    # If all retries fail, return a default IP address
    return "127.0.0.1"

def generate_qr_code(ip_address, port):
    # Generate a QR code with a URL that opens when scanned
    url = f"http://{ip_address}:{port}"  # Construct the URL
    qr = qrcode.QRCode(version=1, box_size=2, border=1)
    qr.add_data(url)
    qr.make(fit=True)

    # Create an image from the QR code
    img = qr.make_image(fill_color="black", back_color="white")

    # Save the QR code image as a PNG
    img_path = f"qr_{ip_address.replace('.', '_')}_{port}.png"
    img.save(img_path)

    return img_path

# Create an image and drawing object
image = Image.new("1", device.size)
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()

# Clear the screen
draw.rectangle(device.bounding_box, outline="black", fill="black")

# Adjust the contrast (0 for low contrast, 255 for high contrast)
contrast = 127  # Adjust this value as needed
device.contrast(contrast)

# Get the IP address and port
ip_address = get_ip_address()
port = 5000  # Change this to your desired port

# Format and draw the IP and port
text = f"{ip_address}:{port}"
draw.text((15, 55), text, fill="white", font=font)

# Generate and display the QR code
qr_code_path = generate_qr_code(ip_address, port)
qr_code = Image.open(qr_code_path)
image.paste(qr_code, (35, 0))

# Display the image on the OLED screen
device.display(image)

try:
    while True:
        time.sleep(100)  # Sleep for 1 second
except KeyboardInterrupt:
    # Cleanup GPIO before exiting
    GPIO.cleanup()
