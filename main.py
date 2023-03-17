from machine import I2C, Pin
from urtc import DS3231
import array, time
from machine import Pin
import rp2

#LED board info
NUM_LEDS = 58
PIN_NUM = 22
brightness = 0.8 #we will change brightness later based on the time of day find at (check_time) & (pixels_show) functions

#RTC board info
i2c = I2C(0,scl = Pin(1),sda = Pin(0),freq = 400000)
rtc = DS3231(i2c)
######LED CODE HERE####
@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0)    [T3 - 1]
    jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
    jmp("bitloop")          .side(1)    [T2 - 1]
    label("do_zero")
    nop()                   .side(0)    [T2 - 1]
    wrap()


# Create the StateMachine with the ws2812 program, outputting on pin
sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(PIN_NUM))

# Start the StateMachine, it will wait for data on its FIFO.
sm.active(1)

# Display a pattern on the LEDs via an array of LED RGB values.
ar = array.array("I", [0 for _ in range(NUM_LEDS)])

##########################################################################
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
WHITE = (255, 255, 255)
ORANGE = (255, 130, 0)
PINK = (255, 0, 127)
BBY_BLUE = (56, 100, 239)
NEON_GREEN = (0, 255, 170)
COLORS = (BLACK, RED, YELLOW, GREEN, CYAN, BLUE, PURPLE, WHITE, ORANGE, PINK, BBY_BLUE,
           NEON_GREEN) #define colors for effects functions

def pixels_show():
    #this changes brightness depending on time...
    if(theHour>=1 and theHour<=6):
        #this means that the time is 1am-6am,,, lowest brightness
        brightness = 0.1
    elif((theHour>=17 and theHour<=23) or theHour==0):
        #5pm to 12am .. checks 6pm to 11pm first then checks if midnight,,, mid brightness
        brightness = 0.15
    else:
        #this is 7am to 4pm,,, highest brightness
        brightness = 0.6
        
    dimmer_ar = array.array("I", [0 for _ in range(NUM_LEDS)])
    for i,c in enumerate(ar):
        r = int(((c >> 8) & 0xFF) * brightness)
        g = int(((c >> 16) & 0xFF) * brightness)
        b = int((c & 0xFF) * brightness)
        dimmer_ar[i] = (g<<16) + (r<<8) + b
    sm.put(dimmer_ar, 8)

def pixels_set(i, color):
    ar[i] = (color[1]<<16) + (color[0]<<8) + color[2]
    ar[i+1] = (color[1]<<16) + (color[0]<<8) + color[2]

def pixels2_set(i, color): #made specifically for the blinker and does what the original pixel_set was supposed to do
    ar[i] = (color[1]<<16) + (color[0]<<8) + color[2]

def pixels_fill(color):
    for i in range(len(ar)):
        pixels_set(i, color)


#turns all the pixels off
def pixels_off():
    for i in range(NUM_LEDS):
        pixels2_set(i, BLACK)
    pixels_show()

#turns a specified pixel off
def one_off(i):
    pixels2_set(i, BLACK)
    pixels_show()
 
 
#An array where every segment will be assigned an LED index

top_seg = [8, 9, 22, 23, 38, 39, 52, 53]  # top part
right_top_seg = [6, 7, 20, 21, 36, 37, 50, 51]
left_top_seg = [10, 11, 24, 25, 40, 41, 54, 55]

mid_seg = [12, 13, 26, 27, 42, 43, 56, 57]  # middle part

bottom_seg = [2, 3, 16, 17, 32, 33, 46, 47]  # bottom part
right_bottom_seg = [4, 5, 18, 19, 34, 35, 48, 49]
left_bottom_seg = [0, 1, 14, 15, 30, 31, 44, 45]

dots = [28, 29] #2 center dots

#blink the two center dots with any given color
def center_blinker(color):
    pixels2_set(dots[0], color)
    pixels2_set(dots[1], color)
    pixels_show()
    time.sleep(1)
    one_off(dots[0])
    one_off(dots[1])

