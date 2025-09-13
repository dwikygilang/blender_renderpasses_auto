bl_info = {
    "name": "Blender RenderPasses Auto",
    "author": "Dwiky Gilang Imrodhani",
    "version": (0, 1),
    "blender": (4, 5, 1),
    "location": "Properties > Render > Render Passes Auto",
    "description": "Auto create render passes and node setup for compositing.",
    "category": "Compositing",
}

import bpy

from .preferences import RenderPassesPreferences
from .ui import RENDER_PT_renderpasses_panel
from .operators import RENDER_OT_setup_renderpasses, RENDER_OT_clear_nodes

classes = (
    RenderPassesPreferences,
    RENDER_PT_renderpasses_panel,
    RENDER_OT_setup_renderpasses,
    RENDER_OT_clear_nodes,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    from bpy.props import BoolProperty, IntProperty, StringProperty
    scene = bpy.types.Scene

    scene.rpa_output_path = StringProperty(
        name="Output Path",
        description="Base path for File Output nodes",
        default="//renders/",
        subtype='DIR_PATH'
    )

    scene.rpa_samples = IntProperty(
        name="Samples",
        description="Render samples (render engine Cycles)",
        default=128,
        min=1,
        max=32768
    )

    scene.rpa_pass_combined = BoolProperty(name="Combined", default=True)
    scene.rpa_pass_z = BoolProperty(name="Depth (Z)", default=True)
    scene.rpa_pass_mist = BoolProperty(name="Mist", default=True)
    scene.rpa_pass_normal = BoolProperty(name="Normal", default=True)
    scene.rpa_pass_vector = BoolProperty(name="Vector", default=True)
    scene.rpa_pass_diffuse = BoolProperty(name="Diffuse", default=True)
    scene.rpa_pass_glossy = BoolProperty(name="Glossy", default=True)
    scene.rpa_pass_ambient_occlusion = BoolProperty(name="Ambient Occlusion", default=True)
    scene.rpa_pass_cryptomatte = BoolProperty(name="Cryptomatte", default=True)

    scene.rpa_denoise = BoolProperty(name="Enable Global Denoise", default=True)
    scene.rpa_denoise_combined = BoolProperty(name="Denoise Combined", default=True)
    scene.rpa_denoise_diffuse = BoolProperty(name="Denoise Diffuse", default=True)
    scene.rpa_denoise_glossy = BoolProperty(name="Denoise Glossy", default=True)
    scene.rpa_denoise_volume = BoolProperty(name="Denoise Volume", default=True)
    scene.rpa_denoise_ao = BoolProperty(name="Denoise AO", default=True)
    scene.rpa_denoise_lightgroups = BoolProperty(name="Denoise Light Groups", default=True)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    scene = bpy.types.Scene
    props = [
        'rpa_output_path', 'rpa_samples', 'rpa_pass_combined', 'rpa_pass_z',
        'rpa_pass_mist', 'rpa_pass_normal', 'rpa_pass_vector', 'rpa_pass_diffuse',
        'rpa_pass_glossy', 'rpa_pass_ambient_occlusion', 'rpa_pass_cryptomatte',
        'rpa_denoise','rpa_denoise_combined','rpa_denoise_diffuse','rpa_denoise_glossy',
        'rpa_denoise_volume','rpa_denoise_ao','rpa_denoise_lightgroups'
    ]
    for p in props:
        if hasattr(scene, p):
            delattr(scene, p)
