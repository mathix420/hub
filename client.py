import logging
import socket
import sys
import gzip
from util import *

logger = logging.getLogger()

def send_file(socket, address, path):
        print('STARTING FILE SHARING')
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

def recieve_file_from_peer(peer_addr, sock):
        data, addr = sock.recvfrom(2048)
        if addr != peer_addr:
                return False
        with open('/tmp/recv.zip', 'ab+') as fp:
                while data != b'#!#end_of_file#!#':
                        fp.write(data)
                        data, addr = sock.recvfrom(2048)
        with open('/tmp/recv.zip', 'rb') as fp:
                data = gzip.decompress(fp.read())
        with open('/tmp/recv.zip', 'wb') as fp:
                fp.write(data)
        return True


def main(server_host='127.0.0.1', server_port=9999, sender=False):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # There I ask the server for the other person address
        sock.sendto(b'I want address', (server_host, server_port))

        # Then I wait for a response
        data, peer_addr = sock.recvfrom(1024)
        print('peer infos recieved from server: {} {}'.format(peer_addr, data))

        # Now we can start listening from peer
        while True:
                if data[:9] == b'#!#prefix':
                        print('GOT FILE PREFIX')
                        sock.sendto(b'#!#can_get_file#!#', peer_addr)
                        recieve_file_from_peer(peer_addr, sock)
                        exit()
                else:
                        addr = msg_to_addr(data)
                        if sender:
                                print('OK')
                                send_file(sock, addr, '/tmp/send.zip')
                                exit()
                        else:
                                print('NO')
                data, peer_addr = sock.recvfrom(1024)


if __name__ == '__main__':
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
        sender = False
        if len(sys.argv) > 1 and sys.argv[1] == 'sender':
                sender = True
        main(sender=sender)
