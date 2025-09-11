bl_info = {
    "name": "Blender RenderPasses Auto",
    "author": "Dwiky Gilang Imrodhani",
    "version": (0, 1),
    "blender": (4, 5, 1),
    "location": "Compositing > Sidebar > Templates",
    "description": "Auto create a renderpasses on workspace compositing.",
    "category": "Compositing",
}

import bpy

# =========================
# Function tambah node 01 NodeTree
# =========================
def setup_render_properties(context):
    scene = context.scene

    # ======================
    # Render Engine → Cycles
    # ======================
    scene.render.engine = 'CYCLES'

    # ======================
    # Device → GPU
    # ======================
    scene.cycles.device = 'GPU'

    # ======================
    # Sampling
    # ======================
    scene.cycles.use_denoising = True  # Render Denoise aktif
    scene.cycles.samples = 128  # Bisa disesuaikan
    scene.cycles.preview_denoising = True  # Viewport denoise aktif

    # ======================
    # Simplify Aktif
    # ======================
    scene.render.use_simplify = True
    scene.render.simplify_subdivision = 2   # Contoh level, bisa disesuaikan
    scene.render.simplify_child_particles = 0.5  # Contoh
    

    print("Render Properties sudah diatur ke Cycles + GPU + Denoise + Simplify")

# =========================
# Function Setup View Layers node 01 NodeTree
# =========================
def setup_view_layers(context):
    """
    Setup View Layer di Blender 4.5:
    - Data Passes: Combined, Z, Mist, Normal, Vector
    - Light Passes: Diffuse Color, Glossy Color, Ambient Occlusion
    - Light Groups: LGKeyLight, LGNeon, LG_INT_FILL, LGFillLight, LGAmbientLight
    """
    view_layer = context.view_layer
    if view_layer is None:
        print("Tidak ada View Layer aktif")
        return

    # =========================
    # Data Passes
    # =========================
    view_layer.use_pass_combined = True
    view_layer.use_pass_z = True
    view_layer.use_pass_mist = True
    view_layer.use_pass_normal = True
    view_layer.use_pass_vector = True
    view_layer.cycles.use_denoising = True
    view_layer.cycles.denoising_store_passes = True
    view_layer.cycles.use_pass_denoising_data = True

    # =========================
    # Light Passes
    # =========================
    view_layer.use_pass_diffuse_color = True
    view_layer.use_pass_glossy_direct = True
    view_layer.use_pass_glossy_indirect = True
    view_layer.use_pass_glossy_color = True
    view_layer.cycles.use_pass_volume_direct = True
    view_layer.use_pass_ambient_occlusion = True
    view_layer.cycles.use_pass_shadow_catcher = True

    # =========================
    # Cryptomatte
    # =========================
    view_layer.use_pass_cryptomatte_object = True
    view_layer.use_pass_cryptomatte_material = True
    view_layer.use_pass_cryptomatte_asset = True


    # =========================
    # Setup Light Groups
    # =========================
    light_groups = ["LGKeyLight", "LGNeon", "LG_INT_FILL", "LGFillLight", "LGAmbientLight"]

    # Ambil view layer aktif
    view_layer = bpy.context.view_layer

    # Tambahkan Light Groups ke View Layer jika belum ada
    existing_lgs = [lg.name for lg in view_layer.lightgroups]

    for group_name in light_groups:
        if group_name not in existing_lgs:
            lg = view_layer.lightgroups.add()
            lg.name = group_name
            print(f"Light Group '{group_name}' ditambahkan ke View Layer.")
        else:
            print(f"Light Group '{group_name}' sudah ada.")


    print("View Layer, Passes, dan Light Groups telah diatur untuk Blender 4.5")


