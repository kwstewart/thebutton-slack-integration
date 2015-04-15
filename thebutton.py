import websocket
import time
import requests
import json
import logging
logging.basicConfig()

####               ####
#### Configuration ####
####               ####

# URL to your Slack Incoming Webhook
slackURL =  "https://hooks.slack.com/services/XXXXXX/XXXXXX/XXXXXXXX"

# Path to the directory that contains the flair images 
imagePath = "http://path.to/the/directory/that/contains/the/flair/images/"

# URL to the button WSS feed
buttonWSS = "wss://wss.redditmedia.com/thebutton?h=XXXXXXX&e=XXXXXXX"





# Load the highscore from the file 
with open ('highscore.txt','r') as hsFile: 
	highScore =int(hsFile.read().replace('\n',''))

# Keep track of the previous data
lastData = {}


# Function to run when a message is received
def on_message(ws, message):

	# Pull in the global variables
	global buttonWSS, slackURL, imagePath, userToAlert, lastData, highScore

	# Parse the message data into an object
	m = json.loads(message)

	# The first message doesn't have anything to compare with 
	if (not lastData):
		lastData = m

	# Check dirty presser id is greater than on the last message (means it was pressed)
	if(m['payload']['participants_text'] > lastData['payload']['participants_text']):
		
		# Seconds left on the clock when the button was pressed
		s = int(lastData['payload']['seconds_left'])
		
		# Assign the text and color based on the number of seconds
		if(s >= 52):
			n = "Purple"
			hexColor = "#820080"
			i = imagePath+"purple-flair.png"
		elif(s < 52 and s >=42):
			n = "Blue"
			hexColor = "#0083C7"
			i = imagePath+"blue-flair.png"
		elif(s < 42 and s >=32):
			n = "Green"
			hexColor = "#02be01"
			i = imagePath+"green-flair.png"
		elif(s < 32 and s >=22):
			n = "Yellow"
			hexColor = "#E5D900"
			i = imagePath+"yellow-flair.png"
		elif(s < 22 and s >=12):
			n = "Orange"
			hexColor = "#e59500"
			i = imagePath+"orange-flair.png"
		elif(s < 12 and s >=1):
			n = "Red"
			hexColor = "#e50000"
			i = imagePath+"red-flair.png"
 
		# If its a new highscore, use Slack banner formatting
		if(s < highScore):
			highScore = s
			payload = {"text":"",'username':"filthiest yet! #"+lastData['payload']['participants_text'],'icon_url':i,"attachments": [{"fallback": "A new highscore of "+str(s)+"s has been set","text": "New High Score of"+str(s)+'s'+" <!channel>","title": str(s)+'s',"pretext": "","color": hexColor}]}

			# Write the new highscore to the file
			hsFile = open('highscore.txt','w')
			hsFile.write(str(highScore))
		
		# Just use the standard Slack message format for non high scores
		else:			
			payload = {'text':str(s)+'s', 'username':"filthy presser #"+lastData['payload']['participants_text'], 'icon_url':i}
		
		# Send the message to Slack
		r = requests.post(slackURL,data=json.dumps(payload))

	# Save this data to compare with on the next tick
	lastData = m

# Function to run when there is a connection error
def on_error(ws, error):
	print "error: "+"*"*10
	print error
	print "*"*17

# Function to run when the connection closes
def on_close(ws):
	print "### closed ###"

# Function to run when the connection opens
def on_open(ws):
	def run(*args):
		ws.send("Hello %d" % i)



# Initialize the script
if __name__ == "__main__":
	ws = websocket.WebSocketApp(buttonWSS,
			on_message = on_message,
			on_error = on_error,
			on_close = on_close)
			
	ws.on_open = on_open
	ws.run_forever()
