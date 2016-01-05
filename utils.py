import string, random, copy, re, sys, curses, os, time


'''
Various utility and helper functions for the main algorithm
'''





'''
Pretty print the grid
'''
def print_grid(grid):
	xdim, ydim = get_dims(grid)
	for y in xrange(ydim):
		for x in xrange(xdim):
			print grid[x][y],
		print

'''
Print to the refreshable console
'''
def console_print(grid, console, i):
	xdim, ydim = get_dims(grid)
	for y in xrange(5, 5 + ydim):
	    for x in xrange(5, 5 + xdim):
	        try:
	            console.addch(y, x, ord(grid[x - 5][y - 5]))
	        except curses.error:
	            pass
    
	step = str(i).zfill(3)
	for x in xrange(5, 5 + len(step)):
		try:
			console.addch(3, x + 15, ord(step[x - 5]))
		except curses.error:
			pass
	for x in xrange(5 + len(step), 10):
		try:
			console.addch(4, x, ord(' '))
		except curses.error:
			pass
	console.refresh(0, 0, 1, 0, ydim + 11, 99)



'''
Return True if the word at (x, y) in the given direction 
has no filled in letters already and is not bordered by any
other words. False otherwise.
'''
def is_unconstrained(grid, x, y, length, direction):
	xdim, ydim = get_dims(grid)
	if direction == "across":
		for x1 in xrange(x, x + length):
			if grid[x1][y] != ' ':
				return False
			elif y > 0 and not (grid[x1][y - 1] == ' ' or grid[x1][y - 1] == '*'):
				return False
			elif y < ydim - 1 and not (grid[x1][y + 1] == ' ' or grid[x1][y + 1] == '*'):
				return False
	else:
		for y1 in xrange(y, y + length):
			if grid[x][y1] != ' ':
				return False
			elif x > 0 and not (grid[x - 1][y1] == ' ' or grid[x - 1][y1] == '*'):
				return False
			elif x < xdim - 1 and not (grid[x + 1][y1] == ' ' or grid[x + 1][y1] == '*'):
				return False
	return True

'''
Add word to the grid
'''
def add_word_to_grid(word, grid, x, y, direction):
	if direction == 'down':
		for y1 in xrange(y, y + len(word)):
			grid[x][y1] = word[y1 - y]
	else:
		for x1 in xrange(x, x + len(word)):
			grid[x1][y] = word[x1 - x]

'''
Return the word at (x, y) as a string, with spaces for blank letters
'''
def extract_word_from_grid(grid, x, y, length, direction):
	if direction == 'down':
		return "".join(grid[x][y:y + length])
	else:
		return "".join([grid[x1][y] for x1 in xrange(x, x + length)])

'''
Returns True if the word beginning at (x, y) is missing at
least one letter, False otherwise
'''
def is_missing_letter(grid, x, y, length, direction):
	if direction == 'down':
		for y1 in xrange(y, y + length):
			if grid[x][y1] == ' ':
				return True
	else:
		for x1 in xrange(x, x + length):
			if grid[x1][y] == ' ':
				return True

	return False

'''
Returns True is the word at (x, y) is missing a letter only at
(x1, y1), False otherwise
'''
def is_missing_one_letter(grid, x, y, x1, y1, length, direction):
	if direction == 'down':
		for y2 in xrange(y, y1):
			if grid[x][y2] == ' ':
				return False
		for y2 in xrange(y1 + 1, y + length):
			if grid[x][y2] == ' ':
				return False
	else:
		for x2 in xrange(x, x1):
			if grid[x2][y] == ' ':
				return False
		for x2 in xrange(x1 + 1, x + length):
			if grid[x2][y] == ' ':
				return False

	return True



'''
get xdim, ydim of the grid
'''
def get_dims(grid):
	return len(grid), len(grid[0])



