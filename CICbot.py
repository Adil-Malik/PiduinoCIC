import RPi.GPIO as GPIO
#import serial
import time
import subprocess
from flask import Flask, render_template
end = 0
ip = ""
serve = False
LCD_RS = 7
LCD_E  = 8
LCD_D4 = 25
LCD_D5 = 24
LCD_D6 = 23
LCD_D7 = 18
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False
M1 = 9
M2 = 10 #M1 and M4 are for the left motor. M1 T and M2 F is foward.
M3 = 4
M4 = 17 #M3 and M4 are for the right motor. M3 F and M4 T is reverse.
LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line

# Timing constants
E_PULSE = 0.00005
E_DELAY = 0.00005


GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
GPIO.setup(LCD_E, GPIO.OUT)  # E
GPIO.setup(LCD_RS, GPIO.OUT) # RS
GPIO.setup(LCD_D4, GPIO.OUT) # DB4
GPIO.setup(LCD_D5, GPIO.OUT) # DB5
GPIO.setup(LCD_D6, GPIO.OUT) # DB6
GPIO.setup(LCD_D7, GPIO.OUT) # DB7
GPIO.setup(M1, GPIO.OUT) # DB4
GPIO.setup(M2, GPIO.OUT) # DB5
GPIO.setup(M3, GPIO.OUT) # DB6
GPIO.setup(M4, GPIO.OUT) # DB7

def Stop():
  GPIO.output(M1, False)
  GPIO.output(M2, False)
  GPIO.output(M3, False)
  GPIO.output(M4, False)

def Forward():
  GPIO.output(M1, True)
  GPIO.output(M2, False)
  GPIO.output(M3, True)
  GPIO.output(M4, False)
  time.sleep(1)
  Stop()

def Left():
  GPIO.output(M1, False)
  GPIO.output(M2, True)
  GPIO.output(M3, True)
 GPIO.output(M4, False)
  time.sleep(1)
  Stop()

def Right():
  GPIO.output(M1, True)
  GPIO.output(M2, False)
  GPIO.output(M3, False)
  GPIO.output(M4, True)
  time.sleep(1)
  Stop()

def Back():
  GPIO.output(M1, False)
  GPIO.output(M2, True)
  GPIO.output(M3, Flase)
  GPIO.output(M4, True)
  time.sleep(1)
  Stop()


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD)
  lcd_byte(0x32,LCD_CMD)
  lcd_byte(0x28,LCD_CMD)
  lcd_byte(0x0C,LCD_CMD)
  lcd_byte(0x06,LCD_CMD)
  lcd_byte(0x01,LCD_CMD)

def lcd_string(message):
  # Send string to display

  message = message.ljust(LCD_WIDTH," ")

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command
 GPIO.output(LCD_RS, mode) # RS

  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)

  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)

def internet_on():
   command = "ifconfig wlan0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1$
   process = subprocess.Popen(command, shell=True,stdout =subprocess.PIPE)
   process.wait()# wait for process to finish
   ip =process.stdout.read()# set the terminal response to the IP
   if ip != "": #Check if returned ip is not empty(No Connection)

       print "Connected to a LAN Network at: " + ip
       lcd_byte(LCD_LINE_1, LCD_CMD)
       lcd_string("Connected at:")
       lcd_byte(LCD_LINE_2, LCD_CMD)
       lcd_string(str(ip))
       time.sleep(8)
       lcd_byte(LCD_LINE_1, LCD_CMD)
       lcd_string("               ")
       lcd_byte(LCD_LINE_2, LCD_CMD)
       lcd_string("               ")

       return 1

   if ip == "":
       print "No LAN Detected!" + ip
       lcd_byte(LCD_LINE_1, LCD_CMD)
       lcd_string("No LAN Detected!")
       time.sleep(1) #Check for an internet connection every 1 second.
       return 0

while end == 0:
    lcd_init()
    end = internet_on()

print "Server has Started on port 8080"

lcd_byte(LCD_LINE_1, LCD_CMD)
lcd_string("Server Runing...")
lcd_byte(LCD_LINE_2, LCD_CMD)
lcd_string("Port 80")
app = Flask(__name__)
@app.route("/")
@app.route("/<state>")
def Control_CICBot(state=None):

        if state == 'F':
           # ser.write("Foward")
            print ("Foward Command Sent")
            lcd_byte(LCD_LINE_1, LCD_CMD)
            Forward()
            lcd_string("Moving Forward")
            lcd_byte(LCD_LINE_2, LCD_CMD)
            lcd_string("                 ")


        if state == 'B':
            #ser.write("Backwards")
            print ("Backward Command Sent")
           lcd_byte(LCD_LINE_1, LCD_CMD)
            Back()
            lcd_string("Moving Back")
            lcd_byte(LCD_LINE_2, LCD_CMD)
            lcd_string("                 ")
        if state == 'L':
            #ser.write("Left")
            print ("Left Command Sent")
            lcd_byte(LCD_LINE_1, LCD_CMD)
            Left()
            lcd_string("Moving Left")
            lcd_byte(LCD_LINE_2, LCD_CMD)
            lcd_string("                 ")

        if state == 'R':
            #ser.write("Right")
            print ("Right Command Sent")
            lcd_byte(LCD_LINE_1, LCD_CMD)
            Right()
            lcd_string("Moving Right")
         lcd_byte(LCD_LINE_2, LCD_CMD)
            lcd_string("                 ")
        if state == 'f':

            shutdown_server()
        return render_template('control.html')

if __name__ == "__main__":
     app.run(host='0.0.0.0', port=80)










