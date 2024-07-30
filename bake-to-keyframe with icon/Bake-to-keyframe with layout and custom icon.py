bl_info = {
    "name": "Bake to keyframe",
    "description": "Generate keyframe",
    "author": "That pokemon trainer",
    "version": (1,0),
    "blender": (3, 1, 0),
    "location": "operator search",
    "category": "simulation",
    }


import bpy
from bpy.props import IntProperty
import os

icons = bpy.utils.previews.new()
icons_dir = os.path.dirname(__file__)

icons.load(name='BAKE',  path= os.path.join(icons_dir, 'bake.png'), path_type='IMAGE')
icons.load(name='DEL',   path= os.path.join(icons_dir, 'del.png'), path_type='IMAGE')
icons.load(name='ADD',   path= os.path.join(icons_dir, 'add.png'), path_type='IMAGE')
icons.load(name='RECAL', path= os.path.join(icons_dir, 'recal.png'), path_type='IMAGE')


# Define required utility functions
def insert_keyframe(frame_number):
    obj = bpy.context.object.data.shape_keys
    obj.keyframe_insert("eval_time", frame = frame_number)
    pass

def delete_keyframe(frame_number):
    obj = bpy.context.object.data.shape_keys
    obj.keyframe_delete("eval_time", frame = frame_number)
    pass

def go_to_frame(frame_number):                              
    bpy.context.scene.frame_current = frame_number          
    pass

def set_linear_interpolation():
    for fcurve in bpy.context.active_object.data.shape_keys.animation_data.action.fcurves:
        for keyframe_point in fcurve.keyframe_points:
            keyframe_point.interpolation = "LINEAR"
    pass

# Define main functions
def prepare_shape_key(Passed_Start_Frame_Parameter, Passed_End_Frame_Parameter):
    
    frame_start = Passed_Start_Frame_Parameter
    frame_end   = Passed_End_Frame_Parameter
    
    #Removes previous shape keys, if there are any           
    try:                                                            
        bpy.ops.object.shape_key_remove(all=True, apply_mix=False)  
    except Exception:                                               
        pass
    
        #Enables modifier in viewport, if unenabled                   
    if bpy.context.object.modifiers["Cloth"].show_viewport == False:  
        bpy.context.object.modifiers["Cloth"].show_viewport = True
        
        #Set up shape keys                                   
    go_to_frame(frame_start)                                                             
    for i in range(frame_start, frame_end+1):                                            
        bpy.ops.object.modifier_apply_as_shapekey(keep_modifier=True, modifier="Cloth")  
        bpy.context.scene.frame_current = i+1
        bpy.ops.wm.redraw_timer(type="DRAW_SWAP",iterations=1)
        
        #Set up shape key interpolation mode        
    bpy.context.object.active_shape_key_index = 1   
    bpy.context.active_object.data.shape_keys.use_relative = False
       
def Bake_Keyframe(Passed_Current_Frame, Passed_Start_Frame_Parameter, Passed_End_Frame_Parameter, Passed_Frame_Skip_Parameter):
    
    frame_current = Passed_Current_Frame
    frame_start   = Passed_Start_Frame_Parameter
    frame_end     = Passed_End_Frame_Parameter
    frame_skip    = Passed_Frame_Skip_Parameter

    Key = bpy.context.active_object.data.shape_keys.name
    
                #Interpolation keyframe method                       
    if frame_skip == 0:
        bpy.data.shape_keys[Key].eval_time = (frame_start*10)                                              
        insert_keyframe(frame_start)                                 
        bpy.data.shape_keys[Key].eval_time = (frame_end*10)        
        insert_keyframe(frame_end)                                   
        bpy.context.object.modifiers["Cloth"].show_viewport = False  
        go_to_frame(frame_current)
        
                                                                        
    else:    #Continoius keyframe method                                                                                            
        go_to_frame(frame_start)
        current_frame = bpy.data.scenes["Scene"].frame_current                                                        
        while  current_frame <= frame_end:                                       
            bpy.data.shape_keys[Key].eval_time = (current_frame*10)           
            insert_keyframe(current_frame)                                                             
            current_frame += frame_skip                                        
        bpy.context.object.modifiers["Cloth"].show_viewport = False                                      
        go_to_frame(frame_current)
        
# Define Properties        
class bake_settings(bpy.types.PropertyGroup):
    frame_start : IntProperty(
        name = "Start",
        description = "Get start frame",
        default = 1,
        min = 0)
    
    frame_end : IntProperty(
        name = "End",
        description = "Get end frame",
        default = 250,
        min = 0)
    
    frame_skip : IntProperty(
        name = "Frame step",
        description = "Get skip frame amount",
        default = 1,
        min = 0)
        
