import bpy
from .operators import RENDER_OT_setup_renderpasses, RENDER_OT_clear_nodes

class RENDER_PT_renderpasses_panel(bpy.types.Panel):
    bl_label = "Render Passes Auto"
    bl_idname = "RENDER_PT_renderpasses_auto"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "rpa_output_path")
        layout.prop(scene, "rpa_samples")

        layout.separator()
        layout.label(text="Enable Render Passes")
        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(scene, "rpa_pass_combined")
        row.prop(scene, "rpa_pass_z")
        row = col.row(align=True)
        row.prop(scene, "rpa_pass_mist")
        row.prop(scene, "rpa_pass_normal")
        row = col.row(align=True)
        row.prop(scene, "rpa_pass_vector")
        row.prop(scene, "rpa_pass_diffuse")
        row = col.row(align=True)
        row.prop(scene, "rpa_pass_glossy")
        row.prop(scene, "rpa_pass_ambient_occlusion")
        row = col.row(align=True)
        row.prop(scene, "rpa_pass_cryptomatte")

        layout.separator()
        layout.label(text="Denoise Options")
        layout.prop(scene, "rpa_denoise")
        row = layout.row(align=True)
        row.prop(scene, "rpa_denoise_combined")
        row.prop(scene, "rpa_denoise_diffuse")
        row = layout.row(align=True)
        row.prop(scene, "rpa_denoise_glossy")
        row.prop(scene, "rpa_denoise_volume")
        row = layout.row(align=True)
        row.prop(scene, "rpa_denoise_ao")
        row.prop(scene, "rpa_denoise_lightgroups")

        layout.separator()
        layout.operator(RENDER_OT_setup_renderpasses.bl_idname, text="Setup Render")
        layout.operator(RENDER_OT_clear_nodes.bl_idname, text="Clear Nodes")
