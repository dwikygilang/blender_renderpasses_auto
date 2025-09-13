import bpy
from bpy.types import Operator
from . import nodes

class RENDER_OT_setup_renderpasses(Operator):
    bl_idname = "rpa.setup_renderpasses"
    bl_label = "Setup Render Passes"
    bl_description = "Setup render engine, view layer passes and compositing nodes according to settings"

    def execute(self, context):
        scene = context.scene

        scene.render.engine = 'CYCLES'
        try:
            scene.cycles.device = 'GPU'
        except Exception:
            pass
        scene.cycles.samples = scene.rpa_samples

        nodes.setup_view_layers(context)
        nodes.setup_render_nodes(context)

        self.report({'INFO'}, "Render passes, view layers & nodes setup complete.")
        return {'FINISHED'}

class RENDER_OT_clear_nodes(Operator):
    bl_idname = "rpa.clear_nodes"
    bl_label = "Clear Nodes"
    bl_description = "Clear all nodes in current compositor tree"

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        nodes.clear_render_nodes(context)
        self.report({'INFO'}, "All nodes deleted.")
        return {'FINISHED'}
