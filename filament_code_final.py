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

#User inputs
diam = float(getInput('Enter filament diameter: ')) 
poreSize = float(getInput('Enter pore size: ')) 
filNum = int(getInput('Enter filament number per layer: ')) 
scaffoldHeight = (int(getInput('Enter scaffold height: ')))

#Material inputs
yMod = float(getInput("Enter Young's modulus (Gpa): "))
pRatio = float(getInput("Enter Poisson's ratio: "))

#Geometry calculations based on user inputs
radius = (diam/2)
rP = diam + poreSize #diameter add poresize to ensure correct filament space
filLen = filNum*diam + (filNum-1)*poreSize #Calculates appropriate filament length

#Prints values to ABAQUS console to check they are correct
print filLen
print rP
print poreSize

#Percent overlap
offset = (diam*0.05)

#topDatumHeight = ((scaffoldHeight - 1)*diam) - ((scaffoldHeight - 1)*(offset))

#Extrude first filament
mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=10.0)
mdb.models['Model-1'].sketches['__profile__'].CircleByCenterPerimeter(center=(
    0.0, 0.0), point1=(0.0, radius))
mdb.models['Model-1'].Part(dimensionality=THREE_D, name='Part-1', type=
    DEFORMABLE_BODY)
mdb.models['Model-1'].parts['Part-1'].BaseSolidExtrude(depth=filLen, sketch=
    mdb.models['Model-1'].sketches['__profile__'])
del mdb.models['Model-1'].sketches['__profile__']

#Start Assembly
mdb.models['Model-1'].rootAssembly.DatumCsysByDefault(CARTESIAN)
mdb.models['Model-1'].rootAssembly.Instance(dependent=OFF, name='Part-1-1', 
    part=mdb.models['Model-1'].parts['Part-1'])
	
mdb.models['Model-1'].rootAssembly.LinearInstancePattern(direction1=(1.0, 0.0, 
    0.0), direction2=(0.0, 1.0, 0.0), instanceList=('Part-1-1', ), number1=1, 
    number2=2, spacing1=2.0, spacing2=(diam-offset))
	
mdb.models['Model-1'].rootAssembly.rotate(angle=90.0, axisDirection=(0.0, filLen, 
    0.0), axisPoint=(0.0, 0.0, 0.0), instanceList=('Part-1-1-lin-1-2', ))
	
mdb.models['Model-1'].rootAssembly.translate(instanceList=('Part-1-1-lin-1-2', 
    ), vector=(-radius, 0.0, 0.0))
	
mdb.models['Model-1'].rootAssembly.translate(instanceList=('Part-1-1-lin-1-2', 
    ), vector=(0.0, 0.0, radius))
	
#First linear pattern
mdb.models['Model-1'].rootAssembly.LinearInstancePattern(direction1=(1.0, 0.0, 
    0.0), direction2=(0.0, 1.0, 0.0), instanceList=('Part-1-1', ), number1=filNum, 
    number2=1, spacing1=rP, spacing2=2.0)
	
#Second linear pattern
mdb.models['Model-1'].rootAssembly.LinearInstancePattern(direction1=(1.0, 0.0, 
    0.0), direction2=(0.0, 0.0, 1.0), instanceList=('Part-1-1-lin-1-2', ), 
    number1=1, number2=filNum, spacing1=2.0, spacing2=rP)
	
#Upward linear pattern
mdb.models['Model-1'].rootAssembly.LinearInstancePattern(direction1=(1.0, 0.0, 
    0.0), direction2=(0.0, 1.0, 0.0), instanceList=(mdb.models['Model-1'].rootAssembly.instances.keys())
	, number1=1, number2=scaffoldHeight, spacing1=22.0, spacing2=
    (diam*2) -(offset*2))
	
#Merge process
a = mdb.models['Model-1'].rootAssembly
LatticePartInstList = a.instances.keys()

a.InstanceFromBooleanMerge(domain=GEOMETRY, 
    instances=([a.instances[LatticePartInstList[i]] for i in range(len(LatticePartInstList))])
    , name='SCAFFOLD', originalInstances=DELETE)
	
del mdb.models['Model-1'].parts['Part-1']

mdb.models['Model-1'].rootAssembly.makeIndependent(instances=(
    mdb.models['Model-1'].rootAssembly.instances['SCAFFOLD-1'], ))

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