'''
For each element in the word at (x, y) check whether it is:
(in order of priority)
already filled		 						'filled'
the last empty in its crossing word 		('last', left/above substring, right/below substring)
constrained on both sides					('both', left/above char, right/below char)
first 2 letters of word, one already filled	('first2', first, second)				[one of first/second will be '']
constrained to the left						('left'/'above', char)					['above' for across words]
constrained to the right					('right'/'below', char)					['below' for across words]
unconstrained 								'unconstrained'

and return an array with such flags, to be used in the scoring function
'''
def word_status(grid, x, y, length, direction, mapping):
	xdim, ydim = get_dims(grid)
	status = [None for _ in xrange(length)]
	if direction == 'down':
		for y1 in xrange(y, y + length):
			if grid[x][y1] != ' ':
				status[y1 - y] = ('filled',)
				continue
			xc, yc, lc = mapping[(x, y1, 'across')]
			if is_missing_one_letter(grid, xc, yc, x, y1, lc, 'across'):
				left = extract_word_from_grid(grid, xc, yc, x - xc, 'across')
				right = extract_word_from_grid(grid, x + 1, yc, lc - (x - xc) - 1, 'across')
				status[y1 - y] = ('last', left, right)
				continue

			left = True if x > 0 and not(grid[x - 1][y1] == ' ' or grid[x - 1][y1] == '*') else False
			right = True if x < xdim - 1 and not(grid[x + 1][y1] == ' ' or grid[x + 1][y1] =='*') else False
			if left and right:
				status[y1 - y] = ('both', grid[x - 1][y1], grid[x + 1][y1])
			elif left:
				status[y1 - y] = ('left', grid[x - 1][y1])
			elif right:
				status[y1 - y] = ('right', grid[x + 1][y1])
			else:
				status[y1 - y] = ('unconstrained',)
	else:
		for x1 in xrange(x, x + length):
			if grid[x1][y] != ' ':
				status[x1 - x] = ('filled',)
				continue
			xc, yc, lc = mapping[(x1, y, 'down')]
			if is_missing_one_letter(grid, xc, yc, x1, y, lc, 'down'):
				above = extract_word_from_grid(grid, xc, yc, y - yc, 'down')
				below = extract_word_from_grid(grid, xc, y + 1, lc - (y - yc) - 1, 'down')
				status[x1 - x] = ('last', above, below)
				continue

			above = True if y > 0 and not(grid[x1][y - 1] == ' ' or grid[x1][y - 1] == '*') else False
			below = True if y < ydim - 1 and not(grid[x1][y + 1] == ' ' or grid[x1][y + 1] == '*') else False
			if above and below:
				status[x1 - x] = ('both', grid[x1][y - 1], grid[x1][y + 1])
			elif above:
				status[x1 - x] = ('above', grid[x1][y - 1])
			elif below:
				status[x1 - x] = ('below', grid[x1][y + 1])
			else:
				status[x1 - x] = ('unconstrained',)
	return status


'''
Words must be at least 3 letters long and contain characters 'A' - 'Z'
'''
def is_valid_word(word):
	if len(word) < 3:
		return False
	for c in word:
		if c not in string.uppercase:
			return False
	return True

def get_dictionary(file_name):
	words = {}
	clues = {}
	with open(file_name) as f:
		for line in f:
			clue, word = line.split('\t')
			word = word[:len(word) - 1]
			if '-Across' in clue or '-Down' in clue:
				continue
			if not is_valid_word(word):
				continue
			if len(word) not in words:
				words[len(word)] = {}
				words[len(word)][word] = 1
			elif word not in words[len(word)]:
				words[len(word)][word] = 1
			else:
				words[len(word)][word] += 1

			if word not in clues:
				clues[word] = clue
	return words, clues

def compare(a, b):
	if a[1] > b[1]:
		return -1
	else:
		return 1

'''
Returns a l x d array of lists of words, where l is the word length and d is the
difficulty level, as well as a dictionary of (word, clue) pairs
'''
def gen_word_dict(file_name, difficulty_levels):
	words, clues = get_dictionary(file_name)
	max_len = max(words.keys())
	word_dict = [[[] for _ in xrange(difficulty_levels)] for _ in xrange(max_len + 1)]
	for k in words:
		word_list = [(w, words[k][w]) for w in words[k]]
		sorted_words = sorted(word_list, cmp=compare)
		cutoff = len(words[k]) / difficulty_levels	
		
		for i in xrange(difficulty_levels):
			for j in xrange(i * cutoff, (i + 1) * cutoff):
				word, _ = sorted_words[j]
				word_dict[k][i].append(word)
	return word_dict, clues



