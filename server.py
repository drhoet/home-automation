from bottle import route, run
from phue import Bridge
import os, configparser, logging, logging.config, threading, time

def writeDefaultConfig():
	logger.debug('No config found. Writing default config to server.cfg. Please adapt accordingly and restart the server.')
	config = configparser.ConfigParser()
	config['Server'] = {
		'host': 'localhost',
		'port': '8080'
	}
	config['HueBridge'] = {
		'ip': '192.168.0.x',
		'user': 'some_username'
	}
	with open('server.cfg', 'w') as configfile:
		config.write(configfile)

def getLightByName(name):
	light_names = bridge.get_light_objects('name')
	return light_names[name]

@route('/api/1.0/wakeUp')
def wakeUp():
	light = getLightByName(config['wakeUp']['lightName'])
	t = threading.Thread(target = hueSendSeries, args=(light, config['wakeUp']) )
	t.deamon = True
	t.start()
	return "OK"

@route('/api/1.0/sleep')
def sleep():
	light = getLightByName(config['sleep']['lightName'])
	light.transitiontime = config['sleep'].getint('transitionTime')
	light.brightness = config['sleep'].getint('brightness')
	light.on = config['sleep'].getboolean('on')
	return "OK"

def hueSendSeries(light, config):
	steps = config.getint('steps')
	for i in range(0, steps):
		logger.debug('Sending step %d', i)
		light.hue = config.getint('hue' + str(i))
		light.sat = config.getint('sat' + str(i))
		light.transitiontime = config.getint('transitionTime' + str(i))
		light.brightness = config.getint('brightness' + str(i))
		light.on = True
		time.sleep(config.getint('transitionTime' + str(i)) / 10.0)


# init logging
logging.config.fileConfig('log.cfg')
logger = logging.getLogger('server')

logger.info('Starting home-automation server')
# loading configuration
logger.debug('Loading config')
if not os.path.isfile('server.cfg'):
	writeDefaultConfig()
	quit()

config = configparser.ConfigParser()
config.read('server.cfg')

logger.info('Connecting to Hue Bridge at %s with user name %s', config['HueBridge']['ip'], config['HueBridge']['user'])
bridge = Bridge( config['HueBridge']['ip'], config['HueBridge']['user'] )

run(host=config['Server']['host'], port=config['Server']['port'], debug=True)