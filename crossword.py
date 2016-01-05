import string, random, copy, re, sys, curses, os, time
from utils import *


'''
Score a word based on the metrics found in word_status
'''
def score_word(word, grid, x, y, direction, status, n2starts, n2grams, n3grams, word_dict, difficulty):
	score = 1.0
	if direction == 'down':
		for y1 in xrange(y, y + len(word)):
			condition = status[y1 - y]
			if condition[0] == 'filled':
				if word[y1 - y] != grid[x][y1]:
					return 0.0
			elif condition[0] == 'last':
				crossing = condition[1] + word[y1 - y] + condition[2]
				if crossing not in word_dict[len(crossing)][difficulty]:
					return 0.0
			elif condition[0] == 'first2':
				bigram = condition[1] + word[y1 - y] + condition[2]
				if n2starts[bigram] == 0.0:
					return 0.0
				score += n2starts[bigram]
			elif condition[0] == 'both':
				trigram = condition[1] + word[y1 - y] + condition[2]
				if n3grams[trigram] == 0.0:
					return 0.0
				score += n3grams[trigram]
			elif condition[0] == 'left':
				bigram = condition[1] + word[y1 - y]
				if n2grams[bigram] == 0.0:
					return 0.0
				score += n2grams[bigram]
			elif condition[0] == 'right':
				bigram = word[y1 - y] + condition[1]
				if n2grams[bigram] == 0.0:
					return 0.0
				score += n2grams[bigram]
	else:
		for x1 in xrange(x, x + len(word)):
			condition = status[x1 - x]
			if condition[0] == 'filled':
				if word[x1 - x] != grid[x1][y]:
					return 0.0
			elif condition[0] == 'last':
				crossing = condition[1] + word[x1 - x] + condition[2]
				if crossing not in word_dict[len(crossing)][difficulty]:
					return 0.0
			elif condition[0] == 'first2':
				bigram = condition[1] + word[x1 - x] + condition[2]
				if n2starts[bigram] == 0.0:
					return 0.0
				score += n2starts[bigram]
			elif condition[0] == 'both':
				trigram = condition[1] + word[x1 - x] + condition[2]
				if n3grams[trigram] == 0.0:
					return 0.0
				score += n3grams[trigram]
			elif condition[0] == 'above':
				bigram = condition[1] + word[x1 - x]
				if n2grams[bigram] == 0.0:
					return 0.0
				score += n2grams[bigram]
			elif condition[0] == 'below':
				bigram = word[x1 - x] + condition[1]
				if n2grams[bigram] == 0.0:
					return 0.0
				score += n2grams[bigram]
	return score



'''
Recursively fill in the grid
'''
def solve(grid, words_used, mapping, word_dict, n2starts, n2grams, n3grams, adjacents, i, difficulty, distribution, longest, console):
	if console != None:
		console_print(grid, console, i)

	# get the location of the word to be filled in 
	x, y, length, direction = get_most_constrained(grid, adjacents, longest)
	
	# all filled in 
	if x == -1:
		return grid

	original_state = extract_word_from_grid(grid, x, y, length, direction)
	# unconstrained, so randomly pick a word of the right length and hardness
	if is_unconstrained(grid, x, y, length, direction):
		tried = 0
		hardness = random.choice(distribution[difficulty])
		cutoff = max(100, int(0.3 * len(word_dict[length][hardness])))
		while tried < cutoff:
			try_word = word_dict[length][hardness][random.randint(0, len(word_dict[length][hardness]) - 1)]
			if try_word in words_used:
				continue
			add_word_to_grid(try_word, grid, x, y, direction)
			words_used[try_word] = 1
			tried += 1
			result = solve(grid, words_used, mapping, word_dict, n2starts, n2grams, n3grams, adjacents, i + 1, difficulty, distribution, longest, console)
			# found a solution
			if not isinstance(result, tuple):
				return result
			# check if we should jump back
			elif result not in adjacents[(x, y, length, direction)] and i > 0:
				words_used.pop(try_word, None)
				add_word_to_grid(original_state, grid, x, y, direction)
				return result
			words_used.pop(try_word, None)
	# otherwise, score the words of the right length and try them in that order
	else:
		def compare_scores(a, b):
			if a[1] > b[1]:
				return -1
			else:
				return 1

		status = word_status(grid, x, y, length, direction, mapping)
		hardness = random.choice(distribution[difficulty])
		rankings = []
		for word in word_dict[length][hardness]:
			score = score_word(word, grid, x, y, direction, status, n2starts, n2grams, n3grams, word_dict, hardness)
			if score > 0.0:
				rankings.append((word, score))
		rankings = sorted(rankings, cmp=compare_scores)
		cutoff = max(100, int(0.3 * len(rankings)))
		rankings = rankings[:cutoff]
		for choice in rankings:
			try_word = choice[0]
			add_word_to_grid(try_word, grid, x, y, direction)
			words_used[try_word] = 1
			result = solve(grid, words_used, mapping, word_dict, n2starts, n2grams, n3grams, adjacents, i + 1, difficulty, distribution, longest, console)
			# found a solution 
			if not isinstance(result, tuple):
				return result
			# check if we should jump back 
			elif result not in adjacents[(x, y, length, direction)]:
				words_used.pop(try_word, None)
				add_word_to_grid(original_state, grid, x, y, direction)
				return result
			words_used.pop(try_word, None)

	add_word_to_grid(original_state, grid, x, y, direction)
	return (x, y, length, direction)



