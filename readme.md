### Dig That
#### Authors
Victoria Lu <viclu at nyu.edu>
Mandy Xu <xx414 at nyu.edu>

#### Description
The streets runs from 0 to num_grid for the convience of everyone.
#### System requirements
Python 3.6.9

#### How to run

To start the game:
should take in three params:
```python3 game.py --grid 5 --phase 3 --tunnel 4```
or use short args:
```python3 game.py -n 5 -p 3 -k 4```

```-n``` or ```--grid```: size of n * n grids
```-p``` or ```--phase```: number of probing phases, including the last round of guessing phase. E.g. --phase 3 meaning two rounds of probing and the last one is guessing
```-k``` or ```--tunnel```: length of tunnel. should be >= n-1

Tunnelers:
should take in three params:
```python3 tunneler_example.py --grid 5 --phase 3 --tunnel 4```
or use short args:
```python3 tunneler_example.py -n 2 -p 2 -k 1```

#### What to hand in
Code for Tunnel:
Should take in three params: ```--grid 5 --phase 3 --tunnel 4```
Should output a file named ```tunnel``` that satisfies the following:
* all intersection coordinates in order, starting from the bottom i.e. (1, y)
* each coordinate should take one line, in the form of ```x,y```
* The last line should be (n+1, y), where n is the the number of grids

Please refer to tunnel_example file as a sample.