def set_File_Output_nodes(context, file_output_node):
    # =====================
    # Atur Properti Node
    # =====================

    # Set direktori output
    file_output_node.base_path = "//TOLONG-DIGANTI-YAAAAA"

    # Set format file
    file_output_node.format.file_format = 'OPEN_EXR_MULTILAYER'
    file_output_node.format.color_depth = '16'  # Float (Half)
    file_output_node.format.exr_codec = 'ZIP'
    file_output_node.format.color_mode = 'RGB'  # bisa juga RGB, BW, dll.

    # =====================
    # Atur Warna Node (Biru)
    # =====================
    file_output_node.use_custom_color = True
    file_output_node.color = (0.2, 0.4, 1.0)  # RGB biru (0-1)
    file_output_node.location = (600, -60)
    file_output_node.hide = True
    # Cari socket input yang namanya 'Image' dan hapus
    for input_socket in file_output_node.inputs:
        if input_socket.name == "Image":
            file_output_node.file_slots.remove(input_socket)
            break
    # =====================
    # Tambahkan Output Slot (jika perlu)
    # =====================
    desired_slots = [
        "Beauty_Denoised",
        "Alpha",
        "Depth",
        "Mist",
        "Normal",
        "Vector",
        "DiffCol",
        "Glossy_Direct_Denoised",
        "Glossy_Indirect_Denoised",
        "Glossy_Color",
        "Volume_Direct_Denoised",
        "Ambient_Occlusion",
        "Shadow_Catcher",
        "CryptoObject00",
        "CryptoObject01",
        "CryptoObject02",
        "CryptoMaterial00",
        "CryptoMaterial01",
        "CryptoMaterial02",
        "CryptoAsset00",
        "CryptoAsset01",
        "CryptoAsset02",
        "Noisy_Image",
        "Noisy_Shadow_Catcher",
        "Denoising_Normal",
        "Denoising_Albedo",
        "Denoising_Depth",
        "Combined_LGKeyLight_Denoised",
        "Combined_LGNeon_Denoised",
        "Combined_LG_INT_FILL_Denoised",
        "Combined_LGFillLight_Denoised",
        "Combined_LGAmbientLight_Denoised",
    ]

    existing_slots = [slot.path for slot in file_output_node.file_slots]

    for name in desired_slots:
        if name not in existing_slots:
            file_output_node.file_slots.new(name)

