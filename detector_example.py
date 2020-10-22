import getopt
import json
import math
import random
import socket
import sys

PLAYER_NAME = 'example'
DATA_SIZE = 4096


def establish_connection(port):
    HOST = 'localhost'
    PORT = port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    return s


def receive_data(conn):
    while True:
        data = conn.recv(DATA_SIZE).decode()
        if data:
            return json.loads(data)


def send_data(conn, data):
    conn.sendall(json.dumps(data).encode())


if __name__ == '__main__':
    optlist, args = getopt.getopt(sys.argv[1:], 'n:p:k:', [
        'grid=', 'phase=', 'tunnel=', 'port='])
    num_grid, num_phase, tunnel_length, port = 0, 0, 0, 8000
    for o, a in optlist:
        if o in ('-n', '--grid'):
            num_grid = int(a)
        elif o in ('-p', '--phase'):
            num_phase = int(a)
        elif o in ('-k', '--tunnel'):
            tunnel_length = int(a)
        elif o in ('--port'):
            port = int(a)
        else:
            assert False, 'unhandled option'

    s = establish_connection(port)
    try:
        # Please fill in your team name here
        send_data(s, {'player_name': PLAYER_NAME})
        res = receive_data(s)
        num_grid = res['grid']
        num_phase = res['remaining_phases']
        tunnel_length = res['tunnel_length']
        while True:
            payload = {'phase': 'probe', 'probes': []}
            for i in range(3):
                x = math.ceil(random.random() * (num_grid))
                y = x = math.ceil(random.random() * (num_grid))
                if [x, y] not in payload['probes']:
                    # for the ease of decoding, please avoid using python tuples
                    payload['probes'].append([x, y])
            print("payload: {}".format(payload))
            send_data(s, payload)
            res = receive_data(s)
            print(res)  # gets probing report
            if res['next_phase'] == 'guess':
                break
        payload = {'phase': 'guess', 'answer': [
            (1, 3), (2, 3), (3, 3), (4, 3), (5, 3)]}
        send_data(s, payload)
        s.close()
    except KeyboardInterrupt:
        s.close()
