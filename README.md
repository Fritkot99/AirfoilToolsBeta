# AirfoilTools
Blender addon to import and generate airfoils,

author: Thibaut Francotte
version: 0.4

Disclaimer: this is a beta version, bugs may occur and more features will be added in future updates.

*******changelog from 0.3******
Solved a bug where for NACA 4-digits airfoils when a camber of 0% was selected the name generator still showed
the camber location - fixed. 

______________________general notes__________________________________

Naca airfoil generation is done according to https://en.wikipedia.org/wiki/NACA_airfoil,
with a correcting factor for the Naca 5-digits design lift coefficient found in https://github.com/dgorissen/naca.

Attention: for file import make sure the text file uses tabs ("\t") as separator between columns, this is the default for 
JavaFoil and http://www.airfoiltools.com/ 's selig dat file. For NACA and NASA airfoils the header is supported but
if you are using another airfoil type like Eppler or other i strongly advise to delete the header in the text file. 


________________________installation__________________________________

step 1: Download the zip file for this addon.

step 2: In Blender>Edit>Preferences go to Add-ons and choose install, then select the zip file.

step 3: Enable the addon by checking the thickbox.

step 4: Enjoy!

_________________________Documentation & tutorial_____________________

A full documentation file is in progress, for now you can find information in the tutorial:
https://www.youtube.com/watch?v=W6oAKTOyMD4


Additional tip(s): 
While cosine points distribution allows to concentrate points toward critical parts of the airfoil,
it slows down the subdivision surface modifier's performance so watch your point count.
