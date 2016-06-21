import obd
import time
import csv
import smbus
import MMA8451 as mma
import gps
import RPi.GPIO as GPIO
from datetime import datetime

# 1 = x
# 2 = -x
# 3 = y
# 4 = -y
# 5 = z
# 6 = -z
ORIENTATION_MAPPING = {
	0b0100: lambda x, y, z: (x, y, z),
	0b0101: lambda x, y, z: (-x, y, -z),
	0b0110: lambda x, y, z: (-y, x, z),
	0b0111: lambda x, y, z: (y, x, -z),
	0b1000: lambda x, y, z: (-x, -y, z),
	0b1001: lambda x, y, z: (x, -y, -z),
	0b1010: lambda x, y, z: (y, -x, z),
	0b1011: lambda x, y, z: (-y, -x, -z),
	0b00000: lambda x, y, z: (-x, -z, -y),
	0b00001: lambda x, y, z: (x, -z, y),
	0b00010: lambda x, y, z: (-y, -z, x),
	0b00011: lambda x, y, z: (y, -z, -x),
	0b00100: lambda x, y, z: (x, z, -y),
	0b00101: lambda x, y, z: (-x, z, y),
	0b00110: lambda x, y, z: (y, z, x),
	0b00111: lambda x, y, z: (-y, z, -x),
	0b01010: lambda x, y, z: (-z, y, x),
	0b01011: lambda x, y, z: (z, y, -x),
	0b01100: lambda x, y, z: (z, x, -y),
	0b01101: lambda x, y, z: (-z, x, y),
	0b10010: lambda x, y, z: (z, -y, x),
	0b10011: lambda x, y, z: (-z, -y, x),
	0b10100: lambda x, y, z: (-z, -x, -y),
	0b10101: lambda x, y, z: (z, -x, y)
}
MAX_SUPPORTED_COMMANDS = 52
KPH_TO_MPH = 0.621371
DIP_IO = [13, 16, 19]
DEBUG = False

connection = None
accel = None
session = None
globalX = None
globalY = None
globalZ = None

def debug(str):
	if DEBUG:
		print str
		
def setupDipSwitch():
	GPIO.setmode(GPIO.BCM)
	for x in DIP_IO:
		GPIO.setup(x, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Direction of accelerometer
# Front 				Down (getOrientation())
# 0 Front			Front
# 1 Back				Back
# 2 Up				PU
# 3 Right			PD
# 4 Down				LR
# 5 Left				LL
def setupDataOrientate():
	dipSetBits = 0
	bitShift = 0
	downDir = mma.getOrientation()
	for x in DIP_IO:
		dipSetBits = dipSetBtis | (GPIO.in(x) << bitShift)
		bitShift += 1
	if dipSetBits <= 1:
		if dipSetBits:
			globalX = '-z'
		else:
			globalX = 'z'
	else:
		downDir = downDir >> 1

def oritentateData(x, y, z):
	return -z, y, -x

def initConnection():
	global connection
	while True:
		try:
			connection = obd.Async()
			debug("connected")
			if len(connection.supported_commands) >= MAX_SUPPORTED_COMMANDS:
				debug("passed")
				connection.watch(obd.commands.ENGINE_LOAD)
				debug("ENGINE_LOAD")
				connection.watch(obd.commands.COOLANT_TEMP)
				debug("COOLANT_TEMP")
				connection.watch(obd.commands.RPM)
				debug("RPM")
				connection.watch(obd.commands.SPEED)
				debug("SPEED")
				connection.watch(obd.commands.INTAKE_TEMP)
				debug("INTAKE_TEMP")
				connection.watch(obd.commands.MAF)
				debug("MAF")
				connection.watch(obd.commands.THROTTLE_POS)
				debug("THROTTLE_POS")
				connection.watch(obd.commands.TIMING_ADVANCE)
				debug("TIMING_ADVANCE")
				connection.start()
				debug("OBD watchdog started!")
				break
			connection.close()
			time.sleep(1)
		except (KeyboardInterrupt, SystemExit):
			raise
		except:
			pass

def logData():
	filename = time.strftime("%Y%m%d%H%M.csv")
	gpsSpeed = gpsLat = gpsLon = gpsAlt = gpsClimb = None
	
	debug(filename)
	
	with open(filename, 'w') as csvfile:
		fieldnames = ['time', 'engineLoad', 'coolantTemp', 'rpm', 'speed', 'intakeTemp', 'maf', 'throttlePos', 'timingAdvance', 'xG', 'yG', 'zG', 'orientation', 'gpsSpeed', 'gpsLat', 'gpsLon', 'gpsAlt', 'gpsClimb']
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		writer.writeheader()
		
		rpm = connection.query(obd.commands.RPM).value
		while rpm == None or rpm == 0.0:
			rpm = connection.query(obd.commands.RPM).value
			time.sleep(1)
		
		debug("Start logging data.")
		while rpm > 0:
			report = session.next()
			while report['class'] != 'TPV':
				report = session.next()
			if report['class'] == 'TPV':
				if hasattr(report, 'speed'):
					gpsSpeed = report.speed * gps.MPS_TO_MPH
				if hasattr(report, 'lat'):
					gpsLat = report.lat
				if hasattr(report, 'lon'):
					gpsLon = report.lon
				if hasattr(report, 'alt'):
					gpsAlt = report.alt
				if hasattr(report, 'climb'):
					gpsClimb = report.climb * gps.MPS_TO_MPH
			timestamp = datetime.now().strftime("%X.%f")
			x, y, z = accel.readScaledData()
			x, y, z = orientateData(x, y, z)
			rpm = connection.query(obd.commands.RPM).value
			writer.writerow(
				{'time': timestamp,
				'engineLoad': connection.query(obd.commands.ENGINE_LOAD).value,
				'coolantTemp': connection.query(obd.commands.COOLANT_TEMP).value,
				'rpm': rpm,
				'speed': (connection.query(obd.commands.SPEED).value * KPH_TO_MPH),
				'intakeTemp': connection.query(obd.commands.INTAKE_TEMP).value,
				'maf': connection.query(obd.commands.MAF).value,
				'throttlePos': connection.query(obd.commands.THROTTLE_POS).value,
				'timingAdvance' : connection.query(obd.commands.TIMING_ADVANCE).value,
				'xG' : x,
				'yG' : y,
				'zG' : z,
				'gpsSpeed' : gpsSpeed,
				'gpsLon' : gpsLon,
				'gpsLat' : gpsLat,
				'gpsAlt' : gpsAlt,
				'gpsClimb' : gpsClimb})
			time.sleep(0.1)
	
	debug("Exiting logging data.")
	connection.stop()
	connection.close()
		
if __name__ == "__main__":
	
	accel = mma.MMA8451()
	ismma = accel.check8451()
	if ismma:
		debug("MMA Found!")
	else:
		debug("No MMA Found.")
	accel.setup()
	
	session = gps.gps("localhost", "2947")
	session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
	for i in range(3):
		session.next()
	
	while True:
		initConnection()
		logData()
