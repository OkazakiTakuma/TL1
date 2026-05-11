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


def register():
    print("level_editor is active")
    
def unregister():
    print("level_editor is nonactive")
    
if __name__=="__main__":
    register()