def main():
	dimension = -1
	grid_path = ''
	difficulty = 2
	dictionary_path = ''
	display = False
	export_grid_path = ''
	export_solution_path = ''

	arg_index = 1
	while arg_index < len(sys.argv):
		if sys.argv[arg_index] == '-dim':
			if arg_index + 1 == len(sys.argv) or not isinstance(int(sys.argv[arg_index + 1]), int):
				usage()
				exit(1)
			else:
				if grid_path != '':
					usage()
					exit(1)
				dimension = int(sys.argv[arg_index + 1])
				arg_index += 2
		elif sys.argv[arg_index] == '-grid':
			if arg_index + 1 == len(sys.argv) or dimension != -1:
				usage()
				exit(1)
			else:
				grid_path = sys.argv[arg_index + 1]
				if not os.path.isfile(grid_path):
					usage()
					exit(1)
				arg_index += 2
		elif sys.argv[arg_index] == '-difficulty':
			if arg_index + 1 == len(sys.argv) or not isinstance(int(sys.argv[arg_index + 1]), int):
				usage()
				exit(1)
			else:
				difficulty = int(sys.argv[arg_index + 1])
				if difficulty < 0 or difficulty > 4:
					usage()
					exit(1)
				arg_index += 2
		elif sys.argv[arg_index] == '-dictionary':
			if arg_index + 1 == len(sys.argv) or not os.path.isfile(sys.argv[arg_index + 1]):
				usage()
				exit(1)
			else:
				dictionary_path = sys.argv[arg_index + 1]
				arg_index += 2
		elif sys.argv[arg_index] == '-display':
			display = True
			arg_index += 1
		elif sys.argv[arg_index] == '-export_grid':
			if arg_index + 1 == len(sys.argv):
				usage()
				exit(1)
			else:
				export_grid_path = sys.argv[arg_index + 1]
				arg_index += 2
		elif sys.argv[arg_index] == '-export_solution':
			if arg_index + 1 == len(sys.argv):
				usage()
				exit(1)
			else:
				export_solution_path = sys.argv[arg_index + 1]
				arg_index += 2
		else:
			usage()
			exit(1)



	if dimension != -1:
		grid_path = 'grids/' + str(dimension) + 'x' + str(dimension) + '-0.txt'
		if not os.path.isfile(grid_path):
			print "No grid found for given dimension", dimension
			exit(1)
		grid = open_grid(grid_path)
	elif grid_path != '':
		grid = open_grid(grid_path)
	else:
		usage()
		exit(1)

	console = None
	if display:
		stdscr = curses.initscr()
		console = curses.newpad(100, 100)
		for y in range(0, 100):
			for x in range(0, 100):
				try:
					console.addch(y, x, ord(' '))
				except curses.error:
					pass
	else:
		console = None



	# skewing[0] is the skewing for difficulty 0
	skewing = 	[[0.8, 0.15, .05, 0.0, 0.0], \
				[0.10, 0.7, 0.10, 0.075, 0.025], \
				[0.1, 0.05, 0.7, 0.05, 0.05], \
				[0.05, 0.05, 0.1, 0.7, 0.1], \
				[0.0, 0.05, 0.15, 0.2, 0.6]]

	num_difficulty_levels = 5

	if dictionary_path == '':
		dictionary_path = 'dictionaries/main_dict.txt'
	grid = open_grid(grid_path)	
	words_used = {}
	blanks = gen_blanks(grid)
	mapping = gen_coord_to_word_mapping(grid)
	word_dict, clues = gen_word_dict(dictionary_path, num_difficulty_levels)
	n2grams = build_2grams(word_dict)
	n3grams = build_3grams(word_dict)
	n2starts = build_2starts(word_dict)
	adjacents = gen_adjacents(grid, mapping, blanks)
	distribution = gen_distribution(skewing)
	longest = get_longest_words(adjacents)
	_, _, l, _ = longest[0]
	dim = max(get_dims(grid))
	if float(l) / dim < 0.75:
		longest = []

	numbered_grid = fill_in_numbers(grid)


	if console != None:
		message = "Words filled: "
		xdim, ydim = get_dims(grid)
		for x in xrange(len(message)):
			try:
				console.addch(3, x + 5, ord(message[x]))
			except curses.error:
				pass

		console.refresh(0, 0, 1, 0, ydim + 11, 99)

	solution = solve(grid, words_used, mapping, word_dict, n2starts, n2grams, \
					n3grams, adjacents, 0, difficulty, distribution, longest, console)
	
	if export_grid_path != '':
		export_grid(numbered_grid, blanks, solution, clues, export_grid_path)

	if export_solution_path != '':
		export_solution(solution, export_solution_path)

	if console != None:
		message = "Press any key to exit"
		for x in xrange(len(message)):
			try:
				console.addch(ydim + 10, x + 5, ord(message[x]))
			except curses.error:
				pass

		console.refresh(0, 0, 1, 0, ydim + 11, 99)
		console.getch()
		if console != None:
			curses.nocbreak()
			stdscr.keypad(False)
			curses.echo()
			curses.endwin()




if __name__ == '__main__':
	main()

