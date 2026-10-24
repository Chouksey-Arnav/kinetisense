from machine import Pin, I2C
import time
import struct

# sensor address and registers (ISM330DHCX datasheet)
ADDR = 0x6A
REG_WHO_AM_I = 0x0F
WHO_AM_I_VALUE = 0x6B
REG_CTRL1_XL = 0x10
REG_CTRL2_G = 0x11
REG_CTRL3_C = 0x12

# settings bytes (provisional, we confirm on the real sensor)
CTRL1_XL_VALUE = 0x74
CTRL2_G_VALUE = 0x71
CTRL3_C_VALUE = 0x44

# where the data starts, and how to convert raw numbers
REG_OUT_START = 0x22
GYRO_DPS_PER_LSB = 0.140
ACCEL_G_PER_LSB = 0.000488

print("main.py is running")
i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400000)

data = i2c.readfrom_mem(ADDR, REG_WHO_AM_I, 1)

if data[0] != WHO_AM_I_VALUE:
    print("wrong chip")
else:
    print("sensor found")

i2c.writeto_mem(ADDR, REG_CTRL1_XL, bytes([CTRL1_XL_VALUE]))
time.sleep_ms(100)
i2c.writeto_mem(ADDR,REG_CTRL2_G , bytes([CTRL2_G_VALUE]))
time.sleep_ms(100)
i2c.writeto_mem(ADDR,REG_CTRL3_C , bytes([CTRL3_C_VALUE]))
time.sleep_ms(100)
print("settings written")
check = i2c.readfrom_mem(ADDR, REG_CTRL2_G, 1)
print("gyro setting reads back as", hex(check[0]))