def add_denoise_nodes(context):
    tree = context.space_data.edit_tree
    if tree is None:
        print("No node tree in context.space_data.edit_tree")
        return None

    # Cari apakah sudah ada node Render Layers
    render_node = None
    for node in tree.nodes:
        if node.type == 'R_LAYERS':
            render_node = node
            break
    if render_node is None:
        # Jika belum ada, buat baru
        render_node = tree.nodes.new(type='CompositorNodeRLayers')
        render_node.location = (0, 0)

    # Cari apakah sudah ada node File Output
    file_output_node = None
    for node in tree.nodes:
        if node.type == 'OUTPUT_FILE':
            file_output_node = node
            break
    if file_output_node is None:
        file_output_node = tree.nodes.new(type='CompositorNodeOutputFile')
        file_output_node.location = (500, 0)
        # Bisa langsung set properti dasar kalau perlu, contoh:
        file_output_node.base_path = "//output"

    # Tambah node Denoise1
    denoise_node1 = tree.nodes.new(type='CompositorNodeDenoise')
    denoise_node1.location = (150, 500)
    denoise_node1.hide = True  # langsung sembunyikan node
    denoise_node1.use_custom_color = True
    denoise_node1.color = (0.2, 0.4, 1.0)
    # Tambah node Denoise2
    denoise_node2 = tree.nodes.new(type='CompositorNodeDenoise')
    denoise_node2.location = (150, 460)
    denoise_node2.hide = True  # langsung sembunyikan node
    denoise_node2.use_custom_color = True
    denoise_node2.color = (0.2, 0.4, 1.0)
    # Tambah node Denoise3
    denoise_node3 = tree.nodes.new(type='CompositorNodeDenoise')
    denoise_node3.location = (150, 420)
    denoise_node3.hide = True  # langsung sembunyikan node
    denoise_node3.use_custom_color = True
    denoise_node3.color = (0.2, 0.4, 1.0)
    # Tambah node Denoise4
    denoise_node4 = tree.nodes.new(type='CompositorNodeDenoise')
    denoise_node4.location = (150, 380)
    denoise_node4.hide = True  # langsung sembunyikan node
    denoise_node4.use_custom_color = True
    denoise_node4.color = (0.2, 0.4, 1.0)
    # Tambah node Denoise5
    denoise_node5 = tree.nodes.new(type='CompositorNodeDenoise')
    denoise_node5.location = (150, 340)
    denoise_node5.hide = True  # langsung sembunyikan node
    denoise_node5.use_custom_color = True
    denoise_node5.color = (0.2, 0.4, 1.0)
    # Tambah node Denoise6
    denoise_node6 = tree.nodes.new(type='CompositorNodeDenoise')
    denoise_node6.location = (150, 300)
    denoise_node6.hide = True  # langsung sembunyikan node
    denoise_node6.use_custom_color = True
    denoise_node6.color = (0.2, 0.4, 1.0)
    # Tambah node Denoise7
    denoise_node7 = tree.nodes.new(type='CompositorNodeDenoise')
    denoise_node7.location = (150, 260)
    denoise_node7.hide = True  # langsung sembunyikan node
    denoise_node7.use_custom_color = True
    denoise_node7.color = (0.2, 0.4, 1.0)
    # Tambah node Denoise8
    denoise_node8 = tree.nodes.new(type='CompositorNodeDenoise')
    denoise_node8.location = (150, 220)
    denoise_node8.hide = True  # langsung sembunyikan node
    denoise_node8.use_custom_color = True
    denoise_node8.color = (0.2, 0.4, 1.0)
    # Tambah node Denoise9
    denoise_node9 = tree.nodes.new(type='CompositorNodeDenoise')
    denoise_node9.location = (150, 180)
    denoise_node9.hide = True  # langsung sembunyikan node
    denoise_node9.use_custom_color = True
    denoise_node9.color = (0.2, 0.4, 1.0)
    # Tambah node Denoise10
    denoise_node10 = tree.nodes.new(type='CompositorNodeDenoise')
    denoise_node10.location = (150, 140)
    denoise_node10.hide = True  # langsung sembunyikan node
    denoise_node10.use_custom_color = True
    denoise_node10.color = (0.2, 0.4, 1.0)

    if "Image" in render_node.outputs and "Image" in denoise_node1.inputs:
        tree.links.new(render_node.outputs["Image"], denoise_node1.inputs["Image"])
    if "Denoising Normal" in render_node.outputs and "Normal" in denoise_node1.inputs:
        tree.links.new(render_node.outputs["Denoising Normal"], denoise_node1.inputs["Normal"])
    if "Denoising Albedo" in render_node.outputs and "Albedo" in denoise_node1.inputs:
        tree.links.new(render_node.outputs["Denoising Albedo"], denoise_node1.inputs["Albedo"])
    
    if "GlossInd" in render_node.outputs and "Image" in denoise_node3.inputs:
        tree.links.new(render_node.outputs["GlossInd"], denoise_node3.inputs["Image"])
    if "Denoising Normal" in render_node.outputs and "Normal" in denoise_node3.inputs:
        tree.links.new(render_node.outputs["Denoising Normal"], denoise_node3.inputs["Normal"])
    if "Denoising Albedo" in render_node.outputs and "Albedo" in denoise_node3.inputs:
        tree.links.new(render_node.outputs["Denoising Albedo"], denoise_node3.inputs["Albedo"])
    
    if "GlossDir" in render_node.outputs and "Image" in denoise_node2.inputs:
        tree.links.new(render_node.outputs["GlossDir"], denoise_node2.inputs["Image"])
    if "Denoising Normal" in render_node.outputs and "Normal" in denoise_node2.inputs:
        tree.links.new(render_node.outputs["Denoising Normal"], denoise_node2.inputs["Normal"])
    if "Denoising Albedo" in render_node.outputs and "Albedo" in denoise_node2.inputs:
        tree.links.new(render_node.outputs["Denoising Albedo"], denoise_node2.inputs["Albedo"])
    
    if "VolumeDir" in render_node.outputs and "Image" in denoise_node4.inputs:
        tree.links.new(render_node.outputs["VolumeDir"], denoise_node4.inputs["Image"])
    if "Denoising Normal" in render_node.outputs and "Normal" in denoise_node4.inputs:
        tree.links.new(render_node.outputs["Denoising Normal"], denoise_node4.inputs["Normal"])
    if "Denoising Albedo" in render_node.outputs and "Albedo" in denoise_node4.inputs:
        tree.links.new(render_node.outputs["Denoising Albedo"], denoise_node4.inputs["Albedo"])
    
    if "AO" in render_node.outputs and "Image" in denoise_node5.inputs:
        tree.links.new(render_node.outputs["AO"], denoise_node5.inputs["Image"])
    if "Denoising Normal" in render_node.outputs and "Normal" in denoise_node5.inputs:
        tree.links.new(render_node.outputs["Denoising Normal"], denoise_node5.inputs["Normal"])
    if "Denoising Albedo" in render_node.outputs and "Albedo" in denoise_node5.inputs:
        tree.links.new(render_node.outputs["Denoising Albedo"], denoise_node5.inputs["Albedo"])
    
    if "Combined_LGKeyLight" in render_node.outputs and "Image" in denoise_node6.inputs:
        tree.links.new(render_node.outputs["Combined_LGKeyLight"], denoise_node6.inputs["Image"])
    if "Denoising Normal" in render_node.outputs and "Normal" in denoise_node6.inputs:
        tree.links.new(render_node.outputs["Denoising Normal"], denoise_node6.inputs["Normal"])
    if "Denoising Albedo" in render_node.outputs and "Albedo" in denoise_node6.inputs:
        tree.links.new(render_node.outputs["Denoising Albedo"], denoise_node6.inputs["Albedo"])
    
    if "Combined_LGNeon" in render_node.outputs and "Image" in denoise_node7.inputs:
        tree.links.new(render_node.outputs["Combined_LGNeon"], denoise_node7.inputs["Image"])
    if "Denoising Normal" in render_node.outputs and "Normal" in denoise_node7.inputs:
        tree.links.new(render_node.outputs["Denoising Normal"], denoise_node7.inputs["Normal"])
    if "Denoising Albedo" in render_node.outputs and "Albedo" in denoise_node7.inputs:
        tree.links.new(render_node.outputs["Denoising Albedo"], denoise_node7.inputs["Albedo"])
    
    if "Combined_LG_INT_FILL" in render_node.outputs and "Image" in denoise_node8.inputs:
        tree.links.new(render_node.outputs["Combined_LG_INT_FILL"], denoise_node8.inputs["Image"])
    if "Denoising Normal" in render_node.outputs and "Normal" in denoise_node8.inputs:
        tree.links.new(render_node.outputs["Denoising Normal"], denoise_node8.inputs["Normal"])
    if "Denoising Albedo" in render_node.outputs and "Albedo" in denoise_node8.inputs:
        tree.links.new(render_node.outputs["Denoising Albedo"], denoise_node8.inputs["Albedo"])
    
    if "Combined_LGFillLight" in render_node.outputs and "Image" in denoise_node9.inputs:
        tree.links.new(render_node.outputs["Combined_LGFillLight"], denoise_node9.inputs["Image"])
    if "Denoising Normal" in render_node.outputs and "Normal" in denoise_node9.inputs:
        tree.links.new(render_node.outputs["Denoising Normal"], denoise_node9.inputs["Normal"])
    if "Denoising Albedo" in render_node.outputs and "Albedo" in denoise_node9.inputs:
        tree.links.new(render_node.outputs["Denoising Albedo"], denoise_node9.inputs["Albedo"])
        
    if "Combined_LGAmbientLight" in render_node.outputs and "Image" in denoise_node10.inputs:
        tree.links.new(render_node.outputs["Combined_LGAmbientLight"], denoise_node10.inputs["Image"])
    if "Denoising Normal" in render_node.outputs and "Normal" in denoise_node10.inputs:
        tree.links.new(render_node.outputs["Denoising Normal"], denoise_node10.inputs["Normal"])
    if "Denoising Albedo" in render_node.outputs and "Albedo" in denoise_node10.inputs:
        tree.links.new(render_node.outputs["Denoising Albedo"], denoise_node10.inputs["Albedo"])
    
    
    if "Alpha" in render_node.outputs and "Alpha" in file_output_node.inputs:
        tree.links.new(render_node.outputs["Alpha"], file_output_node.inputs["Alpha"])
    if "Depth" in render_node.outputs and "Depth" in file_output_node.inputs:
        tree.links.new(render_node.outputs["Depth"], file_output_node.inputs["Depth"])
    if "Mist" in render_node.outputs and "Mist" in file_output_node.inputs:
        tree.links.new(render_node.outputs["Mist"], file_output_node.inputs["Mist"])
    if "Normal" in render_node.outputs and "Normal" in file_output_node.inputs:
        tree.links.new(render_node.outputs["Normal"], file_output_node.inputs["Normal"])
    if "Vector" in render_node.outputs and "Vector" in file_output_node.inputs:
        tree.links.new(render_node.outputs["Vector"], file_output_node.inputs["Vector"])
    if "DiffCol" in render_node.outputs and "DiffCol" in file_output_node.inputs:
        tree.links.new(render_node.outputs["DiffCol"], file_output_node.inputs["DiffCol"])
    if "GlossCol" in render_node.outputs and "Glossy_Color" in file_output_node.inputs:
        tree.links.new(render_node.outputs["GlossCol"], file_output_node.inputs["Glossy_Color"])
    if "Shadow Catcher" in render_node.outputs and "Shadow_Catcher" in file_output_node.inputs:
        tree.links.new(render_node.outputs["Shadow Catcher"], file_output_node.inputs["Shadow_Catcher"])
    if "CryptoObject00" in render_node.outputs and "CryptoObject00" in file_output_node.inputs:
        tree.links.new(render_node.outputs["CryptoObject00"], file_output_node.inputs["CryptoObject00"])
    if "CryptoObject01" in render_node.outputs and "CryptoObject01" in file_output_node.inputs:
        tree.links.new(render_node.outputs["CryptoObject01"], file_output_node.inputs["CryptoObject01"])
    if "CryptoObject02" in render_node.outputs and "CryptoObject02" in file_output_node.inputs:
        tree.links.new(render_node.outputs["CryptoObject02"], file_output_node.inputs["CryptoObject02"])
    if "CryptoMaterial00" in render_node.outputs and "CryptoMaterial00" in file_output_node.inputs:
        tree.links.new(render_node.outputs["CryptoMaterial00"], file_output_node.inputs["CryptoMaterial00"])
    if "CryptoMaterial01" in render_node.outputs and "CryptoMaterial01" in file_output_node.inputs:
        tree.links.new(render_node.outputs["CryptoMaterial01"], file_output_node.inputs["CryptoMaterial01"])
    if "CryptoMaterial02" in render_node.outputs and "CryptoMaterial02" in file_output_node.inputs:
        tree.links.new(render_node.outputs["CryptoMaterial02"], file_output_node.inputs["CryptoMaterial02"])
    if "CryptoAsset00" in render_node.outputs and "CryptoAsset00" in file_output_node.inputs:
        tree.links.new(render_node.outputs["CryptoAsset00"], file_output_node.inputs["CryptoAsset00"])
    if "CryptoAsset01" in render_node.outputs and "CryptoAsset01" in file_output_node.inputs:
        tree.links.new(render_node.outputs["CryptoAsset01"], file_output_node.inputs["CryptoAsset01"])
    if "CryptoAsset02" in render_node.outputs and "CryptoAsset02" in file_output_node.inputs:
        tree.links.new(render_node.outputs["CryptoAsset02"], file_output_node.inputs["CryptoAsset02"])
    if "Noisy Image" in render_node.outputs and "Noisy_Image" in file_output_node.inputs:
        tree.links.new(render_node.outputs["Noisy Image"], file_output_node.inputs["Noisy_Image"])
    if "Noisy shadow Catcher" in render_node.outputs and "Noisy_Shadow_Catcher" in file_output_node.inputs:
        tree.links.new(render_node.outputs["Noisy Shadow Catcher"], file_output_node.inputs["Noisy_Shadow_Catcher"])
    if "Denoising Normal" in render_node.outputs and "Denoising_Normal" in file_output_node.inputs:
        tree.links.new(render_node.outputs["Denoising Normal"], file_output_node.inputs["Denoising_Normal"])
    if "Denoising Albedo" in render_node.outputs and "Denoising_Albedo" in file_output_node.inputs:
        tree.links.new(render_node.outputs["Denoising Albedo"], file_output_node.inputs["Denoising_Albedo"])
    if "Denoising Depth" in render_node.outputs and "Denoising_Depth" in file_output_node.inputs:
        tree.links.new(render_node.outputs["Denoising Depth"], file_output_node.inputs["Denoising_Depth"])
    

    # Hubungkan output Denoise ke File Output node (Input 'Image')
    if "Image" in denoise_node1.outputs and "Beauty_Denoised" in file_output_node.inputs:
        tree.links.new(denoise_node1.outputs["Image"], file_output_node.inputs["Beauty_Denoised"])
    if "Image" in denoise_node2.outputs and "Glossy_Direct_Denoised" in file_output_node.inputs:
        tree.links.new(denoise_node2.outputs["Image"], file_output_node.inputs["Glossy_Direct_Denoised"])
    if "Image" in denoise_node3.outputs and "Glossy_Indirect_Denoised" in file_output_node.inputs:
        tree.links.new(denoise_node3.outputs["Image"], file_output_node.inputs["Glossy_Indirect_Denoised"])
    if "Image" in denoise_node4.outputs and "Volume_Direct_Denoised" in file_output_node.inputs:
        tree.links.new(denoise_node4.outputs["Image"], file_output_node.inputs["Volume_Direct_Denoised"])
    if "Image" in denoise_node5.outputs and "Ambient_Occlusion" in file_output_node.inputs:
        tree.links.new(denoise_node5.outputs["Image"], file_output_node.inputs["Ambient_Occlusion"])
    if "Image" in denoise_node6.outputs and "Combined_LGKeyLight_Denoised" in file_output_node.inputs:
        tree.links.new(denoise_node6.outputs["Image"], file_output_node.inputs["Combined_LGKeyLight_Denoised"])
    if "Image" in denoise_node7.outputs and "Combined_LGNeon_Denoised" in file_output_node.inputs:
        tree.links.new(denoise_node7.outputs["Image"], file_output_node.inputs["Combined_LGNeon_Denoised"])
    if "Image" in denoise_node8.outputs and "Combined_LG_INT_FILL_Denoised" in file_output_node.inputs:
        tree.links.new(denoise_node8.outputs["Image"], file_output_node.inputs["Combined_LG_INT_FILL_Denoised"])
    if "Image" in denoise_node9.outputs and "Combined_LGFillLight_Denoised" in file_output_node.inputs:
        tree.links.new(denoise_node9.outputs["Image"], file_output_node.inputs["Combined_LGFillLight_Denoised"])
    if "Image" in denoise_node10.outputs and "Combined_LGAmbientLight_Denoised" in file_output_node.inputs:
        tree.links.new(denoise_node10.outputs["Image"], file_output_node.inputs["Combined_LGAmbientLight_Denoised"])

