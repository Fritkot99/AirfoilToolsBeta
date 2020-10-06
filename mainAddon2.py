


import numpy as np
import bpy
from mathutils import Vector
from bpy.types import Panel
from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        IntProperty,
        StringProperty
        )
from bpy.types import WindowManager

#from NACAgen import NACA4digits
import sys
import os
bl_info = {
    "name": "Airfoil Tool",
    "description": "Generate airfoil surface from Naca code or file",
    "author": "Fritkot99",
    "version":(0,1),
    "blender": (2,90,1),
    }


def NACA4digits(digits, N, Distrib):

    
    x = np.linspace(0,1,int(round(N/2,0))) #unit chord array from 0 to 1
    #print("checkdependency")
    if Distrib:
        x = 0.5-0.5*np.cos(x*np.pi)
        #print('chckhere')
    # m = 0.02
    # p = 0.4
    # t = 0.12
    
    m = float(digits[0])/100
    p = float(digits[1])/10
    t = float(digits[2:])/100
    
    if digits[0]=="0":
        yt = 5*t*(0.2969*np.sqrt(x)-0.1260*x-0.3516*x**2+0.2843*x**3-0.1015*x**4)
        X_upper = x*1.
        X_lower = x*1.
        
        Y_upper = yt*1.
        Y_lower = -1.*yt
    else:
    #camber line
        p_index = np.argmin(abs(x-p))
        yc = np.hstack(((m/p**2)*(2*p*(x[:p_index])-(x[:p_index]**2)), (m/(1-p)**2)*((1-2*p)+2*p*x[p_index:]-x[p_index:]**2)))
        
        
        #symmetric
        
        yt = 5*t*(0.2969*np.sqrt(x)-0.1260*x-0.3516*x**2+0.2843*x**3-0.1015*x**4)
        
        
        dyc_dx = np.hstack(((2*m/p**2)*(p-x[:p_index]), (2*m/((1-p)**2))*(p-x[p_index:])))
        theta = np.arctan(dyc_dx)
        
        Y_upper = yc + yt*np.cos(theta)
        X_upper = x-yt*np.sin(theta)
        
        Y_lower = yc - yt*np.cos(theta)
        X_lower = x+yt*np.sin(theta)
        
    Y_tot = np.hstack((np.flip(Y_upper), Y_lower[1:]))
    X_tot = np.hstack((np.flip(X_upper), X_lower[1:]))
    
    Pts_tot = np.transpose(np.vstack((X_tot, Y_tot)))
    return Pts_tot

#Pts = NACA4digits("0020", 200)

# plt.plot(Pts[:,0], Pts[:,1])
# plt.axis('equal')
# plt.show()




"""------------------5 digits series----------------------------"""

#camber
# N = 200
# Distrib = None
# Reflexed = True

