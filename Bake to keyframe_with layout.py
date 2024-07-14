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

#Define required functions
def insert_keyframe(frame_number):                          
    obj = bpy.context.object.data.shape_keys         
    obj.keyframe_insert("eval_time", frame = frame_number)  
    pass                                             
                                                     
                                                     
def go_to_frame(frame_number):                              
    bpy.context.scene.frame_current = frame_number          
    pass


def preparation(Passed_Start_Frame_Parameter, Passed_End_Frame_Parameter):
    
    frame_start = Passed_Start_Frame_Parameter
    frame_end   = Passed_End_Frame_Parameter
    
    #Removes previous shape keys, if there is any           
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
        
        #Set up shape key interpolation mode        
    bpy.context.object.active_shape_key_index = 0   
    bpy.data.shape_keys["Key"].use_relative = False
    
    
def Baked_Keyframe(Passed_Current_Frame, Passed_Start_Frame_Parameter, Passed_End_Frame_Parameter, Passed_Frame_Skip_Parameter):
    
    frame_current = Passed_Current_Frame
    frame_start   = Passed_Start_Frame_Parameter
    frame_end     = Passed_End_Frame_Parameter
    frame_skip    = Passed_Frame_Skip_Parameter
    
                #Interpolation keyframe method                       
    if frame_skip == 0:                                              
        insert_keyframe(frame_start)                                 
        bpy.data.shape_keys["Key"].eval_time = (frame_end*10)        
        insert_keyframe(frame_end)                                   
        bpy.context.object.modifiers["Cloth"].show_viewport = False  
        go_to_frame(frame_current)
        
        
                        #Continoius keyframe method                                                      
    else:                                                                                                
        go_to_frame(frame_start)                                                                         
        obj = bpy.context.object.data.shape_keys                                                         
        while bpy.data.scenes["Scene"].frame_current <= frame_end:                                       
            bpy.data.shape_keys["Key"].eval_time = (bpy.data.scenes["Scene"].frame_current*10)           
            obj.keyframe_insert("eval_time")                                                             
            bpy.data.scenes["Scene"].frame_current += frame_skip                                         
        bpy.context.object.modifiers["Cloth"].show_viewport = False                                      
        go_to_frame(frame_current)
        
        
class bake_settings(bpy.types.PropertyGroup):row
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

        preparation(props.frame_start, props.frame_end)
        Baked_Keyframe(frame_current, props.frame_start, props.frame_end, props.frame_skip)
        self.report({"INFO"}, "Finished keframing")
        return {'FINISHED'}
        

class REAL_PT_testpanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_context = "objectmode"
    bl_region_type = "UI"
    bl_label = "Baking to keyframe"
    bl_category = "Bake to keyframe"

    def draw(self, context):
        props=context.scene.settings     

        layout = self.layout
        
        col = layout.column(align=True)
        col.prop(props, 'frame_skip')
        
        row = layout.row(align=True)
        row.prop(props, 'frame_start')
        row.prop(props, 'frame_end')
        
        col = layout.column(align=True)
        col.scale_y=3
        col.operator('poke.mon' , text ='Bake to Keyframe', icon='KEYTYPE_KEYFRAME_VEC')
        col.operator('object.shape_key_remove' , text ='Delete Keyframes', icon='EVENT_D').all= True
        
        col = layout.column(align=True)
        col.operator("ptcache.bake_all", text="Bake").bake = True
        col.operator("ptcache.free_bake_all", text="Delete All Bakes")


def register():
    bpy.utils.register_class(BAKE_OT_ToKeyframe)
    bpy.utils.register_class(REAL_PT_testpanel)
    bpy.utils.register_class(bake_settings)
    bpy.types.Scene.settings = bpy.props.PointerProperty(type=bake_settings)

def unregister():
    bpy.utils.unregister_class(BAKE_OT_ToKeyframe)
    bpy.utils.unregister_class(REAL_PT_testpanel)
    bpy.utils.unregister_class(bake_settings)
    del bpy.types.Scene.settings

if __name__ == "__main__":
    register()
        
