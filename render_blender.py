# A simple script that uses blender to render views of a single object by rotation the camera around it.
# Also produces depth map at the same time.
#
# Example:
# blender --background --python mytest.py -- --views 10 /path/to/my.obj
#

import argparse, sys
parser = argparse.ArgumentParser(description='Renders given obj file by rotation a camera around it.')
parser.add_argument('--views', type=int, default=30,
                   help='number of views to be rendered')
parser.add_argument('obj', type=str,
                   help='Path to the obj file to be rendered.')

argv = sys.argv[sys.argv.index("--") + 1:]
args = parser.parse_args(argv)
f = args.obj

import bpy
from mathutils import Vector

# Set up rendering of depth map:
bpy.context.scene.use_nodes = True
tree = bpy.context.scene.node_tree
links = tree.links

# clear default nodes
for n in tree.nodes:
    tree.nodes.remove(n)

# create input render layer node
rl = tree.nodes.new('CompositorNodeRLayers')

map = tree.nodes.new(type="CompositorNodeMapValue")
# Size is chosen kind of arbitrarily, try out until you're satisfied with resulting depth map.
map.size = [0.5]
map.use_min = True
map.min = [0]
map.use_max = True
map.max = [255]
links.new(rl.outputs[2], map.inputs[0])

invert = tree.nodes.new(type="CompositorNodeInvert")
links.new(map.outputs[0], invert.inputs[1])

# create a file output node and set the path
depthFileOutput = tree.nodes.new(type="CompositorNodeOutputFile")
links.new(invert.outputs[0], depthFileOutput.inputs[0])

# Delete default cube
bpy.data.objects['Cube'].select = True
bpy.ops.object.delete()



bpy.ops.import_scene.obj(filepath=f)

def parent_obj_to_camera(b_camera):
    origin = (0,0,0)
    b_empty = bpy.data.objects.new("Empty", None)
    b_empty.location = origin
    b_camera.parent = b_empty #setup parenting

    scn = bpy.context.scene
    scn.objects.link(b_empty)
    scn.objects.active = b_empty
    return b_empty

scene = bpy.context.scene
scene.render.resolution_x = 600
scene.render.resolution_y = 600
scene.render.resolution_percentage = 100
scene.render.alpha_mode = 'TRANSPARENT'
cam = scene.objects['Camera']
cam.location = Vector((0, 1, 1))
cam_constraint = cam.constraints.new(type='TRACK_TO')
cam_constraint.track_axis = 'TRACK_NEGATIVE_Z'
cam_constraint.up_axis = 'UP_Y'
b_empty = parent_obj_to_camera(cam)
cam_constraint.target=b_empty

fp = scene.render.filepath # get existing output path
scene.render.image_settings.file_format = 'PNG' # set output format to .png

from math import radians

stepsize = 360.0 / args.views
rotation_mode = 'XYZ'
depthFileOutput.base_path = ''

for i in range(0, args.views):
    print("Rotation {}, {}".format((stepsize * i), radians(stepsize * i)))

    scene.render.filepath = fp + 'r_{0:03d}'.format(int(i * stepsize))
    depthFileOutput.file_slots[0].path = scene.render.filepath + "_depth.png"
    bpy.ops.render.render(write_still=True) # render still

    b_empty.rotation_euler[2] += radians(stepsize)
