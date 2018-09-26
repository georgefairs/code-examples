from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from optimization import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *
from abaqus import getInput
from abaqus import getInputs

#User inputs
u = float(getInput('Enter pore size: ')) #pore size, micrometers?
H = int(getInput('Enter scaffold height: '))
W = int(getInput('Enter scaffold width: '))
D = int(getInput('Enter scaffold depth: '))

#Material inputs
yMod = float(getInput("Enter Young's modulus (Gpa): "))
pRatio = float(getInput("Enter Poisson's ratio: "))

#Base Geometry
z = 1
print z
desiredPorosity = (3*u**2)*z - 2*(u**3)
print "Pore volume: ", desiredPorosity

x1 = -z*0.5 #half length of square's side (must be negative)
x2 = -x1
y1 = -x1
y2 = -y1
print x1, y1, x2, y2
print "Depth: ", z
volume = z**3
print "Total volume: ", volume

px1 = (x1 + (z*0.5) - (u*0.5))
py1 = (y1 - (z*0.5) + (u*0.5))
px2 = -px1
py2 = -py1

print px1, px2, py1, py2

poreVolume = u**3 + (6*u**2)*((z-u)/2)
print "Pore Volume: ", poreVolume

radius = ((desiredPorosity*(z)**2)/(3*pi))**0.5

#SKETCH BASIC GEOMETRY
mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=200.0)
mdb.models['Model-1'].sketches['__profile__'].rectangle(point1=(x1, y1), 
    point2=(x2, y2))

myPart = mdb.models['Model-1'].Part(dimensionality=THREE_D, name='UnitCell', type=DEFORMABLE_BODY)	
myPart.BaseSolidExtrude(depth=z, sketch=mdb.models['Model-1'].sketches['__profile__'])


#EXTRUSION CODE SQUARE (put in comments to change to other shape)
#Front face
mdb.models['Model-1'].ConstrainedSketch(gridSpacing=2.59, name='__profile__', 
    sheetSize=103.92, transform=
    mdb.models['Model-1'].parts['UnitCell'].MakeSketchTransform(
    sketchPlane=mdb.models['Model-1'].parts['UnitCell'].faces[4], 
    sketchPlaneSide=SIDE1, 
    sketchUpEdge=mdb.models['Model-1'].parts['UnitCell'].edges[0], 
    sketchOrientation=RIGHT, origin=(0.0, 0.0, z)))
mdb.models['Model-1'].parts['UnitCell'].projectReferencesOntoSketch(filter=
    COPLANAR_EDGES, sketch=mdb.models['Model-1'].sketches['__profile__'])
mdb.models['Model-1'].sketches['__profile__'].rectangle(point1=(px1, py1), 
    point2=(px2, py2))
mdb.models['Model-1'].parts['UnitCell'].CutExtrude(flipExtrudeDirection=OFF, 
    sketch=mdb.models['Model-1'].sketches['__profile__'], sketchOrientation=
    RIGHT, sketchPlane=mdb.models['Model-1'].parts['UnitCell'].faces[4], 
    sketchPlaneSide=SIDE1, sketchUpEdge=
    mdb.models['Model-1'].parts['UnitCell'].edges[0])
del mdb.models['Model-1'].sketches['__profile__']

#Top face
mdb.models['Model-1'].ConstrainedSketch(gridSpacing=2.59, name='__profile__', 
    sheetSize=103.92, transform=
    mdb.models['Model-1'].parts['UnitCell'].MakeSketchTransform(
    sketchPlane=mdb.models['Model-1'].parts['UnitCell'].faces[7], 
    sketchPlaneSide=SIDE1, 
    sketchUpEdge=mdb.models['Model-1'].parts['UnitCell'].edges[15], 
    sketchOrientation=RIGHT, origin=(0.0, y1, y1)))
mdb.models['Model-1'].parts['UnitCell'].projectReferencesOntoSketch(filter=
    COPLANAR_EDGES, sketch=mdb.models['Model-1'].sketches['__profile__'])
mdb.models['Model-1'].sketches['__profile__'].rectangle(point1=(px1, py1), 
    point2=(px2, py2))
mdb.models['Model-1'].parts['UnitCell'].CutExtrude(flipExtrudeDirection=OFF, 
    sketch=mdb.models['Model-1'].sketches['__profile__'], sketchOrientation=
    RIGHT, sketchPlane=mdb.models['Model-1'].parts['UnitCell'].faces[7], 
    sketchPlaneSide=SIDE1, sketchUpEdge=
    mdb.models['Model-1'].parts['UnitCell'].edges[15])
