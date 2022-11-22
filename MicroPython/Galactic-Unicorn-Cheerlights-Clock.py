# Clock example application with a constantly changing background color from the #Cheerlights API
#
# Be sure to create/edit the secrets.py file with your WiFi name and passphrase
#
# Clock will synchronize with NTP on startup and every 24 hours afterwords. Application will poll the #cheerlights REST API every minute
# to grab a new color for the background.
#
# Special Thanks:  
#   @ZodiusInfuser & @MichaelBell for the excellent clock reference application at: https://tnkr.in/5n2
#   @Helgibbons for the excellent Cheerlights_History reference application at: https://tnkr.in/5n4
#   Bytes N Bits tutorial on multi-core, multithreading on the Raspberry Pi Pico: https://tnkr.in/5mp
#   
import time
import math
import machine
from machine import WDT
import network
import ntptime
import _thread
import urequests, json
from galactic import GalacticUnicorn
from picographics import PicoGraphics, DISPLAY_GALACTIC_UNICORN as DISPLAY

# You will want to set this to your timezone offset (UTC+/-?)
utc_offset = -8 #PST America/Los_Angeles


try:
    from secrets import WIFI_SSID, WIFI_PASSWORD
    wifi_available = True
except ImportError:
    print("Create secrets.py with your WiFi credentials to sync the clock and to get cheer colors")
    wifi_available = False

# I advise you not to enable the watchdog timer until your code has been running stable for some time.
# Not only will the watchdog timer mask any issues that you may have in your code,
# but it's also difficult to disable and save your code quickly from your IDE before the board resets itself again.
WDT_ENABLED = False
wdt = None
if WDT_ENABLED:
    wdt = WDT(timeout=10000)

#Create a single wlan object and use as a global for all net calls
wlan = network.WLAN(network.STA_IF)

# create galactic object and graphics surface for drawing
gu = GalacticUnicorn()
graphics = PicoGraphics(DISPLAY)
gu.set_brightness(1)

# create the rtc object
rtc = machine.RTC()
year, month, day, wd, hour, minute, second, _ = rtc.datetime()
last_second = second

# Screen Dimensions
width = GalacticUnicorn.WIDTH
height = GalacticUnicorn.HEIGHT

# Default cheer color is red until the first web call
cheercolor = (255,0,0)

# set up some pens to use later
WHITE = graphics.create_pen(255, 255, 255)
BLACK = graphics.create_pen(0, 0, 0)

#Timer global variables
last_time_sync = time.time()
last_cheerlight_check = time.time()


# Paint all the pixes the cheercolor before the clock text is overlayed.
def set_background():
    global cheercolor
    graphics.set_pen(graphics.create_pen(int(cheercolor[0]), int(cheercolor[1]), int(cheercolor[2])))
    for x in range(0,width):
        for y in range(0,height):
            graphics.pixel(x, y)


#From Pimoroni's sample applications. The text is easier to read if it has a black outline
def outline_text(text, x, y):
    graphics.set_pen(BLACK)
    graphics.text(text, x - 1, y - 1, -1, 1)
    graphics.text(text, x, y - 1, -1, 1)
    graphics.text(text, x + 1, y - 1, -1, 1)
    graphics.text(text, x - 1, y, -1, 1)
    graphics.text(text, x + 1, y, -1, 1)
    graphics.text(text, x - 1, y + 1, -1, 1)
    graphics.text(text, x, y + 1, -1, 1)
    graphics.text(text, x + 1, y + 1, -1, 1)

    graphics.set_pen(WHITE)
    graphics.text(text, x, y, -1, 1)


def wifi_connect():
    global wlan
    if not wifi_available:
        return
    
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    # Wait for connect success or failure
    max_wait = 100
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        if WDT_ENABLED:
            wdt.feed()
        time.sleep(0.2)

    if max_wait > 0:
        print("Connected")


# Connect to wifi and synchronize the RTC time from and NTP server
def sync_time():
    global wlan
    if not wifi_available:
        return

    if not wlan.isconnected():
        wifi_connect()

    try:
        ntptime.settime()
        print("Time set")
    except OSError as e:
        print(e)
        pass


# Set the cheer color after doing a little network housekeeping
def get_cheerlight_color():
    global cheercolor, wlan

    if not wifi_available:
        return
    
    if not wlan.isconnected():
        wifi_connect()
    
    try:
        newcolor = get_color()
        if newcolor != None:
            cheercolor = newcolor
    except OSError as e:
        print(e)
        pass


def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def get_color():
    url = "http://api.thingspeak.com/channels/1417/field/2/last.json"
    try:
        r = urequests.get(url)
        if r.status_code > 199 and r.status_code < 300:
            cheerlights = json.loads(r.content.decode('utf-8'))
            print(cheerlights['field2'])
            color = hex_to_rgb(cheerlights['field2'])
            r.close()
            return color
        else:
            print(r.status_code)
            return None
    except Exception as e:
        print(e)
        return None


def sync_time_if_reqd():
    global last_time_sync
    if time.time() - last_time_sync > 86400: #Sync once per day
        print ("Running Time Sync")
        sync_time()
        last_time_sync = time.time()


def get_cheerlight_color_if_reqd():
    global last_cheerlight_check
    if time.time() - last_cheerlight_check > 60: #Sync once per minute. Be kind, Cheerlights is a free API
        print ("Getting cheerlight color")
        get_cheerlight_color()
        last_cheerlight_check = time.time()
        

# Check whether the RTC time has changed and if so redraw the display
def redraw_display_if_reqd():
    global year, month, day, wd, hour, minute, second, last_second

    year, month, day, wd, hour, minute, second, _ = rtc.datetime()
    if second != last_second:
        hour += utc_offset
        if hour < 0:
            hour += 24
        elif hour >= 24:
            hour -= 24

        set_background()

        clock = "{:02}:{:02}:{:02}".format(hour, minute, second)

        # set the font
        graphics.set_font("bitmap8")

        # calculate text position so that it is centred
        w = graphics.measure_text(clock, 1)
        #x = int(width / 2 - w / 2 + 1)
        x = 10
        y = 2

        outline_text(clock, x, y)

        last_second = second

# Run the web service calls as a separate thread so that network response time does not interrupt the clock display.
def ws_thread():
    while True:
        sync_time_if_reqd()
        get_cheerlight_color_if_reqd()
        if WDT_ENABLED:
            wdt.feed()
        time.sleep(0.01) # Leave a millisecond delay on all while true loops to keep from locking up the PICO's USB serial interface

# The clock display runs on its own thread so that the display does not freeze when network tasks are waiting for a response.
def clock_thread():
    while True:
        redraw_display_if_reqd()
        gu.update(graphics)
        if WDT_ENABLED:
            wdt.feed()
        time.sleep(0.01) # Leave a millisecond delay on all while true loops to keep from locking up the PICO's USB serial interface
    

# Network initialization & clock sync
sync_time()

#Start the clock display thread on the second core
second_thread = _thread.start_new_thread(clock_thread, ())

#Finally run the main thread loop for the network services
ws_thread()