'''
construct a dictionary of standard 2-gram frequencies
'''
def build_2grams(word_dict):
	pairs = {}
	for n1 in list(string.ascii_uppercase):
		for n2 in list(string.ascii_uppercase):
			pairs[n1 + n2] = 0

	count = 0
	for length in word_dict:
		for difficulty in length:
			for word in difficulty:
				for i in xrange(1, len(word) - 2):
					pairs[word[i:i + 2]] += 1
					count += 1

	for key in pairs:
		pairs[key] = float(pairs[key]) / count
	return pairs


'''
construct a dictionary of standard 3-gram frequencies
'''
def build_3grams(word_dict):
	pairs = {}
	for n1 in list(string.ascii_uppercase):
		for n2 in list(string.ascii_uppercase):
			for n3 in list(string.ascii_uppercase):
				pairs[n1 + n2 + n3] = 0

	count = 0
	for length in word_dict:
		for difficulty in length:
			for word in difficulty:
				for i in xrange(len(word) - 3):
					pairs[word[i:i + 3]] += 1
					count += 1

	for key in pairs:
		pairs[key] = float(pairs[key]) / count
	return pairs


'''
construct a dictionary of 2-gram frequencies
for the starts of words
'''
def build_2starts(word_dict):
	pairs = {}
	for n1 in list(string.ascii_uppercase):
		for n2 in list(string.ascii_uppercase):
			pairs[n1 + n2] = 0

	count = 0
	for length in word_dict:
		for difficulty in length:
			for word in difficulty:
				pairs[word[:2]] += 1
				count += 1

	for key in pairs:
		pairs[key] = float(pairs[key]) / count
	return pairs

'''
construct a dictionary that takes (x, y, direction)
tuples and returns the identifying (x1, y1, length)
of the word
'''
def gen_coord_to_word_mapping(grid):
	mapping = {}
	xdim, ydim = get_dims(grid)
	y = 0
	while y < ydim:
		x = 0
		while x < xdim:
			if grid[x][y] == '*':
				x += 1
				continue
			x1, y1 = x, y
			length = 0
			while x < xdim and grid[x][y] != '*':
				length += 1
				x += 1
			x, y = x1, y1
			while x < xdim and grid[x][y] != '*':
				mapping[(x, y, 'across')] = (x1, y1, length)
				x += 1
		y += 1

	x = 0
	while x < xdim:
		y = 0
		while y < ydim:
			if grid[x][y] == '*':
				y += 1
				continue
			x1, y1 = x, y
			length = 0
			while y < ydim and grid[x][y] != '*':
				length += 1
				y += 1
			x, y = x1, y1
			while y < ydim and grid[x][y] != '*':
				mapping[(x, y, 'down')] = (x1, y1, length)
				y += 1
		x += 1

	return mapping

'''
open a .txt file containing a blank grid as an array
'''
def open_grid(file_name):
	xdim, ydim, _= map(int, re.findall(r'\d+', file_name))
	grid = [[None for _ in xrange(ydim)] for _ in xrange(xdim)]
	with open(file_name) as f:
		for y, line in enumerate(f):
			for x, c in enumerate(line):
				if c == '\n':
					continue
				val = ' ' if c == ' ' else '*'
				grid[x][y] = val
	return grid

'''
Generate an array of all positions in the grid
'''
def gen_blanks(grid):
	blanks = []
	xdim, ydim = get_dims(grid)
	y = 0
	while y < ydim:
		x = 0
		while x < xdim:
			if grid[x][y] == '*':
				x += 1
				continue
			x1, y1 = x, y
			length = 0
			while x < xdim and grid[x][y] != '*':
				length += 1
				x += 1
			blanks.append((x1, y1, length, 'across'))
		y += 1

	x = 0
	while x < xdim:
		y = 0
		while y < ydim:
			if grid[x][y] == '*':
				y += 1
				continue
			x1, y1 = x, y
			length = 0
			while y < ydim and grid[x][y] != '*':
				length += 1
				y += 1
			blanks.append((x1, y1, length, 'down'))
		x += 1

	return blanks

