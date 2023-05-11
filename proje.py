import RPi.GPIO as GPIO
import time
import os
import pygame
import board
import neopixel
from math import log10
import busio
import digitalio
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import pyaudio
import audioop 

# açılacak satırlar 43, 147, 438


# GPIO pinlerini tanımlayın
button1_pin = 4
button2_pin = 17
button3_pin = 27
button4_pin = 22
#potentiometer_pin = 22
#mic_pin = 12

# GPIO ayarlarını yapın
GPIO.setmode(GPIO.BCM)
GPIO.setup(button1_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button2_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button3_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button4_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(potentiometer_pin, GPIO.IN)
#GPIO.setup(mic_pin, GPIO.IN)

# create the spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# create the cs (chip select)
cs = digitalio.DigitalInOut(board.D25)

# create the mcp object
mcp = MCP.MCP3008(spi, cs)

# create an analog input channel on pin 0
chan0 = AnalogIn(mcp, MCP.P0)
#chan1 = AnalogIn(mcp, MCP.P1)

pygame.mixer.init()
pixels=neopixel.NeoPixel(board.D18, 60, brightness=1)
    #potansiyometre ve ses ayarları
    
last_read = 0       # this keeps track of the last potentiometer value
tolerance = 250     # to keep from being jittery we'll only change
                    # volume when the pot has moved a significant amount
                    # on a 16-bit ADC
def remap_range(value, left_min, left_max, right_min, right_max):
    # this remaps a value from original (left) range to new (right) range
    # Figure out how 'wide' each range is
    left_span = left_max - left_min
    right_span = right_max - right_min

    # Convert the left range into a 0-1 range (int)
    valueScaled = int(value - left_min) / int(left_span)

    # Convert the 0-1 range into a value in the right range.
    return int(right_min + (valueScaled * right_span))

def set_volume(level):
    pygame.mixer.music.set_volume(level/100)
       # os.system("amixer set PCM -- {}%".format(level))
        
def increase_volume(amount):
    current_level = pygame.mixer.music.get_volume() * 100
        #current_level = int(os.open("amixer get PCM").read().split("Front Left:")[1].split("%")[0]) 
    new_level = min(current_level + amount, 100)
    set_volume(new_level)   
        
def decrease_volume(amount):
    current_level = pygame.mixer.music.get_volume() * 100
        #current_level = int(os.open("amixer get PCM").read().split("Front Left:")[1].split("%")[0])
    new_level = max(current_level + amount, 0)
    set_volume(new_level)     

    # potentiometer değerini okuyan fonksiyon
def read_potentiometer():
    return chan0.value



pygame.mixer.music.set_volume(0.5)

# def adjust_volume(value):
#         # ses seviyesini ayarlamak için amixer komutunu kullanın
#     prevPotVal = read_potentiometer()
#     val = value - prevPotVal
#     if val > 0:
#         increase_volume(val)
#     elif val < 0:
#         decrease_volume(-val)   
            
    #potansiyometre ve ses ayarları  

   
I0 = 10 ** -12

# def measure_decibel():
#     data = chan1.value
#     if data == 0:
#         data = 1
#     dB = 10 * log10(data / I0)
#     return dB - 80
    #MICROPHONE
p = pyaudio.PyAudio()
WIDTH = 2
RATE = int(p.get_default_input_device_info()['defaultSampleRate'])
DEVICE = p.get_default_input_device_info()['index']
rms = 1

def callback(in_data, frame_count, time_info, status):
    global rms
    rms = audioop.rms(in_data, WIDTH) / 32767
    return in_data, pyaudio.paContinue


stream = p.open(format=p.get_format_from_width(WIDTH),
                input_device_index=DEVICE,
                channels=1,
                rate=RATE,
                input=True,
                output=False,
                stream_callback=callback)

stream.start_stream()

def measure_decibel():
    db = 20 * log10(rms) + 120
    
    return db

    #RGB
    # https://core-electronics.com.au/guides/raspberry-pi/fully-addressable-rgb-raspberry-pi/
rgb_mode_count = 8
#pixels=neopixel.NeoPixel(board.D18, 30, brightness=1)
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def high_volume_indicator():
    decibel = measure_decibel()
#    decibel = chan1.value / 120

    if decibel > 81:
        pixels.fill((255, 0, 0))
    else:
        pixels.fill((0, 0, 0))   

def double_way_decibel():
    pixels.fill((0, 0, 0))
    desibel = measure_decibel()
    yesil = (25, 209, 25) 
    mavi = (0, 137, 255) 
    kirmizi = (255, 0, 0)
    sari = (250, 228, 34) 
    if desibel <= 0:
        pixels.fill((0, 0, 0))
    elif  1 < desibel < 60:
        pixels[49:51] = [yesil] * 2
    elif 60 <= desibel < 65:
        pixels[48:52] = [yesil] * 4
    elif 65 <= desibel < 67:
        pixels[47:53] = [yesil] * 6
    elif 67 <= desibel < 72:
        pixels[45:54] = [sari] * 9
    elif 72 <= desibel < 75:
        pixels[43:55] = [sari] * 12
    elif 75 <= desibel < 78:
        pixels[41:56] = [mavi] * 15
    elif 78 <= desibel < 80:
        pixels[38:57] = [mavi] * 19
    elif 80 <= desibel < 82:
        pixels[36:58] = [kirmizi] * 22
    elif 82 <= desibel < 84:
        pixels[33:59] = [kirmizi] * 26
    elif 84 <= desibel:
        pixels[31:60] = [kirmizi] * 29


def show_desibel():
        # min 65 74    max 85
    desibel = measure_decibel()
   # desibel = chan1.value / 130
    pixels.fill((0, 0, 0))
    yesil = (25, 209, 25) 
    mavi = (0, 137, 255) 
    kirmizi = (255, 0, 0)
    sari = (250, 228, 34) 
    if desibel <= 0:
        pixels.fill((0, 0, 0))
    elif  1 < desibel < 60:
        pixels[0:6] = [yesil] * 6
    elif 60 <= desibel < 65:
        pixels[0:12] = [yesil] * 12
    elif 65 <= desibel < 67:
        pixels[0:18] = [yesil] * 18
    elif 67 <= desibel < 72:
        pixels[0:24] = [sari] * 24
    elif 72 <= desibel < 75:
        pixels[0:30] = [sari] * 30
    elif 75 <= desibel < 78:
        pixels[0:36] = [mavi] * 36
    elif 78 <= desibel < 80:
        pixels[0:42] = [mavi] * 42
    elif 80 <= desibel < 82:
        pixels[0:48] = [kirmizi] * 48
    elif 82 <= desibel < 84:
        pixels[0:54] = [kirmizi] * 54
    elif 84 <= desibel:
        pixels[0:60] = [kirmizi] * 60

def show_volume(volume):
    pixels.fill((0, 0, 0))
    yesil = (25, 209, 25) 
    mavi = (0, 137, 255) 
    kirmizi = (255, 0, 0)
    sari = (250, 228, 34) 
    if volume <= 0:
        pixels.fill((0, 0, 0))
    elif  0 < volume < 10:
        pixels[0:6] = [yesil] * 6
    elif 10 <= volume < 20:
        pixels[0:12] = [yesil] * 12
    elif 20 <= volume < 30:
        pixels[0:18] = [yesil] * 18
    elif 30 <= volume < 40:
        pixels[0:24] = [sari] * 24
    elif 40 <= volume < 50:
        pixels[0:30] = [sari] * 30
    elif 50 <= volume < 60:
        pixels[0:36] = [mavi] * 36
    elif 60 <= volume < 70:
        pixels[0:42] = [mavi] * 42
    elif 70 <= volume < 80:
        pixels[0:48] = [kirmizi] * 48
    elif 80 <= volume < 90:
        pixels[0:54] = [kirmizi] * 54
    elif 90 <= volume:
        pixels[0:60] = [kirmizi] * 60

color_switch_i = 0
def color_switch():
    global color_switch_i
    pixels.fill((0, 0, 0))
    yesil = (25, 209, 25) 
    mavi = (0, 137, 255) 
    kirmizi = (255, 0, 0)
    sari = (250, 228, 34) 
    turuncu = (255, 165, 0)
    mor = (75, 0, 130)
    pembe = (238, 130, 238)
        
        
    color_switch_i = color_switch_i + 1
    color_switch_i = color_switch_i % 350
    i = color_switch_i
    if 0 <= i <= 50:
        pixels.fill(yesil)
    elif 50 < i <= 100:
        pixels.fill(mavi)
    elif 100 < i <= 150:
        pixels.fill(kirmizi)
    elif 150 < i <= 200:
        pixels.fill(sari)
    elif 200 < i <= 250:
        pixels.fill(turuncu)
    elif 250 < i <= 300:
        pixels.fill(mor)
    elif 300 < i <= 350:
        pixels.fill(pembe)           


color_shift_i = 0
def color_shift():
    global color_shift_i
    pixels.fill((0, 0, 0))
    yesil = (25, 209, 25) 
    mavi = (0, 137, 255) 
    kirmizi = (255, 0, 0)
    sari = (250, 228, 34) 
    color_shift_i = color_shift_i + 1
    color_shift_i = color_shift_i % 100
    i = color_shift_i
    if 0 <= i <= 25:
        pixels[0:15] = [yesil]*15
        pixels[15:30] = [mavi]*15
        pixels[30:45] = [kirmizi]*15
        pixels[45:60] = [sari]*15
    elif 25 < i <= 50:
        pixels[0:15] = [sari]*15
        pixels[15:30] = [yesil]*15
        pixels[30:45] = [mavi]*15
        pixels[45:60] = [kirmizi]*15
    elif 50 < i <= 750:
        pixels[0:15] = [kirmizi]*15
        pixels[15:30] = [sari]*15
        pixels[30:45] = [yesil]*15
        pixels[45:60] = [mavi]*15 
    elif 75 < i <= 100:
        pixels[0:15] = [mavi]*15
        pixels[15:30] = [kirmizi]*15
        pixels[30:45] = [sari]*15
        pixels[45:60] = [yesil]*15

police_siren_i = 0
def police_siren():
    global police_siren_i
    pixels.fill((0, 0, 0))
    police_siren_i = police_siren_i + 1
    police_siren_i = police_siren_i % 2000
    i = police_siren_i
    if i < 1001:
        for j  in range(0,60,2):
            pixels[j] = (255, 0, 0)
            pixels[j+1] = (0, 137, 255)    
    else:
        for j  in range(0,60,2):
            pixels[j] = (0, 137, 255) 
            pixels[j+1] = (255, 0, 0) 

one_led_run_i = 0  
def one_led_run():
    global one_led_run_i
    pixels.fill((0, 0, 0))
    one_led_run_i = one_led_run_i + 1
    one_led_run_i = one_led_run_i % 59
    i = one_led_run_i
    pixels[i+1] = (0, 20, 255)         

def RGB_color_mode_switch(num):
    i = num
    print("RGB_color_mode_switch num: ", num)
    if i == 0:
       double_way_decibel()
    elif i == 1:
        high_volume_indicator()
    elif i == 2:
        show_desibel()
    elif i == 3:
       show_volume(remap_range(read_potentiometer(), 0, 40000, 0, 100))
    elif i == 4:
        color_switch()
    elif i == 5:
        color_shift()
    elif i == 6:  
        police_siren()
    elif i == 7:  
        one_led_run()
    #RGB



    #butonlar 
folder = "./music"
files = os.listdir(folder)

files.sort()
current_song_index = 0

def play_song():
    global current_song_index
    pygame.mixer.music.load(os.path.join(folder, files[current_song_index]))
    pygame.mixer.music.play()

def play_next_song():
    global current_song_index
    current_song_index += 1
    if current_song_index >= len(files):
        current_song_index = 0
    play_song()

def play_previous_song():
    global current_song_index
    current_song_index -= 1
    if current_song_index < 0:
        current_song_index = len(files) - 1
    play_song()

def toggle_pause():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
    else:
        pygame.mixer.music.unpause()

def stop():
        pygame.mixer.music.stop()
    #butonlar    

    
        
rgb = 0
baslat = False
# düğmeleri dinleyin
print("sssss")
while True:
    # we'll assume that the pot didn't move
    trim_pot_changed = False
    trim_pot = read_potentiometer()
    # how much has it changed since the last read?
    pot_adjust = abs(trim_pot - last_read)

    if pot_adjust > tolerance:
        trim_pot_changed = True

    if trim_pot_changed:
        set_volume(remap_range(trim_pot, 0, 40000, 0, 100))
        print('Changed value: ', trim_pot)
        last_read = trim_pot

    if not GPIO.input(button1_pin):
        if not baslat:
            print("baslat")
            baslat = True
            play_song()
        else:
            print("durdur")
            baslat = False
            toggle_pause()      
    if not GPIO.input(button2_pin):
        print("sonraki")
        play_next_song()
    if not GPIO.input(button3_pin):
        print("onceki")
        play_previous_song()
    if not GPIO.input(button4_pin):
        print("renk degistir")
        rgb = (rgb + 1) % rgb_mode_count

    print("decibel: ",measure_decibel())
    RGB_color_mode_switch(rgb)

    #print("breadboard mic: ", chan1.value)

            
    time.sleep(0.1)

stream.stop_stream()
stream.close()

p.terminate()