def NACA5digits(digits, N, Distrib):
    
    L, P, S, TT = int(digits[0]), int(digits[1]), int(digits[2]), float(digits[3:])
    
    Cldes = L*0.15
    camberloc = 0.05*P
    Reflexed = bool(S)
    t = TT/100.
    
    p_lst = [0.05,0.10,0.15,0.20,0.25] 
    m_lst = [[0.0580,0.1260,0.2025,0.2900,0.3910], [0.1300, 0.2170, 0.3180, 0.4410]]
    k_lst = [[361.4,51.64,15.957,6.643,3.230], [51.990, 15.793, 6.520, 3.191]]
    k2k1_lst = [0.000764, 0.00677, 0.0303, 0.1355]
    
    x = np.linspace(0,1,int(round(N/2,0))) #unit chord array from 0 to 1
    if Distrib:
        x = 0.5-0.5*np.cos(x*np.pi)
        
    reflexed_ind = int(Reflexed)
    
    p_loc = p_lst.index(round(camberloc, 2))
    print("stuff", p_loc, camberloc)
    k = k_lst[reflexed_ind][p_loc]
    m = m_lst[reflexed_ind][p_loc]
    
    x1 = x[x<m]
    x2 = x[x>=m]
    
    if not Reflexed:
    
        yc = np.hstack((((k/6)*(x1**3-3*m*x1**2 + (m**2)*(3-m)*x1)),((k*m**3)/6)*(1-x2)))
    
    if Reflexed:
        k2k1 = k2k1_lst[p_loc]
        
        yc1 = (k/6)*((x1-m)**3-k2k1*x1*(1-m)**3 - x1* m**3 + m**3)
        yc2 = (k/6)*((k2k1*(x2-m)**3 - k2k1*x2*(1-m)**3- x2*m**3 + m**3))
        yc = np.hstack((yc1, yc2))
    
        
    zc = (Cldes/0.3)*yc
    yt = 5*t*(0.2969*np.sqrt(x)-0.1260*x-0.3516*x**2+0.2843*x**3-0.1015*x**4)
    
    
    dyc_dx = np.hstack(((yc[1:]-yc[:-1])/(x[1:]-x[:-1]), np.array([0])))
    theta = np.arctan(dyc_dx)
    
    Y_upper = zc + yt*np.cos(theta)
    X_upper = x-yt*np.sin(theta)
    
    Y_lower = zc - yt*np.cos(theta)
    X_lower = x+yt*np.sin(theta)
    Y_tot = np.hstack((np.flip(Y_upper), Y_lower[1:]))
    X_tot = np.hstack((np.flip(X_upper), X_lower[1:]))
    
    Pts_tot = np.transpose(np.vstack((X_tot, Y_tot)))
    
    # plt.plot(x, yc)
    # plt.plot(Pts_tot[:,0], Pts_tot[:,1])
    # plt.axis('equal')
    # plt.show()
    return Pts_tot


Pts = None
Distribution = None
Faceornot = True
Path = "none"
afname = "2412"
afname5 = "23012"
chordLength = 1.0
meshname = "airfoil"


"""------------------------------------------------------File import------------------------------------"""
class ImportAirfoil(bpy.types.Operator):
    
    bl_idname = "import.some_data"
    bl_label = "Import airfoil coordinates"
    bl_description = "Import airfoil points from file"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not (None or not (None))

    def execute(self, context):
        global Pts
        global Path
        global meshname
        #file = open(self.filepath, 'r')
        #file.read("Hello World " + context.object.name)
        FilaAF = open(self.filepath, 'r') #open airfoil data points

        cellcount = 0
        newfile = []
        for lines in FilaAF:
            lines = lines.replace("\t"," ")
            lines = lines.replace("\n","")
            line2 = lines.split(" ")
            newline = []
            cellcount +=1
            if (lines.count('NACA')==0) and (lines.count('NASA')==0):
                
                for cell in line2:
                    
                    if cell != '':
                        
                        newcell = float(cell)
                        newline.append(newcell)
        
                    
            if newline != []:        
                newfile.append(newline)
            # if newline.count('NACA') !=0:
            #     newfile.pop(-1)        
        
        FilaAF.close()
        Pts = np.array(newfile)
        
        Path = str(self.filepath)
 
        
        meshname = "Airfoil"
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class MakeNaca4digits(bpy.types.Operator):

    
    bl_idname = "ops.naca4digits"
    bl_label = "Create Points"
    bl_description = "Generate airfoil points"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        global Pts
        global afname
        global Distribution
        global meshname
        global nacaPts

        Pts = NACA4digits(afname, nacaPts, Distribution)

        
        meshname = "NACA" + afname
        return {'FINISHED'}
        
        
        

class MakeNaca5digits(bpy.types.Operator):



    
    bl_idname = "ops.naca5digits"
    bl_label = "Create Points"
    bl_description = "Generate airfoil points"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        global Pts
        global afname5
        global Distribution
        global meshname
        global nacaPts
        

        Pts = NACA5digits(afname5, nacaPts, Distribution)
  
        meshname = "NACA" + afname5
        return {'FINISHED'}
    
    
