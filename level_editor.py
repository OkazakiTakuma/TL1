import bpy 

bl_info = {
    "name": "level_editor",
    "author": "Takuma Okazaki",
    "version": (4, 4),
    "blender": (4, 4, 0),
    "location": "",
    "description": "level_editor",
    "category": "Object",
}

# --- 1. メニューのクラス定義 ---
class TOPBAR_MT_my_menu(bpy.types.Menu):
    bl_idname = "TOPBAR_MT_my_menu"
    bl_label = "My Menu" 
    bl_description = "拡張メニュー by " + bl_info["author"]

    # ★ここが最重要ポイントです★
    # 以下の2行は、class の行よりも右にずらして（字下げして）記述されています。
    def draw(self, context):
        self.layout.operator("wm.url_open_preset", text="Manual", icon='HELP')

classes = [
    TOPBAR_MT_my_menu,
]

# --- 2. トップバーにメニューを追加するための関数 ---
def submenu(self, context):
    self.layout.menu(TOPBAR_MT_my_menu.bl_idname)

# --- 3. 登録処理 ---
def register():
    for cls in classes:        
        bpy.utils.register_class(cls)
    
    bpy.types.TOPBAR_MT_editor_menus.append(submenu)
    print("レベルエディタがアクティブになりました")
    
def unregister():
    bpy.types.TOPBAR_MT_editor_menus.remove(submenu)
    
    for cls in classes:
        bpy.utils.unregister_class(cls)
    print("レベルエディタが非アクティブになりました")

if __name__ == "__main__":
    register()