#turns off a chosen segment. i is the segment needed to be turned off
def seg_off(i):
    pixels_set(top_seg[i], BLACK)
    pixels_set(left_top_seg[i], BLACK)
    pixels_set(right_top_seg[i], BLACK)
    pixels_set(mid_seg[i], BLACK)
    pixels_set(left_bottom_seg[i], BLACK)
    pixels_set(right_bottom_seg[i], BLACK)
    pixels_set(bottom_seg[i], BLACK)
    pixels_show()

#takes in i, segment place, num the number value, color the color
def translate(i, num, color):
    if num == '0':
        pixels_set(top_seg[i], color)
        pixels_set(left_top_seg[i], color)
        pixels_set(right_top_seg[i], color)
        pixels_set(left_bottom_seg[i], color)
        pixels_set(right_bottom_seg[i], color)
        pixels_set(bottom_seg[i], color)
        pixels_set(mid_seg[i], BLACK)#OFF
        pixels_show()
    elif num == '1':
        pixels_set(right_top_seg[i], color)
        pixels_set(right_bottom_seg[i], color)
        pixels_set(left_top_seg[i], BLACK)#OFF
        pixels_set(left_bottom_seg[i], BLACK)#OFF
        pixels_set(top_seg[i], BLACK)#OFF
        pixels_set(bottom_seg[i], BLACK)#OFF
        pixels_set(mid_seg[i], BLACK)#OFF
        pixels_show()
    elif num == '2':
        pixels_set(top_seg[i], color)
        pixels_set(right_top_seg[i], color)
        pixels_set(mid_seg[i], color)
        pixels_set(left_bottom_seg[i], color)
        pixels_set(bottom_seg[i], color)
        pixels_set(left_top_seg[i], BLACK)#OFF
        pixels_set(right_bottom_seg[i], BLACK)#OFF
        pixels_show()
    elif num == '3':
        pixels_set(top_seg[i], color)
        pixels_set(right_top_seg[i], color)
        pixels_set(mid_seg[i], color)
        pixels_set(right_bottom_seg[i], color)
        pixels_set(bottom_seg[i], color)
        pixels_set(left_top_seg[i], BLACK)#OFF
        pixels_set(left_bottom_seg[i], BLACK)#OFF
        pixels_show()
    elif num == '4':
        pixels_set(left_top_seg[i], color)
        pixels_set(mid_seg[i], color)
        pixels_set(right_top_seg[i], color)
        pixels_set(right_bottom_seg[i], color)
        pixels_set(top_seg[i], BLACK)#OFF
        pixels_set(left_bottom_seg[i], BLACK)#OFF
        pixels_set(bottom_seg[i], BLACK)#OFF
        pixels_show()
    elif num == '5':
        pixels_set(top_seg[i], color)
        pixels_set(left_top_seg[i], color)
        pixels_set(mid_seg[i], color)
        pixels_set(right_bottom_seg[i], color)
        pixels_set(bottom_seg[i], color)
        pixels_set(right_top_seg[i], BLACK) #OFF
        pixels_set(left_bottom_seg[i], BLACK)#OFF
        pixels_show()
    elif num == '6':
        pixels_set(top_seg[i], color)
        pixels_set(left_top_seg[i], color)
        pixels_set(mid_seg[i], color)
        pixels_set(left_bottom_seg[i], color)
        pixels_set(bottom_seg[i], color)
        pixels_set(right_bottom_seg[i], color)
        pixels_set(right_top_seg[i], BLACK)#OFF
        pixels_show()
    elif num == '7':
        pixels_set(top_seg[i], color)
        pixels_set(right_top_seg[i], color)
        pixels_set(right_bottom_seg[i], color)
        pixels_set(left_top_seg[i], BLACK)#OFF
        pixels_set(left_bottom_seg[i], BLACK)#OFF
        pixels_set(bottom_seg[i], BLACK)#OFF
        pixels_set(mid_seg[i], BLACK)#OFF
        pixels_show()
    elif num == '8':
        pixels_set(top_seg[i], color)
        pixels_set(left_top_seg[i], color)
        pixels_set(right_top_seg[i], color)
        pixels_set(mid_seg[i], color)
        pixels_set(left_bottom_seg[i], color)
        pixels_set(right_bottom_seg[i], color)
        pixels_set(bottom_seg[i], color)
        pixels_show()
    elif num == '9':
        pixels_set(top_seg[i], color)
        pixels_set(left_top_seg[i], color)
        pixels_set(right_top_seg[i], color)
        pixels_set(mid_seg[i], color)
        pixels_set(right_bottom_seg[i], color)
        pixels_set(bottom_seg[i], color)
        pixels_set(left_bottom_seg[i], BLACK)#OFF
        pixels_show()
        

