import sys, uselect
from machine import UART, Pin, ADC, I2C
import eeprom_24xx64

i2c = I2C(0)
eeprom = eeprom_24xx64.EEPROM_24xx64(i2c)

uart_remote_port = 1
uart_remote_pin_tx = 33
uart_remote_pin_rx = 32
uart_remote_speed = 9600

group_id = 9001

uart_remote = UART(uart_remote_port, baudrate = uart_remote_speed, tx = uart_remote_pin_tx, rx = uart_remote_pin_rx)

usb = uselect.poll()
usb.register(sys.stdin, uselect.POLLIN)

print("Two-way ESP32 remote data system\n")
print("EEPROM GROUP", eeprom.read_string(100))
print("EEPROM VOLTAGE", eeprom.read_string(200))

def get_battery_voltage():
    battery_adc = ADC(Pin(25, Pin.IN), atten=3)
    adc_value = battery_adc.read()    
    
    voltage = (((adc_value) * (3.3)) / (3800))
    
    return voltage * 2


while True:
    if uart_remote.any() > 0:
        string = uart_remote.read().decode()
        string = string.strip()
        print("Remote: " + string)
        
        if string == "rd bat":
            string_to_send = "batVoltage={}".format( round(get_battery_voltage(), 2) )
            uart_remote.write(string_to_send)
                        
        elif string == "rd group":
            uart_remote.write( "groupId={}".format(group_id) )
        
        elif string.startswith("batVoltage="):
            print("Remote battery voltage is:", string[11:])
            eeprom.write_string(200, string[11:])
        
        elif string.startswith("groupId="):
            print("Remote group ID is:", string[8:])
            eeprom.write_string(100, string[8:])
        
    if usb.poll(0):
        string = sys.stdin.readline()
        sys.stdin.readline()
        string = string.strip()
        print("USB   : " + string)
        
        uart_remote.write(string + "\n")

