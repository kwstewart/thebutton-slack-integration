import datetime

# Class for keeping track of button statistics
class thebutton_stats:
	
	start_time = 0
	
	def getColor(self, color):
		return self.colors[color]
		
	def setColor(self, color, value):
		self.colors[color] = value

	def incColor(self, color, amount = 1):
		self.setColor(color,self.getColor(color) + amount)
		
	def getTotal(self):
		return self.colors["red"] + self.colors["orange"] + self.colors["yellow"] + self.colors["green"] + self.colors["blue"] + self.colors["purple"]
		
	def __init__(self):
		self.start_time = datetime.datetime.now().strftime('%s')
		self.colors = {
			"red": 0,
			"orange": 0,
			"yellow": 0,
			"green": 0,
			"blue": 0,
			"purple": 0
		}	

