import sys
import getopt


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class InputError(Error):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message
# n x n??


class Game:
    def __init__(self, num_grid, num_phase, tunnel_length):

        if num_grid < 2:
            raise InputError(
                num_grid, "grid size should be greater than or equal to 2")
        if num_phase < 2:
            raise InputError(
                num_phase, "number of phases should be greater or equal to 2")
        if tunnel_length < num_grid - 1:
            raise InputError(
                tunnel_length, "tunnel length should be at least n-1 for n * n grid")

        self.num_grid = num_grid
        self.num_phase = num_phase
        self.tunnel_length = tunnel_length
        self.intersections = [
            [0 for _ in range(self.num_grid+1)] for _ in range(self.num_grid+1)]
        self.intersection_neighbors = {}

    def load_tunnel(self):
        f = open("tunnel", "r")
        prev = None
        route = []

        # form the map
        for line in f:
            str_x, str_y = line.split(',')
            x = int(str_x)
            y = int(str_y)
            route.append((x, y))
            print(x, y)
            if prev is not None and not abs(prev[0] - x) ^ abs(prev[1] - y):
                raise InputError((x, y), "tunnel is not connected")
            self.intersections[x][y] = 1
            self.intersection_neighbors[(x, y)] = []
            # look for existing neighbors and set neighbor map
            for d_x in [-1, 0, 1]:
                for d_y in [-1, 0, 1]:
                    # skip itself
                    if d_x == 0 and d_y == 0:
                        continue
                    print("deltas: {}, {}".format(x+d_x, y+d_y))
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
        print(route)
        print(self.intersection_neighbors)

        # validations
        if route[0][0] != 1:
            assert False, "Starting point {} should be at index 1, i.e. (1,x)".format(
                route[0][0])
        if route[-1][0] != self.num_grid:
            assert False, "Ending point {} should be at index {}, i.e. ({},x)".format(
                route[-1][0],  self.num_grid,  self.num_grid)

        if len(self.intersection_neighbors.get(route[0])) != 1:
            assert False, "Starting point should only have one neighboring intersection."
        if len(self.intersection_neighbors.get(route[-1])) != 1:
            assert False, "Ending point should only have one neighboring intersection."
        for i in route[2:-1]:
            if len(self.intersection_neighbors.get(i)) != 2:
                assert False, "Intersection {} has only one or more than 2 neighbors. \
                    Please check if it is dead end or part of a loop".format(route[i])
        if len(route) - 1 > tunnel_length:
            assert False, "tunnel route is of length {}, longer than the limit of {}".format(
                len(route), tunnel_length)


if __name__ == "__main__":
    optlist, args = getopt.getopt(sys.argv[1:], 'n:p:k:', [
        'grid=', 'phase=', 'tunnel='])
    num_grid, num_phase, tunnel_length = 0, 0, 0

    for o, a in optlist:
        if o in ("-n", "--grid"):
            num_grid = int(a)
        elif o in ("-p", "--phase"):
            num_phase = int(a)
        elif o in ("-k", "--tunnel"):
            tunnel_length = int(a)
        else:
            assert False, "unhandled option"
    game = Game(num_grid, num_phase, tunnel_length)

    game.load_tunnel()
