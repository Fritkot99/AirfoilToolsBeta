# -*- coding: utf-8 -*-
"""
Created on Sun Oct  4 10:26:50 2020

@author: thiba
"""

#import bpy
#import importlib
#import sys

bl_info = {'name' : 'AirfoilTool',
           'version': (0,  6),
           'blender': (2, 93, 5),
           'description': "Airfoil import/generation tool",
           'author': "Thibaut Francotte"
            }

if "bpy" in locals():
    import imp
    imp.reload(mainAddon2)
    print("Reloaded multifiles")
else:
    from . import mainAddon2
    print("Imported multifiles")

import bpy
import os  
 
#from . import mainAddon2    

classes = (mainAddon2.airfoilClassPanel,
            mainAddon2.airfoilClassPanel2,
             mainAddon2.GenerateSurface,
             mainAddon2.ImportAirfoil, 
             mainAddon2.ChooseInputType, 

             mainAddon2.MakeNaca4digits,
             mainAddon2.MakeNaca5digits,
             mainAddon2.ClearPoints)

def register():
    for cls in classes:
            bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
            bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
