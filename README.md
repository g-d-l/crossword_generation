The program generates crossword puzzles from blank grids, providing a solution and list of clues. The clues are courtesy of [this archive][c] of clue/word pairs from 1996 to 2012 in the New York Times. The potentially exponential runtime is sped up through a number of heuristics. Most 15x15 grids run in under a couple of seconds.

[c]: https://github.com/donohoe/nyt-crossword

# Usage

`python crossword.py [-dim D] [-grid PATH1] [-difficulty L] [-dictionary PATH2] [-display] [-export_grid PATH3] [-export_solution PATH4]`



- Either the [`-dim D`] flag must be provided with a dimension for the grid, or 
[`-grid PATH1`] must be provided with `PATH1` being a txt file grid, as is 
produced by the `blank_grid_extractor.py` script.

Optional:

- [`-difficulty L`] specifices the difficuly of the puzzle, 0 <= `L` <= 4, 4 
being the hardest. Default value is 1.

- [`-dictionary PATH2`], if provided, must point to a text file containing 
words and clues, of the form

    `clue<tab>word`
    
one on each line.

- [`-display`] means print the grid at each iteration as it is being filled in. 
An error will be thrown if the terminal is too small to display the full grid

- [`-export_grid PATH3`], if provided, indicates file name for the blank grid and 
clues to be outputted to.

- [`-export_solution PATH4`], if provided, indicates file name for the solution 
to be outputted to.


# Input Grids
Grids are .txt files that use spaces for blank squares and * characters for filled squares. Each row corresponds to a row of the puzzle. See the `/grids` folder for examples. Currently there are grids of dimension 4, 8, 13, 15, 17, 19, and 23 provided. To generate new ones from image files, save the image file in `/grid_images` with the next available suffix (i.e., 23x23-1.gif) and run 

`python blank_grid_extract.py`

to turn them into .txt files. This functionality requires the Pillow Python package.

Helper functions to generate the dictionary, ngram dictionaries, check various grid conditions, etc. are all found in utils.py.