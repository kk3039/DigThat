import getopt
import json
import socket
import sys
import random

PLAYER_NAME = "example"
DATA_SIZE = 4096


def establish_connection(port):
    HOST = "localhost"
    PORT = port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    return s


def receive_data(server):
    while True:
        data = server.recv(DATA_SIZE).decode()
        if data:
            return data


if __name__ == "__main__":
    optlist, args = getopt.getopt(sys.argv[1:], 'n:p:k:', [
        'grid=', 'phase=', 'tunnel=', 'port='])
    num_grid, num_phase, tunnel_length, port = 0, 0, 0, 8000
    for o, a in optlist:
        if o in ("-n", "--grid"):
            num_grid = int(a)
        elif o in ("-p", "--phase"):
            num_phase = int(a)
        elif o in ("-k", "--tunnel"):
            tunnel_length = int(a)
        elif o in ("--port"):
            port = int(a)
        else:
            assert False, "unhandled option"

    server = establish_connection(port)
    try:
        # Please fill in your team name here
        server.sendall(f'{PLAYER_NAME}'.encode())
        res = receive_data(server)
        print(res)
    except (KeyboardInterrupt, OSError, TypeError):
        server.close()
