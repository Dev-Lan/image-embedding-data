import os
# os.environ['PYOPENGL_PLATFORM'] = 'egl'

import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.tri as mtri
import trimesh
import pyrender
from PIL import Image
from numpy.linalg import inv


from os import linesep

inFolder = './in/'
outFolder = './out/'
csvFilename = 'exampleShapeParams.csv'

renderLarge = False
interactiveView = False

def main():

    subsetToTest = open(inFolder + csvFilename)
    rows = subsetToTest.readlines()
    headerStrings = [val.rstrip() for val in rows[0].split(',')]
    m_i = headerStrings.index('m')
    n1_i = headerStrings.index('n1')
    n2_i = headerStrings.index('n2')
    n3_i = headerStrings.index('n3')
    a_i = headerStrings.index('a')
    b_i = headerStrings.index('b')
    if 'imageKey' in headerStrings:
        img_i = headerStrings.index('imageKey')
    else:
        img_i = -1

    # set up static things
    goldMaterial = pyrender.MetallicRoughnessMaterial(baseColorFactor=[ 1.0, 0.766, 0.336, 1.0 ], roughnessFactor=.25, metallicFactor=1, emissiveFactor=0)
    scene = pyrender.Scene()

    cameraObj = pyrender.PerspectiveCamera(yfov=np.pi / 3.0)

    # camera position
    camPos = np.array([4, -4, 2.5])
    origin = np.array([0,0,0])
    upVec = np.array([0,0,1])
    camera_pose, leftVec = lookat(camPos, origin, upVec)
    camera_pose = np.array(inv(camera_pose))
    scene.add(cameraObj, pose=camera_pose)

    # lighting
    scene.ambient_light = .01
    dirLightObj = pyrender.DirectionalLight(color=[1,1,1], intensity=1000)
    coneLightObj = pyrender.SpotLight(color=[1,1,1], intensity=3000, innerConeAngle=(np.pi/8.0), outerConeAngle=(np.pi / 2.0))

    spotlightPositions = [[-.1, -.1, 10], np.array([0, 0, 50]) - 8*leftVec]
    headlampOffset = 20.0
    spotlightPositions.append(camPos + headlampOffset * leftVec + 1.5 * upVec)
    spotlightPositions.append(camPos - headlampOffset * leftVec + 1.2 * upVec)

    for lightPos in spotlightPositions:
        matrix, leftVec = lookat(lightPos, origin, upVec)
        lightPose = np.array(inv(matrix))
        scene.add(dirLightObj, pose=lightPose)

    # for implicit resolution
    unitCubeSize = 3
    nGridPointsPerDimension = 200


    if renderLarge:
        bigImgW,bigImgH = 960, 720
        smallImgSize = 320
    else:
        bigImgW,bigImgH = 96, 72
        smallImgSize = 32

    totalImgW, totalImgH = bigImgW, bigImgH + smallImgSize
    r = pyrender.OffscreenRenderer(bigImgW, bigImgH)

    smallSize = (smallImgSize, smallImgSize)
    sliceImg = Image.new('RGB', smallSize)

    # render all the particles
    for rowIndex in range(1, len(rows)):
        print('shape %i / %i' % (rowIndex + 1, len(rows)), end='\r')
        row = rows[rowIndex]
        row = row.split(',')
        m = float(row[m_i])
        n1 = float(row[n1_i])
        n2 = float(row[n2_i])
        n3 = float(row[n3_i])
        a = float(row[a_i])
        b = float(row[b_i])

        X, Y, Z, triIndices = superformula3D(m, n1, n2, n3, a, b, 50000)
        verts = np.column_stack((X,Y,Z))

        shapeMesh = trimesh.Trimesh(vertices=verts, faces=triIndices)


        if img_i >= 0:
            filename = row[img_i]
        else:
            filename = str(rowIndex - 1)
            while len(filename) < len(str(len(rows))):
                filename = '0' + filename
            filename = filename + '.png'

        mesh = pyrender.Mesh.from_trimesh(shapeMesh, material=goldMaterial)

        meshNode = scene.add(mesh)

        if interactiveView:
            pyrender.Viewer(scene, use_raymond_lighting=True)
        

        pilImg = Image.new('RGB',(totalImgW, totalImgH))
        
        color, depth = r.render(scene)

        scene.remove_node(meshNode)

        color = [(pixel[0], pixel[1], pixel[2]) for pixel in color.reshape(-1, 3)]
        pilImg.putdata(color)
        # scene.clear()

        # add slices:
        grid = supershape3dImplicit(unitCubeSize, smallImgSize, a, b, m, n1, n2, n3)
        # binaryGrid = np.where(grid >=0, 1, 0)
        minVal = np.min(grid)
        maxVal = np.max(grid)
        midIndex = math.floor(smallImgSize / 2.0)

        for index, view in enumerate([grid[:,:,midIndex], grid[:,midIndex,:].T, grid[midIndex,:,:].T]):
            flatData = [getColor(x, minVal, maxVal) for x in view.flatten()]
            sliceImg.putdata(flatData)
            topLeft = (index * smallImgSize, bigImgH)
            pilImg.paste(sliceImg, topLeft)

        pilImg.save(outFolder + filename)
        

    return


