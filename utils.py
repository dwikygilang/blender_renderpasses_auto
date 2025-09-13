import bpy

def ensure_compositor_space(context):
    area = context.area
    if area and area.type == 'NODE_EDITOR':
        space = area.spaces.active
        if space and space.tree_type == 'CompositorNodeTree':
            return space.edit_tree
    if context.scene is not None:
        context.scene.use_nodes = True
        return context.scene.node_tree
    return None
