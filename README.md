# Tactic-toe Software

## Project Details

* **Overview:** [amierulhakeem.dev/projects/tactictoe-overview/](https://amierulhakeem.dev/projects/tactictoe-overview/)
* **Software:** [amierulhakeem.dev/projects/tactictoe-software/](https://amierulhakeem.dev/projects/tactictoe-software/)

## File Versions

| File | Implementation |
| :--- | :--- |
| `tictactoe.py` | Original CS50ai Implementation |
| `tactictoe.py` | Tactic-Toe modification |
| `tactictoeV2.py` | Minimax AI version 2 |
| `tactictoeV2_negamax_basic.py` | Negamax implementation |
| **`calculation.py`** | **Final Implementation:** Also exports best moves in .h and .json |


## Execution

### 1. Run the Game

* `runner.py` / `runner_V2.py`: Play against the AI.
* `runner_auto.py`: Watch the AI play against itself.

### 2. Switch AI Versions

Modify the import in any runner file:

``` python
import tactictoeV2_negamax_basic as ttt  # Swap with any version file
```

## Web Version

`/web_version/index.html`: HTML version of the game