def superformula3D(m, n1, n2, n3, a, b, numPoints):
    numPointsRoot = round(math.sqrt(numPoints))

    theta = np.linspace(-math.pi, math.pi, endpoint=True, num=numPointsRoot)
    phi = np.linspace(-math.pi / 2.0, math.pi/2.0, endpoint=True, num=numPointsRoot)
    
    theta, phi = np.meshgrid(theta, phi)
    theta, phi = theta.flatten(), phi.flatten()

    r1 = superformula2D(m, n1, n2, n3, a, b, theta)
    r2 = superformula2D(m, n1, n2, n3, a, b, phi)

    x = r1 * r2 * np.cos(theta) * np.cos(phi)
    y = r1 * r2 * np.sin(theta) * np.cos(phi)
    z = r2 * np.sin(phi)

    tri = mtri.Triangulation(theta, phi)
    return x, y, z, tri.triangles

def supershape3dImplicit(unitCubeSize, nGridPointsPerDimension, a, b, m, n1, n2, n3):
    x = np.linspace(-unitCubeSize, unitCubeSize, nGridPointsPerDimension)
    y = np.linspace(-unitCubeSize, unitCubeSize, nGridPointsPerDimension)
    z = np.linspace(-unitCubeSize, unitCubeSize, nGridPointsPerDimension)
    [x,y,z] = np.meshgrid(x,y,z)
    theta = np.arctan2(y, x)
    r_theta = superformula2D(m, n1, n2, n3, a, b, theta)
    theta2 = np.arctan(y/x)


    phi1 = np.arctan(z * r_theta * np.sin(theta)/ y)
    phi2 = np.arctan(z * r_theta * np.cos(theta)/ x)
    # plotHeatmap(phi2[:,:,0])
    # print(abs(abs(phi1) - abs(phi2)).max())
    # phi = (phi1 + phi2) / 2.0
    r_phi = superformula2D(m, n1, n2, n3, a, b, phi2)

    fullGrid = 1 - ( x**2 + y**2 + (r_theta**2) * (z**2) ) / ( (r_theta**2) * (r_phi**2) )
    return fullGrid

def superformula2D(m, n1, n2, n3, a, b, theta):
    r = abs((1 / a) * np.cos(m * theta / 4.0))**n2  +  abs((1 / b) * np.sin(m * theta / 4.0))**n3
    return r**(-1 / n3)

def getColor(val, minVal, maxVal):
    if val == 0:
        return (255, 255, 255)
    if val > 0:
        # return (int(255 * val / float(maxVal)), 0, 0)
        return (255, 0, 0)

    return (0, 0, int(255 * val / float(minVal)))


def plotHeatmap(grid):
    fig, ax = plt.subplots()
    im = ax.imshow(grid, 'hot')
    fig.tight_layout()
    plt.show()
    plt.clf()
    return



# from (with slight modification) https://community.khronos.org/t/view-and-perspective-matrices/74154
# lookat
# translate
# magnitude
# normalize
def lookat(eye, target, up):
    eye = np.array(eye)
    target = np.array(target)
    up = np.array(up)
    lookVec = eye[:3] - target[:3]
    lookVec = normalize(lookVec)
    U = normalize(up[:3])
    leftVec = np.cross(U, lookVec)
    upVec = np.cross(lookVec, leftVec)
    M = np.matrix(np.identity(4))
    M[:3,:3] = np.vstack([leftVec,upVec,lookVec])
    T = translate(-eye)
    return M * T, leftVec

def translate(xyz):
    x, y, z = xyz
    return np.matrix([[1,0,0,x],
                      [0,1,0,y],
                      [0,0,1,z],
                      [0,0,0,1]])

def magnitude(v):
    return math.sqrt(np.sum(v ** 2))

def normalize(v):
    m = magnitude(v)
    if m == 0:
        return v
    return v / m

if __name__ == '__main__':
    main()