#    return denoise_node1, render_node, file_output_node     

def add_render_and_output_nodes(context):
    bpy.context.scene.use_nodes = True
    bpy.context.scene.render.use_compositing = True
    tree = bpy.context.scene.node_tree
    for node in tree.nodes:
        tree.nodes.remove(node)
    setup_render_properties(context)
    setup_view_layers(bpy.context)
    
    tree = context.space_data.edit_tree
    if tree is None:
        return

    # Tambah Render Layers node
    render_node = tree.nodes.new(type='CompositorNodeRLayers')
    render_node.location = (-500, -100)
    render_node.hide = True
    render_node.use_custom_color = True
    render_node.color = (0.2, 0.4, 1.0)  # RGB biru (0-1)
    
    # Tambah File Output node
    file_output_node = tree.nodes.new(type='CompositorNodeOutputFile')
    file_output_node.location = (300, 0)
    file_output_node.color = (0.2, 0.4, 1.0)  # RGB biru (0-1)
    file_output_node.hide = True

    # Panggil fungsi set_File_Output_nodes dan kirim file_output_node sebagai parameter
    set_File_Output_nodes(context, file_output_node)
    
    add_denoise_nodes(bpy.context)



# =========================
# Operator: Tambah Node
# =========================
class TEMPLATE_OT_add_nodes(bpy.types.Operator):
    bl_idname = "template.add_nodes"
    bl_label = "Tambah Render + Output"
    bl_description = "Menambahkan Render Layers dan File Output Node"

    def execute(self, context):
        add_render_and_output_nodes(context)
        self.report({'INFO'}, "Node Render Layers & File Output ditambahkan!")
        return {'FINISHED'}


