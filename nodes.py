import bpy

def setup_view_layers(context):
    view_layer = context.view_layer
    scene = context.scene
    if view_layer is None:
        return
    scene.render.engine = 'CYCLES'
    view_layer.use_pass_combined = bool(getattr(scene, "rpa_pass_combined", True))
    view_layer.use_pass_z = bool(getattr(scene, "rpa_pass_z", True))
    view_layer.use_pass_mist = bool(getattr(scene, "rpa_pass_mist", True))
    view_layer.use_pass_normal = bool(getattr(scene, "rpa_pass_normal", True))
    view_layer.use_pass_vector = bool(getattr(scene, "rpa_pass_vector", True))
    if hasattr(view_layer, "cycles") and view_layer.cycles:
        view_layer.cycles.use_denoising = bool(getattr(scene, "rpa_denoise", True))
        view_layer.cycles.denoising_store_passes = bool(getattr(scene, "rpa_denoise", True))
        view_layer.cycles.use_pass_denoising_data = bool(getattr(scene, "rpa_denoise", True))
        view_layer.cycles.use_pass_volume_direct = True
        view_layer.cycles.use_pass_shadow_catcher = True
    view_layer.use_pass_diffuse_color = bool(getattr(scene, "rpa_pass_diffuse", True))
    view_layer.use_pass_diffuse_direct = bool(getattr(scene, "rpa_pass_diffuse", True))
    view_layer.use_pass_diffuse_indirect = bool(getattr(scene, "rpa_pass_diffuse", True))
    view_layer.use_pass_glossy_direct = bool(getattr(scene, "rpa_pass_glossy", True))
    view_layer.use_pass_glossy_indirect = bool(getattr(scene, "rpa_pass_glossy", True))
    view_layer.use_pass_glossy_color = bool(getattr(scene, "rpa_pass_glossy", True))
    view_layer.use_pass_ambient_occlusion = bool(getattr(scene, "rpa_pass_ambient_occlusion", True))
    view_layer.use_pass_cryptomatte_object = bool(getattr(scene, "rpa_pass_cryptomatte", True))
    view_layer.use_pass_cryptomatte_material = bool(getattr(scene, "rpa_pass_cryptomatte", True))
    view_layer.use_pass_cryptomatte_asset = bool(getattr(scene, "rpa_pass_cryptomatte", True))
    if hasattr(view_layer, "lightgroups"):
        light_groups = ["LGKeyLight", "LGNeon", "LG_INT_FILL", "LGFillLight", "LGAmbientLight"]
        existing = [lg.name for lg in view_layer.lightgroups]
        for g in light_groups:
            if g not in existing:
                lg = view_layer.lightgroups.add()
                lg.name = g

def setup_render_nodes(context):
    scene = context.scene
    if not scene.use_nodes:
        scene.use_nodes = True
    tree = scene.node_tree
    if tree is None:
        scene.use_nodes = True
        tree = scene.node_tree
    # clear nodes
    try:
        tree.nodes.clear()
    except Exception:
        for n in list(tree.nodes):
            tree.nodes.remove(n)

    render_node = create_render_layers_node(tree)
    file_output_node = create_file_output_node(tree, base_path=getattr(scene, "rpa_output_path", "//renders/"))
    configure_file_output_slots(file_output_node, scene)

    denoise_nodes = {}
    if getattr(scene, "rpa_denoise", True):
        candidates = [
            ("Image", "Beauty_Denoised", "rpa_denoise_combined"),
            ("DiffCol", "Diffuse_Denoised", "rpa_denoise_diffuse"),
            ("GlossCol", "Glossy_Denoised", "rpa_denoise_glossy"),
            ("VolumeDir", "Volume_Denoised", "rpa_denoise_volume"),
            ("AO", "AO_Denoised", "rpa_denoise_ao"),
        ]
        index = 0
        for render_out, slot_name, prop in candidates:
            if getattr(scene, prop, False) and render_out in render_node.outputs:
                dn = add_denoise_for_pass(tree, render_node, file_output_node, render_out, slot_name, index)
                if dn:
                    denoise_nodes[render_out] = dn
                    index += 1

        if getattr(scene, "rpa_denoise_lightgroups", False):
            lg_names = [
                "Combined_LGKeyLight", "Combined_LGNeon", "Combined_LG_INT_FILL",
                "Combined_LGFillLight", "Combined_LGAmbientLight"
            ]
            for lg in lg_names:
                slot = f"{lg}_Denoised"
                if lg in render_node.outputs:
                    dn = add_denoise_for_pass(tree, render_node, file_output_node, lg, slot, index)
                    if dn:
                        denoise_nodes[lg] = dn
                        index += 1

    connect_passes_to_file_output(tree, render_node, file_output_node, scene, denoise_nodes)

