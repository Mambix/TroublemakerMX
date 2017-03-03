import trimesh
import numpy as np
import copy
import math
import threading

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
    THREADS = 8
    E = dxfElements(dxf, extrude=extrude)
    stl = E['IZREZ']
    H = E['HOLES']
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

# stl = dxf2stl('../dxf/blocks/6mm_les_izrez_gor - LM8UU.dxf', 6.0)
# stl.export('../stl/GOR.stl')
stl = trimesh.load('../stl/GOR.stl')
stl.apply_transform(trimesh.transformations.translation_matrix( (.0, .0, 478.0) ))
stl.export('../stl/movedGOR.stl')

# stl = dxf2stl('../dxf/blocks/6mm_les_izrez_dol - LM8UU.dxf', 6.0)
# stl.export('../stl/DOL.stl')
stl = trimesh.load('../stl/DOL.stl')
stl.apply_transform(trimesh.transformations.rotation_matrix(math.pi, (.0, 1.0, .0), (.0, .0, .0) ))
stl.apply_transform(trimesh.transformations.translation_matrix( (.0, .0, 74.0) ))
stl.export('../stl/movedDOL.stl')

# stl = dxf2stl('../dxf/blocks/6mm_les_izrez_levo - LM8UU.dxf', 6.0)
# stl.export('../stl/LEVO.stl')
stl = trimesh.load('../stl/LEVO.stl')
stl.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2, (.0, .0, 1.0), (.0, .0, .0) ))
stl.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2, (.0, 1.0, .0), (.0, .0, .0) ))
stl.apply_transform(trimesh.transformations.translation_matrix( (-205.0, 211.0, .0) ))
# stl.apply_transform(trimesh.transformations.translation_matrix( (.0, .0, 478.0) ))
stl.export('../stl/movedLEVO.stl')

# stl = dxf2stl('../dxf/blocks/6mm_les_izrez_desno - LM8UU.dxf', 6.0)
# stl.export('../stl/DESNO.stl')
stl = trimesh.load('../stl/DESNO.stl')
stl.apply_transform(trimesh.transformations.rotation_matrix(-math.pi/2, (.0, .0, 1.0), (.0, .0, .0) ))
# stl.apply_transform(trimesh.transformations.translation_matrix( (.0, .0, 478.0) ))
stl.export('../stl/movedDESNO.stl')
