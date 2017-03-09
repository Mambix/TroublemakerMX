import trimesh
import numpy as np
import copy
import math
import threading
import os.path

def dxfElements(dxfFile, extrude=None):
    dxf = trimesh.load(dxfFile)
    layers = np.unique(dxf.metadata['layers'])

    elements = {}

    for layer in layers:
        E = copy.deepcopy(dxf.entities[dxf.metadata['layers'] == layer])
        path = trimesh.path.Path2D(entities=E, vertices=dxf.vertices.copy())
        if extrude is None:
            elements[layer] = path
        else:
            elements[layer] = path.extrude(extrude)

    return elements

class stlUnion(threading.Thread):
    def __init__(self, e1, e2):
        threading.Thread.__init__(self)
        self.E1 = e1
        self.E2 = e2
        self.result = None
    def run(self):
        self.result = self.E1.union(self.E2)

def dxf2stl(dxf, extrude):
    THREADS = 6
    E = dxfElements(dxf, extrude=extrude)
    print E.keys()
    stl = E['IZREZ']
    if 'IZREZ_PLEXI' in E:
        if E['IZREZ_PLEXI'] != []:
            stl = stl.difference(E['IZREZ_PLEXI'], engine='blender')
    H = E['HOLES']
    if not isinstance(H, list):
        H = [H]
    while len(H)>1:
        H1 = H[0::2]
        H2 = H[1::2]
        H = []

        if len(H1)>len(H2):
            H.append(H1[0])
            del H1[0]

        # threadLock = threading.Lock()
        while len(H2)>0:
            threads = []
            for i in range(len(H2)):
                T = stlUnion(H1[-1], H2[-1])
                del H1[-1]
                del H2[-1]
                T.start()
                threads.append(T)
                if len(threads) == THREADS:
                    break

            for t in threads:
                t.join()
                H.append(t.result)

    # stl.show()
    return stl.difference(H[0], engine='blender')

def setColor(stl, color):
    facets = stl.facets()
    for facet in facets:
        stl.visual.face_colors[facet] = color

def transform(name, save, extrude, transformations=None, full=True):
    if full:
        file = '../dxf/blocks/{}.dxf'.format(name)
        if not os.path.isfile(file):
            print('Error: {}'.format(file))
            return
        stl = dxf2stl(file, extrude)
        stl.export('../stl/{}.stl'.format(save))
    else:
        file = '../stl/{}.stl'.format(save)
        if not os.path.isfile(file):
            print('Error: {}'.format(file))
            return
        stl = trimesh.load(file)
    for trans in transformations:
        stl.apply_transform(trans)
    # setColor(stl, [34, 59, 205, 255])
    stl.export('../stl/moved{}.stl'.format(save))

full = False
transform('6mm_les_izrez_gor - LM8UU', 'GOR', 6.0, [
    trimesh.transformations.translation_matrix( (.0, .0, 478.0) )
], full)

transform('6mm_les_izrez_dol - LM8UU', 'DOL', 6.0, [
    trimesh.transformations.rotation_matrix(math.pi, (.0, 1.0, .0), (.0, .0, .0) ),
    trimesh.transformations.translation_matrix( (.0, .0, 80.0) )
], full)

transform('6mm_les_izrez_levo - LM8UU', 'LEVO', 6.0, [
    trimesh.transformations.rotation_matrix(math.pi/2, (.0, .0, 1.0), (.0, .0, .0) ),
    trimesh.transformations.rotation_matrix(math.pi/2, (.0, 1.0, .0), (.0, .0, .0) ),
    trimesh.transformations.translation_matrix( (-205.0, 211.0, .0) )
], full)

transform('6mm_les_izrez_desno - LM8UU', 'DESNO', 6.0, [
    trimesh.transformations.rotation_matrix(-math.pi/2, (.0, .0, 1.0), (.0, .0, .0) ),
    trimesh.transformations.rotation_matrix(-math.pi/2, (.0, 1.0, .0), (.0, .0, .0) ),
    trimesh.transformations.translation_matrix( (205.0, 211.0, .0) )
], full)

transform('6mm_les_izrez_spredaj - LM8UU', 'SPREDAJ', 6.0, [
    trimesh.transformations.rotation_matrix(math.pi / 2, (1.0, .0, .0), (.0, .0, .0)),
    trimesh.transformations.translation_matrix((209.0, -198.0, .0))
], full)

transform('6mm_les_izrez_zadaj - LM8UU', 'ZADAJ', 6.0, [
    trimesh.transformations.rotation_matrix(math.pi / 2, (1.0, .0, .0), (.0, .0, .0)),
    trimesh.transformations.translation_matrix((-209.0, 205.0, .0))
], full)


transform('6mm_les_izrez_hotend_top', 'HE_TOP', 6.0, [
    trimesh.transformations.translation_matrix((0.0, 0.0, 16.0))
], full)

