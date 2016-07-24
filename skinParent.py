'''
Created by Samuel B

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


bl_info = {
    "name": "SkinParent",
    "description": "Skin parent (vertex group with full weight) the selected objects to a bone",
    "author": "Samuel Bernou",
    "version": (1, 0, 0),
    "blender": (2, 77, 0),
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

                ## check if it targets the same object
                # if m.object == None:
                #     m.object = bpy.data.objects[targetRig]
                # elif m.object != bpy.data.objects[targetRig]:
                #     return (m.object)


def CheckFullWeight(ob, vgName):
    '''take an object, a valid vertex group name and return True if vertex weight are at 1 else False'''
    vg = ob.vertex_groups.get(vgName)
    for i in ob.data.vertices:
        if vg.weight(i.index) != 1.0:
            return (False)
    return (True)


def VertexGroupToBone(ob, targetBone, context):
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

    if context.scene.SP_onlyBone: #if onlybone is True then delete other vertex groups associated to bones
        for bone in bpy.data.armatures[context.scene.SP_target_armature].bones:
            if ob.vertex_groups.get(bone.name):
                if bone.name != targetBone:
                    if context.scene.SP_keepWeighted:
                        if CheckFullWeight(ob, bone.name):
                            #if vertex group is full weighted, delete
                            ob.vertex_groups.remove(ob.vertex_groups[bone.name])

                    else:
                        ob.vertex_groups.remove(ob.vertex_groups[bone.name])




class SkinParentOP(bpy.types.Operator):
    bl_idname = "rig.skinparent"
    bl_label = "Skin parent to bone"
    bl_description = "skin parent(fullweight) selected objects to target bone (create armature and assign vertex group)"
    bl_options = {"REGISTER"}


    def execute(self, context):
        if context.object.type != 'ARMATURE':
            targetRig = context.scene.SP_target_armature
            targetBone = context.scene.SP_targetbone

            for ob in context.selected_objects:
                if ob.type != 'ARMATURE':
                    context.scene.objects.active = ob
                    CreateArmatureModifier(ob, targetRig)  
                    VertexGroupToBone(ob, targetBone,context)
                
                else:
                    print (ob.name, "skipped(armature objects cannot be skin parented)")

        else:
            self.report({'WARNING'}, "Can't skin parent armature")

        # if bypassed:
        #     self.report({'INFO'},"some objects were skipped (see console)")
        #     print ("following object has armature modifier with another target")
        #     print (bypassed)
            
        
        return {"FINISHED"}

class SkinParentUI(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "Skin parent"
    bl_category ="RIG Tools"

    bpy.types.Scene.SP_target_armature = bpy.props.StringProperty(name = "targetRig", description = "Select Armature (show armature name not object name !)")
    bpy.types.Scene.SP_targetbone = bpy.props.StringProperty(name = "targetBone", description = "Select Bone to skin parent")
    bpy.types.Scene.SP_onlyBone = bpy.props.BoolProperty(name = 'onlyBone', default=False, description = "Delete vertex groups associated with other bones of this armature (destructive!)")
    bpy.types.Scene.SP_keepWeighted = bpy.props.BoolProperty(name = 'keepWeighted', default=False, description = "delete vertex groups only if they are full weighted to a bone")


    def draw(self, context):
        layout = self.layout
        row = layout.row(align = True)
        row.prop_search(context.scene, "SP_target_armature", bpy.data, "armatures",text="target rig ")
        row = layout.row(align = True)
        if context.scene.SP_target_armature:
            row.prop_search(context.scene, "SP_targetbone", bpy.data.armatures[context.scene.SP_target_armature], "bones",text="target bone")
        row = layout.row(align = True)
        row.prop(context.scene, "SP_onlyBone", text="kill other vertex groups")
        row.operator("rig.skinparent",text= "Skin to Bone")
        if context.scene.SP_onlyBone:
            row = layout.row(align = True)
            row.prop(context.scene, "SP_keepWeighted", text="delete only full weighted groups")




def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()

