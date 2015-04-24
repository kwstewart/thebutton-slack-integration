import websocket
import datetime
import requests
import json
import re

import thebutton_stats
import thebutton_config

class thebutton_slack:
	
	logFile = thebutton_config.logFile
	
	# URL to your Slack Incoming Webhook
	slackURL =  thebutton_config.slackURL
	
	# Path to the directory that contains the flair images 
	imagePath = thebutton_config.imagePath
	
	# URL to the button WSS feed 
	buttonWSS = "";

	# Keep track of the lowest time
	highScore = 60
	
	# Keep track of the previous button data
	lastData = {}
	
	# Keep track of running statistics
	#overallStats = thebutton_stats.thebutton_stats()
	hourlyStats = thebutton_stats.thebutton_stats()
	
	colorNames = ["purple","blue","green","yellow","orange","red"]

	# Hex colors for the flairs
	hexColors = {
		"purple" : "#820080",
		"blue" : "#0083C7",
		"green" : "#02BE01",
		"yellow" : "#E5D900",
		"orange" : "#E59500",
		"red" : "#E50000",
	}

	def log(self, data):
		self.logFile.write(data+"\n")
		self.logFile.flush()

	def get_highscore(self):		
		# Load the highscore from the file 
		with open ('highscore.txt','r') as hsFile: 
			return int(hsFile.read().replace('\n',''))

	def set_highscore(self, s):
		# Write the new highscore to the file
		self.highScore = s
		hsFile = open('highscore.txt','w')
		hsFile.write(str(s))
		hsFile.close()

	def get_wss_url(self):
		self.log("### getting new wss url ###")
		r = requests.get("http://cors-unblocker.herokuapp.com/get?url=https%3A%2F%2Fwww.reddit.com%2Fr%2Fthebutton")
		wssUrl = re.search(r'wss://wss\.redditmedia\.com\/thebutton\?h=[^"]*',r.text)
		u = wssUrl.group(0)
		self.log(u)
		return u
	
	# Function to run when a message is received
	def on_message(self, ws, message):

		# Parse the message data into an object
		m = json.loads(message)
		
		# The first message doesn't have anything to compare with 
		if (not self.lastData):
			self.lastData = m
	
		# Check dirty presser id is greater than on the last message (means it was pressed)
		if(m['payload']['participants_text'] > self.lastData['payload']['participants_text']):
			
			# Seconds left on the clock when the button was pressed
			s = int(self.lastData['payload']['seconds_left'])
			
			# Determine the color
			if(s >= 52):
				c = "purple"
			elif(s < 52 and s >=42):
				c = "blue"
			elif(s < 42 and s >=32):
				c = "green"
			elif(s < 32 and s >=22):
				c = "yellow"
			elif(s < 22 and s >=12):
				c = "orange"
			elif(s < 12 and s >=1):
				c = "red"
	 
	 		# Assign the text and stuff based on color
			n = c.capitalize()
			hexColor = self.hexColors[c]
			i = self.imagePath+c+"-flair.png"
			self.hourlyStats.incColor(c)
			#self.overallStats.incColor(c)
	 
			# If its a new highscore, use Slack banner formatting
			if(s < self.highScore):				
				payload = {
					"text":"",
					"username":"filthiest yet! #"+self.lastData['payload']['participants_text'],
					"icon_url":i,
					"attachments": [
						{
							"fallback": "A new highscore of "+str(s)+"s has been set",
							"text": "New High Score of"+str(s)+'s'+" <!channel>",
							"title": str(s)+'s',
							"pretext": "",
							"color": hexColor
						}
					]
				}
				
				self.set_highscore(s)				
			
			# Just use the standard Slack message format for non high scores
			else:			
				payload = {
					"text": str(s)+"s", 
					"username":"filthy presser #"+self.lastData['payload']['participants_text'], 
					'icon_url':i
				}
			
			# Send the message to Slack
			r = requests.post(self.slackURL,data=json.dumps(payload))
		
		# Send hourly stats
		now = datetime.datetime.now()
		if(int(now.minute) == 0 and int(now.second) <= 1):
			
			# Get current total
			t = self.hourlyStats.getTotal()
			
			# If the total is 0, skip
			if(t > 0):
			
				payload = {
					'icon_url': self.imagePath+"statistics.png",
					'username':"button statistics",
					#"text":"<!channel> here are the hourly button statistics",
					"text":"here are the hourly button statistics",
					"attachments": [
						{
							"fallback": "total: "+str(t),
							"text": "total: "+str(t),
							"title": "",
							"pretext": "",
							"color": "#000000"
						}
					]
				}
				
				
				# Loop through each color's stats
				for color in self.colorNames:
					
					# Skip over the timestamp
					if color == "start_time":
						continue
					
					# Calculate percentage
					k = self.hourlyStats.colors[color]
					p = str(int(100 * k / t))
					
					payload["attachments"].append({
						"fallback": color+": "+str(k)+" ("+p+"%)",
						"text": str(k)+" ("+p+"%)",
						"title": "",
						"pretext": "",
						"color": self.hexColors[color]
					})
					
				# Send the message to Slack
				r = requests.post(self.slackURL,data=json.dumps(payload))
						
				# Reset hourlyStats
				self.hourlyStats = thebutton_stats.thebutton_stats()
	
		# Save this data to compare with on the next tick
		self.lastData = m
		
	
	# Function to run when there is a connection error
	def on_error(self,ws, error):
		self.log("error: "+"*"*10)
		self.log(error)
		self.log("*"*17)
	
	# Function to run when the connection closes
	def on_close(self, ws):
		self.log("### closed - attempting to reopen ###")
		self.buttonWSS = self.get_wss_url()
		self.init_connection()
		
	
	# Function to run when the connection opens
	def on_open(self,ws):
		self.log("### opening connection ###")
		def run(*args):
			st = "Hello %d" % i
			ws.send(st)
	
	def init_connection(self):	
		self.ws = websocket.WebSocketApp(self.buttonWSS,
				on_message = self.on_message,
				on_error = self.on_error,
				on_close = self.on_close)
				
		self.ws.on_open = self.on_open
		self.ws.run_forever()
	
	def __init__(self):		
		self.buttonWSS = self.get_wss_url()
		self.highScore = self.get_highscore()
		self.init_connection()
		

# Start the script
if __name__ == "__main__":
	tbs = thebutton_slack()
	