from bge import logic as G
from bge import events
import mathutils
import math
import Rasterizer

stats = None
keyboardLayout = None
anim = None
camera = None
motion = None

def init(cont):
	global stats, keyboardLayout, anim, camera, char_motion
	box = cont.owner
	for ob in box.children:
		if 'col_empty' in ob:
			col_sens = ob.sensors['Collision']
			del ob['col_empty']
		elif 'head' in ob:
			head = ob
			del head['head']
			for obj in ob.children:
				if 'third_person' in obj:
					cam = obj
		elif 'UpDown' in ob:
			arma = ob
	
	char_motion = char_motion(box, col_sens)
	stats = stats()
	keyboardLayout = keyboardLayout()
	anim = anim(arma)
	camera = camera(cam, head, box)
	G.getCurrentScene().active_camera = cam

def unload():
	char_motion.box.endObject()

class stats:
	def __init__(self):
		self.godmode = False
		self.life = [125, 150]
		self.mana = [125, 150]
		self.energy = 100
		
		self.hunger = 0
		self.sickness = 0
		self.weight = 65

class keyboardLayout:
	def __init__(self):
		self.move_w = events.WKEY
		self.move_b = events.SKEY
		self.move_l = events.AKEY
		self.move_r = events.DKEY
		self.sprint = events.LEFTSHIFTKEY
		self.crouch = events.LEFTCTRLKEY
		self.jump = events.SPACEKEY
		self.interact = events.EKEY
		self.fly = events.RKEY
		
		self.person_swap = events.MIDDLEMOUSE
		self.zoom_in = events.WHEELUPMOUSE
		self.zoom_out = events.WHEELDOWNMOUSE

class anim:
	def __init__(self, arma):
		self.armature = arma
		self.animList = {}
		self.setUpAnimationList()
		self.start = 0
		self.end = 0
		self.anim_speed = 1.0
		self.anim = 'wait'
		self.prevanim = None
	
	def setUpAnimationList(self):
		self.animList['wait'] = [0, 500, 0.6]
		self.animList['walkF'] = [1, 21, 0.2]
		self.animList['walkB'] = [1, 21, 0.4]
		self.animList['runF'] = [1, 16, 0.1]
		self.animList['runB'] = [1, 16, 0.1]
		self.animList['swimF'] = [1, 40, 0.1]
		self.animList['swimB'] = [1, 40, 0.1]
		self.animList['swimL'] = [1, 40, 0.1]
		self.animList['swimR'] = [1, 40, 0.1]
		self.animList['idleSwim'] = [1, 40, 1.0]
		self.animList['jump'] = [1, 13, 1.0]
		self.animList['attack'] = [22, 42, 1.0]
		self.animList['sit'] = []
		self.animList['fall'] = [1, 42, 0.2]
		self.animList['landdie'] = []
		self.animList['fall_move'] = []
		self.animList['fall_shake'] = []
	
	def play(self, name):
		if name == self.anim:
			return
		self.prevanim = self.anim
		self.anim = name
		anim = self.animList[name]
		self.start = anim[0]
		self.end = anim[1]
		self.anim_speed = anim[2]
		self.armature['frame'] = self.start
		self.armature['anim'] = not self.armature['anim']
	
	def loop(self):
		if self.armature['frame'] > self.end:
			self.armature['frame'] = self.start + self.armature['frame']-self.end
		else:	
			self.armature['frame'] += char_motion.motionspeed*self.anim_speed

class camera:
	def __init__(self, cam, head, pbox):
		self.mblur = False
		self.mblur_ticks = 0
		self.sensitivity = 2
		self.cam_cap = 80
		self.cam = cam
		self.head = head
		self.box = pbox
		self.mouselook_blocked = False
		self.third_person = False
		self.up_down_enabled = True
		self.head_rotX = 0
		self.camDistance = -1
		self.zoomDistance = 0
		self.init = 1

	def rotateOb(self, ob, angle, axis):
		omat = ob.localOrientation
		rmat = mathutils.Quaternion(axis, angle).to_matrix()
		ob.orientation = rmat*omat

	def mouseLook(self):
		if self.mouselook_blocked:	return
		x = (0.5-G.mouse.position[0])*self.sensitivity
		y = (G.mouse.position[1]-0.5)*self.sensitivity
		if abs(x) < 0.01 and abs(y) < 0.01:
			return
		
		if self.mblur:
			strength = abs(x)+abs(y)
			if strength > 0.2:
				print(strength)
				strength = min(strength*2,0.8)
				Rasterizer.enableMotionBlur(strength)
				self.mblur_ticks = 0
			elif self.mblur_ticks > 120:
				Rasterizer.disableMotionBlur()
			else:	self.mblur_ticks += 1
		
		self.rotateOb(self.box, x, (0,0,1))
		
		pot_rotX = self.head_rotX + math.degrees(y)
		if abs(pot_rotX) < self.cam_cap:
			self.head_rotX = pot_rotX
			if self.up_down_enabled:
				anim.armature['UpDown'] = -pot_rotX+90
			self.rotateOb(self.head, y, (-1,0,0))
		
		#Reset cursor
		G.mouse.position = 0.5,0.5

	def zoom(self):
		if G.mouse.events[keyboardLayout.person_swap] == 1:
			if self.third_person:
				self.cam['third_person'] = False
				self.third_person = False
			else:
				self.cam['third_person'] = True
				self.third_person = True
		else: pass

