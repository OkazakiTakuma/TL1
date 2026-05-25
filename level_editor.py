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

# 1. 【新機能】頂点を伸ばす機能（オペレーター）を定義するクラス
class MYADDON_OT_stretch_vertex(bpy.types.Operator):
    bl_idname = "myaddon.stretch_vertex"
    bl_label = "頂点を伸ばす"
    bl_description = "選択しているメッシュの頂点を伸ばします"
    bl_options = {'REGISTER', 'UNDO'} # Undo（元に戻す）ができるように設定

    def execute(self, context):
        # 現在選択されているアクティブなオブジェクトを取得
        obj = context.active_object
        
        # メッシュオブジェクトが正しく選択されているかチェック
        if obj and obj.type == 'MESH':
            # 0番目の頂点のX座標を 1.0 変化させる
            obj.data.vertices[0].co.x += 1.0
            
            # 【重要】変更をBlenderの画面に即座に反映させるためのアップデート処理
            obj.data.update()
            
            print("頂点を伸ばしました")
            return {'FINISHED'}
        else:
            print("エラー：メッシュオブジェクト（Cubeなど）を選択してください")
            return {'CANCELLED'}

# 2. メニューの見た目や中身を定義するクラス
class TOPBAR_MT_my_menu(bpy.types.Menu):
    bl_idname = "TOPBAR_MT_my_menu"
    bl_label = "My Menu" 
    bl_description = "拡張メニュー by " + bl_info["author"]

    def draw(self, context):
        # マニュアルを開くボタン
        self.layout.operator("wm.url_open_preset", text="Manual", icon='HELP')
        
        # 追加した「頂点を伸ばす」ボタンをメニューに登録
        self.layout.operator("myaddon.stretch_vertex", text="頂点を伸ばす", icon='MESH_DATA')

# 3. トップバーにメニューを追加するための関数
def draw_menu_button(self, context):
    self.layout.menu(TOPBAR_MT_my_menu.bl_idname)

# Blenderに登録するクラスのリスト
# 新しく作った「MYADDON_OT_stretch_vertex」もここに並べます！
classes = [
    MYADDON_OT_stretch_vertex,
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