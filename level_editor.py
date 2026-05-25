import bpy

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

# 1. 頂点を伸ばす機能（オペレーター）
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

# 2. 【新機能】Ico Sphereを作成する機能（オペレーター）
class MYADDON_OT_create_ico_sphere(bpy.types.Operator):
    bl_idname = "myaddon.create_ico_sphere"
    bl_label = "Ico Sphereを作成"
    bl_description = "Ico Sphereをシーンに追加します"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        #  Subdivision（細分化）が 2、半径が 1 の Ico Sphere を作成
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1)
        print("Ico Sphereを作成しました")
        return {'FINISHED'}


# 3. メニューの見た目や中身を定義するクラス
class TOPBAR_MT_my_menu(bpy.types.Menu):
    bl_idname = "TOPBAR_MT_my_menu"
    bl_label = "My Menu" 
    bl_description = "拡張メニュー by " + bl_info["author"]

    def draw(self, context):
        # マニュアルを開くボタン
        self.layout.operator("wm.url_open_preset", text="Manual", icon='HELP')
        
        # 「頂点を伸ばす」ボタン
        self.layout.operator("myaddon.stretch_vertex", text="頂点を伸ばす", icon='MESH_DATA')

        # 新しく追加した「Ico Sphereを作成」ボタン
        self.layout.operator("myaddon.create_ico_sphere", text="Ico Sphereを作成", icon='MESH_DATA')


# 4. トップバーにメニューを追加するための関数
def draw_menu_button(self, context):
    self.layout.menu(TOPBAR_MT_my_menu.bl_idname)


# 【修正ポイント】Blenderに登録するクラスのリスト
# 新しく作った「MYADDON_OT_create_ico_sphere」をここに追加しました！
classes = [
    MYADDON_OT_stretch_vertex,
    MYADDON_OT_create_ico_sphere,  # ← これが抜けていました
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