import bpy
import math
import gpu
import gpu_extras.batch
import copy
from bpy_extras.io_utils import ExportHelper

# アドオンの情報
bl_info = {
    "name": "level_editor",
    "author": "Takuma Okazaki",
    "version": (4, 4),
    "blender": (4, 4, 0),
    "location": "Top Bar > Editor Menus",
    "description": "level_editor",
    "category": "Object",
}

# 1. 頂点を伸ばす機能
class MYADDON_OT_stretch_vertex(bpy.types.Operator):
    bl_idname = "myaddon.stretch_vertex"
    bl_label = "頂点を伸ばす"
    bl_description = "選択しているメッシュの頂点を伸ばします"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if obj and obj.type == 'MESH':
            obj.data.vertices[0].co.x += 1.0
            obj.data.update()
            print("頂点を伸ばしました")
            return {'FINISHED'}
        else:
            print("エラー：メッシュオブジェクト（Cubeなど）を選択してください")
            return {'CANCELLED'}

# 2. Ico Sphereを作成する機能
class MYADDON_OT_create_ico_sphere(bpy.types.Operator):
    bl_idname = "myaddon.create_ico_sphere"
    bl_label = "Ico Sphereを作成"
    bl_description = "Ico Sphereをシーンに追加します"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1)
        print("Ico Sphereを作成しました")
        return {'FINISHED'}

# 3. シーン出力（エクスポート）機能
class MYADDON_OT_export_scene(bpy.types.Operator, ExportHelper):
    bl_idname = "myaddon.export_scene"
    bl_label = "シーンをエクスポート"
    bl_description = "現在のシーンのオブジェクト情報をファイルに保存します"
    bl_options = {'REGISTER', 'UNDO'}
    
    filename_ext = ".scene"
    
    filter_glob: bpy.props.StringProperty(
        default="*.scene",
        options={'HIDDEN'},
        maxlen=255,
    )

    def show_log(self, message):
        print(message)                  
        self.report({'INFO'}, message)   

    def write_object_info(self, file, obj, level):
        indent = "    " * level
        
        file.write(f"{indent}名前: {obj.name}, 位置: {obj.location}\n")
        
        # 【新規】カスタムプロパティ（ファイル名、コライダー）の出力
        if "file_name" in obj:
            file.write(f"{indent}ファイル名: {obj['file_name']}\n")
            
        if "collider" in obj:
            file.write(f"{indent}コライダー種類: {obj['collider']}\n")
            if "collider_size" in obj:
                c_size = obj["collider_size"]
                file.write(f"{indent}コライダーサイズ: [{c_size[0]:.2f}, {c_size[1]:.2f}, {c_size[2]:.2f}]\n")
        
        trans, rot, scale = obj.matrix_local.decompose()
        rot = rot.to_euler()
        
        rot_x = math.degrees(rot.x)
        rot_y = math.degrees(rot.y)  
        rot_z = math.degrees(rot.z)
        
        file.write(f"{indent}座標: {trans}\n")
        file.write(f"{indent}回転: X:{rot_x:.2f}, Y:{rot_y:.2f}, Z:{rot_z:.2f}\n")
        file.write(f"{indent}スケール: {scale}\n") 
        
        if obj.parent:
            file.write(f"{indent}親オブジェクト: {obj.parent.name}\n")
            
        file.write(f"{indent}--------------------\n")

    def parse_scene_recursive(self, file, obj, level):
        self.write_object_info(file, obj, level)
        
        for child in obj.children:
            self.parse_scene_recursive(file, child, level + 1)

    def export(self, context):
        self.show_log(f"シーン情報出力開始... {self.filepath}")
        
        with open(self.filepath, 'w', encoding='utf-8') as file:
            file.write("SCENE\n")
            
            for obj in context.scene.objects:
                if not obj.parent:
                    self.parse_scene_recursive(file, obj, 0)

        self.show_log(f"--- エクスポート完了: {self.filepath} ---")

    def execute(self, context):
        self.export(context)
        return {'FINISHED'}

# 4. メニューの見た目や中身を定義するクラス
class TOPBAR_MT_my_menu(bpy.types.Menu):
    bl_idname = "TOPBAR_MT_my_menu"
    bl_label = "My Menu" 
    bl_description = "拡張メニュー by " + bl_info["author"]

    def draw(self, context):
        self.layout.operator("wm.url_open_preset", text="Manual", icon='HELP')
        self.layout.operator("myaddon.stretch_vertex", text="頂点を伸ばす", icon='MESH_DATA')
        self.layout.operator("myaddon.create_ico_sphere", text="Ico Sphereを作成", icon='MESH_DATA')
        self.layout.operator("myaddon.export_scene", text="シーンをエクスポート", icon='EXPORT')