'''
Generate a dictionary indexed by (x, y, direction) that returns
a set of all other words either parallel and adjacents to it or
intersecting it
'''
def gen_adjacents(grid, mapping, blanks):
	xdim, ydim = get_dims(grid)
	adjacents = {}
	for word in blanks:
		x, y, length, direction = word
		adjacents[(x, y, length, direction)] = set()
		if direction == 'down':
			for y1 in xrange(y, y + length):
				if x > 0 and grid[x - 1][y1] == ' ':
					xp, yp, lp = mapping[(x - 1, y1, 'down')]
					adjacents[(x, y, length, direction)].add((xp, yp, lp, 'down'))
				if x < xdim - 1 and grid[x + 1][y1] == ' ':
					xp, yp, lp = mapping[(x + 1, y1, 'down')]
					adjacents[(x, y, length, direction)].add((xp, yp, lp, 'down'))
				xc, yc, lc = mapping[(x, y1, 'across')]
				adjacents[(x, y, length, direction)].add((xc, yc, lc, 'across'))
		else:
			for x1 in xrange(x, x + length):
				if y > 0 and grid[x1][y - 1] == ' ':
					xp, yp, lp = mapping[(x1, y - 1, 'across')]
					adjacents[(x, y, length, direction)].add((xp, yp, lp, 'across'))
				if y < ydim - 1 and grid[x1][y + 1] == ' ':
					xp, yp, lp = mapping[(x1, y + 1, 'across')]
					adjacents[(x, y, length, direction)].add((xp, yp, lp, 'across'))
				xc, yc, lc = mapping[(x1, y, 'down')]
				adjacents[(x, y, length, direction)].add((xc, yc, lc, 'down'))

	return adjacents

'''
Return the most constrained word by fraction of letters
already filled, using the longer word to break ties 
'''
def get_most_constrained(grid, adjacents, longest):
	for word in longest:
		x, y, l, d = word
		if is_missing_letter(grid, x, y, l, d):
			return word
	max_frac_filled = 0.
	maxx, maxy, maxl, maxd = -1, -1, 0, ''
	for word in adjacents:
		x, y, l, d = word
		num_filled = 0
		if d == 'down':
			for y1 in xrange(y, y + l):
				if grid[x][y1] != ' ':
					num_filled += 1
			frac = float(num_filled) / l
			if max_frac_filled < frac < 1.:
				max_frac_filled = frac
				maxx, maxy, maxl, maxd = x, y, l, d
			elif max_frac_filled == frac and maxl < l:
				max_frac_filled = frac
				maxx, maxy, maxl, maxd = x, y, l, d
		else:
			for x1 in xrange(x, x + l):
				if grid[x1][y] != ' ':
					num_filled += 1
			frac = float(num_filled) / l
			if max_frac_filled < frac < 1.:
				max_frac_filled = frac
				maxx, maxy, maxl, maxd = x, y, l, d
			elif max_frac_filled == frac and maxl < l:
				max_frac_filled = frac
				maxx, maxy, maxl, maxd = x, y, l, d
	return maxx, maxy, maxl, maxd

'''
Generate a sampling distribution given an array of skewing factors
'''
def gen_distribution(skewing):
	dist = [[] for _ in xrange(len(skewing))]
	for x in xrange(len(skewing)):
		for i, y in enumerate(skewing[x]):
			dist[x].extend([i] * int(y * 100))
	return dist 

'''
Generate a list of the longest word(s)'s positions
'''
def get_longest_words(adjacents):
	max_len = 0
	longest = []
	for word in adjacents:
		x, y, l, d = word
		if l > max_len:
			max_len = l
			longest = [(x, y, l, d)]
		elif l == max_len:
			longest.append((x, y, l, d))
	return longest

