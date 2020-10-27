import sys
import getopt
import json
import socket
import signal
import time

TIME_LIMIT = 120
DATA_SIZE = 4096
PROBE_PHASE = 'probe'
GUESS_PHASE = 'guess'


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class TimeOutException(Exception):
    pass


class InputError(Error):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


class Detector:
    def __init__(self, name, num_grid):
        self.name = name
        self.probes = []
        self.probe_map = [
            [0 for _ in range(num_grid+1)] for _ in range(num_grid+1)]

    def update_probes(self, probes):
        self.probes.extend(x for x in probes if x not in self.probes)
        for (px, py) in probes:
            self.probe_map[px][py] = 1

    def draw_probes(self, intersections, insec_neighbors, num_grid):
        grid = ''
        for i in reversed(range(1, num_grid+1)):
            row = '\n'
            col = '\n'
            for j in range(1, num_grid+1):
                # don't draw columns after the last row
                if i > 1:
                    if (self.probe_map[i][j] == 1 or self.probe_map[i-1][j] == 1) \
                            and intersections[i][j] == 1 \
                            and (i-1, j) in insec_neighbors.get((i, j)):
                        col += '‖   '
                    else:
                        col += '|   '

                if self.probe_map[i][j] == 1:
                    row += 'O'
                else:
                    row += '+'
                if j < num_grid:
                    if (self.probe_map[i][j] == 1 or self.probe_map[i][j+1] == 1) \
                            and intersections[i][j] == 1 \
                            and (i, j+1) in insec_neighbors.get((i, j)):
                        row += '==='
                    else:
                        row += '---'

            grid += row
            grid += col

        print(grid)


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
        self.route = []
        self.node_set = []

    def draw_grid(self, insec, insec_neighbors):
        grid = ''
        for i in reversed(range(1, self.num_grid+1)):
            row = '\n+'
            col = '\n'
            for j in range(1, self.num_grid+1):
                # don't draw columns after the last row
                if i > 1:
                    if insec[i][j] == 1 and (i-1, j) in insec_neighbors.get((i, j)):
                        col += '‖   '
                    else:
                        col += '|   '
                if j < self.num_grid:
                    if insec[i][j] == 1 and (i, j+1) in insec_neighbors.get((i, j)):
                        row += '===+'
                    else:
                        row += '---+'

            grid += row
            grid += col

        print(grid)

    def isEnded(self):
        return self.num_phase <= 0

    def set_player(self, name):
        self.detector = Detector(name, self.num_grid)

    def use_probes(self, probes):
        self.detector.update_probes(probes)

    def check_answer(self, answers):
        self.num_phase -= 1
        is_answer_correct = True

        guess_insec = [
            [0 for _ in range(self.num_grid+1)] for _ in range(self.num_grid+1)]
        guess_insec_neighbors = {}
        for ([s_x, s_y], [e_x, e_y]) in answers:
            start_node = (s_x, s_y)
            end_node = (e_x, e_y)
            # fill in guess grid
            guess_insec[s_x][s_y] = 1
            guess_insec[e_x][e_y] = 1
            if start_node not in guess_insec_neighbors:
                guess_insec_neighbors[start_node] = []
            if end_node not in guess_insec_neighbors:
                guess_insec_neighbors[end_node] = []
            guess_insec_neighbors.get(start_node).append(end_node)
            guess_insec_neighbors.get(end_node).append(start_node)

            # check with tunnel grid
            if self.intersections[s_x][s_y] != 1 or \
                    (e_x, e_y) not in self.intersection_neighbors.get((s_x, s_y)):
                print("({},{}), ({},{}) is not part of the tunnel".format(
                    s_x, s_y, e_x, e_y))
                is_answer_correct = False
        print("Detector's guess")
        self.draw_grid(guess_insec, guess_insec_neighbors)
        if len(answers) != len(self.route):
            is_answer_correct = False
            print("answer is shorter than tunnel")
            return sys.maxsize
        elif not is_answer_correct:
            print("answer is not correct")
            return sys.maxsize
        return len(self.detector.probes)

    def fill_in_grid(self):
        f = open('tunnel', 'r')
        route = []
        node_set = []
        # fill in the grid
        for line in f:
            start, end = line.split(' ')
            str_s_x, str_s_y = start.split(',')
            str_e_x, str_e_y = end.split(',')
            s_x = int(str_s_x)
            s_y = int(str_s_y)
            e_x = int(str_e_x)
            e_y = int(str_e_y)
            start_node = (s_x, s_y)
            end_node = (e_x, e_y)
            route.append([start_node, end_node])
            if start_node not in node_set:
                node_set.append(start_node)
            if end_node not in node_set:
                node_set.append(end_node)

            self.intersections[s_x][s_y] = 1
            self.intersections[e_x][e_y] = 1
            if start_node not in self.intersection_neighbors:
                self.intersection_neighbors[start_node] = []
            if end_node not in self.intersection_neighbors:
                self.intersection_neighbors[end_node] = []
            self.intersection_neighbors.get(start_node).append(end_node)
            self.intersection_neighbors.get(end_node).append(start_node)
        self.route = route
        self.node_set = node_set
        print(route)

    def validate_tunnel(self):
        if len(self.route) > tunnel_length:
            assert False, 'tunnel route is of length {}, longer than the limit of {}'.format(
                len(self.route), tunnel_length)
        # validations
        # at least one point in (1,x) shoule be occupied
        south_street_occupancy = list(filter(
            lambda x: x == 1, self.intersections[1]))
        north_street_occupancy = list(filter(
            lambda x: x == 1, self.intersections[-1]))
        if len(south_street_occupancy) < 1:
            assert False, 'Origin should start from the south, i.e. (1,x)'
        # at least one point in (n,x) shoule be occupied
        if len(north_street_occupancy) < 1:
            assert False, 'Destination should end at the north, i.e. (n,x)'

        # Only two points can have only one neighbor. These two points must be (1,x) and (n,x)
        # The rest of neighbor map should have two neighbors, or else it's dead end or part of a loop
        origin = None
        destination = None
        for i in self.node_set:
            if len(self.intersection_neighbors.get(i)) != 2:
                # only two points can have only one neighbor. These two points must be (1,x) and (n,x)
                if i[0] == 1 and origin is None:
                    origin = i
                elif i[0] == num_grid and destination is None:
                    destination = i
                else:
                    assert False, 'Intersection {} might be part of a loop or a deadend. \
                        Current neighbors: {}'.format(i, self.intersection_neighbors.get(i))
        if origin is None or destination is None:
            assert False, 'Cannot find origin or destination. Detected origin as {}, \
                destination as {}'.format(origin, destination)
        print(self.intersection_neighbors)

    def load_tunnel(self):

        self.fill_in_grid()
        self.draw_grid(self.intersections, self.intersection_neighbors)
        self.validate_tunnel()

    def investigate(self, probes):
        self.num_phase -= 1
        if self.num_phase == 1:
            self.curr_phase = GUESS_PHASE
        self.use_probes(probes)
        report = []
        for [x, y] in probes:
            if self.intersections[x][y] == 1:
                report.append(
                    {'[{},{}]'.format(x, y): self.intersection_neighbors.get((x, y))})
        self.detector.draw_probes(
            self.intersections, self.intersection_neighbors, self.num_grid)
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


def alarm_handler(signum, frame):
    print("Detector exceeds time limit")
    raise TimeOutException()


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
            game.set_player(data['player_name'])
        # game info

        payload = game.get_info()
        send_data(conn, payload)

        # begin timer here
        # probing phase
        signal.signal(signal.SIGALRM, alarm_handler)
        signal.alarm(TIME_LIMIT)
        while not game.isEnded():
            print("phase {}".format(num_phase - game.num_phase + 1))
            req = receive_data(conn)
            if game.num_phase > 1 and req['phase'] == PROBE_PHASE:
                prob_result = game.investigate(req['probes'])
                print('Detector probes: {}'.format(req['probes']))
                print('Probe report: {}'.format(prob_result))
                print('\n')
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
