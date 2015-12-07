f = '/home/moser/Downloads/02828884/1042d723dfc31ce5ec56aed2da084563/model.obj'
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
map.size = [0.08]
map.use_min = True
map.min = [0]
map.use_max = True
map.max = [255]
links.new(rl.outputs[2], map.inputs[0])

invert = tree.nodes.new(type="CompositorNodeInvert")
links.new(map.outputs[0], invert.inputs[1])

depthViewer = tree.nodes.new(type="CompositorNodeViewer")
links.new(invert.outputs[0], depthViewer.inputs[0])
# Use alpha from input.
links.new(rl.outputs[1], depthViewer.inputs[1])

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
cam.location = Vector((0, 2, 2))
cam_constraint = cam.constraints.new(type='TRACK_TO')
cam_constraint.track_axis = 'TRACK_NEGATIVE_Z'
cam_constraint.up_axis = 'UP_Y'
b_empty = parent_obj_to_camera(cam)
cam_constraint.target=b_empty

fp = scene.render.filepath # get existing output path
scene.render.image_settings.file_format = 'PNG' # set output format to .png

from math import radians


num_steps = 30
stepsize = 360.0 / num_steps
rotation_mode = 'XYZ'
for i in range(0, num_steps):
    print("Rotation {}, {}".format((stepsize * i), radians(stepsize * i)))

    scene.render.filepath = fp + 'r_{0:03d}'.format(int(i * stepsize))
    bpy.ops.render.render(write_still=True) # render still
    # This will only work if blender was started in GUI
    bpy.data.images['Viewer Node'].save_render(scene.render.filepath + "_depth.png")

    b_empty.rotation_euler[2] += radians(stepsize)
