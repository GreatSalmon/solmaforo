
LogFile = "/home/pi/solmaforo_logs/logs.log"


def Log(msg):
	print(msg.strip())
	with open(LogFile, "a") as logfile:
		logfile.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "; " + msg + "\n")

def GetAddresses():
	#Try to get PPP0 (mobile) address
	#If it doesn't work, get Local ethernet address
	try:
		myMAC = open('/sys/class/net/eth0/address').read().strip()
		myIP = get_ip_address("ppp0")
	except IOError as e:
		utils.Log(str(e))
		try:
			myMAC = open('/sys/class/net/wwan0/address').read().strip()
			myIP = get_ip_address("ppp0")
		except IOError as e:
			utils.Log(str(e))
			myMAC = "No MAC"
			myIP = "No IP"

	return myMAC, myIP