class GenerateSurface(bpy.types.Operator):


    bl_idname = "ops.generate_surface"
    bl_label = "Generate airfoil surface"
    bl_description = "Generate airfoil surface/outline"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        global Pts
        
        return Pts is not None

    def execute(self, context):
        global Pts
        global Faceornot
        global chordLength
        global meshname
        
        PtsNew = Pts*chordLength
   
        scene = context.scene
        edges = []
        faces = []
        faces1 = [list(range(len(Pts)))]
        edges01 = np.vstack((np.transpose(np.vstack((np.array(range(len(Pts)-1)), np.array(range(1, len(Pts)))))), np.array([len(Pts)-1, 0])))
        edges02 = []
        for i in edges01: edges02.append(tuple(i))
        edges1 = list(edges02)
       
        verts1 = []

        run = True
        i = 0
        while run:
            verts1.append(Vector((PtsNew[i][0], PtsNew[i][1], 0)))
            i+=1
            if i>len(Pts)-1:
                run = False

        mesh = bpy.data.meshes.new(name="New Object Mesh")
        
        
        
        object = bpy.data.objects.new( meshname, mesh )
        bpy.context.collection.objects.link( object )
        
        if Faceornot:
            mesh.from_pydata(verts1, edges, faces1)
            mesh.update( calc_edges=True )
        else:
            mesh.from_pydata(verts1, edges1, faces)
    
        
        return {'FINISHED'}    
 
 
"""---------------------------------------classes for ui-----------------------------------"""   
    
class ChooseInputType(bpy.types.Operator):
    bl_idname = "ops.airfoil_type_selection"
    bl_label = "Choose airfoil input type"
    bl_description = "Choose airfoil input type"
    my_string: bpy.props.StringProperty(name = "String Value")
    def execute(self, context):
        print("Test nnin", self.my_string)
        return {'FINISHED'}
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


        
        
    

    
class ClearPoints(bpy.types.Operator):
    bl_idname = "ops.clear_airfoil_points"
    bl_label = "Clear points"
    bl_description = "Clear airfoil points"
    
    @classmethod
    def poll(cls, context):
        global Pts
        
        return Pts is not None
    
    def execute(self, context):
        global Pts
        Pts = None       
        
        
        return {'FINISHED'}
   
"""-------------------------------------------------------------UI panel-----------------------------------------"""
class airfoilClassPanel(Panel):
    bpy.types.Scene.naca_or_file = True
 
    bl_label = "Airfoil selection"
    bl_idname = "_PT_TestPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "AirfoilTools"
    

   
    
    bpy.types.Scene.airfoilmode = EnumProperty(
                                          name = "Mode",
                                          description = "choose mode",
                                          items = {('Fimp', 'File import', 'File import'),
                                                    ('N4d', 'Naca 4 digits','NACA 4 digits'),
                                                    ('N5d', 'Naca 5 digits','NACA 5 digits')
                                                    },
                                          default = 'Fimp'
                                          )
                                          
    bpy.types.Scene.distribution= BoolProperty(name = "Cosine points distribution",
                                               description = 'Concentrates points towards leading and trailing edge',
                                               default = True)
                                               

                                                                                                                            
    bpy.types.Scene.nacapoints= IntProperty(
                                          name="Points", 
                                          description="Total points to be used to plot the airfoil",
                                          default = 201,
                                          min=1,
                                          max = 500
                                          )
    bpy.types.Scene.nacathickness= IntProperty(
                                          name = "Thickness [%]",
                                          description = "Airfoil max thickness in [%] of the chord length",
                                          default = 11,
                                          min = 1,
                                          max = 25
                                          )
   
    """------------for naca 4 digits airfoils----"""
    bpy.types.Scene.nacacamber= IntProperty(
                                            name = "Max camber [%]",
                                            description = "Max camber in [%] of the chord length",
                                            default = 2,
                                            min = 0,
                                            max = 5
                                            )
    bpy.types.Scene.camberloc= FloatProperty(name = "Max camber location",
                                             description = "Max camber location, in fraction of the chord length",
                                            min = 0.1,
                                            max = 0.8,
                                            step = 10,
                                            default = 0.4)
                                        
    """------------------for naca 5 digits airfoils----"""

    bpy.types.Scene.cldesign = FloatProperty(
                                            name = "Design lift coefficient",
                                            description = "Design lift coefficient (C_l) of the airfoil",
                                            default = 0.3,
                                            min = 0.0,
                                            max = 0.8,
                                            step = 10
                                            )
    bpy.types.Scene.camberlocation2 = FloatProperty(
                                            name = "Max camber location",
                                            description = "Max camber location, in fraction of the chord length",
                                            default = 0.25,
                                            min = 0.05,
                                            max = 0.25,
                                            step = 5
                                            )
    bpy.types.Scene.reflexedornot = BoolProperty(
                                            name = "Reflexed",
                                            description = "Select a reflexed airfoil to get a moment coefficient almost zero, slightly positive (ideal for flying wings)",
                                            
                                            default = False
                                            )
    #bpy.types.Scene.nacacamber[0](set==(self, 2) )                               
    wm = WindowManager
    # register internal property
    wm.visibleLine = BoolProperty(default=True)
    wm.nbLine = IntProperty(default=0)
    
