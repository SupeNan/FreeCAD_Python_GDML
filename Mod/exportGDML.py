#***************************************************************************
#*                                                                         
#*   Copyright (c) 2019 Keith Sloan <keith@sloan-home.co.uk>              *
#*                                                                        *
#*   This program is free software; you can redistribute it and/or modify *
#*   it under the terms of the GNU Lesser General Public License (LGPL)   *
#*   as published by the Free Software Foundation; either version 2 of    *
#*   the License, or (at your option) any later version.                  *
#*   for detail see the LICENCE text file.                                *
#*                                                                        *
#*   This program is distributed in the hope that it will be useful,      *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of       *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the        *
#*   GNU Library General Public License for more details.                 *
#*                                                                        *
#*   You should have received a copy of the GNU Library General Public    *
#*   License along with this program; if not, write to the Free Software  *
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 *
#*   USA                                                                  *
#*                                                                        *
#*   Acknowledgements : Ideas & code copied from                          *
#*                      https://github.com/ignamv/geanTipi                *
#*                                                                        *
#***************************************************************************
__title__="FreeCAD - GDML exporter Version"
__author__ = "Keith Sloan <keith@sloan-home.co.uk>"
__url__ = ["https://github.com/KeithSloan/FreeCAD_Geant4"]

import FreeCAD, os, Part, math
from FreeCAD import Vector
from GDMLObjects import GDMLcommon, GDMLBox, GDMLTube

# xml handling
#import argparse
import lxml.etree  as ET
#from   xml.etree.ElementTree import XML 
#################################

try: import FreeCADGui
except ValueError: gui = False
else: gui = True

global zOrder

from GDMLObjects import GDMLQuadrangular, GDMLTriangular, \
                        GDML2dVertex, GDMLSection, \
                        GDMLmaterial, GDMLfraction, \
                        GDMLcomposite, GDMLisotope, \
                        GDMLelement, GDMLconstant

#***************************************************************************
# Tailor following to your requirements ( Should all be strings )          *
# no doubt there will be a problem when they do implement Value
if open.__module__ in ['__builtin__', 'io']:
    pythonopen = open # to distinguish python built-in open function from the one declared here

#################################
# Switch functions
################################
class switch(object):
    value = None
    def __new__(class_, value):
        class_.value = value
        return True

def case(*args):
    return any((arg == switch.value for arg in args))

