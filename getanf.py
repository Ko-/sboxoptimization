#!/usr/bin/env python3

#########################
#                       #
#         Setup         #
#                       #
#########################

import argparse  # requires Python >= 3.2
import math
import sys
import textwrap

# adding your own S-box is as easy as adding an item to this dictionary
sboxes = dict()
sboxes['ctc2']          = [7, 6, 0, 4, 2, 5, 1, 3]
sboxes['present']       = [12, 5, 6, 11, 9, 0, 10, 13, 3, 14, 15, 8, 4, 7, 1, 2]
sboxes['ascon']         = [4, 11, 31, 20, 26, 21, 9, 2, 27, 5, 8, 18, 29, 3, 6, 28, 30, 19, 7, 14, 0, 13, 17, 24, 16, 12, 1, 25, 22, 10, 15, 23]
sboxes['icepole']       = [31, 5, 10, 11, 20, 17, 22, 23, 9, 12, 3, 2, 13, 8, 15, 14, 18, 21, 24, 27, 6, 1, 4, 7, 26, 29, 16, 19, 30, 25, 28, 0]
sboxes['ketje']         = [0, 5, 10, 11, 20, 17, 22, 23, 9, 12, 3, 2, 13, 8, 15, 14, 18, 21, 24, 27, 6, 1, 4, 7, 26, 29, 16, 19, 30, 25, 28, 31]
sboxes['keyak']         = sboxes['ketje']
sboxes['primate']       = [1, 0, 25, 26, 17, 29, 21, 27, 20, 5, 4, 23, 14, 18, 2, 28, 15, 8, 6, 3, 13, 7, 24, 16, 30, 9, 31, 10, 22, 12, 11, 19]
sboxes['primate_inv']   = [1, 0, 14, 19, 10, 9, 18, 21, 17, 25, 27, 30, 29, 20, 12, 16, 23, 4, 13, 31, 8, 6, 28, 11, 22, 2, 3, 7, 15, 5, 24, 26]
sboxes['joltik']        = [14, 4, 11, 2, 3, 8, 0, 9, 1, 10, 7, 15, 6, 12, 5, 13]
sboxes['joltik_inv']    = [6, 8, 3, 4, 1, 14, 12, 10, 5, 7, 9, 2, 13, 15, 0, 11]
sboxes['lac']           = [14, 9, 15, 0, 13, 4, 10, 11, 1, 2, 8, 3, 7, 6, 12, 5]
sboxes['minalpher']     = [11, 3, 4, 1, 2, 8, 12, 15, 5, 13, 14, 0, 6, 9, 10, 7]
sboxes['prost']        = [0, 4, 8, 15, 1, 5, 14, 9, 2, 7, 10, 12, 11, 13, 6, 3]
sboxes['rectangle']     = [9, 4, 15, 10, 14, 1, 0, 6, 12, 7, 3, 8, 2, 11, 5, 13]
sboxes['rectangle_inv'] = [6, 5, 12, 10, 1, 14, 7, 9, 11, 0, 3, 13, 8, 15, 4, 2]


#########################
#                       #
#    Helper functions   #
#                       #
#########################

# write equations for all pairs ai,aj s.t. only one ak is allowed to be 1
def maxonea(start, end):
    for i in range(start, end):
        for j in range(i + 1, end):
            print('a_{:d} * a_{:d}'.format(i, j))


# write equations for all pairs ai,bj for sets a and b s.t. no pair is allowed to be both 1
def maxone(lista, listb):
    for i in lista:
        for j in listb:
            print('a_{:d} * a_{:d}'.format(i, j))


#########################
#                       #
#          Main         #
#                       #
#########################