#    self.my_float: bpy.props.FloatProperty(name="Float")
#    self.my_bool: bpy.props.BoolProperty(name="Toggle Option")
    #afname: bpy.props.StringProperty(name="String Value")
    
    
    
    def draw(self, context):
        global Path
        global afname
        global afname5
        global nacaPts
        global Pts
        global Distribution
        global Faceornot
        global chordLength
        
        #nacacamber2 = self.nacacamber
        
        layout = self.layout
        
        row = layout.row()
        row.label(text = "Airfoil Selection tool")
        row = layout.row()
        
        
        #row.StringProperty(name = "test")
        row = layout.row()
#        row.prop(context.scene, "x_Subdivisions")
#        row = layout.row()
        row.prop(context.scene, "airfoilmode")
        #print(bpy.types.Scene.naca_or_file)
        
        
        """------------------------------------------NACA 4 digits------------------------------------"""
        if bpy.context.scene.airfoilmode=='N4d':
            row = layout.row()
          
#            row.operator("ops.airfoil_type_selection")
#            row = layout.row()
            
            row.prop(context.scene,"nacacamber")
            row = layout.row()
            row.prop(context.scene,"camberloc")
            row = layout.row()
            row.prop(context.scene,"nacathickness")
            row = layout.row()
            row.prop(context.scene,"nacapoints")
            row = layout.row()
            row.prop(context.scene, "distribution")
            #print("herenow",nacacamber)
            #print(bpy.context.scene.nacacamber)
            nacaName = str(bpy.context.scene.nacacamber) + str(int(round(bpy.context.scene.camberloc*10,0))) 
            
            
            thickname = str(bpy.context.scene.nacathickness)
            
            if len(thickname)<2:
                thickname = "0"+str(thickname)
            #print(IntProperty(bpy.types.Scene.nacacamber, get(self)))
            row.label(text = "NACA " + nacaName + thickname)
            
            afname = nacaName + thickname
            nacaPts = bpy.context.scene.nacapoints
            Distribution = bpy.context.scene.distribution
            
            row = layout.row()
            row.operator("ops.naca4digits")
            row.operator("ops.clear_airfoil_points")
            
        """------------------------------------------NACA 5 digits---------------------------------------"""    
        if bpy.context.scene.airfoilmode=='N5d':

            row = layout.row()
