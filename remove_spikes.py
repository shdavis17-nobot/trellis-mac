import bpy

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Import the perfected STL
import_path = '/Users/shawn/Projects/trellis-mac/bigfoot_perfected.stl'
bpy.ops.wm.stl_import(filepath=import_path)

obj = bpy.context.selected_objects[0]
bpy.context.view_layer.objects.active = obj

# Apply a Laplacian Smooth Modifier
# This is specifically designed to "melt" thin, sharp spikes while trying to preserve volume
smooth_mod = obj.modifiers.new(name="SpikeRemover", type='LAPLACIANSMOOTH')
smooth_mod.iterations = 15
smooth_mod.lambda_factor = 1.0  # Maximum smoothing strength

# Apply modifier
bpy.ops.object.modifier_apply(modifier="SpikeRemover")

# Export
export_path = '/Users/shawn/Projects/trellis-mac/bigfoot_despiked.stl'
bpy.ops.wm.stl_export(filepath=export_path)

print(f"Successfully smoothed and saved to {export_path}")