class char_motion:
	def __init__(self, pbox, col_sens):
		self.box = pbox
		self.speed = [10.5, 20.0]
		self.motionspeed = 5.0
		self.acceleration = self.speed[1]/60.0
		self.jump_height = 1.0
		self.motion_blocked = False
		self.fallZ = None
		self.jump = False
		self.swim = False
		self.fly = False
		self.col = col_sens
	
	def setSpeed(self, value):
		self.speed[1] *= value
		self.acceleration = self.speed[1]/60.0
	
	def move(self):
		if self.motion_blocked:		return
		
		keys = G.keyboard.events
		
		#toggle flymode
		if keys[keyboardLayout.fly] == 1: 
			self.fly = not self.fly
			self.swim = not self.swim
			if self.fly:
				self.setSpeed(5)
				camera.up_down_enabled = False
			else:	
				self.setSpeed(1/5)
				camera.up_down_enabled = True
				camera.rotateOb(camera.head, math.radians(-camera.head_rotX), (1,0,0))
				self.box.alignAxisToVect((0,0,2),2)
		#flymode, else: normal mode or no motion
		if self.swim:
			self.box.applyForce((0,0,9.8),0)
			self.box.orientation = camera.head.worldOrientation
			camera.head.localOrientation = [[1,0,0],[0,1,0],[0,0,1]]
			if keys[keyboardLayout.jump]:
				z = 1.0*self.motionspeed
			else:	z = 0.0
		elif not self.col.positive:
			if self.box.getLinearVelocity()[2] < 0:
				self.fall()
			else:	anim.play('jump')
			return
		#jump
		elif keys[keyboardLayout.jump] == 1:
			z = 3.0*self.jump_height
			self.fallZ = self.box.position[2]
		else:
			z = self.box.getLinearVelocity()[2]
			if self.fallZ:	self.fallZ = None
		
		#W,A,S,D,Shift,Ctrl
		if keys[keyboardLayout.move_w]:		y = 0.8*self.motionspeed
		elif keys[keyboardLayout.move_b]:		y = -0.7*self.motionspeed
		else:	y = 0.0
		if keys[keyboardLayout.move_l]:
			if not keys[keyboardLayout.move_r]:	x = -0.8*self.motionspeed
			else:	x = 0.0
		elif keys[keyboardLayout.move_r]:			x = 0.8*self.motionspeed
		else:	x = 0.0
		if keys[keyboardLayout.sprint]:
			sprint = True
			self.motionspeed = min(self.motionspeed+self.acceleration, self.speed[1])
		else:	
			sprint = False
			self.motionspeed = self.speed[0]
		if keys[keyboardLayout.crouch]:
			crouch = True
			x /= 3
			y /= 3
		else:	crouch = False
		
		if x and y:
			x *= 0.66
			y *= 0.66
		if x or y:
			if not self.swim:
				if x > 0:
					if not y:	anim.armature['LR_step'] = 5
					elif y > 0:	anim.armature['LR_step'] = 4
					else:		anim.armature['LR_step'] = 2
				elif x < 0:
					if not y:	anim.armature['LR_step'] = 1
					elif y > 0:	anim.armature['LR_step'] = 2
					else:		anim.armature['LR_step'] = 4
				else:			anim.armature['LR_step'] = 3
				
				if sprint:
					if y > 0:	anim.play('runF')
					elif y < 0:	anim.play('runB')
					if x:		anim.play('runF')
				else:
					if y > 0:	anim.play('walkF')
					elif y < 0:	anim.play('walkB')
					if x:		anim.play('walkF')
			else:
				if y > 0:	anim.play('swimF')
				elif y < 0:	anim.play('swimB')
				if x:		anim.play('swimF')
		else:	anim.play('wait')
		
		#final motion
		self.box.setLinearVelocity((x,y,0),1)
		if z:
			linV = self.box.getLinearVelocity()
			self.box.setLinearVelocity((linV[0], linV[1], z), 0)

	def fall(self):
		anim.play('fall')