#########################################################
# Pretty format GDML                                    #
#########################################################
def indent(elem, level=0):
    i = "\n" + level*"  "
    j = "\n" + (level-1)*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for subelem in elem:
            indent(subelem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = j
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = j
    return elem
#################################
#  Setup GDML environment
#################################
def GDMLstructure() :
    print("Setup GDML structure")
    #################################
    # globals
    ################################
    global gdml, define, materials, solids, structure, setup, worldVOL
    global defineCnt, LVcount, PVcount, POScount, ROTcount

    defineCnt = LVcount = PVcount = POScount =  ROTcount = 1

    #gdml = ET.Element('gdml', {
          #'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
          #'xsi:noNamespaceSchemaLocation': "http://service-spi.web.cern.ch/service-spi/app/releases/GDML/schema/gdml.xsd"
#})
    gdml = ET.Element('gdml')
    define = ET.SubElement(gdml, 'define')
    materials = ET.SubElement(gdml, 'materials')
    solids = ET.SubElement(gdml, 'solids')
    structure = ET.SubElement(gdml, 'structure')
    setup = ET.SubElement(gdml, 'setup', {'name': 'Default', 'version': '1.0'})
    #worldVOL = None
    # worldVOL needs to be added after file scanned.
    #ET.ElementTree(gdml).write("/tmp/test2", 'utf-8', True)


def defineMaterials():
    # Replaced by loading Default
    print("Define Materials")
    global materials
   
def defineWorldBox(bbox):
    for obj in FreeCAD.ActiveDocument.Objects :
        # print("{} + {} = ".format(bbox, obj.Shape.BoundBox))
        if hasattr(obj,"Shape"):
           bbox.add(obj.Shape.BoundBox)
        if hasattr(obj,"Mesh"):
           bbox.add(obj.Mesh.BoundBox)
        if hasattr(obj,"Points"):
           bbox.add(obj.Points.BoundBox)
    #   print(bbox)
    # Solids get added to solids section of gdml ( solids is a global )
    name = 'WorldBox'
    ET.SubElement(solids, 'box', {'name': name,
                             'x': str(1000), \
                             'y': str(1000), \
                             'z': str(1000), \
                     #'x': str(2*max(abs(bbox.XMin), abs(bbox.XMax))), \
                     #'y': str(2*max(abs(bbox.YMin), abs(bbox.YMax))), \
                     #'z': str(2*max(abs(bbox.ZMin), abs(bbox.ZMax))), \
                     'lunit': 'mm'})
    return(name)

def addObjectToVol(obj, lvol, name, solidName, material) :
    #lvol = ET.SubElement(vol,'volume', {'name':name})
    ET.SubElement(lvol, 'materialref', {'ref': material})
    ET.SubElement(lvol, 'solidref', {'ref': solidName})

def createLVandPV(obj, name, solidName):
    #
    # Cannot rely on obj.Name so have to pass name
    # Logical & Physical Volumes get added to structure section of gdml
    #
    #ET.ElementTree(gdml).write("test9d", 'utf-8', True)
    #print("Object Base")
    #dir(obj.Base)
    #print dir(obj)
    #print dir(obj.Placement)
    global PVcount, POScount, ROTcount
    return
    pvName = 'PV'+name+str(PVcount)
    PVcount += 1
    pos  = obj.Placement.Base
    lvol = ET.SubElement(structure,'volume', {'name':pvName})
    ET.SubElement(lvol, 'materialref', {'ref': 'SSteel0x56070ee87d10'})
    ET.SubElement(lvol, 'solidref', {'ref': solidName})
    # Place child physical volume in World Volume
    phys = ET.SubElement(lvol, 'physvol')
    ET.SubElement(phys, 'volumeref', {'ref': pvName})
    x = pos[0]
    y = pos[1]
    z = pos[2]
    if x!=0 and y!=0 and z!=0 :
       posName = 'Pos'+name+str(POScount)
       POScount += 1
       ET.SubElement(phys, ' positionref' {'name': posName})
       ET.SubElement(define, 'position', {'name': posName, 'unit': 'mm', \
                  'x': str(x), 'y': str(y), 'z': str(z) })
    angles = obj.Placement.Rotation.toEuler()
    print ("Angles")
    print (angles)
    a0 = angles[0]
    a1 = angles[1]
    a2 = angles[2]
    if a0!=0 and a1!=0 and a2!=0 :
       rotName = 'Rot'+name+str(ROTcount)
       ROTcount += 1
       ET.SubElement(phys, 'rotationref', {'name': rotName})
       ET.SubElement(define, 'rotation', {'name': rotName, 'unit': 'deg', \
                  'x': str(-a2), 'y': str(-a1), 'z': str(-a0)})

def createAdjustedLVandPV(obj, name, solidName, delta):
    # Allow for difference in placement between FreeCAD and GDML
    adjObj = obj
    rot = FreeCAD.Rotation(obj.Placement.Rotation)
    adjObj.Placement.move(rot.multVec(delta))#.negative()
    createLVandPV(adjObj, name, solidName)

def reportObject(obj) :
    
    print("Report Object")
    print(obj)
    print("Name : "+obj.Name)
    print("Type : "+obj.TypeId) 
    if hasattr(obj,'Placement') :
       print("Placement")
       print("Pos   : "+str(obj.Placement.Base))
       print("axis  : "+str(obj.Placement.Rotation.Axis))
       print("angle : "+str(obj.Placement.Rotation.Angle))
    
    while switch(obj.TypeId) :

      ###########################################
      # FreeCAD GDML Parts                      #
      ###########################################
      if case("Part::FeaturePython") : 
         print("Part::FeaturePython")
         if hasattr(obj.Proxy,'Type'):
            print (obj.Proxy.Type)
            print (obj.Name)
         else :
            print("Not a GDML Feature")
            
         #print dir(obj)
         #print dir(obj.Proxy)
         #print("cylinder : Height "+str(obj.Height)+ " Radius "+str(obj.Radius))
         break
      ###########################################
      # FreeCAD Parts                           #
      ###########################################
      if case("Part::Sphere") :
         print("Sphere Radius : "+str(obj.Radius))
         break
           
      if case("Part::Box") : 
         print("cube : ("+ str(obj.Length)+","+str(obj.Width)+","+str(obj.Height)+")")
         break

      if case("Part::Cylinder") : 
         print("cylinder : Height "+str(obj.Height)+ " Radius "+str(obj.Radius))
         break
   
      if case("Part::Cone") :
         print("cone : Height "+str(obj.Height)+ " Radius1 "+str(obj.Radius1)+" Radius2 "+str(obj.Radius2))
         break

      if case("Part::Torus") : 
         print("Torus")
         print(obj.Radius1)
         print(obj.Radius2)
         break

      if case("Part::Prism") :
         print("Prism")
         break

      if case("Part::RegularPolygon") :
         print("RegularPolygon")
         break

      if case("Part::Extrusion") :
         print("Extrusion")
         break

      if case("Circle") :
         print("Circle")
         break

      if case("Extrusion") : 
         print("Wire extrusion")
         break

      if case("Mesh::Feature") :
         print("Mesh")
         #print dir(obj.Mesh)
         break


      print("Other")
      print(obj.TypeId)
      break

def processPlanar(obj, shape, name ) :
    print ('Polyhedron ????')
    global defineCnt
    #
    print("Add tessellated Solid")
    tess = ET.SubElement(solids,'tessellated',{'name': name})
    print("Add Vertex positions")
    for f in shape.Faces :
       baseVrt = defineCnt
       for vrt in f.Vertexes :
           vnum = 'v'+str(defineCnt)
           ET.SubElement(define, 'position', {'name': vnum, \
              'x': str(vrt.Point.x), \
              'y': str(vrt.Point.y), \
              'z': str(vrt.Point.z), \
              'unit': 'mm'})
           defineCnt += 1
       print("Add vertex to tessellated Solid")
       vrt1 = 'v'+str(baseVrt)
       vrt2 = 'v'+str(baseVrt+1)
       vrt3 = 'v'+str(baseVrt+2)
       vrt4 = 'v'+str(baseVrt+3)
       NumVrt = len(f.Vertexes)
       if NumVrt == 3 :
          ET.SubElement(tess,'triangular',{ \
                      'vertex1': vrt1, \
                      'vertex2': vrt2, \
                      'vertex3': vrt3, \
                      'type': 'ABSOLUTE'})
       elif NumVrt == 4 :   
          ET.SubElement(tess,'quadrangular',{ \
                      'vertex1': vrt1, \
                      'vertex2': vrt2, \
                      'vertex3': vrt3, \
                      'vertex4': vrt4, \
                      'type': 'ABSOLUTE'})

def checkShapeAllPlanar(Shape) :
    for f in Shape.Faces :
        if f.Surface.isPlanar() == False :
           return False
        break
    return True

#    Add XML for TessellateSolid
def mesh2Tessellate(mesh, name) :
     global defineCnt

     baseVrt = defineCnt
     print ("mesh")
     print (mesh)
     print (dir(mesh))
     print ("Facets")
     print (mesh.Facets)
     print ("mesh topology")
     print (dir(mesh.Topology))
     print (mesh.Topology)
#
#    mesh.Topology[0] = points
#    mesh.Topology[1] = faces
#
#    First setup vertex in define section vetexs (points) 
     print("Add Vertex positions")
     for fc_points in mesh.Topology[0] : 
         print(fc_points)
         v = 'v'+str(defineCnt)
         ET.SubElement(define, 'position', {'name': v, \
                  'x': str(fc_points[0]), \
                  'y': str(fc_points[1]), \
                  'z': str(fc_points[2]), \
                  'unit': 'mm'})
         defineCnt += 1         
#                  
#     Add faces
#
     print("Add Triangular vertex")
     tess = ET.SubElement(solids,'tessellated',{'name': name})
     for fc_facet in mesh.Topology[1] : 
       print(fc_facet)
       vrt1 = 'v'+str(baseVrt+fc_facet[0])
       vrt2 = 'v'+str(baseVrt+fc_facet[1])
       vrt3 = 'v'+str(baseVrt+fc_facet[2])
       ET.SubElement(tess,'triangular',{ \
         'vertex1': vrt1, 'vertex2': vrt2 ,'vertex3': vrt3, 'type': 'ABSOLUTE'})


def processMesh(obj, Mesh, Name) :
    #  obj needed for Volune names
    #  object maynot have Mesh as part of Obj
    #  Name - allows control over name
    print("Create Tessellate Logical Volume")
    createLVandPV(obj, Name, 'Tessellated')
    mesh2Tessellate(Mesh, Name)
    return(Name)

def shape2Mesh(shape) :
     import MeshPart
     return (MeshPart.meshFromShape(Shape=shape, Deflection = 0.0))
#            Deflection= params.GetFloat('meshdeflection',0.0)) 

def processObjectShape(obj) :
    # Check if Planar
    # If plannar create Tessellated Solid with 3 & 4 vertex as appropriate
    # If not planar create a mesh and the a Tessellated Solid with 3 vertex
    print("Process Object Shape")
    print(obj)
    print(obj.PropertiesList)
    if not hasattr(obj,'Shape') :
       return 
    shape = obj.Shape
    print (shape)
    print(shape.ShapeType)
    while switch(shape.ShapeType) : 
      if case("Mesh::Feature") :
         print("Mesh - Should not occur should have been handled")
         #print("Mesh")
         #tessellate = mesh2Tessellate(mesh) 
         #return(tessellate)
         #break

         print("ShapeType Not handled")
         print(shape.ShapeType)
         break

#   Dropped through to here
#   Need to check has Shape

    print('Check if All planar')
    planar = checkShapeAllPlanar(shape)
    print(planar)

    if planar :
       return(processPlanar(obj,shape,obj.Name))

    else :
       # Create Mesh from shape & then Process Mesh
       #to create Tessellated Solid in Geant4
       return(processMesh(obj,shape2Mesh(shape),obj.Name))

def processBoxObject(obj, addVolsFlag) :
    # Needs unique Name
    boxName = 'Box' + obj.Name
    ET.SubElement(solids, 'box',{'name': boxName, \
                           'x': str(obj.Length.Value),  \
                           'y': str(obj.Width.Value),  \
                           'z': str(obj.Height.Value),  \
                           'lunit' : 'mm'})
    if addVolsFlag :
       # Adjustment for position in GDML
       delta = FreeCAD.Vector(obj.Length.Value / 2, \
                           obj.Width.Value / 2,  \
                           obj.Height.Value / 2)

       createAdjustedLVandPV(obj, obj.Name, boxName, delta)
    return(boxName)

def processCylinderObject(obj, addVolsFlag) :
    # Needs unique Name
    cylName = 'Cyl-' + obj.Name
    ET.SubElement(solids, 'tube',{'name': cylName, \
                           'rmax': str(obj.Radius.Value), \
                           'deltaphi': str(float(obj.Angle)), \
                           'aunit': obj.aunit,
                           'z': str(obj.Height.Value),  \
                           'lunit' : 'mm'})
    if addVolsFlag :
       # Adjustment for position in GDML
       delta = FreeCAD.Vector(0, 0, obj.Height.Value / 2)
       createAdjustedLVandPV(obj, obj.Name, cylName, delta)
    return(cylName)

def processConeObject(obj, addVolsFlag) :
    # Needs unique Name
    coneName = 'Cone' + obj.Name
    ET.SubElement(solids, 'cone',{'name': coneName, \
                           'rmax1': str(obj.Radius1.Value),  \
                           'rmax2': str(obj.Radius2.Value),  \
                           'deltaphi': str(float(obj.Angle)), \
                           'aunit': obj.aunit,
                           'z': str(obj.Height.Value),  \
                           'lunit' : 'mm'})
    if addVolsFlag :
       # Adjustment for position in GDML
       delta = FreeCAD.Vector(0, 0, obj.Height.Value / 2)
       createAdjustedLVandPV(obj, obj.Name, coneName, delta)
    return(coneName)

def processSection(obj, addVolsflag) :
    print("Process Section")
    ET.SubElement(solids, 'section',{'vertex1': obj.v1, \
            'vertex2': obj.v2, 'vertex3': obj.v3, 'vertex4': obj.v4, \
            'type': obj.vtype})


def processSphereObject(obj, addVolsFlag) :
    # Needs unique Name
    sphereName = 'Sphere' + obj.Name
    ET.SubElement(solids, 'sphere',{'name': sphereName, \
                           'rmax': str(obj.Radius.Value), \
                           'starttheta': str(90.-float(obj.Angle2)), \
                           'deltatheta': str(float(obj.Angle2-obj.Angle1)), \
                           'deltaphi': str(float(obj.Angle3)), \
                           'aunit': obj.aunit,
                           'lunit' : 'mm'})
    if addVolsFlag :
       createLVandPV(obj,obj.Name,sphereName)
    return(sphereName)

def addPhysVol(obj, vol, volName) :
    print("Add PhysVol to Vol") 
    pvol = ET.SubElement(vol,'physvol')
    ET.SubElement(pvol,'volumeref',{'ref':volName})
    return pvol
    
def addPositionReferenceSolid(obj, solid) :
    # not also function to add without reference
    global POScount, ROTcount

    print("Add pos and rot references to PhysVol")
    pos = obj.Placement.Base
    print(pos)
    x = pos[0]
    y = pos[1]
    z = pos[2]
    name = obj.Name
    posName = 'PS'+name+str(POScount)
    POScount += 1
    ET.SubElement(define,'position',{'name' : posName, 'unit': 'mm', \
            'x': str(x), 'y': str(y), 'z': str(z) })
    ET.SubElement(solid,'positionref',{'ref' : posName})
    angles = obj.Placement.Rotation.toEuler()
    print ("Angles")
    print (angles)
    a0 = angles[0]
    a1 = angles[1]
    a2 = angles[2]
    if a0!=0 or a1!=0 or a2!=0 :
       rotName = 'Rot'+name+str(ROTcount)
       ROTcount += 1
       ET.SubElement(define, 'rotation', {'name': rotName, 'unit': 'deg', \
                  'x': str(-a2), 'y': str(-a1), 'z': str(-a0)})
       ET.SubElement(solid,'rotationref',{'ref' : rotName})


def addPositionRotationPVol(obj,pvol) :
    # This does not add references - Is it redundant
    global POScount, ROTcount

    print("Add pos and rot to PhysVol")
    pos = obj.Placement.Base
    print(pos)
    x = pos[0]
    y = pos[1]
    z = pos[2]
    posName = 'PS'+obj.Name+str(POScount)
    POScount += 1
    ET.SubElement(pvol,'position',{'name' : posName, 'unit': 'mm', \
            'x': str(x), 'y': str(y), 'z': str(z) })
    angles = obj.Placement.Rotation.toEuler()
    print ("Angles")
    print (angles)
    a0 = angles[0]
    a1 = angles[1]
    a2 = angles[2]
    if a0!=0 or a1!=0 or a2!=0 :
       rotName = 'Rot'+name+str(ROTcount)
       ROTcount += 1
       ET.SubElement(pvol, 'rotation', {'name': rotName, 'unit': 'deg', \
                  'x': str(-a2), 'y': str(-a1), 'z': str(-a0)})

def addVolRef(vol,solidName,material) :
    ET.SubElement(vol,'solidref',{'ref': solidName})
    ET.SubElement(vol,'materialref',{'ref': material})

def testDefaultPlacement(obj) :
    #print(dir(obj.Placement.Rotation))
    print(obj.Placement.Base)
    print(obj.Placement.Rotation.Angle)
    if obj.Placement.Base == FreeCAD.Vector(0,0,0) and \
       obj.Placement.Rotation.Angle == 0 :
       return True
    else :
       return False

# Should no longer be used
def postProcessObject(obj, vol, solidName ) :
    material = obj.material
    addVolRef(vol,solidName,material)
    print(testDefaultPlacement(obj))
    if testDefaultPlacement(obj) == False :
       print("Not Default placement")
       volName = 'PV-'+obj.Name
       addVol(volName, solidName, material)
       pvol = addPhysVol(obj,vol,volname)
       addPositionRotationPVol(obj,pvol)    


def processGDMLBoxObject(obj, vol, addVolsFlag) :
    # Needs unique Name
    # flag needed for boolean otherwise parse twice
    boxName = 'Box' + obj.Name
    ET.SubElement(solids, 'box',{'name': boxName, \
                          'x': str(obj.x.Value),  \
                          'y': str(obj.y.Value),  \
                          'z': str(obj.z.Value),  \
                          'lunit' : 'mm'})
    return (boxName)

def processGDMLConeObject(obj, vol, addVolsFlag) :
    # Needs unique Name
    # flag needed for boolean otherwise parse twice
    coneName = 'Cone' + obj.Name
    ET.SubElement(solids, 'cone',{'name': coneName, \
                          'rmin1': str(obj.rmin1.Value),  \
                          'rmin2': str(obj.rmin2.Value),  \
                          'rmax1': str(obj.rmax1.Value),  \
                          'rmax2': str(obj.rmax2.Value),  \
                          'startphi': str(obj.startphi), \
                          'deltaphi': str(obj.deltaphi), \
                          'aunit': obj.aunit,
                          'z': str(obj.z.Value),  \
                          'lunit' : 'mm'})
    return(coneName)

def processGDMLEllipsoidObject(obj, vol, addVolsFlag) :
    # Needs unique Name
    # flag needed for boolean otherwise parse twice
    ellipsoidName = 'Ellipsoid' + obj.Name
    ET.SubElement(solids, 'ellipsoid',{'name': ellipsoidName, \
                          'ax': str(obj.ax.Value),  \
                          'by': str(obj.by.Value),  \
                          'cz': str(obj.cz.Value),  \
                          'zcut1': str(obj.zcut1.Value),  \
                          'zcut2': str(obj.zcut2.Value),  \
                          'lunit' : 'mm'})
    return(ellipsoidName)

def processGDMLElTubeObject(obj, vol, addVolsFlag) :
    # Needs unique Name
    # flag needed for boolean otherwise parse twice
    eltubeName = 'Cone' + obj.Name
    ET.SubElement(solids, 'eltube',{'name': eltubeName, \
                          'dx': str(obj.dx.Value),  \
                          'dy': str(obj.dy.Value),  \
                          'dz': str(obj.dz.Value),  \
                          'lunit' : 'mm'})
    return(eltubeName)

def processGDMLPolyconeObject(obj, vol, addVolsFlag) :
    # Needs unique Name
    # flag needed for boolean otherwise parse twice
    #polyconeName = 'Cone' + obj.Name
    polyconeName = obj.Name
    ET.SubElement(solids, 'genericPolycone',{'name': polyconeName, \
                          'startphi': str(obj.startphi),  \
                          'deltaphi': str(obj.deltaphi),  \
                          'aunit': obj.aunit,  \
                          'lunit' : 'mm'})
    print(obj.OutList)
    for zplane in obj.OutList :
        ET.SubElement(solids, 'zplane',{'rmin': str(zplane.rmin), \
                               'rmax' : str(zplane.rmax), \
                               'z' : str(zplane.z)})

    return(polyconeName)

def processGDMLQuadObject(obj, addVolsFlag) :
    print("GDMLQuadrangular")
    ET.SubElement(solids, 'quadrangular',{'vertex1': obj.v1, \
            'vertex2': obj.v2, 'vertex3': obj.v3, 'vertex4': obj.v4, \
            'type': obj.vtype})
    

def processGDMLSphereObject(obj, vol, addVolsFlag) :
    # Needs unique Name
    # flag needed for boolean otherwise parse twice
    sphereName = 'Sphere' + obj.Name
    ET.SubElement(solids, 'sphere',{'name': sphereName, \
                           'rmin': str(obj.rmin.Value),  \
                           'rmax': str(obj.rmax.Value),  \
                           'startphi': str(obj.startphi), \
                           'deltaphi': str(obj.deltaphi), \
                           'aunit': obj.aunit,
                           'lunit' : 'mm'})
    return(sphereName)

def processGDMLTessellatedObject(obj, vol, addVolsFlag) :
    # Needs unique Name
    # flag needed for boolean otherwise parse twice
    # Need to output unique define positions
    # Need to create set of positions
    #for items in obj.Outlist :
    #    ET.SubElement(GDMLShared.define,'position',{'name': obj.Name + 'v1', \
    #            'x':items.x , 'y':items.y, 'z':items.z,'unit':'mm')

    tessName = 'Tess' + obj.Name
    ET.SubElement(solids, 'tessellated',{'name': tessName})
    print(len(obj.OutList))
    for items in obj.OutList :
        if hasattr(items,'v4' ) :
            ET.SubElement(solids,'quadrangular',{'vertex1':'v1', \
                    'vertex2':'v2', 'vertex3':'v3', 'vertex4':'v4',
                                 'type':'ABSOLUTE'})
        else :    
            ET.SubElement(solids,'triangular',{'vertex1':'v1', 'vertex2':'v2', \
                                 'vertex3':'v3','type':'ABSOLUTE'})

    return(tessName)


def processGDMLTrapObject(obj, vol, addVolsFlag) :
    # Needs unique Name
    # flag needed for boolean otherwise parse twice
    trapName = 'Trap' + obj.Name
    ET.SubElement(solids, 'trap',{'name': trapName, \
                           'z': str(obj.z.Value),  \
                           'theta': str(obj.theta),  \
                           'phi': str(obj.phi), \
                           'x1': str(obj.x1.Value),  \
                           'x2': str(obj.x2.Value),  \
                           'x3': str(obj.x3.Value),  \
                           'x4': str(obj.x4.Value),  \
                           'y1': str(obj.y1.Value),  \
                           'y2': str(obj.y2.Value),  \
                           'alpha1': str(obj.alpha), \
                           'alpha2': str(obj.alpha), \
                           'aunit': obj.aunit, \
                           'lunit': obj.lunit})
    return(trapName)

def processGDMLTrdObject(obj, vol, addVolsFlag) :
    # Needs unique Name
    # flag needed for boolean otherwise parse twice
    trdName = 'Trd' + obj.Name
    ET.SubElement(solids, 'trd',{'name': trdName, \
                           'z': str(obj.z.Value),  \
                           'x1': str(obj.x1.Value),  \
                           'x2': str(obj.x2.Value),  \
                           'y1': str(obj.y1.Value),  \
                           'y2': str(obj.y2.Value),  \
                           'lunit': obj.lunit})
    return(trdName)

def processGDMLTriangle(obj, addVolsFlag) :
    print("Process GDML Triangle")
    ET.SubElement(solids, 'triangular',{'vertex1': obj.v1, \
            'vertex2': obj.v2, 'vertex3': obj.v3,  \
            'type': obj.vtype})

def processGDMLTubeObject(obj, vol, addVolsFlag) :
    # Needs unique Name
    # flag needed for boolean otherwise parse twice
    tubeName = 'Tube' + obj.Name
    ET.SubElement(solids, 'tube',{'name': tubeName, \
                           'rmin': str(obj.rmin.Value),  \
                           'rmax': str(obj.rmax.Value),  \
                           'startphi': str(obj.startphi), \
                           'deltaphi': str(obj.deltaphi), \
                           'aunit': obj.aunit,
                           'z': str(obj.z.Value),  \
                           'lunit' : 'mm'})
    return(tubeName)

def processGDMLXtruObject(obj, vol, addVolsFlag) :
    # Needs unique Name
    # flag needed for boolean otherwise parse twice
    #tubeName = 'Tube' + obj.Name
    xtruName = obj.Name
    ET.SubElement(solids, 'xtru',{'name': xtruName, \
                           'lunit' : 'mm'})
    for items in obj.OutList :
        if items.Type == 'twoDimVertex' :
           ET.SubElement(solids, 'twoDimVertex',{'x': str(items.x), \
                                   'y': str(items.y)})
        if items.Type == 'section' :
           ET.SubElement(solids, 'section',{'zOrder': str(items.zOrder), \
                                  'zPosition': str(items.zPosition), \
                                  'xOffset' : str(items.xOffset), \
                                  'yOffset' : str(items.yOffset), \
                                  'scalingFactor' : str(items.scalingFactor)})
    return(xtruName)

def processGDML2dVertex(obj, addVolsFlag) :
    print("Process 2d Vertex")
    ET.SubElement(solids, 'twoDimVertex',{'x': obj.x, 'y': obj.y})


# Need to add position of object2 relative to object1
# Need to add rotation ??? !!!!
def addBooleanPositionAndRotation(element,obj1,obj2):
    print ("addBooleanPosition")
    print ("Position obj1")
    print (obj1.Placement.Base)
    print ("Position obj2")
    print (obj2.Placement.Base)
    global defineCnt
    positionName = 'Pos'+str(defineCnt)
    pos = obj2.Placement.Base - obj1.Placement.Base
    # Need to add rotation ??? !!!!
    ET.SubElement(define, 'position', {'name': positionName, \
            'x': str(pos[0]), 'y': str(pos[1]), 'z': str(pos[2]), \
            'unit': 'mm'})
    defineCnt += 1
    ET.SubElement(element,'positionref', {'ref': positionName})

def processGroup(obj, vol, newvol, pName, addVolsFlag) :
    print("Group Num : "+str(len(obj.Group)))
    for grp in obj.Group :
        processObject(grp, vol, newVol, pName, addVolsFlag)

def processElement(obj, item): # maybe part of material or element (common code)
    if hasattr(obj,'Z') :
       #print(dir(obj))
       item.set('Z',str(obj.Z)) 

    if hasattr(obj,'atom_unit') :
       atom = ET.SubElement(item,'atom') 
       atom.set('unit',str(obj.atom_unit)) 
            
       if hasattr(obj,'atom_value') :
          atom.set('value',str(obj.atom_value)) 

def processMaterials() :
    print("\nProcess Materials")
    global materials
   
    for obj in FreeCAD.ActiveDocument.Objects:
        print(obj.TypeId+" : "+obj.Label)

        #processMaterialObject(obj)
        if processMaterialObject(obj) == False :
           break

def processMaterialObject(obj) :
    global item
    print(obj.Label)
    while switch(obj.TypeId) :
       if case("App::DocumentObjectGroupPython"):
          print("   Object List : "+obj.Name)
          #print(obj)
          while switch(obj.Name) :
             if case("Materials") : 
                print("Materials")
                #return True
                break

             if case("Isotopes") :
                print("Isotopes")
                #return True
                break
            
             if case("Elements") :
                print("Elements")
                #return True
                break
         
             break
          
          if isinstance(obj.Proxy,GDMLconstant) :
             print("GDML constant")
             #print(dir(obj))

             item = ET.SubElement(define,'constant',{'name': obj.Name, \
                                 'value': obj.value })
             #return True
          #return   
            
          if isinstance(obj.Proxy,GDMLmaterial) :
             print("GDML material")
             #print(dir(obj))

             item = ET.SubElement(materials,'material',{'name': obj.Name})

             # process common options material / element
             processElement(obj, item)

          if hasattr(obj,'Dunit') :
             ET.SubElement(item,'D',{'unit': obj.Dunit, \
                                      'value': str(obj.Dvalue)})

          if hasattr(obj,'Tunit') :
             ET.SubElement(item,'T',{'unit': obj.Tunit, \
                                      'value': str(obj.Tvalue)})
           
          if hasattr(obj,'MEEunit') :
             ET.SubElement(item,'MEE',{'unit': obj.MEEunit, \
                                               'value': str(obj.MEEvalue)})

          #return True
          #break

          if isinstance(obj.Proxy,GDMLfraction) :

             print("GDML fraction")
             ET.SubElement(item,'fraction',{'n': str(obj.n), \
                                          'ref': obj.Name})
             #return True
             break

          if isinstance(obj.Proxy,GDMLcomposite) :
             print("GDML Composite")
             #return True
             break

          if isinstance(obj.Proxy,GDMLisotope) :
             print("GDML isotope")
             item = ET.SubElement(materials,'isotope',{'N': str(obj.N), \
                                                      'Z': str(obj.Z), \
                                                      'name' : obj.Name})
             ET.SubElement(item,'atom',{'unit': obj.unit, \
                                      'value': str(obj.value)})
             #return True
             break

          if isinstance(obj.Proxy,GDMLelement) :
             print("GDML element")
             item = ET.SubElement(materials,'element',{'name': obj.Name})
             processElement(obj,item)
             #return True
             break

          # Commented out as individual objects will also exist
          #if len(obj.Group) > 1 :
          #   for grp in obj.Group :
          #       processObject(grp, addVolsFlag)
          # All non Material Objects should terminate Loop
          #return False
          break

       return False
       break

def processGDMLsolid(obj, vol, addVolsFlag) :
    # flag needed for boolean otherwise parse twice
    while switch(obj.Proxy.Type) :
       if case("GDMLBox") :
          print("      GDMLBox") 
          return(processGDMLBoxObject(obj, vol, addVolsFlag))
          break

       if case("GDMLEllipsoid") :
          print("      GDMLEllipsoid") 
          return(processGDMLEllipsoidObject(obj, vol, addVolsFlag))
          break

       if case("GDMLElTube") :
          print("      GDMLElTube") 
          return(processGDMLElTubeObject(obj, vol, addVolsFlag))
          break

       if case("GDMLCone") :
          print("      GDMLCone") 
          return(processGDMLConeObject(obj, vol, addVolsFlag))
          break

       if case("GDMLPolycone") :
          print("      GDMLPolycone") 
          return(processGDMLPolyconeObject(obj, vol, addVolsFlag))
          break
             
       if case("GDMLSphere") :
          print("      GDMLSphere") 
          return(processGDMLSphereObject(obj, vol, addVolsFlag))
          break

       if case("GDMLTessellated") :
          print("      GDMLTessellated") 
          return(processGDMLTessellatedObject(obj, vol, addVolsFlag))
          break

       if case("GDMLTrap") :
          print("      GDMLTrap") 
          return(processGDMLTrapObject(obj, vol, addVolsFlag))
          break

       if case("GDMLTrd") :
          print("      GDMLTrd") 
          return(processGDMLTrdObject(obj, vol, addVolsFlag))
          break

       if case("GDMLTube") :
          print("      GDMLTube") 
          return(processGDMLTubeObject(obj, vol, addVolsFlag))
          print("GDML Tube processed")
          break

       if case("GDMLXtru") :
          print("      GDMLXtru") 
          return(processGDMLXtruObject(flag, obj, vol, addVolsFlag))
          break

       print("Not yet Handled")
       break  

import collections
from itertools import islice

def consume(iterator) :
    next(islice(iterator,2,2), None)

def processObject(obj, vol, newVol, pName, addVolsFlag) :
    # return solid or boolean reference name or None
    # addVolsFlag = True then create Logical & Physical Volumes
    #             = False needed for booleans
    #ET.ElementTree(gdml).write("test9a", 'utf-8', True)
    print("Process Object : "+obj.Name)
    while switch(obj.TypeId) :

      if case("App::Part") :
         if hasattr(obj,'OutList') :
            name = obj.Label
            vol = newVol
            newVOL = ET.SubElement(structure,'volume',{'name':name}) 
            global lst
            lst = iter(obj.OutList)
            for sub in lst :
                print(sub.Name)
                ret = processObject(sub, vol, newVOL, name, addVolsFlag) 
                # once first solid is processed set flag to add PV
                if ret != None :
                   print("First Solid : "+ret)
                   addVolsFlag = True 
         return    
         break
         
      if case("App::Origin") :
         print("App Origin")
         return
         break

      if case("App::GeoFeature") :
         print("App GeoFeature")
         return
         break

      if case("App::Line") :
         print("App Line")
         return
         break

      if case("App::Plane") :
         print("App Plane")
         return
         break

      if case("Part::Cut") :
         # Maybe Booleans could be grouped with GDML solids 
         print("   Cut")
         cutName = 'Cut'+obj.Name
         ref1 = processGDMLsolid(obj.Base, vol, False)
         ref2 = processGDMLsolid(obj.Tool, vol, False)
         subtract = ET.SubElement(solids,'subtraction',{'name': cutName })
         ET.SubElement(subtract,'first', {'ref': ref1})
         ET.SubElement(subtract,'second',{'ref': ref2})
         addVolRef(newVol,cutName,obj.Base.material)
         pvol = addPhysVol(obj,vol,pName)
         defaultPlacement = testDefaultPlacement(obj)
         if defaultPlacement == False :
            addPositionReferenceSolid(obj,subtract)    
         consume(lst)
         return cutName
         break

      if case("Part::Fuse") :
         print("   Union")
         unionName = 'Union'+obj.Name
         ref1 = processGDMLsolid(obj.Base, vol, False)
         ref2 = processGDMLsolid(obj.Tool, vol, False)
         union = ET.SubElement(solids,'union',{'name': unionName })
         ET.SubElement(union,'first', {'ref': ref1})
         ET.SubElement(union,'second',{'ref': ref2})
         addVolRef(newVol,unionName,obj.Base.material)
         pvol = addPhysVol(obj,vol,pName)
         defaultPlacement = testDefaultPlacement(obj)
         if defaultPlacement == False :
            addPositionReferenceSolid(obj,union)    
         consume(lst)
         return unionName
         break

      if case("Part::Common") :
         print("   Intersection")
         intersectName = 'Intersect'+obj.Name
         ref1 = processGDMLsolid(obj.Base, vol, False)
         ref2 = processGDMLsolid(obj.Tool, vol, False)
         intersect = ET.SubElement(solids,'intersection',{'name': intersectName })
         ET.SubElement(intersect,'first', {'ref': ref1})
         ET.SubElement(intersect,'second',{'ref': ref2})
         addVolRef(newVol,intersectName,obj.Base.material)
         pvol = addPhysVol(obj,vol,pName)
         defaultPlacement = testDefaultPlacement(obj)
         if defaultPlacement == False :
            addPositionReferenceSolid(obj,intersect)    
         consume(lst)
         return intersectName
         break

      if case("Part::MultiFuse") :
         print("   Multifuse") 
         multName = 'MultiFuse'+obj.Name
         multUnion = ET.Element('multiUnion',{'name': multName })
         for subobj in obj.Shapes:
            solidName = processObject(subobj, vol, newVol, pName, False)
            node = ET.SubElement(multUnion,'multiUnionNode', \
               {'MF-Node' : 'Node-'+solidName})
            ET.SubElement(node,'solid', {'ref': solidName})
            addBooleanPositionAndRotation(node,subobj.Base,subobj.Tool)
            #addPositionAndRotation(node,subobj)
         solids.append(multUnion) 
         return multName
         break

      if case("Part::MultiCommon") :
         print("   Multi Common / intersection")
         print("   Not available in GDML")
         exit(-3)
         break

      if case("Mesh::Feature") :
         print("   Mesh Feature") 
         return(processMesh(obj, obj.Mesh, obj.Name))
         break

      if case("Part::FeaturePython"):
          print("   Python Feature")
          if hasattr(obj.Proxy, 'Type') :
             print(obj.Proxy.Type) 
             solidName = processGDMLsolid(obj, newVol, addVolsFlag)
             material = obj.material
             addVolRef(newVol,solidName,material)
             print(testDefaultPlacement(obj))
             defaultPlacement = testDefaultPlacement(obj)
             if defaultPlacement == False or addVolsFlag == True :
                print("Add Physical Volume : "+pName ) 
                #addVol(volName, solidName, material)
                pvol = addPhysVol(obj,vol,pName)
                print("Not Default placement")
                if defaultPlacement == False :
                   addPositionRotationPVol(obj,pvol)    
             return solidName
          else :
             print("Not a GDML Feature")
          break  
      # Same as Part::Feature but no position
      if case("App::FeaturePython") :
         print("App::FeaturePython") 
         # Following not needed as handled bu Outlist on Tessellated
         #if isinstance(obj.Proxy, GDMLQuadrangular) :
         #   return(processGDMLQuadObject(obj, addVolsFlag))
         #   break
  
         #if isinstance(obj.Proxy, GDMLTriangular) :
         #   return(processGDMLTriangleObject(obj, addVolsFlag))
         #   break
          
    # Following not needed as handled bu Outlist on Xtru

         #if isinstance(obj.Proxy, GDML2dVertex) :
         #   return(processGDML2dVertObject(obj, addVolsFlag))
         #   break
            
         #if isinstance(obj.Proxy, GDMLSection) :
         #   return(processGDMLSection(obj, addVolsFlag))
         #   break
         break  

      #
      #  Now deal with objects that map to GDML solids
      #
      if case("Part::Box") :
         print("    Box")
         return(processBoxObject(obj, addVolsFlag))
         break

      if case("Part::Cylinder") :
         print("    Cylinder")
         return(processCylinderObject(obj, addVolsFlag))
         break

      if case("Part::Cone") :
         print("    Cone")
         return(processConeObject(obj, addVolsFlag))
         break

      if case("Part::Sphere") :
         print("    Sphere")
         return(processSphereObject(obj, addVolsFlag))
         break

      # Not a Solid that translated to GDML solid
      # Dropped through so treat object as a shape
      # Need to check obj has attribute Shape
      # Create tessellated solid
      #
      #return(processObjectShape(obj, addVolsFlag))
      print("Convert FreeCAD shape to GDML Tessellated")
      print(obj.TypeId)
      if hasattr(obj,'Shape') :
         if obj.Shape.isValid() : 
            return(processObjectShape(obj))
      break

def createWorldVol():
    print("Need to create World Volume")
    bbox = FreeCAD.BoundBox()
    ET.SubElement(setup,'world', {'ref':name})
    return ET.SubElement(structure,'volume',{'name':name}) 

def processWorldVol(first) :
    # Check If Pure GDML workbench 
    # return worldVol xml element
    global setup, structure
    #print(dir(first)
    if hasattr(first,'OutList') :
       objList = first.OutList
       print("Length of List : "+str(len(objList)))
       if first.TypeId == "App::Part" :
          print("Found App Part")
          name = first.Name
          # Also allow for App::Origin 
          print(objList[1].TypeId)
          if isinstance(objList[1].Proxy,GDMLcommon) : 
          #if isinstance(objList[1].Proxy,GDMLBox) or \
          #   isinstance(objList[1].Proxy,GDMLTube) :
             print("Adjust Setup")
             ET.SubElement(setup,'world', {'ref':name})
             return(structure)

    # drop through if not handled
    print("Need to create World Volume")
    bbox = FreeCAD.BoundBox()
    name = defineWorldBox(bbox)
    ET.SubElement(setup,'world', {'ref':name})
    worldVol = ET.SubElement(structure,'volume',{'name': name}) 
    ET.SubElement(worldVol, 'solidref',{'ref': name})
    print("Need to FIX !!!! To use defined gas")
    ET.SubElement('worldVOL', 'materialref',{'ref': 'G4_Galactic'})

def export(exportList,filename) :
    "called when FreeCAD exports a file"
    
    first = exportList[0]
    if first.TypeId == "App::Part" :
       # GDML Export
       print("\nStart GDML Export 0.1")

       GDMLstructure()
       zOrder = 1
       processMaterials()

       vol = processWorldVol(exportList[0])
       for obj in exportList :
           #reportObject(obj)
           processObject(obj, vol, None, None, False)

       # format & write GDML file 
       indent(gdml)
       print("Write to GDML file")
       #ET.ElementTree(gdml).write(filename, 'utf-8', True)
       ET.ElementTree(gdml).write(filename)
       print("GDML file written")
    
    else :
       print("Need to select World Part") 