def check_time(time):
    if(theHour>=1 and theHour<=6):
        #this means that the time is 1am-6am,,, lowest brightness
        color1 = PINK
        color2 = RED
        center_blinker(color2)
    elif((theHour>=18 and theHour<=23) or theHour==0):
        #6pm to 12am .. checks 6pm to 11pm first then checks if midnight,, mid brightness
        color1 = PINK
        color2 = ORANGE
        center_blinker(color2)
    else:
        #this is 7am to 5pm,,, highest brightness
        #brightness is changed in pixels_show
        color1 = PINK
        color2 = NEON_GREEN
        center_blinker(color2)
        
    
    if (len(time) == 7):#hours are single digits. Let segment 0 off.
        seg_off(0) #turns off segment 0
        translate(2,time[0], color1)
        translate(4,time[2], color2)#ignore the : that separates time
        translate(6,time[3], color2)
    else:#hours are double digits. all segments are being used.
        translate(0,time[0], color1)
        translate(2,time[1], color1)
        translate(4,time[3], color2)
        translate(6,time[4], color2)

#######LED CODE ENDS HERE######

#####RTC CODE STARTS BELOW######

#takes inputs for the RTC once, edit out later
 
'''year = int(input("Year : "))
month = int(input("month (Jan --> 1 , Dec --> 12): "))
date = int(input("date : "))
day = int(input("day (1 --> monday , 2 --> Tuesday ... 0 --> Sunday): "))
hour = int(input("hour (24 Hour format): "))
minute = int(input("minute : "))
second = int(input("second : "))

now = (year,month,date,day,hour,minute,second,0)
rtc.datetime(now)'''


#takes in an hour and minute value from the RTC to translate it to 12hr format rather than 24hr
#also formats it nicely
def whatsTheTime(theHour, theMinute):
    ans = ''
    theMinuteConverted = str(theMinute)
    theHourConverted = ''
    if (theHour <= 11):  # if military time is from 0>11 which is 12AM TO 11AM
        if (theHour == 0):  # IF MILI IS 0
            theHourConverted = '12'
        else:  # IF MILI IS ANYTHING UP TO 11AM
            theHourConverted = str(theHour)  # 1-11 mili is equivalent to 1-11am
        if (theMinute <= 9):
            theMinuteConverted = '0%d' % (theMinute)
        ans = (theHourConverted + ':' + theMinuteConverted + ' AM')
    else:  # the hour 12-23mili or 12 pm to 11 pm
        if (theHour == 12):  # IF MILI IS 0
            theHourConverted = '12'
        else:
            theHourConverted = str(theHour - 12)
        if (theMinute <= 9):
            theMinuteConverted = '0%d' % (theMinute)
        ans = (theHourConverted + ':' + theMinuteConverted + ' PM')
    
    #color and brightnes management. Easier when done w 24 HR format using the 24H variables.
    return ans 


#where the magic happens.
while True:
    (year,month,date,day,hour,minute,second,p1)=rtc.datetime() #get the RTC working
    time.sleep(1)#delay program for one second
    rtc_time = rtc.datetime()
    theHour = rtc_time[4] #stealing value from rtc to translate the time into 12hr format
    theMinute = rtc_time[5]
    print('\r' + whatsTheTime(theHour, theMinute), end ='') #debugging purposes. This shows the time.
    check_time(whatsTheTime(theHour, theMinute))#Finally calls this function which calls the translate function and the center blinkers to blink the dots.




