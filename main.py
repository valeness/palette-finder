from PIL import Image
from time import sleep

class Palette():
	def __init__(self):
		self.img = ''
		self.data = ''
		self.height = 0
		self.width = 0
		self.colors = {}
		self.aggr = {}

	def getImage(self, path):
		self.img = Image.open(path)
		self.height = self.img.height
		self.width = self.img.width
		self.data = self.img.load()

	def getPalette(self):
		self.getImage('canyon.png')

		# Current Row and Column iteration
		row = 0
		column = 0

		# Tile Height/Width
		size = 47

		# found tells wether or nto we have iterated over all tiles
		found = False
		# current tile counter
		counter = 0

		while not found:

			#increment counter
			counter += 1

			# current x offset for tile
			column_offset = size * column

			# iterate over x/y pixels of image
			for x in range(column_offset, column_offset + size):

				# current y ofset for tile
				row_offset = size * row
				for y in range(row_offset, row_offset + size):

					# if self.data[(x, y)] throws an error, it must mean we are outside the bounds of the image
					# such as a tile not being even and exceeding the width
					try:
						color = self.data[(x, y)]
					except:
						break

					# If the color is not in our dict, init the count to 1
					# otherwise increment
					if not color in self.colors:
						self.colors[color] = 1
					else:
						self.colors[color] += 1

			# print('Tile #: ', counter)

			# Determine the top color of the current tile
			# And increment the "score" for the tile like we do for individual pixels above
			top_color = self.sortDict(self.colors)[0]
			if(top_color[0] not in self.aggr):
				self.aggr[top_color[0]] = 1
			else:
				self.aggr[top_color[0]] += 1

			# reset our colors list since each new tile makes a new top color
			# If you don't refresh the colors dict, it becomes VERY slow
			self.colors = {}

			# shift our column
			column += 1

			# If this is the last column, set the column to 0 and shift down a row
			if(column_offset + size >= self.width):
				column = 0
				row += 1
				print('ROW DONE')

			# If this is the final row, then break out of loop so we can determine the final palette
			if(row_offset + size >= self.height):
				print('WE ARE FINISHED')
				found = True

		top = self.sortDict(self.aggr)
		for i in top:
			# Get Difference from sum of other numbers
			# Here we will determine the "distance" of the color from the rest 
			# by summing up the red, green, and blue values respecitvely
			# Then we find the difference from the sum, and score that color on total distance
			# We then select the top 6 most unique colors



	def getHexCode(self, rgb):
		shex = '{0:02x}{1:02x}{2:02x}'.format(rgb[0], rgb[1], rgb[2])
		return shex

	def sortDict(self, dicto):
		return sorted(dicto.items(), key=lambda x: x[1], reverse=True)

palette = Palette()
palette.getPalette()