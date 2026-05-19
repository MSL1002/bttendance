from machine import Pin, SPI
import time

class MFRC522:
    OK = 0
    NOTAGERR = 1
    ERR = 2
    REQIDL = 0x26
    REQALL = 0x52
    AUTHENT1A = 0x60
    AUTHENT1B = 0x61
    
    def __init__(self, sck, mosi, miso, rst, cs):
        self.sck = Pin(sck, Pin.OUT)
        self.mosi = Pin(mosi, Pin.OUT)
        self.miso = Pin(miso, Pin.IN)
        self.rst = Pin(rst, Pin.OUT)
        self.cs = Pin(cs, Pin.OUT)
        
        self.cs.value(1)
        self.spi = SPI(0, sck=self.sck, mosi=self.mosi, miso=self.miso, baudrate=1000000)
        self.rst.value(1)
        time.sleep(0.1)
        
        # Initialize the RC522 hardware
        self.init()
    
    def init(self):
        """Initialize RC522"""
        self._write(0x01, 0x0F)  # Reset
        time.sleep(0.05)
        self._write(0x2B, 0x8D)  # Timer config
        self._write(0x2D, 0x26)  # Timer reload
        self._write(0x2C, 0x52)  # Prescaler
        self._write(0x15, 0x40)  # TX ASK
        self._write(0x11, 0x3D)  # RX gain
        self.antenna_on()        # Turn on antenna
    
    def antenna_on(self):
        """Turn on antenna"""
        val = self._read(0x14)
        if not (val & 0x03):
            self._write(0x14, val | 0x03)
    
    def _write(self, reg, data):
        """Write to register"""
        self.cs.value(0)
        self.spi.write(bytes([(reg << 1) & 0x7E, data]))
        self.cs.value(1)
    
    def _read(self, reg):
        """Read from register"""
        self.cs.value(0)
        self.spi.write(bytes([(reg << 1) | 0x80]))
        data = self.spi.read(1)
        self.cs.value(1)
        return data[0] if data else 0
    
    def request(self, mode):
        """Request card"""
        self._write(0x0D, 0x07)
        status, bits, data = self._tocard(mode, [mode])
        return status, bits
    
    def anticoll(self):
        """Anti-collision"""
        self._write(0x0D, 0x00)
        status, bits, data = self._tocard(0x1F, [0x20])
        return status, data
    
    def select_tag(self, uid):
        """Select tag"""
        buf = [0x93, 0x70] + uid[:4]
        status, bits, data = self._tocard(0x03, buf)
        return status
    
    def auth(self, mode, addr, sect, uid):
        """Auth"""
        buf = [mode, addr] + sect + uid[:4]
        status, bits, data = self._tocard(0x0E, buf)
        return status
    
    def read(self, addr):
        """Read"""
        buf = [0x30, addr]
        status, bits, data = self._tocard(0x0C, buf)
        return data if status == self.OK else None
    
    def write(self, addr, data):
        """Write"""
        buf = [0xA0, addr]
        status, bits, data_ret = self._tocard(0x0C, buf)
        if status != self.OK:
            return self.ERR
        buf = data
        status, bits, data_ret = self._tocard(0x0C, buf)
        return status
    
    def _tocard(self, cmd, send_data):
        """Send command to card"""
        self._write(0x01, 0x00)
        self._write(0x0D, 0x00)
        
        for byte in send_data:
            self._write(0x09, byte)
        
        self._write(0x01, cmd)
        
        # Wait for completion
        for i in range(2000):
            n = self._read(0x04)
            if not (n & 0x80):
                break
        
        # Check error
        error = self._read(0x06)
        if error & 0x1B != 0:
            return self.ERR, 0, None
        
        # Get response data
        n = self._read(0x0A)
        lastbits = self._read(0x0C) & 0x07
        
        if lastbits != 0:
            backbits = (n - 1) * 8 + lastbits
        else:
            backbits = n * 8
        
        if n == 0:
            n = 1
        if n > 16:
            n = 16
        
        recv_data = []
        for j in range(n):
            recv_data.append(self._read(0x09))
        
        if recv_data:
            return self.OK, backbits, recv_data
        else:
            return self.OK, backbits, None