# コライダー（線）を描画するクラス
class DrawCollider:
    handle = None
    
    def draw_collider():
        vertices = {"pos": []} 
        indices = []
        offsets = [
            [-0.5, -0.5, -0.5],
            [+0.5, -0.5, -0.5],
            [-0.5, +0.5, -0.5],
            [+0.5, +0.5, -0.5],
            [-0.5, -0.5, +0.5],
            [+0.5, -0.5, +0.5],                   
            [-0.5, +0.5, +0.5],
            [+0.5, +0.5, +0.5],
        ]        
        
        for obj in bpy.context.scene.objects:
            if "collider" not in obj:
                continue

            start = len(vertices["pos"])
            size = obj.get("collider_size", [2.0, 2.0, 2.0])
            
            for offset in offsets:
                pos = obj.location.copy() 
                pos[0] += offset[0] * size[0]
                pos[1] += offset[1] * size[1]
                pos[2] += offset[2] * size[2]
                vertices["pos"].append(pos)
                
            indices.append([start+0, start+1])
            indices.append([start+2, start+3])
            indices.append([start+0, start+2])
            indices.append([start+1, start+3])
            
            indices.append([start+4, start+5])
            indices.append([start+6, start+7])
            indices.append([start+4, start+6])
            indices.append([start+5, start+7])
            
            indices.append([start+0, start+4])
            indices.append([start+1, start+5])
            indices.append([start+2, start+6])
            indices.append([start+3, start+7])
        
        if not vertices["pos"]:
            return
        
        shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        batch = gpu_extras.batch.batch_for_shader(shader, "LINES", vertices, indices=indices)
        color = [0.5, 1.0, 1.0, 1.0] # 水色 (R, G, B, Alpha)
        
        shader.bind()
        shader.uniform_float("color", color)
        batch.draw(shader)

# 5. トップバーにメニューを追加するための関数
def draw_menu_button(self, context):
    self.layout.menu(TOPBAR_MT_my_menu.bl_idname)

# 6. プロパティ画面のパネル
class OBJECT_PT_file_name(bpy.types.Panel):
    bl_idname = "OBJECT_PT_file_name"
    bl_label = "レベルエディタ設定" 
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        if not context.object:
            self.layout.label(text="オブジェクトを選択してください")
            return

        # ファイル名プロパティの表示
        if "file_name" in context.object:
            self.layout.prop(context.object, '["file_name"]', text="ファイル名")
        else:
            self.layout.operator(MYADDON_OT_add_filename.bl_idname, text="ファイル名プロパティを追加")

        # コライダープロパティの表示
        if "collider" in context.object:
            self.layout.prop(context.object, '["collider"]', text="コライダー種類")
            self.layout.prop(context.object, '["collider_size"]', text="サイズ")
        else:
            self.layout.operator(MYADDON_OT_add_collider.bl_idname, text="コライダーを追加", icon='MESH_CUBE')

        self.layout.separator() 

        # 既存の機能
        self.layout.operator(MYADDON_OT_stretch_vertex.bl_idname, text="頂点を伸ばす")
        self.layout.operator(MYADDON_OT_create_ico_sphere.bl_idname, text="Ico Sphereを作成")
        self.layout.operator(MYADDON_OT_export_scene.bl_idname, text="シーンをエクスポート")

# 7. ファイル名プロパティを追加する機能
class MYADDON_OT_add_filename(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_add_filename"
    bl_label = "Add File Name"
    bl_description="['file_name']プロパティを追加する"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.object:
            context.object["file_name"] = ""
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "オブジェクトが選択されていません")
            return {'CANCELLED'}

# 8. コライダープロパティを追加する機能
class MYADDON_OT_add_collider(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_add_collider"
    bl_label = "Add Collider"
    bl_description="コライダー設定を追加します"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.object:
            context.object["collider"] = "BOX" 
            context.object["collider_size"] = [2.0, 2.0, 2.0] 
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "オブジェクトが選択されていません")
            return {'CANCELLED'}

# Blenderに登録するクラスのリスト
classes = [
    MYADDON_OT_stretch_vertex,
    MYADDON_OT_create_ico_sphere,
    MYADDON_OT_export_scene,
    TOPBAR_MT_my_menu,
    MYADDON_OT_add_filename,
    MYADDON_OT_add_collider, 
    OBJECT_PT_file_name
]

# アドオンが有効になったときの処理
def register():
    for cls in classes:        
        bpy.utils.register_class(cls)
    
    bpy.types.TOPBAR_MT_editor_menus.append(draw_menu_button)
    
    DrawCollider.handle = bpy.types.SpaceView3D.draw_handler_add(DrawCollider.draw_collider, (), "WINDOW", "POST_VIEW")
    
    print("レベルエディタがアクティブになりました")
    
# アドオンが無効になったときの処理
def unregister():
    bpy.types.TOPBAR_MT_editor_menus.remove(draw_menu_button)
    
    for cls in classes:
        bpy.utils.unregister_class(cls)
        
    bpy.types.SpaceView3D.draw_handler_remove(DrawCollider.handle, "WINDOW")
    
    print("レベルエディタが非アクティブになりました")

if __name__ == "__main__":
    register()