# Define Operator class        
class BAKE_OT_ToKeyframe(bpy.types.Operator):
    bl_idname = "poke.mon"
    bl_label = "POKE.MON"
    bl_description = "Create baked keyframe"    
    
    
    def execute(self, context):
        
        props=context.scene.settings     

        frame_current= bpy.data.scenes["Scene"].frame_current 
        # frame_start = bpy.data.scenes["Scene"].frame_start    
        # frame_end = bpy.data.scenes["Scene"].frame_end        
        # frame_skip = 10
        
        prepare_shape_key(props.frame_start, props.frame_end)
        Bake_Keyframe(frame_current, props.frame_start, props.frame_end, props.frame_skip)
        set_linear_interpolation()
        self.report({"INFO"}, "Finished keframing")
        
        return {'FINISHED'}

class PLACE_OT_Keyframe(bpy.types.Operator):
    bl_idname = "place.keyframe"
    bl_label = "PLACE.KEYFRAME"
    bl_description = "Places keyframe"    
    
    
    def execute(self, context):
        Key = bpy.context.active_object.data.shape_keys.name
        this_frame= bpy.data.scenes["Scene"].frame_current 
        bpy.data.shape_keys[Key].eval_time = ((this_frame)*10)                                              
        insert_keyframe(this_frame)
        set_linear_interpolation()
        self.report({"INFO"}, "Inserted a keframing")
        
        return {'FINISHED'}

class RECALCULATE_OT_Keyframe(bpy.types.Operator):
    bl_idname = "recalculate.keyframe"
    bl_label = "RECALCULATE.KEYFRAME"
    bl_description = "Reacalculate keyframe"    
    
    
    def execute(self, context):
        try:
            frame = 0
            while True:
                delete_keyframe(frame)
                frame +=1
        except Exception:
            props=context.scene.settings
            frame_current= bpy.data.scenes["Scene"].frame_current
            Bake_Keyframe(frame_current, props.frame_start, props.frame_end, props.frame_skip)
            set_linear_interpolation()
            self.report({"INFO"}, "Recalculated keframing")
        
        return {'FINISHED'}

# Define panel layout clsass
class REAL_PT_testpanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_context = "objectmode"
    bl_region_type = "UI"
    bl_label = "Baking to keyframe"
    bl_category = "Bake to keyframe"

    def draw(self, context):
        
        props=context.scene.settings   
        layout = self.layout
        # try:
        #     len(bpy.context.active_object.data.shape_keys.key_blocks)
        #     length=1
        # except Exception:
        #     length=0
        

        try:
            modifiers_info=bpy.context.active_object.modifiers.items()
            modifiers_list=[]
            for i,j in modifiers_info:
                modifiers_list.append(i)

            modifiers_list.index('Cloth')

            row = layout.row(align=True)
            row.operator('object.modifier_remove', icon='X').modifier='Cloth'
            row.prop(bpy.context.active_object.modifiers['Cloth'], 'show_viewport', text='')
            row.prop(bpy.context.active_object.modifiers['Cloth'], 'show_render', text='')
            
            col = layout.column(heading=' ', align=True)
            col.prop(props, 'frame_skip')
            
            row = layout.row(align=False)
            row.prop(props, 'frame_start')
            row.prop(props, 'frame_end')
            
            row = layout.row(align=True)
            row.scale_y=2
            row.operator('poke.mon' , text ='Bake to Keyframe', icon_value=icons['BAKE'].icon_id)
            row.scale_x=2
            row.operator('object.shape_key_remove' , icon_value=icons['DEL'].icon_id, text='').all= True

            
            col = layout.column(align=True)
            col.scale_y=2
            col.operator('place.keyframe' , text ='Place Keyframe', icon_value=icons['ADD'].icon_id)
            col.operator('recalculate.keyframe' , text ='Recalculate Keyframe', icon_value=icons['RECAL'].icon_id)
            
            col.separator()
            col = layout.column(align=True)
            col.operator("ptcache.bake_all", text="Bake").bake = True
            col.operator("ptcache.free_bake_all", text="Delete All Bakes")

        except Exception:
            col = layout.column(align=True)
            col.operator('object.modifier_add', text='Cloth Modifier', icon='MOD_CLOTH').type='CLOTH'


def register():
    bpy.utils.register_class(BAKE_OT_ToKeyframe)
    bpy.utils.register_class(PLACE_OT_Keyframe)
    bpy.utils.register_class(RECALCULATE_OT_Keyframe)
    bpy.utils.register_class(REAL_PT_testpanel)
    bpy.utils.register_class(bake_settings)
    bpy.types.Scene.settings = bpy.props.PointerProperty(type=bake_settings)

def unregister():
    bpy.utils.unregister_class(BAKE_OT_ToKeyframe)
    bpy.utils.unregister_class(PLACE_OT_Keyframe)
    bpy.utils.unregister_class(RECALCULATE_OT_Keyframe)
    bpy.utils.unregister_class(REAL_PT_testpanel)
    bpy.utils.unregister_class(bake_settings)
    del bpy.types.Scene.settings
    # bpy.utils.previews.remove(icons)

if __name__ == "__main__":
    register()
        