transform('6mm_les_izrez_hotend_bottom', 'HE_BOTTOM', 6.0, [
    trimesh.transformations.translation_matrix((0.0, 0.0, -22.0))
], full)

transform('6mm_les_izrez_hotend_side_7', 'HE_FRONT', 6.0, [
    trimesh.transformations.rotation_matrix(math.pi / 2, (1.0, .0, .0), (.0, .0, .0)),
    trimesh.transformations.translation_matrix((0.0, -7.0, 0.0))
], full)

transform('6mm_les_izrez_hotend_side_7', 'HE_BACK', 6.0, [
    trimesh.transformations.rotation_matrix(math.pi / 2, (1.0, .0, .0), (.0, .0, .0)),
    trimesh.transformations.translation_matrix((0.0, 13.0, 0.0))
], full)

transform('6mm_les_izrez_hotend_side_7', 'HE_LEFT', 6.0, [
    trimesh.transformations.rotation_matrix(-math.pi / 2, (.0, .0, 1.0), (.0, .0, .0)),
    trimesh.transformations.rotation_matrix(math.pi / 2, (.0, 1.0, .0), (.0, .0, .0)),
    trimesh.transformations.translation_matrix((-13.0, 0.0, 0.0))
], full)

transform('6mm_les_izrez_hotend_side_7', 'HE_RIGHT', 6.0, [
    trimesh.transformations.rotation_matrix(-math.pi / 2, (.0, .0, 1.0), (.0, .0, .0)),
    trimesh.transformations.rotation_matrix(math.pi / 2, (.0, 1.0, .0), (.0, .0, .0)),
    trimesh.transformations.translation_matrix((7.0, 0.0, 0.0))
], full)

# stl = dxf2stl('../dxf/blocks/.dxf', 6.0)
# stl.export('../stl/GOR.stl')
# stl = trimesh.load('../stl/GOR.stl')
# stl.apply_transform()
# setColor(stl, [34, 59, 205, 255])
# stl.export('../stl/movedGOR.stl')

# stl = dxf2stl('../dxf/blocks/6mm_les_izrez_dol - LM8UU.dxf', 6.0)
# stl.export('../stl/DOL.stl')
# stl = trimesh.load('../stl/DOL.stl')
# stl.apply_transform(trimesh.transformations.rotation_matrix(math.pi, (.0, 1.0, .0), (.0, .0, .0) ))
# stl.apply_transform(trimesh.transformations.translation_matrix( (.0, .0, 80.0) ))
# setColor(stl, [34, 59, 205, 255])
# stl.export('../stl/movedDOL.stl')

# stl = dxf2stl('../dxf/blocks/6mm_les_izrez_levo - LM8UU.dxf', 6.0)
# stl.export('../stl/LEVO.stl')
# stl = trimesh.load('../stl/LEVO.stl')
# stl.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2, (.0, .0, 1.0), (.0, .0, .0) ))
# stl.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2, (.0, 1.0, .0), (.0, .0, .0) ))
# stl.apply_transform(trimesh.transformations.translation_matrix( (-205.0, 211.0, .0) ))
# setColor(stl, [34, 205, 59, 255])
# stl.export('../stl/movedLEVO.stl')

# stl = dxf2stl('../dxf/blocks/6mm_les_izrez_desno - LM8UU.dxf', 6.0)
# stl.export('../stl/DESNO.stl')
# stl = trimesh.load('../stl/DESNO.stl')
# stl.apply_transform(trimesh.transformations.rotation_matrix(-math.pi/2, (.0, .0, 1.0), (.0, .0, .0) ))
# stl.apply_transform(trimesh.transformations.rotation_matrix(-math.pi/2, (.0, 1.0, .0), (.0, .0, .0) ))
# stl.apply_transform(trimesh.transformations.translation_matrix( (205.0, 211.0, .0) ))
# setColor(stl, [34, 205, 59, 255])
# stl.export('../stl/movedDESNO.stl')

# stl = dxf2stl('../dxf/blocks/6mm_les_izrez_spredaj - LM8UU.dxf', 6.0)
# stl.export('../stl/SPREDAJ.stl')
# stl = trimesh.load('../stl/SPREDAJ.stl')
# stl.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2, (1.0, .0, .0), (.0, .0, .0) ))
# stl.apply_transform(trimesh.transformations.translation_matrix( (209.0, -198.0, .0) ))
# setColor(stl, [205, 59, 34, 255])
# stl.export('../stl/movedSPREDAJ.stl')

# stl = dxf2stl('../dxf/blocks/6mm_les_izrez_zadaj - LM8UU.dxf', 6.0)
# stl.export('../stl/ZADAJ.stl')
# stl = trimesh.load('../stl/ZADAJ.stl')
# stl.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2, (1.0, .0, .0), (.0, .0, .0) ))
# stl.apply_transform(trimesh.transformations.translation_matrix( (-209.0, 205.0, .0) ))
# setColor(stl, [205, 59, 34, 255])
# stl.export('../stl/movedZADAJ.stl')
