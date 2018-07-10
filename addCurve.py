import bpy
import numpy as np
import random
from math import cos, sin


FRAMES_TO_RENDER = 10 # Render this number of rames
RESOLUTION_X = 254
RESOLUTION_Y = 254
PATH_TO_SAVE = "/home/brans/Documents/3dModeling/rendering/"

COORDS_COUNT = 20
CAMERA_PATH_RADIUS = 5

RANDOM_STEP_CHECK = 4 # evry this step we will change velocity in Z axis
CAMERA_Z_MAX_VELOCITY = 0.5 # velocity will be in {-CAMERA_Z_MAX_VELOCITY; +CAMERA_Z_MAX_VELOCITY} range. 

def BuildCoords():
	angelStep = 360 / COORDS_COUNT # We will make a step on this angel
	currentVelocity = 0
	curZ = 0

	points = []

	for i in range(COORDS_COUNT):
		if(i > 0 and i % RANDOM_STEP_CHECK == 0):
			currentVelocity = np.random.uniform(-CAMERA_Z_MAX_VELOCITY, CAMERA_Z_MAX_VELOCITY)

		curAngel = angelStep * i # theta
		x = CAMERA_PATH_RADIUS * cos(curAngel)
		y = CAMERA_PATH_RADIUS * sin(curAngel)
		curZ += currentVelocity
		if(curZ < 0):
			curZ = 0

		points.append([x, y, curZ])

	return points



def AddCurv(coords, curType):
	# create the Curve Datablock
	curveData = bpy.data.curves.new('cameraPath', type='CURVE')
	curveData.dimensions = '3D'
	curveData.resolution_u = 2

	# map coords to spline
	polyline = curveData.splines.new(curType)
	polyline.points.add(len(coords))
	for i, coord in enumerate(coords):
		x,y,z = coord
		polyline.points[i].co = (x, y, z, 1)

	# create Object
	curveOB = bpy.data.objects.new('cameraPath', curveData)

	# attach to scene and validate context
	scn = bpy.context.scene
	scn.objects.link(curveOB)
	scn.objects.active = curveOB
	curveOB.select = True

def AddConstrains():
	# Make camera follow the path 
	bpy.ops.object.select_all(action='DESELECT')

	camera = bpy.data.objects['Camera']
	path = bpy.data.objects['cameraPath']
	cube = bpy.data.objects['Cube']

	#lamp = bpy.data.objects['Lamp']

	camera.select = True
	#lamp.select = True
	path.select = True

	bpy.context.scene.objects.active = path #parent

	bpy.ops.object.parent_set(type='FOLLOW')

	#---------------------------
	# Make camera track to the cube

	bpy.ops.object.select_all(action='DESELECT')
	ttc = camera.constraints.new(type='TRACK_TO')
	ttc.target = cube
	ttc.track_axis = 'TRACK_NEGATIVE_Z'
	# we don't care about the up_axis
	# but default is Z and it needs to be different that track_axis
	ttc.up_axis = 'UP_Y'

	bpy.ops.object.select_all(action='DESELECT')
	camera.select = True
	bpy.ops.object.visual_transform_apply()
	#camera.constraints.remove(ttc)

def DeleteCameraPath():
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects['cameraPath'].select = True
    bpy.ops.object.delete() 

def get_random_color():
    r, g, b = [random.random() for i in range(3)]
    return (r, g, b)

def SetUp():
	bpy.ops.object.select_all(action='DESELECT')

	# Change cube color and position
	bpy.data.objects["Cube"].active_material.diffuse_color = get_random_color()
	bpy.data.objects["Cube"].location.z += 1.0

	# Add the floor
	bpy.ops.mesh.primitive_plane_add(radius = 8)

	# Add the lamp
	scene = bpy.context.scene

	# Create new lamp datablock
	lamp_data = bpy.data.lamps.new(name="New Lamp", type='POINT')

	# Create new object with our lamp datablock
	lamp_object = bpy.data.objects.new(name="New Lamp", object_data=lamp_data)

	# Link lamp object to the scene so it'll appear in this scene
	scene.objects.link(lamp_object)

	# Place lamp to a specified location
	lamp_object.location = (5.0, 5.0, 5.0)

	# And finally select it make active
	lamp_object.select = True
	scene.objects.active = lamp_object


SetUp()
# sample data
#DeleteCameraPath()
coords = BuildCoords() 
AddCurv(coords, 'POLY')
AddConstrains()
bpy.ops.object.select_all(action='DESELECT')

# bpy.context.scene.render.resolution_x = RESOLUTION_X 
# bpy.context.scene.render.resolution_y = RESOLUTION_Y

# for curFrame in range(FRAMES_TO_RENDER):
#     fileName = '/shot_%d.jpg' % curFrame
#     bpy.data.scenes["Scene"].render.filepath = PATH_TO_SAVE + fileName
#     bpy.ops.render.render(animation=True)

bpy.data.scenes["Scene"].render.filepath = PATH_TO_SAVE 
bpy.data.scenes["Scene"].frame_end = 50
bpy.ops.render.render(animation=True)