def clear_render_nodes(context):
    scene = context.scene
    if scene.use_nodes and scene.node_tree:
        try:
            scene.node_tree.nodes.clear()
        except Exception:
            for n in list(scene.node_tree.nodes):
                scene.node_tree.nodes.remove(n)

def create_render_layers_node(tree):
    node = tree.nodes.new(type='CompositorNodeRLayers')
    node.location = (-500, 0)
    node.hide = True
    node.use_custom_color = True
    node.color = (0.2, 0.4, 1.0)
    return node

def create_file_output_node(tree, base_path="//renders/"):
    node = tree.nodes.new(type='CompositorNodeOutputFile')
    node.location = (400, 0)
    node.hide = True
    node.use_custom_color = True
    node.color = (0.2, 0.4, 1.0)
    node.base_path = base_path
    # Hapus socket input default "Image" (jika ada)
    for inp in list(node.inputs):
        try:
            if inp.name.lower() == "image":
                node.inputs.remove(inp)
        except Exception:
            pass
    # Hapus semua file_slots (kadang ada default)
    try:
        for s in list(node.file_slots):
            node.file_slots.remove(s)
    except Exception:
        pass
    return node

def configure_file_output_slots(file_output_node, scene):
    slots = []
    if getattr(scene, "rpa_pass_combined", True):
        slots.append("Combined")
    if getattr(scene, "rpa_pass_z", True):
        slots.append("Depth")
    if getattr(scene, "rpa_pass_mist", True):
        slots.append("Mist")
    if getattr(scene, "rpa_pass_normal", True):
        slots.append("Normal")
    if getattr(scene, "rpa_pass_vector", True):
        slots.append("Vector")
    if getattr(scene, "rpa_pass_diffuse", True):
        slots.append("DiffCol")
    if getattr(scene, "rpa_pass_glossy", True):
        slots.append("GlossCol")
    if getattr(scene, "rpa_pass_ambient_occlusion", True):
        slots.append("Ambient_Occlusion")
    if getattr(scene, "rpa_pass_cryptomatte", True):
        slots.extend([
            "CryptoObject00","CryptoObject01","CryptoObject02",
            "CryptoMaterial00","CryptoMaterial01","CryptoMaterial02",
            "CryptoAsset00","CryptoAsset01","CryptoAsset02"
        ])
    if getattr(scene, "rpa_denoise", True):
        if getattr(scene, "rpa_denoise_combined", True):
            slots.append("Beauty_Denoised")
        if getattr(scene, "rpa_denoise_diffuse", True):
            slots.append("Diffuse_Denoised")
        if getattr(scene, "rpa_denoise_glossy", True):
            slots.append("Glossy_Denoised")
        if getattr(scene, "rpa_denoise_volume", True):
            slots.append("Volume_Denoised")
        if getattr(scene, "rpa_denoise_ao", True):
            slots.append("AO_Denoised")
        if getattr(scene, "rpa_denoise_lightgroups", True):
            slots.extend([
                "Combined_LGKeyLight_Denoised","Combined_LGNeon_Denoised","Combined_LG_INT_FILL_Denoised",
                "Combined_LGFillLight_Denoised","Combined_LGAmbientLight_Denoised"
            ])
        slots.extend(["Denoising_Normal","Denoising_Albedo","Denoising_Depth","Noisy_Image","Noisy_Shadow_Catcher"])
    existing = [s.path for s in file_output_node.file_slots]
    for s in slots:
        if s not in existing:
            try:
                file_output_node.file_slots.new(s)
            except Exception:
                pass
    fmt = file_output_node.format
    fmt.file_format = 'OPEN_EXR_MULTILAYER'
    fmt.color_depth = '16'
    fmt.exr_codec = 'ZIP'
    fmt.color_mode = 'RGB'

