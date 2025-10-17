bl_info = {
    "name": "GoldSrc Map Exporter",
    "author": "Quentin Lurkin",
    "version": (0, 1),
    "blender": (4, 0, 0),
    "location": "File > Export > GoldSrc .map",
    "description": "Exports Blender meshes Blender to .map file format for CS 1.5 / Half-Life",
    "category": "Import-Export",
}

import bpy  # noqa: E402
from bpy_extras.io_utils import ExportHelper  # noqa: E402


def show_popup(message: str, title="Info", icon="INFO"):
    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)  # type: ignore


def enum_collections(self, context):
    items = []
    for coll in bpy.data.collections:
        items.append((coll.name, coll.name, f"Exporter la collection {coll.name}"))
    return items


class ExportGoldSrcMap(bpy.types.Operator, ExportHelper):  # type: ignore
    bl_idname = "export_scene.goldsrc_map"
    bl_label = "Export to GoldSrc (.map)"
    filename_ext = ".map"

    collection_name: bpy.props.EnumProperty(
        name="Collection",
        description="Choisir la collection à exporter",
        items=enum_collections,
    )  # type: ignore

    def invoke(self, context, event):  # type: ignore
        wm = context.window_manager
        return wm.invoke_props_dialog(self)  # type: ignore

    def execute(self, context):  # type: ignore
        """
        Export the `EXPORT` collection
        """
        collection = bpy.data.collections.get(self.collection_name)

        if not collection:
            show_popup(
                f"Collection '{self.collection_name}' introuvable.",
                title="Erreur",
                icon="ERROR",
            )
            return {"CANCELLED"}

        depsgraph = context.evaluated_depsgraph_get()
        meshes_found = False

        with open(self.filepath, "w") as f:  # type: ignore
            for obj in collection.objects:
                if obj.type != "MESH":
                    continue

                meshes_found = True
                mesh = obj.evaluated_get(depsgraph).to_mesh()
                f.write(f"// --- {obj.name} ---\n")

                for v in mesh.vertices:
                    co_world = obj.matrix_world @ v.co
                    f.write(f"v {co_world.x:.6f} {co_world.y:.6f} {co_world.z:.6f}\n")

                for poly in mesh.polygons:
                    verts = " ".join(str(i) for i in poly.vertices)
                    f.write(f"f {verts}\n")

                obj.to_mesh_clear()

        if not meshes_found:
            show_popup(
                f"Aucun mesh trouvé dans la collection '{self.collection_name}'.",
                title="Avertissement",
                icon="ERROR",
            )
            return {"CANCELLED"}

        show_popup(f"Export terminé : {self.filepath}", title="Succès", icon="INFO")  # type: ignore
        return {"FINISHED"}


def menu_func_export(self, context):
    self.layout.operator(ExportGoldSrcMap.bl_idname, text="GoldSrc Map (.map)")  # type: ignore


def register():
    bpy.utils.register_class(ExportGoldSrcMap)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportGoldSrcMap)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()
