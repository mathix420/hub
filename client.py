import logging
import socket
import sys
import gzip
from util import *

logger = logging.getLogger()

def send_file(socket, address, path):
        print('START FILE')
        with open(path, 'rb') as fp:
                bytes = gzip.compress(fp.read())
        socket.sendto(b'#!#prefix#!#', address)
        data, addr = socket.recvfrom(1024)
        print('GET RESPONSE')
        if data == b'#!#can_get_file#!#':
                print('GOOD RESPONSE')
                while bytes:
                        socket.sendto(bytes[:2048], address)
                        bytes = bytes[2048:]
                socket.sendto(b'#!#end_of_file#!#', address)
        else:
                print('error cannot send file')

def main(host='e3r1p11.42.fr', port=9999, sender=False):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(b'I want address', (host, port))
        while True:
                data, addr = sock.recvfrom(1024)
                print('client received: {} {}'.format(addr, data))
                # sock.sendto(b'Hello', addr)
                if data[:9] == b'#!#prefix':
                        print('IN')
                        sock.sendto(b'#!#can_get_file#!#', addr)
                        file_bytes = b''
                        data, addr = sock.recvfrom(2048)
                        with open('/tmp/recv.zip', 'ab+') as fp:
                                while data != b'#!#end_of_file#!#':
                                        file_bytes += data
                                        data, addr = sock.recvfrom(2048)
                                        fp.write(file_bytes)
                        # with open('/tmp/recv.zip', 'ab+') as fp:
                        #         with open('/tmp/recv.zip', 'wb+') as fw:
                        #                 fw.write(gzip.decompress(fp.read()))
                        print("FILE WRITED CORRECTLY (I BET)")
                else:
                        addr = msg_to_addr(data)
                        if sender:
                                print('OK')
                                send_file(sock, addr, '/tmp/send.zip')
                        print('NO')

                print('client received: {} {}'.format(addr, data))

if __name__ == '__main__':
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
        sender = False
        if len(sys.argv) > 1 and sys.argv[1] == 'sender':
                sender = True
        main(sender=sender)
