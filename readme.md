### Dig That

#### Authors

Victoria Lu

 viclu at nyu.edu

Mandy Xu

xx414 at nyu.edu

#### Description
https://cs.nyu.edu/courses/fall20/CSCI-GA.2965-001/digthatcomp.html

The streets runs from 1 to num_grid.
Here's an example for 5x5 grid:
```
5   +---+---+---+---+
    |   |   ‖   |   |
4   +---+---+---+---+
    |   |   ‖   |   |
3   +---+---+===+---+
    |   |   |   ‖   |
2   +---+---+===+---+
    |   |   ‖   |   |
1   +---+---+---+---+
    1   2   3   4   5
```
Double lines are the tunnels. The graph shows a tunnel that originates at (1,3) and ends at (5,3). The coordinate format is (row, col).

#### System requirements

Python 3.6.8

#### Structure
The project consists of a server `game.py`, a program that produces the tunnel (e.g. `tunneler_example.py`), a program that detects the tunnel (e.g. `dectector_example.py`). `run_game.sh` passes down the arguments and runs the tunneler, follows by the game. The tunneler produces the tunnel in file named `tunnel` and `game.py` will look for `tunnel` and load it up. It then starts the server, waiting for the detector to join. Detector program should be triggered by `run_detect.sh`.


#### How to run
To start the game: \
`./run_game.sh 5 3 9` \
 to run tunneler and start the game. Params are given in the order of num_grid, num_phases, tunnel_length. \
`./run_detect.sh` to start the detector. The detector will get params from the server.

The given example is a simple tunnel with the detector guessing correctly. To see a failed example, rename `tunnel_example` to `tunnel` and rerun the game.

The following gives information on how to run each part.

##### Server:
`python3 game.py --grid 5 --phase 3 --tunnel 4` \
or use short args: \
`python3 game.py -n 5 -p 3 -k 4`

`-n` or `--grid`: size of n \* n grids \
`-p` or `--phase`: number of probing phases, including the last round of guessing phase. E.g. --phase 3 meaning two rounds of probing and the last one is guessing \
`-k` or `--tunnel`: length of tunnel. should be >= n-1

##### Tunneler
Tunnelers should take in three params and produces `tunnel`. For example: \
`python3 tunneler_example.py --grid 5 --phase 3 --tunnel 4` \
or use short args: \
`python3 tunneler_example.py -n 2 -p 2 -k 1`

##### Detector
Detectors will receive params from the server. \
`python3 detector_example.py`

#### Data structures:
The communication between server and detector is a json object.

The server will send:
```
{'grid': number of grid,
 'remaining_phases': number of remaining phases,
 'tunnel_length': tunnel length,
 'curr_phase': 'probe' or 'guess',
 'next_phase': 'probe' or 'guess'; 'guess' if the next is the last round
 'result': probe report if any probe detects a tunnel. If no probe is correct, will return an empty array
}
```
For example:
```
{'grid': 5,
'remaining_phases': 2,
'tunnel_length': 9,
'curr_phase': 'probe',
'result': [{'[3,3]': [[3, 4], [4, 3]]}],
'next_phase': 'probe'}
```


The detector will send:
In probe phase:
```
{'phase': 'probe', 'probes': [[3, 3], [4, 4]]}
```
`probes` field is a list of intersection coordinates to be probed. If there is still probing phases but player do not want to put probes, use empty array to skip the round or just directly go into the guess phase by using the format below. Please note that once a player starts to guess, s/he may not go back to probing phase any more.

In guess phase:
```
{'phase': 'guess', 'answer': [
            [[1, 3], [2, 3]], [[2, 3], [3, 3]], [[3, 3], [4, 3]], [[4, 3], [5, 3]]]}
```
The `answer` field is a list of tunnel segments. One segment is defined by two intersection coordinates, in the format of `[[x1, y1], [x2, y2]]`
#### What to hand in
* Tunneler program (which should produce `tunnel`)
* Detector program
* ./run_game.sh that includes the commands to start tunneler
* ./run_detector.sh that includes teh commands to start detector

**Tunneler program** \
Should take in three params: `--grid 5 --phase 3 --tunnel 4` \
Should output a file named `tunnel`. Each tunnel segment should take one line, in the form of `x1,y1 x2,y2` i.e. starting coordinates and ending coordinates should separate by a space.

Please refer to tunnel_example file as a sample.


