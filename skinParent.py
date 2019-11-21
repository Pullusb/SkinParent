bl_info = {
    "name": "SkinParent",
    "description": "Skin parent (vertex group with full weight) the selected objects to a bone",
    "author": "Samuel Bernou",
    "version": (2, 1, 0),
    "blender": (2, 81, 0),
    "location": "View3D > Tool Shelf > RIG tool > Skin parent",
    "warning": "",
    "wiki_url": "",
    "category": "Object" }


import bpy
C = bpy.context


def CreateArmatureModifier(ob, targetRig):
    '''
    Create armature modifier if necessary and place it on top of stack
    or just after the first miror modifier
    return a list of bypassed objects
    '''

    #get object from armature data with a loop (only way to get armature's owner)
    for obArm in bpy.data.objects:
        if obArm.type == 'ARMATURE' and obArm.data.name == targetRig:
            ArmatureObject = obArm

    #add armature modifier that points to designated rig:
    if not 'ARMATURE' in [m.type for m in ob.modifiers]:
        mod = ob.modifiers.new('Armature', 'ARMATURE')
        mod.object = ArmatureObject#bpy.data.objects[targetRig]

        #bring Armature modifier to the top of the stack
        pos = 1
        if 'MIRROR' in [m.type for m in ob.modifiers]:
            #if mirror, determine it's position
            for mod in ob.modifiers:
                if mod.type == 'MIRROR':
                    pos += 1
                    break
                else:
                    pos += 1

        if len(ob.modifiers) > 1:
            for i in range(len(ob.modifiers) - pos):
                bpy.ops.object.modifier_move_up(modifier="Armature")

    else: #armature already exist
        for m in ob.modifiers:
            if m.type == 'ARMATURE':
                m.object = ArmatureObject#bpy.data.objects[targetRig]

                ## maybe check if it targets the same object ?
                # if m.object == None:
                #     m.object = bpy.data.objects[targetRig]
                # elif m.object != bpy.data.objects[targetRig]:
                #     return (m.object)


def CheckFullWeight(ob, vgName):
    '''take an object, a valid vertex group name and return True if vertex weight are at 1 else False'''
    vg = ob.vertex_groups.get(vgName)
    for i in ob.data.vertices:
        try:
            if vg.weight(i.index) != 1.0:
                return (False)
        except RuntimeError:#if vertice isn't assigned in this group
            return (False)

    return (True)

def SimpleVertexGroupToBone(ob, targetRig, targetBone, context):
    '''
    Add a vertex group to the object named afer the given bone
    assign full weight to this vertex group
    return a list of bypassed object (due to vertex group already existed)
    '''

    #if the vertex group related to the chosen bone is'nt here, create i and Skin parent (full weight)
    if not targetBone in [i.name for i in ob.vertex_groups]:
        vg = ob.vertex_groups.new(name=targetBone)

    else: #vertex group exist, or weight it (leave it untouched ?)
        vg = ob.vertex_groups[targetBone]

    verts = [i.index for i in ob.data.vertices]
    vg.add(verts, 1, "ADD")


def VertexGroupToBone(ob, targetRig, targetBone, context):
    '''
    Add a vertex group to the object named afer the given bone
    assign full weight to this vertex group
    return a list of bypassed object (due to vertex group already existed)
    '''

    #if the vertex group related to the chosen bone is'nt here, create i and Skin parent (full weight)
    if not targetBone in [i.name for i in ob.vertex_groups]:
        vg = ob.vertex_groups.new(name=targetBone)

    else: #vertex group exist, or weight it (leave it untouched ?)
        vg = ob.vertex_groups[targetBone]

    verts = [i.index for i in ob.data.vertices]
    vg.add(verts, 1, "ADD")

    #Delete other vertex groups option
    if context.scene.SP_killVG:
        if not context.scene.SP_onlyBone:#simply delete other vertex groups
            for vgroup in ob.vertex_groups:
                #if vgroup.name != targetBone:
                if vgroup != vg:
                    if context.scene.SP_keepWeighted:
                        if CheckFullWeight(ob, vgroup.name):
                            #if vertex group is full weighted, delete
                            ob.vertex_groups.remove(vgroup)
                    else:
                        ob.vertex_groups.remove(vgroup)
                        # ob.vertex_groups.remove(ob.vertex_groups[vgroup.name])

        else:#if onlybone is True then delete other vertex groups associated to bones
            for bone in bpy.data.armatures[targetRig].bones:
                if ob.vertex_groups.get(bone.name):
                    if bone.name != targetBone:
                        if context.scene.SP_keepWeighted:
                            if CheckFullWeight(ob, bone.name):
                                #if vertex group is full weighted, delete
                                ob.vertex_groups.remove(ob.vertex_groups[bone.name])

                        else:
                            ob.vertex_groups.remove(ob.vertex_groups[bone.name])