def update():
	camera.mouseLook()
	camera.zoom()
	char_motion.move()
	anim.loop()

def playAnim(cont):
	if cont.sensors[0].positive:
		cont.deactivate(anim.prevanim)
		cont.activate(anim.anim)
'''
def cameraCollision():
	cam = Character.camera
	pos = cam.cameraCollision()
	if pos:
		cam.cam.worldPosition = pos
	else:
		pos = cam.cam.localPosition
		cam.cam.position = [pos[0], -cam.camDistance, pos[2]]
'''

def hanging():
	actions = Character.actions
	
	box = actions.box
	hitpos, hitnor, hangZ = actions.hangRay()
	
	if hitpos:
		box.applyForce((0,0,9.8))
		box.alignAxisToVect((0,0,1),2)
		box.alignAxisToVect((-hitnor[0],-hitnor[1],0),1)
		
		new_pos = hitpos[:]
		
		if hangZ:	new_pos[2]-= 0.425
		else:		new_pos[2]-= 0.25
		
		actions.setLocalPosition([0,-0.23,0],new_pos)
		
		keyboard = UserInput.keyboard
		keys = keyboard.keysPressed(['w','s','a','d','space','f'])
		x = y = z = 0
		if keys[0]:
			if not hangZ:	z = 0.25
			else:
				actions.motionCooldown = 1	#Climb up
				###Character.climbing = 1
				box['ready_timer'] = 0
				box.state += 8	# -8 + 16
				actions.climbing = 1
				return
		elif keys[1]:
			col = actions.touchGround()
			if not col[0]:	z = -0.25
			else:
				y = -1.2
				actions.motionCooldown = 0.5
				box['ready_timer'] = 0
				box.state += 8	# -8 + 16
		
		if keys[2]:		x = -0.25
		elif keys[3]:	x = 0.25
		
		if keys[4]:
			if not keys[1]:
				y = -1
				z = 2
			else:
				y = -0.3
				z = 2
			actions.motionCooldown = 0.6
			box['ready_timer'] = 0
			box.state += 8	# -8 + 16
		elif keys[5]:
			y = -1
			actions.motionCooldown = 0.4
			box['ready_timer'] = 0
			box.state += 8	# -8 + 16
		
		box.setLinearVelocity([x,y,z],1)
	else:
		actions.motionCooldown = 0.4
		box['ready_timer'] = 0
		actions.hanging = 0
		box.state += 8	# -8 + 16

def resetMotion():
	actions = Character.actions
	cam = Character.camera
	if actions.climbing:
		actions.climbUp()
	elif actions.motionCooldown:
		if actions.box['ready_timer'] > actions.motionCooldown:
			actions.motionCooldown = 0
			if actions.turnblocked:
				actions.turnblocked = 0
				cam.resetCam()
			actions.box.state = 3
	else:
		if actions.turnblocked:
			actions.turnblocked = 0
			cam.resetCam()
		actions.box.state = 3

def updateStatus():
	actions = Character.actions
	anim = Character.animation
	properties = Character.properties
	
	col = actions.exactTouchGround()
	if not col[0] and not col[1]:
		if not actions.fallZ:
			z = actions.box.getLinearVelocity()[2]
			if z < 0:
				actions.fallZ = actions.box.position[2]
		anim.A['anim'] = 12
	elif actions.fallZ:
		if not properties.godmode:
			dmg = ((actions.fallZ-actions.box.position[2])**2)/200*properties.maxlife
			if dmg > properties.maxlife/20:
				actions.receiveDamage(dmg)
		actions.fallZ = None

	actions.lifeReg()
	actions.manaReg()

def interaction(cont):
	actions = Character.actions
	kb = UserInput.keyboard
	
	ray = cont.sensors[1]
	if ray.positive:
		curscn = G.getCurrentScene().objects
		hitobj = ray.hitObject
		
		if 'door' in hitobj:
			if 'scene' in hitobj:
				act = cont.actuators['setScene']
				act.scene = hitobj['scene']
				actions.door = hitobj['door']
				Character.camera.person = 0
				cont.activate(act)
			else:
				actions.door = hitobj['door']
				actions.doorPositioning()