# =========================
# Operator: Hapus Node dengan konfirmasi
# =========================
class TEMPLATE_OT_clear_nodes(bpy.types.Operator):
    bl_idname = "template.clear_nodes"
    bl_label = "Hapus Semua Node"
    bl_description = "Menghapus semua node di NodeTree Compositing"

    confirm: bpy.props.BoolProperty(default=False)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Are you sure you want to delete all nodes?")

    def execute(self, context):
        tree = context.space_data.edit_tree
        if tree is not None:
            tree.nodes.clear()
            self.report({'INFO'}, "All Nodes has been Deleted!")
        else:
            self.report({'WARNING'}, "Tidak ada NodeTree aktif!")
        return {'FINISHED'}


# =========================
# Panel Sidebar
# =========================
class TEMPLATE_PT_panel(bpy.types.Panel):
    bl_label = "Templates"
    bl_idname = "TEMPLATE_PT_panel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Template"

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'CompositorNodeTree'

    def draw(self, context):
        layout = self.layout
        layout.label(text="Just Click button below")
        layout.operator("template.add_nodes", text="Templates 01")
        layout.operator("template.clear_nodes", text="Delete NodeTree")


# =========================
# Register & Unregister
# =========================
classes = [
    TEMPLATE_PT_panel,
    TEMPLATE_OT_clear_nodes,
    TEMPLATE_OT_add_nodes
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