class SKP_OT_convert_parent_to_skin(bpy.types.Operator):
    bl_idname = "rig.convert_parent_to_skinning"
    bl_label = "Convert parent to skin"
    bl_description = "All select object that are directly parented to a bone get an armature modifier instead"
    bl_options = {"REGISTER"}


    def execute(self, context):
        keep_transform = context.scene.SP_keepTransform

        print('-'*5)
        for ob in bpy.context.selected_objects:
            if ob.parent:
                print("ob has parent", ob.parent.name)
                targetRig = ob.parent.data.name
                if ob.parent_type == 'BONE':
                    print("is bone parented to")
                    if ob.parent_bone:
                        targetBone = ob.parent_bone
                        print("ob.parent_bone", ob.parent_bone)#Dbg

                        if keep_transform:
                            #Clear and keep transform (matrix reattribution)
                            matrixcopy = ob.matrix_world.copy()
                            ob.parent = None
                            ob.matrix_world = matrixcopy
                        else:
                            ob.parent = None

                        #replace by armature
                        CreateArmatureModifier(ob, targetRig)
                        SimpleVertexGroupToBone(ob, targetRig, targetBone, bpy.context)

        return {"FINISHED"}

class SKP_OT_skin_parent(bpy.types.Operator):
    bl_idname = "rig.skinparent"
    bl_label = "Skin to bone"
    bl_description = "skin parent(fullweight) selected objects to target bones (create armature and assign vertex group)"
    bl_options = {"REGISTER"}


    def execute(self, context):

        mesh_selection = [o for o in bpy.context.selected_objects if o.type == 'MESH']
        if mesh_selection:

            #if context.mode == 'OBJECT':
            #target armature data not armature object !
            targetRig = context.scene.SP_target_armature
            targetBone = context.scene.SP_targetbone

            if context.mode == 'POSE':
                targetRig = context.active_pose_bone.id_data.data.name #one more 'data' necessary to get armatrue data in pose mode
                targetBone = context.active_pose_bone.name

            elif context.mode == 'EDIT_ARMATURE':
                targetRig = context.active_bone.id_data.name
                targetBone = context.active_bone.name

            print ('RIG>> ', targetRig)
            print ('BONE> ', targetBone)

            if targetRig and targetBone:
                actob = context.object #backup current active obj

                for ob in mesh_selection:
                    context.view_layer.objects.active = ob
                    CreateArmatureModifier(ob, targetRig)
                    VertexGroupToBone(ob, targetRig, targetBone, context)

                context.view_layer.objects.active = actob #re-assign active obj
            else:
                self.report({'ERROR'}, "target missing")

        else:
            self.report({'ERROR'}, "No mesh selected")



        return {"FINISHED"}

class SKP_PT_skin_parent_ui(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Skin parent"
    bl_category ="RIG Tools"

    bpy.types.Scene.SP_target_armature = bpy.props.StringProperty(name = "targetRig", description = "Select Armature (show armature name not object name !)")
    bpy.types.Scene.SP_targetbone = bpy.props.StringProperty(name = "targetBone", description = "Select Bone to skin parent")
    bpy.types.Scene.SP_killVG = bpy.props.BoolProperty(name = 'killVG', default=False, description = "Delete others existing vertex groups (destructive!)")
    bpy.types.Scene.SP_onlyBone = bpy.props.BoolProperty(name = 'onlyBone', default=False, description = "Delete only vertex groups associated with other bones of this armature")
    bpy.types.Scene.SP_keepWeighted = bpy.props.BoolProperty(name = 'keepWeighted', default=False, description = "delete vertex groups only if they are full weighted")
    
    bpy.types.Scene.SP_keepTransform = bpy.props.BoolProperty(name = 'Keep transform', default=True, description = "Keep transformation when deleteting the parent (before skinning to armature)")


    def draw(self, context):
        layout = self.layout
        '''
        ### box to search for the rig and bones manually (maybe let it activable ?)
        row = layout.row(align = True)
        row.prop_search(context.scene, "SP_target_armature", bpy.data, "armatures",text="target rig ")
        row = layout.row(align = True)
        if context.scene.SP_target_armature:
            row.prop_search(context.scene, "SP_targetbone", bpy.data.armatures[context.scene.SP_target_armature], "bones",text="target bones")
        '''
        layout.operator("rig.convert_parent_to_skinning")
        layout.prop(context.scene, "SP_keepTransform")
        layout.separator()
        row = layout.row(align = True)
        row.operator("rig.skinparent")
        if context.mode == 'POSE' or context.mode == 'EDIT_ARMATURE':
            row.enabled = True
        else:
            row.enabled = False

        row = layout.row(align = True)
        row.prop(context.scene, "SP_killVG", text="Kill other vertex groups")
        if context.scene.SP_killVG:
            #separator label
            row = layout.row(align = True)
            row.label(text = 'Delete filters:')

            #options
            row = layout.row(align = True)
            row.prop(context.scene, "SP_onlyBone", text="Only groups related to this armature")
            row = layout.row(align = True)
            row.prop(context.scene, "SP_keepWeighted", text="Only fully weighted groups")


classes = (
SKP_OT_convert_parent_to_skin,
SKP_OT_skin_parent,
SKP_PT_skin_parent_ui,
)




### --- REGISTER ---

register, unregister = bpy.utils.register_classes_factory(classes)

'''#detailed
def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
'''

if __name__ == "__main__":
    register()