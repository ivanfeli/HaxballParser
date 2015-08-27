import socket
import struct
import zlib
import io
from .utils import ParserError

class Parser:
    def __init__(self, btsio):
        self.fh = io.BytesIO(btsio)
    
    def pos(self):
        return self.fh.tell()
    
    def nxt(self, amount):
        return self.fh.read(amount)

    def parse_uint(self):
        bts = self.nxt(4)
        unpacked = struct.unpack("<I", bts)[0]
        return socket.ntohl(unpacked)

    def parse_ushort(self):
        bts = self.nxt(2)
        unpacked = struct.unpack("<H", bts)[0]
        return socket.ntohs(unpacked)
        
    def parse_str(self):
        length = self.parse_ushort()
        result = struct.unpack('<{}s'.format(length), self.nxt(length))[0]

        return result.decode('ascii', errors='ignore')

    def parse_byte(self):
        bts = self.nxt(1)
        return struct.unpack("<B", bts)[0]

    def parse_bool(self):
        return self.nxt(1) == b'\x01' # ord(self.nxt(1)) == 1

    def parse_side(self):
        side = self.parse_byte()
        if side == 1:
            return 'Red'
        elif side == 2:
            return 'Blue'
        elif side == 0:
            return 'Spectator'
        else:
            return 'parse_side() error'

    def parse_double(self):
        bts = self.nxt(8)[::-1]
        unpacked = struct.unpack("<d", bts)[0]
        return unpacked
            
    def parse_pos(self):
        return {'x': self.parse_double(), 'y': self.parse_double()}

    def parse_stadium(self):
        maps = [
            'Classic',
            'Easy',
            'Small',
            'Big',
            'Rounded',
            'Hockey',
            'Big Hockey',
            'Big Easy',
            'Big Rounded',
            'Huge'
        ]
        
        b = self.parse_byte()
        if b == 255:
            raise ParserError('Custom stadiums are not supported.')
        if b >= len(maps): # Bug?
            return 'BUG'
        return maps[b]

    def deflate(self):
        decompressed = zlib.decompress(self.fh.read())
        self.fh.close()

        self.fh = io.BytesIO()
        self.fh.write(decompressed)
        self.fh.seek(0)