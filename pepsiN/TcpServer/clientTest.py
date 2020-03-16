# Socket client example in python

import socket
import sys
import threading
import time
import struct
import json
import random


host = 'localhost'
port = 9875

IS_LEADER = 1
sockets = []
p = {"id":1,"raw_data":[],"plc_data":[]}


def setRandomVal():
    return random.randrange(9, 10)


def send_data_test_time():
    p["id"] = str(0 + 1)
    p["raw_data"]["velocity"] = setRandomVal()
    p["raw_data"]["distance"] = setRandomVal()
    p["plc_data"] = setRandomVal()
    d = json.dumps(p) + '\n'
    d = d.encode()
    sockets[0].sendall(d)

def init_socket(num_of_sockets):
    try:
        for i in range(num_of_sockets):
            sockets.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
    except socket.error:
        print('Failed to create socket')
        sys.exit()
    try:
        remote_ip = socket.gethostbyname(host)
    except socket.gaierror:
        print('Hostname could not be resolved. Exiting')
        sys.exit()

    # sockets[0].connect((socket.gethostbyname(host), port))
    #
    for i in range(num_of_sockets):
        sockets[i].connect((remote_ip, port))
        threading.Thread(
            target=handle_client_connection,
            args=(sockets[i],)
            # without comma you'd get a... TypeError: handle_client_connection()
            # argument after * must be a sequence, not _socketobject
        ).start()

def send_data(num_of_sockets):
    counter = 0
    r = 1
    try:
        while True:
            r = r if r else 1
            r *= -(counter % 4)
            for i in range(num_of_sockets):

                # if counter % 2:
                #     r = 15
                # to_bytes = request.to_bytes(4, 'little')
                # print(''.join('{:02x}'.format(x) for x in to_bytes))
                p = (i + 1).to_bytes(1, byteorder='big') + (2).to_bytes(2, byteorder='big') + (1).to_bytes(1, byteorder='big')
                for dt in range(1):



                    if dt < 1:
                        rand = setRandomVal()+ r
                        p += rand.to_bytes(2,byteorder='big')
                    # rand = setRandomVal()+ r
                    # p += rand.to_bytes(4, byteorder='big')
                    # rand = setRandomVal()+ r
                    # p += rand.to_bytes(4, byteorder='big')
                # d = json.dumps(p) + '\n'
                # d = d.encode()
                # if i == 0:
                #     print("send--",p[4:],'\n')
                sockets[i].sendall(p)
            counter += 1
            time.sleep(1)

    except socket.error:
        print('Send failed')
        sys.exit()

def run():
    if not sockets:
        init_socket(8)
    send_data(8)


def handle_client_connection(client_socket):
    print(3)
    while True:
        reply = client_socket.recv(8)
        if reply:
            p = ""
            p = (1).to_bytes(1, byteorder='big') + (1).to_bytes(2, byteorder='big') + (4).to_bytes(1,byteorder='big')
            p += (1).to_bytes(1, byteorder='big')
            p += (1).to_bytes(1, byteorder='big') + (1).to_bytes(2, byteorder='big') + (5).to_bytes(1, byteorder='big')
            p += (0).to_bytes(1, byteorder='big')
            p += (1).to_bytes(1, byteorder='big') + (6).to_bytes(2, byteorder='big') + (6).to_bytes(1, byteorder='big')
            p += (12345677).to_bytes(6, byteorder='big')
            p += (1).to_bytes(1, byteorder='big') + (1).to_bytes(2, byteorder='big') + (7).to_bytes(1, byteorder='big')
            p += (2).to_bytes(1, byteorder='big')
            p += (1).to_bytes(1, byteorder='big') + (5).to_bytes(2, byteorder='big') + (9).to_bytes(1, byteorder='big')
            p += "moshe".encode()
            p += (1).to_bytes(1, byteorder='big') + (16).to_bytes(2, byteorder='big') + (8).to_bytes(1, byteorder='big')
            p += (15).to_bytes(2, byteorder='big')
            p += (34).to_bytes(2, byteorder='big')
            p += (67).to_bytes(2, byteorder='big')
            p += (23).to_bytes(2, byteorder='big')
            p += (12).to_bytes(2, byteorder='big')
            p += (13).to_bytes(2, byteorder='big')
            p += (14).to_bytes(2, byteorder='big')
            p += (16).to_bytes(2, byteorder='big')




            sockets[0].sendall(p)
            p = ""
            print(f'reply:{reply}')
            # break

# /etc/init.d/eu_service stop
