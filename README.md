# SkinParent

Skin parent the selected objects to a bone


### Description

Just select the objects to skin parent then select the bone in pose mode or edit armature mode then click on skin parents 


### Where ?

Viewport Toolbar ('t' key) > "RIG tools" tab  

<!-- Old method
**Target rig**  
Select the armature. Important note : In this list you see the Armature *Data* name, not the Armature *object* name

**Target bone** (appears once you've selected an armature)  
List the bones of the targeted rig
-->

### Options

**kill other vertex groups**  
All others vertex groups of the current object are deleted  

#### Delete filters descriptions  
(appears if you've ticked previous checkbox)

**Only groups related to this armature**  
Delete only vertex groups associated with the current armature (named after a bone of current armature).
Usefull to keep vertex groups created for any other purpose than skinning.

**delete only full weighted groups**   
Existing vertex groups of selected objects are deleted only if all their vertex are 100% assigned (fully weighted).

<!-- Old method
![skin parent panel](https://github.com/Pullusb/images_repo/raw/master/blender_SkinParent_panel.png)
-->
