# S-box optimization using SAT solvers

These tools are part of the paper "Optimizing S-box Implementations for Several Criteria using SAT Solvers" by Ko Stoffelen, published at FSE 2016.

## getanf.py

`getanf.py` generates `C'`, given an optimization goal, an S-box and a `k`. It writes to `stdout`. Adding another S-box can easily be done with 1 line of code.

```
$ ./getanf.py -h
usage: getanf.py [-h] mode cipher k [width]

positional arguments:
  mode        Mode to operate in. One of:
              mc     for multiplicative complexity
              bgc    for bitslice gate complexity
              gc     for gate complexity
              depth  for depth complexity
  cipher      Name of cipher of which the S-box should be used. One of:
              ascon, ctc2, icepole, joltik, joltik_inv, ketje, keyak, lac,
              minalpher, present, primate, primate_inv, prost, rectangle,
              rectangle_inv
  k           Value to test for. E.g. number of nonlinear gates for mode=mc,
              circuit depth for mode=depth, etc.
  width       Only applicable to mode=depth. Set width of circuit layer to test
              for.

optional arguments:
  -h, --help  show this help message and exit
```

## cnfclaimtoclaim.py

In DIMACS CNF format, all variables are replaced by numbers. `cnfclaimtoclaim.py` takes care of a preprocessing step to translate a solution found by the SAT solver (CNF claim file) back to the original variable names. It writes to `stdout`.

```
$ ./cnfclaimtoclaim.py -h
usage: cnfclaimtoclaim.py [-h] claim [resolve]

positional arguments:
  claim       Name of the CNF claim file as provided by the SAT solver.
  resolve     Name of the resolve file as provided by xl0.exe. If omitted,
              <claim>.eqs.cnf.resolve will be used

optional arguments:
  -h, --help  show this help message and exit
```

## getsolution.py

`getsolution.py` reconstructs the S-box implementation from the original ANF file and the file outputted by `cnfclaimtoclaim.py`. It writes to `stdout`. It is possible that some 'gates' are not actually being used. They can freely be removed from the implementation.

```
$ ./getsolution.py -h
usage: getsolution.py [-h] [-m mode] [-c claim] file

positional arguments:
  file        Name of the anf file as generated by getanf.py

optional arguments:
  -h, --help  show this help message and exit
  -m mode     Mode to operate in. One of:
              mc     for multiplicative complexity
              bgc    for bitslice gate complexity
              gc     for gate complexity
              depth  for depth complexity
              If omitted, the mode will be based on the filename
  -c claim    Name of the claim file as generated by cnfclaimtoclaim.py. If
              omitted, <file>.claim.txt will be used
```

## Dependencies

An implementation of Bard-Courtois-Jefferson for converting a sparse system of low-degree multivariate polynomials over GF(2) from ANF to CNF can be found [here](http://www.nicolascourtois.com/software/CourtoisBardJefferson_public_distribution.zip). It is also implemented in the xl0 tool, available [here](http://www.nicolascourtois.com/software/xl0.exe) ([documentation](http://cryptosystem.net/aes/tools.html)). Unfortunately it is only distributed as a Windows binary.

Optionally, if one wants to optimize linear parts separately, as done for the S-box used by the PRIMATE permutation in Section 4 of the paper, an implementation of Fuhs-Kamp by Thom Wiggers is available on [GitHub](https://github.com/thomwiggers/find-shortest-slp). He also implemented Boyar-Matthews-Peralta, which can be found [here](https://github.com/thomwiggers/slp-heuristic).

## Example

A typical run will go like this. Assume we want to optimize the RECTANGLE S-box for gate complexity and we want to test if there exists a circuit implementing the S-box with 11 gates. Any SAT solver that reads DIMACS CNF files can be used.

```
$ ./getanf.py gc rectangle 11 > rectangle_gc11.eqs
C:\> xl0.exe /deg3 /dontsat /bard rectangle_gc11.eqs
$ nohup ./myfavouritesatsolver rectangle_gc11.eqs.cnf > rectangle_gc11.eqs.cnf.claim &
$ ./cnfclaimtoclaim.py rectangle_gc11.eqs.cnf.claim > rectangle_gc11.eqs.claim.txt
$ ./getsolution.py rectangle_gc11.eqs > rectangle_gc11.solution
```
