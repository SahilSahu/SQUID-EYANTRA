import RPi.GPIO as GPIO
import serial
import time,sys

SERIAL_PORT = "/dev/ttyS0"

ser = serial.Serial(SERIAL_PORT, baudrate = 9600, timeout = 5)

ser.write("AT\r")
print("AT Okay")
ser.write("ATD8879354575;\r")
print("Dialing..")
time.sleep(10)
ser.write("ATH\r")
