import bpy
import math
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

    # 【関数分け 1】履歴（ログ）を表示する専用の関数
    def show_log(self, message):
        print(message)                  # コンソールへの出力
        self.report({'INFO'}, message)   # Blender画面下部へのポップアップ表示

    # 【関数分け 2】オブジェクトの情報をファイルに書き込む専用の関数
    def write_object_info(self, file, obj, level):
        # 階層の深さに合わせて字下げ（半角スペース4つ分）を作る
        indent = "    " * level
        
        # データの書き込み
        file.write(f"{indent}名前: {obj.name}, 位置: {obj.location}\n")
        
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

    # 【関数分け 3】シーンを再帰的に解析（パース）する専用の関数
    def parse_scene_recursive(self, file, obj, level):
        # 1. まず渡されたオブジェクトの情報を書き込む（関数2を呼び出す）
        self.write_object_info(file, obj, level)
        
        # 2. 子オブジェクトがいたら、階層（level）を1つ下げて自分自身を呼び出す（再帰）
        for child in obj.children:
            self.parse_scene_recursive(file, child, level + 1)

    # エクスポート処理の大枠（橋渡し役）
    def export(self, context):
        # 履歴表示関数を使って開始ログを出力
        self.show_log(f"シーン情報出力開始... {self.filepath}")
        
        with open(self.filepath, 'w', encoding='utf-8') as file:
            file.write("SCENE\n")
            
            # 親を持たない（ルートの）オブジェクトから解析をスタート
            for obj in context.scene.objects:
                if not obj.parent:
                    # 再帰解析関数（関数3）を呼び出す
                    self.parse_scene_recursive(file, obj, 0)

        # 履歴表示関数を使って完了ログを出力
        self.show_log(f"--- エクスポート完了: {self.filepath} ---")

    # Blenderが実行するメインの処理
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