del mdb.models['Model-1'].sketches['__profile__']

#Right face
mdb.models['Model-1'].ConstrainedSketch(gridSpacing=2.59, name='__profile__', 
    sheetSize=103.92, transform=
    mdb.models['Model-1'].parts['UnitCell'].MakeSketchTransform(
    sketchPlane=mdb.models['Model-1'].parts['UnitCell'].faces[10], 
    sketchPlaneSide=SIDE1, 
    sketchUpEdge=mdb.models['Model-1'].parts['UnitCell'].edges[38], 
    sketchOrientation=RIGHT, origin=(x1, 0.0, y1)))
mdb.models['Model-1'].parts['UnitCell'].projectReferencesOntoSketch(filter=
    COPLANAR_EDGES, sketch=mdb.models['Model-1'].sketches['__profile__'])
mdb.models['Model-1'].sketches['__profile__'].rectangle(point1=(px1, py1), 
    point2=(px2, py2))
mdb.models['Model-1'].parts['UnitCell'].CutExtrude(flipExtrudeDirection=OFF, 
    sketch=mdb.models['Model-1'].sketches['__profile__'], sketchOrientation=
    RIGHT, sketchPlane=mdb.models['Model-1'].parts['UnitCell'].faces[10], 
    sketchPlaneSide=SIDE1, sketchUpEdge=
    mdb.models['Model-1'].parts['UnitCell'].edges[38])
	
del mdb.models['Model-1'].sketches['__profile__']

#Apply material properties
mdb.models['Model-1'].Material(name='Material-1')
mdb.models['Model-1'].materials['Material-1'].Elastic(table=((yMod, pRatio), ))
mdb.models['Model-1'].HomogeneousSolidSection(material='Material-1', name=
    'Section-1', thickness=None)
mdb.models['Model-1'].parts['SCAFFOLD'].Set(cells=
    mdb.models['Model-1'].parts['SCAFFOLD'].cells, name='Set-1')
mdb.models['Model-1'].parts['SCAFFOLD'].SectionAssignment(offset=0.0, 
    offsetField='', offsetType=MIDDLE_SURFACE, region=
    mdb.models['Model-1'].parts['SCAFFOLD'].sets['Set-1'], sectionName=
    'Section-1', thicknessAssignment=FROM_SECTION)

#ASSEMBLY
mdb.models['Model-1'].rootAssembly.DatumCsysByDefault(CARTESIAN)
mdb.models['Model-1'].rootAssembly.Instance(dependent=ON, name='UnitCell-1', 
    part=mdb.models['Model-1'].parts['UnitCell'])
	
mdb.models['Model-1'].rootAssembly.makeDependent(instances=(
    mdb.models['Model-1'].rootAssembly.instances['UnitCell-1'], ))

#SCAFFOLD GENERATION
mdb.models['Model-1'].rootAssembly.LinearInstancePattern(direction1=(1.0, 0.0, 
    0.0), direction2=(0.0, 1.0, 0.0), instanceList=(mdb.models['Model-1'].rootAssembly.instances.keys()), number1=W, 
    number2=H, spacing1=1.0, spacing2=1.0)
	
mdb.models['Model-1'].rootAssembly.LinearInstancePattern(direction1=(1.0, 0.0, 
    0.0), direction2=(0.0, 0.0, 1.0), instanceList=(mdb.models['Model-1'].rootAssembly.instances.keys()), number1=1, 
    number2=D, spacing1=1.0, spacing2=1.0)

#MERGE PROCESS
a = mdb.models['Model-1'].rootAssembly
LatticePartInstList = a.instances.keys()
	
#STEP INITILIZATION
mdb.models['Model-1'].StaticStep(name='MainStep', previous='Initial')
a.InstanceFromBooleanMerge(domain=GEOMETRY, 
    instances=([a.instances[LatticePartInstList[i]] for i in range(len(LatticePartInstList))]), name=
    'Part-1', originalInstances=DELETE)

#LOAD VIEWPORT 
myViewport = session.Viewport(name='Viewer',
    origin=(10, 10), width=150, height=100)
myViewport.setValues(displayedObject=myPart)
myViewport.partDisplay.setValues(renderStyle=SHADED)