if __name__ == "__main__":
    # parsing command line input
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('mode', metavar='mode', choices=['mc', 'bgc', 'gc', 'depth'], help="Mode to operate in. One of:\nmc     for multiplicative complexity\nbgc    for bitslice gate complexity\ngc     for gate complexity\ndepth  for depth complexity")
    parser.add_argument('cipher', metavar='cipher', choices=sorted(sboxes.keys()), help="Name of cipher of which the S-box should be used. One of:\n" + textwrap.fill(', '.join(sorted(sboxes.keys())), 68))
    parser.add_argument('k', metavar='k', type=int, choices=range(1, 50), help=textwrap.fill('Value to test for. E.g. number of nonlinear gates for mode=mc, circuit depth for mode=depth, etc.', 68))
    parser.add_argument('width', metavar='width', nargs='?', type=int, choices=range(1, 50), help=textwrap.fill('Only applicable to mode=depth. Set width of circuit layer to test for.', 68))
    args = parser.parse_args()
    if args.mode == 'depth' and args.width is None:
        parser.print_usage(sys.stderr)
        print(sys.argv[0] + ': error: the following arguments are required for mode=depth: width', file=sys.stderr)
        exit()

    # initialize globals using command line input
    sbox = sboxes[args.cipher]
    n = m = int(math.log(len(sbox), 2))  # currently only considering square S-boxes, but it also works if you set n and m to different values
    x = y = q = t = 0  # rename these, but ...

    for i in range(len(sbox)):
        a = b = 0  # ... leave these the same

        # initially, let Z contain input bits
        Z = ['x_' + str(x + _x) for _x in range(n)]

        for depth in range(args.k):
            width = args.width if args.mode == 'depth' else 1
            for _q in range(2*width):
                if args.mode == 'mc':
                    print('q_{:d} = a_{:d}'.format(q + _q, a), end='')
                    a = a + 1
                    for z in Z:
                        print(' + a_{:d} * {:s}'.format(a, z), end='')
                        a = a + 1
                    print()
                else:
                    print('q_{:d} = '.format(q + _q), end='')
                    print(' + '.join('a_{:d} * {:s}'.format(a + _a, Z[_a]) for _a in range(len(Z))))
                    if i == 0:  # only necessary once
                        maxonea(a, a + len(Z))
                        # make sure that this gate really requires a new depth layer (do not use e.g. 2 x's as inputs at depth = 1)
                        if args.mode == 'depth' and _q % 2 == 1 and depth > 0:
                            maxone(list(range(a - len(Z), a - width)), list(range(a, a + len(Z) - width)))
                    a = a + len(Z)
            for _ in range(width):
                if args.mode == 'mc':
                    # add AND gate
                    print('t_{:d} = q_{:d} * q_{:d}'.format(t, q, q + 1))
                elif args.mode == 'bgc':
                    # add a binary XOR/AND/OR gate or the unary NOT gate
                    print('t_{:d} = b_{:d} * q_{:d} * q_{:d} + b_{:d} * q_{:d} + b_{:d} * q_{:d} + b_{:d} + b_{:d} * q_{:d}'.format(t, b, q, q + 1, b + 1, q, b + 1, q + 1, b + 2, b + 2, q))
                elif args.mode == 'gc' or args.mode == 'depth':
                    # add any gate
                    print('t_{:d} = b_{:d} * q_{:d} * q_{:d} + b_{:d} * q_{:d} + b_{:d} * q_{:d} + b_{:d}'.format(t, b, q, q + 1, b + 1, q, b + 1, q + 1, b + 2))

                if args.mode == 'bgc' and i == 0:  # only necessary once to disallow NAND/NOR/XNOR
                    print('b_{:d} * b_{:d}'.format(b, b + 2))
                    print('b_{:d} * b_{:d}'.format(b + 1, b + 2))

                Z.append('t_' + str(t))
                t = t + 1
                q = q + 2
                b = b + 3

        # set each output bit yi to be equal to one of the previous variables in Z
        for _y in range(m):
            print('y_{:d} = '.format(y + _y), end='')
            print(' + '.join(['a_{:d} * {:s}'.format(a + _a, Z[_a]) for _a in range(len(Z))]))
            if args.mode != 'mc' and i == 0:
                maxonea(a, a + len(Z))
            a = a + len(Z)

        # S-box specific contraints
        # substitute the known pairs (x,y)
        binrepr = bin(i)[2:].zfill(n)
        for j in range(n):
            print(('1+x_{:d}' if binrepr[j] == '1' else 'x_{:d}').format(x))
            x = x + 1
        binrepr = bin(sbox[i])[2:].zfill(m)
        for j in range(m):
            print(('1+y_{:d}' if binrepr[j] == '1' else 'y_{:d}').format(y))
            y = y + 1
