import bpy
import math

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
class MYADDON_OT_export_scene(bpy.types.Operator):
    bl_idname = "myaddon.export_scene"
    bl_label = "シーンをエクスポート"
    bl_description = "現在のシーンのオブジェクト情報をコンソールに出力します"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print("--- シーンのエクスポートを開始します ---")
        
        for obj in context.scene.objects:
            print(f"名前: {obj.name}, 位置: {obj.location}")
            
            trans, rot, scale = obj.matrix_world.decompose()
            rot = rot.to_euler()
            
            rot.x = math.degrees(rot.x)
            rot.y = math.degrees(rot.y)  
            rot.z = math.degrees(rot.z)
            
            print(f"座標: {trans}")
            print(f"回転: {rot}")
            print(f"スケール: {scale}") 
            
            # 【ポイント】ここのインデント（字下げ）をしっかり半角スペースで揃えています
            if obj.parent:
                print(f"親オブジェクト: {obj.parent.name}")

        print("--- エクスポートが完了しました ---")
        
        self.report({'INFO'}, "シーン情報をコンソールに出力しました")
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

# 5. トップバーにメニューを追加するための関数
def draw_menu_button(self, context):
    self.layout.menu(TOPBAR_MT_my_menu.bl_idname)

# Blenderに登録するクラスのリスト
classes = [
    MYADDON_OT_stretch_vertex,
    MYADDON_OT_create_ico_sphere,
    MYADDON_OT_export_scene,
    TOPBAR_MT_my_menu,
]

# アドオンが有効になったときの処理
def register():
    for cls in classes:        
        bpy.utils.register_class(cls)
    
    bpy.types.TOPBAR_MT_editor_menus.append(draw_menu_button)
    print("レベルエディタがアクティブになりました")
    
# アドオンが無効になったときの処理
def unregister():
    bpy.types.TOPBAR_MT_editor_menus.remove(draw_menu_button)
    
    for cls in classes:
        bpy.utils.unregister_class(cls)
    print("レベルエディタが非アクティブになりました")

if __name__ == "__main__":
    register()