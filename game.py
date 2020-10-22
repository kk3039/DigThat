import sys
import getopt
import json
import socket

DATA_SIZE = 4096
PROBE_PHASE = 'probe'
GUESS_PHASE = 'guess'


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class InputError(Error):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


class Detector:
    def __init__(self, name):
        self.name = name
        self.num_probe = 0

    def update_probes(self, num_probe):
        self.num_probe += num_probe


class Game:
    def __init__(self, num_grid, num_phase, tunnel_length):

        if num_grid < 2:
            raise InputError(
                num_grid, 'grid size should be greater than or equal to 2')
        if num_phase < 2:
            raise InputError(
                num_phase, 'number of phases should be greater or equal to 2')
        if tunnel_length < num_grid - 1:
            raise InputError(
                tunnel_length, 'tunnel length should be at least n-1 for n * n grid')

        self.num_grid = num_grid
        self.num_phase = num_phase
        self.tunnel_length = tunnel_length
        self.phase = PROBE_PHASE if num_phase > 2 else GUESS_PHASE
        self.intersections = [
            [0 for _ in range(self.num_grid+1)] for _ in range(self.num_grid+1)]
        self.intersection_neighbors = {}

    def isEnded(self):
        return self.num_phase <= 0

    def set_player(self, name):
        self.detector = Detector(name)

    def use_probes(self, num_probes):
        self.detector.update_probes(num_probes)

    def check_answer(self, answers):
        self.num_phase -= 1
        is_answer_correct = True
        if len(answers) - 1 != tunnel_length:
            is_answer_correct = False
        for [x, y] in answers:
            if self.intersections[x][y] != 1:
                print("({},{}) is not part of the tunnel".format(x, y))
                is_answer_correct = False
        if not is_answer_correct:
            print("answer is not correct")
            return sys.maxsize
        return self.detector.num_probe

    def load_tunnel(self):
        f = open('tunnel', 'r')
        prev = None
        route = []

        # form the map
        for line in f:
            str_x, str_y = line.split(',')
            x = int(str_x)
            y = int(str_y)
            route.append((x, y))

            if prev is not None and not abs(prev[0] - x) ^ abs(prev[1] - y):
                raise InputError((x, y), 'tunnel is not connected')
            self.intersections[x][y] = 1
            self.intersection_neighbors[(x, y)] = []
            # look for existing neighbors and set neighbor map
            for d_x in [-1, 0, 1]:
                for d_y in [-1, 0, 1]:
                    # skip itself
                    if d_x == 0 and d_y == 0:
                        continue
                    if x + d_x >= 1 and x + d_x < self.num_grid \
                            and y + d_y >= 1 and y + d_y < self.num_grid and \
                            self.intersections[x+d_x][y+d_y] == 1:
                        if (x + d_x, y + d_y) not in self.intersection_neighbors:
                            self.intersection_neighbors[(
                                x + d_x, y + d_y)] = []
                        neighbor_node_neighbors = self.intersection_neighbors.get(
                            (x + d_x, y + d_y))
                        neighbor_node_neighbors.append((x, y))
                        curr_node_neighbors = self.intersection_neighbors.get(
                            (x, y))
                        curr_node_neighbors.append(
                            (x + d_x, y + d_y))

            prev = (x, y)
        # print(route)
        # print(self.intersection_neighbors)

        # validations
        if route[0][0] != 1:
            assert False, 'Starting point {} should be at index 1, i.e. (1,x)'.format(
                route[0][0])
        if route[-1][0] != self.num_grid:
            assert False, 'Ending point {} should be at index {}, i.e. ({},x)'.format(
                route[-1][0],  self.num_grid,  self.num_grid)

        if len(self.intersection_neighbors.get(route[0])) != 1:
            assert False, 'Starting point should only have one neighboring intersection.'
        if len(self.intersection_neighbors.get(route[-1])) != 1:
            assert False, 'Ending point should only have one neighboring intersection.'
        for i in route[2:-1]:
            if len(self.intersection_neighbors.get(i)) != 2:
                assert False, 'Intersection {} has only one or more than 2 neighbors. \
                    Please check if it is dead end or part of a loop'.format(route[i])
        if len(route) - 1 > tunnel_length:
            assert False, 'tunnel route is of length {}, longer than the limit of {}'.format(
                len(route), tunnel_length)

    def investigate(self, probes):
        self.num_phase -= 1
        if self.num_phase == 1:
            self.curr_phase = GUESS_PHASE

        report = []
        for [x, y] in probes:
            if self.intersections[x][y] == 1:
                report.append(
                    {'[{},{}]'.format(x, y): self.intersection_neighbors.get((x, y))})

        return report

    def get_info(self, result=[]):
        info = {'grid': self.num_grid, 'remaining_phases': self.num_phase,
                'tunnel_length': self.tunnel_length, 'curr_phase': self.phase, 'result': result}
        if self.num_phase > 1:
            info['next_phase'] = PROBE_PHASE
        elif self.num_phase == 1:
            info['next_phase'] = GUESS_PHASE
        return info


def establish_connection(port):
    HOST = 'localhost'
    PORT = port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(5)
    (conn, addr) = s.accept()
    return conn


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

    game = Game(num_grid, num_phase, tunnel_length)
    game.load_tunnel()

    conn = establish_connection(port)
    try:
        data = receive_data(conn)
        if data:
            print(data)
            game.set_player(data['player_name'])
        # game info

        payload = game.get_info()
        send_data(conn, payload)

        # probing phase
        # begin timer here
        while not game.isEnded():
            print("phase {}".format(num_phase - game.num_phase + 1))
            req = receive_data(conn)
            if game.num_phase > 1 and req['phase'] == PROBE_PHASE:
                prob_result = game.investigate(req['probes'])
                payload = game.get_info(prob_result)
                send_data(conn, payload)
            elif req['phase'] == GUESS_PHASE:
                score = game.check_answer(req['answer'])
                print("player {} got score {}".format(
                    game.detector.name, score))
            else:
                assert False, "This is the guessing round"

        conn.close()
    except Error as e:
        print(e)
        conn.close()
