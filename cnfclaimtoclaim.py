#!/usr/bin/env python3

import argparse  # requires Python >= 3.2
import re
import sys
import textwrap

if __name__ == "__main__":
    # parsing command line input
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('claim', help=textwrap.fill('Name of the CNF claim file as provided by the SAT solver.', 68))
    parser.add_argument('resolve', nargs='?', metavar='resolve', help=textwrap.fill('Name of the resolve file as provided by xl0.exe. If omitted, <claim>.eqs.cnf.resolve will be used', 68))
    args = parser.parse_args()
    if args.resolve is None:
        # rewrite [path/]file.extension to [path/]file.eqs.cnf.resolve
        path = args.claim.split('/')
        args.resolve = '/'.join(path[:-1]) + ('/' if len(path) > 1 else '') + path[-1].split('.')[0] + '.eqs.cnf.resolve'

    # read resolve file to translate between variable names and DIMACS CNF numbers
    d = dict()
    with open(args.resolve, 'rt') as cnfresolve_file:
        for line in cnfresolve_file.readlines()[5:]:  # [5:] to skip comments
            m = re.match(r'^(\d+)\s+signifies\s+(.+)$', line)  # e.g.: 1  signifies a_0
            if m:
                d[int(m.group(1))] = m.group(2)

    # print SAT solver claim using variable names, to be used by getsolution.py
    with open(args.claim, 'rt') as cnfclaim_file:
        for x in cnfclaim_file.readlines()[1].split(' '):  # e.g.: -1 -2 -3 -4 -5 -6 -7 8 -9 -10 -11 ...
            if x[0] == '-':
                y = int(x[1:])
                if y not in d:
                    break
                print(d[y] + '=0')
            elif int(x) in d:
                print(d[int(x)] + '=1')
            else:
                break
