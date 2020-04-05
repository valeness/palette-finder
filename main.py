import json
import math

from PIL import Image, ImageEnhance, ImageDraw
from os import listdir
from os.path import isfile, join
import redis


class Palette():
	def __init__(self, image_name):
		self.img = ''
		self.data = ''
		self.height = 0
		self.width = 0
		self.colors = {}
		self.aggr = {}
		self.image_name = image_name
		self.distance_threshold = 120
		self.tile_size = 15

	def getImage(self, path):
		self.img = Image.open('/var/www/html/storage/app/public/images/' + path)
		enhancer = ImageEnhance.Contrast(self.img)
		# self.img = enhancer.enhance(1.2)

		# enhancer = ImageEnhance.Sharpness(self.img)
		# self.img = enhancer.enhance(1.05)

		enhancer = ImageEnhance.Brightness(self.img)
		# self.img = enhancer.enhance(1.05)

		# self.img.save('tmp_enhanced_image.png', 'PNG')

		self.height = self.img.height
		self.width = self.img.width
		self.data = self.img.load()

	def getColorDistance(self, c1, c2):
		r1 = c1[0]
		r2 = c2[0]

		g1 = c1[1]
		g2 = c2[1]

		b1 = c1[2]
		b2 = c2[2]

		r_diff = pow(r1 - r2, 2)
		g_diff = pow(g1 - g2, 2)
		b_diff = pow(b1 - b2, 2)

		distance = math.sqrt(r_diff + g_diff + b_diff)

		return distance


	def getPalette(self):

		trimmed_name = self.image_name.replace('.png', '').replace('.jpg', '').replace('.jpeg', '')

		if isfile('/var/www/html/storage/app/public/images/{0}_palette.png'.format(trimmed_name)):
			return False


		self.getImage(self.image_name)

		# Current Row and Column iteration
		row = 0
		column = 0

		# Tile Height/Width
		size = round(self.width / self.tile_size)
		print(size)

		# found tells whether or not we have iterated over all tiles
		found = False
		# current tile counter
		counter = 0

		new_colors = 0
		# while not found:

		#increment counter
		counter += 1

		# current x offset for tile
		column_offset = size * column

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

		self.colors = {}
		for color in self.aggr:
			existing_color = self.color_diff(color)
			white_distance = self.getColorDistance((255, 255, 255), color)
			black_distance = self.getColorDistance((0, 0, 0), color)
			if not existing_color and white_distance > 15 and black_distance > 15:
				print(existing_color)
				# If the color is not in our dict, init the count to 1
				# otherwise increment
				if not color in self.colors:
					self.colors[color] = 1
				else:
					self.colors[color] += 1
			elif white_distance > 15 and black_distance > 15:
				self.colors[existing_color] += 1

		self.colors = self.sortDict(self.colors)
		print(self.colors)

		if len(self.colors) < 5 and self.distance_threshold > 10:
			self.distance_threshold -= 10
			self.colors = {}
			return self.getPalette()

		# f = open('newimage.png', 'w')

		im = Image.new('RGB', (250, 50))
		square_size = math.floor(self.width / 15)
		offset = 0
		for color in self.colors:
			print(color[0])
			draw = ImageDraw.Draw(self.img)
			draw.rectangle([(offset, self.height - square_size), (square_size + offset, self.height)], fill=color[0])
			offset += square_size
		# im.save('{0}_palette.png'.format(trimmed_name), 'PNG')
		self.img.save('/var/www/html/storage/app/public/images/{0}_palette.png'.format(trimmed_name))
		self.img.close()


	def color_diff(self, main_color):

		for color, score in self.colors.items():
			distance = self.getColorDistance(main_color, color)
			if(distance < self.distance_threshold):
				return color
		return False


	def diff(self, ins):
		print(ins[0])

	def getHexCode(self, rgb):
		shex = '{0:02x}{1:02x}{2:02x}'.format(rgb[0], rgb[1], rgb[2])
		return shex

	def sortDict(self, dicto):
		return sorted(dicto.items(), key=lambda x: x[1], reverse=True)

# onlyfiles = [f for f in listdir('source_images') if isfile(join('source_images', f))]
#
# for filename in onlyfiles:
# 	print(filename)
#
# 	palette = Palette(filename)
# 	palette.getPalette()


conn = redis.Redis(host='localhost', port=6379, db=0)

while True:
	try:

		packed = conn.blpop('laravel_database_queues:getimagepalette', 30)

		if not packed:
			continue

		payload = json.loads(packed[1])
		job = payload.get('job')
		file_path = payload.get('file_path')

		print(job, file_path)
		palette = Palette(file_path)
		palette.getPalette()

	except KeyboardInterrupt:
		break
