
from __future__ import print_function
from time import sleep
import smbus


REG_INTR_STATUS_1 = 0x00
REG_INTR_STATUS_2 = 0x01

REG_INTR_ENABLE_1 = 0x02
REG_INTR_ENABLE_2 = 0x03

REG_FIFO_WR_PTR = 0x04
REG_OVF_COUNTER = 0x05
REG_FIFO_RD_PTR = 0x06
REG_FIFO_DATA = 0x07
REG_FIFO_CONFIG = 0x08

REG_MODE_CONFIG = 0x09
REG_SPO2_CONFIG = 0x0A
REG_LED1_PA = 0x0C

REG_LED2_PA = 0x0D
REG_PILOT_PA = 0x10
REG_MULTI_LED_CTRL1 = 0x11
REG_MULTI_LED_CTRL2 = 0x12

REG_TEMP_INTR = 0x1F
REG_TEMP_FRAC = 0x20
REG_TEMP_CONFIG = 0x21
REG_PROX_INT_THRESH = 0x30
REG_REV_ID = 0xFE
REG_PART_ID = 0xFF


class MAX30102():
   
    def __init__(self, channel=1, address=0x57):
        
        self.address = address
        self.channel = channel
        self.bus = smbus.SMBus(self.channel)

        self.reset()

        sleep(1)  

        
        reg_data = self.bus.read_i2c_block_data(self.address, REG_INTR_STATUS_1, 1)
        
        self.setup()
        

    def shutdown(self):
      
        self.bus.write_i2c_block_data(self.address, REG_MODE_CONFIG, [0x80])

    def reset(self):
        
        self.bus.write_i2c_block_data(self.address, REG_MODE_CONFIG, [0x40])

    def setup(self, led_mode=0x03):
        
        self.bus.write_i2c_block_data(self.address, REG_INTR_ENABLE_1, [0xc0])
        self.bus.write_i2c_block_data(self.address, REG_INTR_ENABLE_2, [0x00])

        self.bus.write_i2c_block_data(self.address, REG_FIFO_WR_PTR, [0x00])
       
        self.bus.write_i2c_block_data(self.address, REG_OVF_COUNTER, [0x00])
        
        self.bus.write_i2c_block_data(self.address, REG_FIFO_RD_PTR, [0x00])

        self.bus.write_i2c_block_data(self.address, REG_FIFO_CONFIG, [0x4f])

        self.bus.write_i2c_block_data(self.address, REG_MODE_CONFIG, [led_mode])
    
        self.bus.write_i2c_block_data(self.address, REG_SPO2_CONFIG, [0x27])

        self.bus.write_i2c_block_data(self.address, REG_LED1_PA, [0x24])

        self.bus.write_i2c_block_data(self.address, REG_LED2_PA, [0x24])

        self.bus.write_i2c_block_data(self.address, REG_PILOT_PA, [0x7f])


    def set_config(self, reg, value):
        self.bus.write_i2c_block_data(self.address, reg, value)

    def get_data_present(self):
        read_ptr = self.bus.read_byte_data(self.address, REG_FIFO_RD_PTR)
        write_ptr = self.bus.read_byte_data(self.address, REG_FIFO_WR_PTR)
        if read_ptr == write_ptr:
            return 0
        else:
            num_samples = write_ptr - read_ptr
            if num_samples < 0:
                num_samples += 32
            return num_samples

    def read_fifo(self):
       
        red_led = None
        ir_led = None

        reg_INTR1 = self.bus.read_i2c_block_data(self.address, REG_INTR_STATUS_1, 1)
        reg_INTR2 = self.bus.read_i2c_block_data(self.address, REG_INTR_STATUS_2, 1)

        d = self.bus.read_i2c_block_data(self.address, REG_FIFO_DATA, 6)

        red_led = (d[0] << 16 | d[1] << 8 | d[2]) & 0x03FFFF
        ir_led = (d[3] << 16 | d[4] << 8 | d[5]) & 0x03FFFF

        return red_led, ir_led

    def read_sequential(self, amount=100):
      
        red_buf = []
        ir_buf = []
        count = amount
        while count > 0:
            num_bytes = self.get_data_present()
            while num_bytes > 0:
                red, ir = self.read_fifo()

                red_buf.append(red)
                ir_buf.append(ir)
                num_bytes -= 1
                count -= 1

        return red_buf, ir_buf
