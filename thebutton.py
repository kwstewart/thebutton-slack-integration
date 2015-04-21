import websocket
import time
import requests
import json
import re
import logging
logging.basicConfig()


class thebutton_slack:
	
	# URL to your Slack Incoming Webhook
	slackURL =  "https://hooks.slack.com/services/XXXXXX/XXXXXX/XXXXXXXX"
	
	# Path to the directory that contains the flair images 
	imagePath = "http://path.to/the/directory/that/contains/the/flair/images/"
	
	# URL to the button WSS feed 
	buttonWSS = "";

	# Keep track of the lowest time
	highScore = 60
	
	# Keep track of the previous button data
	lastData = {}

	def get_highscore(self):		
		# Load the highscore from the file 
		with open ('highscore.txt','r') as hsFile: 
			return int(hsFile.read().replace('\n',''))

	def set_highscore(self, s):
		# Write the new highscore to the file
		self.highScore = s
		hsFile = open('highscore.txt','w')
		hsFile.write(str(s))

	def get_wss_url(self):
		print "### getting new wss url ###"
		r = requests.get("http://cors-unblocker.herokuapp.com/get?url=https%3A%2F%2Fwww.reddit.com%2Fr%2Fthebutton")
		wssUrl = re.search(r'wss://wss\.redditmedia\.com\/thebutton\?h=[^"]*',r.text)
		u = wssUrl.group(0)
		print u
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
			
			# Assign the text and color based on the number of seconds
			if(s >= 52):
				n = "Purple"
				hexColor = "#820080"
				i = self.imagePath+"purple-flair.png"
			elif(s < 52 and s >=42):
				n = "Blue"
				hexColor = "#0083C7"
				i = self.imagePath+"blue-flair.png"
			elif(s < 42 and s >=32):
				n = "Green"
				hexColor = "#02be01"
				i = self.imagePath+"green-flair.png"
			elif(s < 32 and s >=22):
				n = "Yellow"
				hexColor = "#E5D900"
				i = self.imagePath+"yellow-flair.png"
			elif(s < 22 and s >=12):
				n = "Orange"
				hexColor = "#e59500"
				i = self.imagePath+"orange-flair.png"
			elif(s < 12 and s >=1):
				n = "Red"
				hexColor = "#e50000"
				i = self.imagePath+"red-flair.png"
	 
			# If its a new highscore, use Slack banner formatting
			if(s < self.highScore):				
				payload = {"text":"",'username':"filthiest yet! #"+self.lastData['payload']['participants_text'],'icon_url':i,"attachments": [{"fallback": "A new highscore of "+str(s)+"s has been set","text": "New High Score of"+str(s)+'s'+" <!channel>","title": str(s)+'s',"pretext": "","color": hexColor}]}
				
				self.set_highscore(s)				
			
			# Just use the standard Slack message format for non high scores
			else:			
				payload = {'text':str(s)+'s', 'username':"filthy presser #"+self.lastData['payload']['participants_text'], 'icon_url':i}
			
			# Send the message to Slack
			r = requests.post(self.slackURL,data=json.dumps(payload))
	
		# Save this data to compare with on the next tick
		self.lastData = m
		
	
	# Function to run when there is a connection error
	def on_error(self,ws, error):
		print "error: "+"*"*10
		print error
		print "*"*17
	
	# Function to run when the connection closes
	def on_close(self, ws):
		print "### closed - attempting to reopen ###"
		self.buttonWSS = self.get_wss_url()
		self.init_connection()
		
	
	# Function to run when the connection opens
	def on_open(self,ws):
		print "### opening connection ###"
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
		



if __name__ == "__main__":
	tbs = thebutton_slack()
	