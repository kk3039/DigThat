import sys
import getopt
import random
import math


def build_tunnel(num_grid, tunnel_length, f):
    y = math.ceil(num_grid/2)
    # e.g. 6 grid means 7 streets
    for i in range(1, num_grid+1):
        f.write("{},{}\n".format(i, y))


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

    f = open("tunnel", "w")
    build_tunnel(num_grid, tunnel_length, f)
    f.close()