'''
Return a new grid with the numbers labeled in the canonical crossword way
'''
def fill_in_numbers(grid):
	new_grid = copy.deepcopy(grid)
	counter = 1
	xdim, ydim = get_dims(grid)
	for y in xrange(ydim):
		for x in xrange(xdim):
			if new_grid[x][y] != '*' and (x == 0 or y == 0 or new_grid[x - 1][y] == '*' or new_grid[x][y - 1] == '*'):
				new_grid[x][y] = counter
				counter += 1

	return new_grid


def usage():
	usage_str = \
	"\nUSAGE:\n\n\tpython crossword.py [-dim D] [-grid PATH1] [-difficulty L] [-dictionary PATH2] [-display] [-export_grid PATH3] [-export_solution PATH4]\n\
	\n\
	\n\
	Either the [-dim D] flag must be provided with a dimension for the grid, or [-grid PATH1] must be provided\n\
	with PATH1 being a txt file grid, as is produced by the blank_grid_extractor script.\n\
	\n\
	Optional:\n\
	\n\
	[-difficulty L] specifices the difficuly of the puzzle, 0 <= L <= 4, 4 being the hardest. Default value is 1.\n\
	\n\
	[-dictionary PATH2], if provided, must point to a text file containing words and clues, of the form \n\n\
	\t\tclue<tab>word\n\n\
	one on each line.\n\
	\n\
	[-display] means print the grid at each iteration as it is being filled in. An error will be thrown if\n\
	the terminal is too small to display the full grid\n\
	\n\
	[-export_grid PATH3], if provided, indicates file name for the blank grid and clues to be outputted to.\n\
	\n\
	[-export_solution PATH4], if provided, indicates file name for the solution to be outputted to.\n"

	print usage_str

'''
Export a blank, numbered grid and its clueing
'''
def export_grid(numbered_grid, blanks, filled_grid, clues, path):

	def compare(a, b):
		xa, ya, _, _ = a
		xb, yb, _, _ = b
		a_num = numbered_grid[xa][ya]
		b_num = numbered_grid[xb][yb]
		if a_num < b_num:
			return -1
		else:
			return 1

	xdim, ydim = get_dims(numbered_grid)
	with open(path, 'w') as f:
		f.write(' ')
		for x in xrange(xdim):
			f.write('--- ')
		f.write('\n')

		for y in xrange(ydim):
			f.write('|')
			for x in xrange(xdim):
				if numbered_grid[x][y] == '*':
					f.write('***|')
				elif numbered_grid[x][y] == ' ':
					f.write('   |')
				else:
					num = str(numbered_grid[x][y])
					f.write(num.ljust(3) + '|')
			f.write('\n|')
			for x in xrange(xdim):
				if numbered_grid[x][y] == '*':
					f.write('***|')
				else:
					f.write('   |')
			f.write('\n ')
			for x in xrange(xdim):
				f.write('--- ')
			f.write('\n')

		f.write('\n\n\n\n\n')
		f.write('Across\n\n')

		acrosses = sorted([b for b in blanks if b[3] == 'across'], cmp=compare)
		downs = sorted([b for b in blanks if b[3] == 'down'], cmp=compare)
		for blank in acrosses:
			x, y, l, d = blank
			num = numbered_grid[x][y]
			word = extract_word_from_grid(filled_grid, x, y, l, d)
			clue = clues[word]
			f.write(str(num) + '. ' + clue + '\n')

		f.write('\n\n\nDown\n\n')

		for blank in downs:
			x, y, l, d = blank
			num = numbered_grid[x][y]
			word = extract_word_from_grid(filled_grid, x, y, l, d)
			clue = clues[word]
			f.write(str(num) + '. ' + clue + '\n')

		f.write('\n')


'''
Export the solution grid
'''
def export_solution(solution_grid, file_path):
	xdim, ydim = get_dims(solution_grid)
	with open(file_path, 'w') as f:
		for y in xrange(ydim):
			for x in xrange(xdim):
				f.write(solution_grid[x][y])
			f.write('\n')