#            row.operator("ops.airfoil_type_selection")
#            row = layout.row()
            
            row.prop(context.scene,"cldesign")
            row = layout.row()
            row.prop(context.scene,"camberlocation2")
            row = layout.row()
            row.prop(context.scene,"nacathickness")
            row = layout.row()
            row.prop(context.scene,"nacapoints")
            row = layout.row()
            row.prop(context.scene, "distribution")
            row = layout.row()
            row.prop(context.scene, "reflexedornot")
            #print("herenow",nacacamber)
            #print(bpy.context.scene.nacacamber)
            nacaName = str(int(round(bpy.context.scene.cldesign/0.15,0)))\
             + str(int(bpy.context.scene.camberlocation2/0.05)) \
             +str(int(bpy.context.scene.reflexedornot))
            
            
            thickname = str(bpy.context.scene.nacathickness)
            
            if len(thickname)<2:
                thickname = "0"+str(thickname)
            #print(IntProperty(bpy.types.Scene.nacacamber, get(self)))
            row.label(text = "NACA " + nacaName + thickname)
            
            afname5 = nacaName + thickname
            nacaPts = bpy.context.scene.nacapoints
            Distribution = bpy.context.scene.distribution
            
            row = layout.row()
            row.operator("ops.naca5digits")
            row.operator("ops.clear_airfoil_points")
            
        """--------------------------------------------File import---------------------------------"""    
            
               
        if bpy.context.scene.airfoilmode=='Fimp':
          
            row = layout.row()
            row.operator("import.some_data")
            row = layout.row()
            row.label(text = Path)
            row = layout.row()
            row.operator("ops.clear_airfoil_points")
            
        
        
        

        
        

        #row.prop(obj, "name")
        

class airfoilClassPanel2(Panel):
    bpy.types.Scene.naca_or_file = True
    #obj = context.object
    bl_label = "Geometry"
    bl_idname = "_PT_TestPanel2"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "AirfoilTools"
    
#    bpy.context.scene.nacacamber = 2
#    bpy.context.scene.camberloc = 4
#    bpy.context.scene.nacathickness = 12
    
                                               
    bpy.types.Scene.faceornot= BoolProperty(name = "Fill surface",
                                            description = "If selected, the airfoil outline will be filled to make a plane",
                                            default = True)
                                                                                                                            
    
    
    bpy.types.Scene.chordlength = FloatProperty(
                                            name = "Chord",
                                            description = "Chord length",
                                            default = 1.0
                                            )    
    
    #bpy.types.Scene.nacacamber[0](set==(self, 2) )                               
    wm = WindowManager
    # register internal property
    wm.visibleLine = BoolProperty(default=True)
    wm.nbLine = IntProperty(default=0)
    
#    self.my_float: bpy.props.FloatProperty(name="Float")
#    self.my_bool: bpy.props.BoolProperty(name="Toggle Option")
    #afname: bpy.props.StringProperty(name="String Value")
    
    
    
    def draw(self, context):
        global Path
        global afname
        global afname5
        global nacaPts
        global Pts
        global Distribution
        global Faceornot
        global chordLength
        
        #nacacamber2 = self.nacacamber
        
        layout = self.layout
        
        
        
        #row.StringProperty(name = "test")
    
        #print(bpy.types.Scene.naca_or_file)
  
        row = layout.row()
        row.label(text = "Draw geometry")
        
        row = layout.row()
        row.prop(context.scene, "faceornot")
        row.prop(context.scene, "chordlength")
        row = layout.row()
        
        
        row.operator("ops.generate_surface")
        
        Faceornot = bpy.context.scene.faceornot
        chordLength = bpy.context.scene.chordlength
   
    
classes = [airfoilClassPanel,
            airfoilClassPanel2,
             GenerateSurface,
             ImportAirfoil, 
             ChooseInputType, 

             MakeNaca4digits,
             MakeNaca5digits,
             ClearPoints]

        
#register and unregister

def register():
#    bpy.utils.register_class(airfoilClassPanel)
#    
#    
#    bpy.utils.register_class(GenerateSurface)
#    bpy.utils.register_class(ImportAirfoil)
#    bpy.utils.register_class(ChooseInputType)
    for cls in classes:
        bpy.utils.register_class(cls)
    
    
    
def unregister():
#    bpy.utils.unregister_class(airfoilClassPanel)
#    
#    bpy.utils.unregister_class(GenerateSurface)
#    bpy.utils.unregister_class(ImportAirfoil)
#    bpy.utils.unregister_class(ChooseInputType)
    for cls in classes:
        bpy.utils.unregister_class(cls)
if __name__ == "__main__":
    register()
    