def add_denoise_for_pass(tree, render_node, file_output_node, render_out_name, denoised_slot_name, index=0):
    denoise = tree.nodes.new(type='CompositorNodeDenoise')
    denoise.label = f"Denoise {render_out_name}"
    denoise.location = (render_node.location.x + 400, render_node.location.y + (index * 40))
    denoise.use_custom_color = True
    denoise.color = (0.2, 0.4, 1.0)
    denoise.hide = True

    links = tree.links
    try:
        if render_out_name in render_node.outputs and denoise.inputs.get("Image"):
            links.new(render_node.outputs[render_out_name], denoise.inputs["Image"])
    except Exception:
        pass
    try:
        if "Denoising Normal" in render_node.outputs and denoise.inputs.get("Normal"):
            links.new(render_node.outputs["Denoising Normal"], denoise.inputs["Normal"])
    except Exception:
        pass
    try:
        if "Denoising Albedo" in render_node.outputs and denoise.inputs.get("Albedo"):
            links.new(render_node.outputs["Denoising Albedo"], denoise.inputs["Albedo"])
    except Exception:
        pass

    existing = [s.path for s in file_output_node.file_slots]
    if denoised_slot_name not in existing:
        try:
            file_output_node.file_slots.new(denoised_slot_name)
        except Exception:
            pass

    if denoise.outputs.get("Image") and denoised_slot_name in file_output_node.inputs:
        try:
            links.new(denoise.outputs["Image"], file_output_node.inputs[denoised_slot_name])
        except Exception:
            pass

    return denoise

def connect_passes_to_file_output(tree, render_node, file_output_node, scene, denoise_nodes=None):
    links = tree.links
    mapping = {
        "Image": "Combined",
        "Alpha": "Alpha",
        "Depth": "Depth",
        "Mist": "Mist",
        "Normal": "Normal",
        "Vector": "Vector",
        "DiffDir": "DiffDir",
        "DiffInd": "DiffInd",
        "DiffCol": "DiffCol",
        "GlossCol": "GlossCol",
        "AO": "Ambient_Occlusion",
        "CryptoObject00": "CryptoObject00",
        "CryptoObject01": "CryptoObject01",
        "CryptoObject02": "CryptoObject02",
        "CryptoMaterial00": "CryptoMaterial00",
        "CryptoMaterial01": "CryptoMaterial01",
        "CryptoMaterial02": "CryptoMaterial02",
        "CryptoAsset00": "CryptoAsset00",
        "CryptoAsset01": "CryptoAsset01",
        "CryptoAsset02": "CryptoAsset02",
        "Noisy Image": "Noisy_Image",
        "Noisy Shadow Catcher": "Noisy_Shadow_Catcher",
        "Denoising Normal": "Denoising_Normal",
        "Denoising Albedo": "Denoising_Albedo",
        "Denoising Depth": "Denoising_Depth",
    }
    for src, dst in mapping.items():
        try:
            if src in render_node.outputs and dst in file_output_node.inputs:
                links.new(render_node.outputs[src], file_output_node.inputs[dst])
        except Exception:
            pass
    # denoise_nodes are already linked inside add_denoise_for_pass
    return
