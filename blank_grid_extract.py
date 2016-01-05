from PIL import Image
import os, re

'''
Convert image files of blank crossword puzzles in the /grid_images folder into
.txt files in the /grids folder. Each file must be named as MxN-i.gif, where M and
N are the dimensions of the grid and i is the index of that size (for duplicate sizes). 

Works by checking the pixels from the squares for a white or black RGB value

Saved as a .txt file where spaces denote blank squares as '*' characters denote black
squares
'''


def main():
	sub_dir = 'grids'
	try:
	    os.mkdir(sub_dir)
	except Exception:
	    pass

	print "Creating..."
	for name in [os.path.join('grid_images', f) for f in os.listdir('grid_images') if os.path.isfile(os.path.join('grid_images', f)) and f[0] != '.']:
		im = Image.open(name)
		im = im.convert('RGB')
		xdim, ydim, _ = map(int, re.findall(r'\d+', name))
		xpix, ypix = im.size
		xstepsize = xpix / xdim
		ystepsize = ypix / ydim
		xstart = xstepsize / 2
		ystart = ystepsize / 2
		new_name = re.search(r'grid_images/([0-9a-z,-]+).*', name).group(1)
		outfile = os.path.join('grids', new_name + '.txt')
		print outfile
		with open(outfile, 'w+') as out:
			for y in xrange(ystart, ypix, ystepsize):
				for x in xrange(xstart, xpix, xstepsize):
					r, g, b = im.getpixel((x, y))
					if r < 10:
						out.write('*')
					else:
						out.write(' ')
				out.write('\n')



if __name__ == '__main__':
	main()



