import bpy

class RenderPassesPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    default_output: bpy.props.StringProperty(
        name="Default Output Path",
        subtype='DIR_PATH',
        default='//renders/'
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "default_output")
