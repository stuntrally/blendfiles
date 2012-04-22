from bge import logic as G
import GameKeys

class_sky = None

def load():
	pass
	#GameLogic.LibLoad('sky.blend', 'Scene')
	
def unload():
	global class_sky
	class_sky.sc2.end()
	class_sky.sun_lamp.endObject()
	class_sky.hemi1.endObject()
	class_sky.hemi2.endObject()
	class_sky.shad_lamp.endObject()
	class_sky.light_empty.endObject()
	class_sky = None
	print( G.getSceneList())

def init():
	#Get Scenes
	sc1 = G.getSceneList()[1]
	sc2 = G.getCurrentScene()

	#Get ObjectScenes
	scn1 = sc1.objects
	scn2 = sc2.objects

	#Get Cameras
	cam1 = sc1.active_camera
	cam2 = scn2['SkyCam']
	
	#Get Objects
	sempty = scn2['SunEmpty']
	lempty = scn1['LightsEmpty']
	shadlamp = scn1['Shadow_lamp']
	sun = scn1['Sun_lamp']
	hemi1 = scn1['Hemi1']
	hemi2 = scn1['Hemi2']
	sky = scn2['Sky']
	clouds = scn2['clouds']
	sun_ob = scn2['Sonne']
	moon = scn2['Moon']
	slamp = scn2['SkyShade']
	
	#Get Class
	global class_sky
	class_sky = class_sky(cam1, cam2, lempty, sempty, shadlamp, sun, hemi1, hemi2, sky, clouds, sun_ob, moon, slamp, sc1, sc2)

def update():
	class_sky.updateRotation()
	class_sky.changeDaytime()

class class_sky:
	def __init__(self, scam, ocam, lempty, sempty, shlamp, sun_lamp, h1, h2, sky, clouds, sun, moon, shade_lamp, sc1, sc2):
		self.sc1 = sc1
		self.sc2 = sc2
		self.sc_cam = scam
		self.ov_cam = ocam
		self.light_empty = lempty
		self.sun_empty = sempty
		self.shad_lamp = shlamp
		self.sun_lamp = sun_lamp
		self.hemi1 = h1
		self.hemi2 = h2
		self.sky = sky
		self.clouds = clouds
		self.sun = sun
		self.moon = moon
		self.shade_lamp = shade_lamp
		self.daysPerHour = 1
		self.prevframe = 0
		self.daytimePulse = 0
	
	def updateRotation(self):
		self.ov_cam.orientation = self.sc_cam.orientation
		self.light_empty.position = self.sc_cam.position
	
	def changeDaytime(self):
		if self.daytimePulse < 5:
			self.daytimePulse += 1
			return
		else:	self.daytimePulse = 0
		
		if G.keyboard.events[GameKeys.TKEY] == 2:
			self.sky['time'] += 40.0/self.daysPerHour
		frame = self.sky['time']*self.daysPerHour
		diff = (frame - self.prevframe)*0.002
		self.prevframe = frame
		
		'''  Uhrzeit in hour/minute
		hour = int(frame/150)
		minute = int(frame/2.5)-(hour*60)
		'''
		self.sun_empty['tframe'] = frame
		self.light_empty['tframe'] = frame
		self.shad_lamp['tframe'] = frame
		self.sun_lamp['tframe'] = frame
		self.hemi1['tframe'] = frame
		self.hemi2['tframe'] = frame
		self.sky['tframe'] = frame
		self.clouds['tframe'] = frame
		self.sun['tframe'] = frame
		self.moon['tframe'] = frame
		self.shade_lamp['tframe'] = frame
		
		if frame > 3600:
			self.sky['time'] = 0
		elif frame > 900 and frame < 970:
			self.duskSunColor(diff)
		elif frame > 2500 and frame < 2580:
			self.dawnSunColor(diff)
	
		self.moveUV(self.clouds, diff, 0)
	
	def dawnSunColor(self, diff):
		sun = self.sun_lamp
		r,g,b = sun.color
		r +=min(diff,1)
		g +=min(diff*2.5,1)
		b +=min(diff*3,1)
		sun.color = [r,g,b]
	
	def duskSunColor(self, diff):
		sun = self.sun_lamp
		r,g,b = sun.color
		r -=diff
		g -=diff*2.5
		b -=diff*3
		sun.color = [r,g,b]
	
	def moveUV(self, ob, sx, sy):
		me = ob.meshes[0]
		alen = me.getVertexArrayLength(0)
		for x in range(alen):
			vert = me.getVertex(0,x)
			uv = vert.getUV()
			uv[0] += sx
			uv[1] += sy
			vert.setUV(uv)