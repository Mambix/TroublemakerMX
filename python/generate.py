import ezdxf
import os
import operator


def addLayer(layerName, dxf, srcDxf):
    if layerName not in dxf.layers:
        lay = srcDxf.layers.get(layerName)
        dxf.layers.new(name=lay.dxf.name, dxfattribs={'linetype': lay.dxf.linetype, 'color': lay.dxf.color})

def mergeDXF(target, source, move = (0.0, 0.0), ignoreLayers = None, renameLayers = None):
    if not os.path.isfile(source):
        return False
    if not ezdxf.is_dxf_file(source):
        return False
    src = ezdxf.readfile(source)

    if ignoreLayers is None:
        ignoreLayers = []
    if renameLayers is None:
        renameLayers = {}

    print('Adding {}[{}] to {}'.format(source, src.dxfversion, target))
    dxf = ezdxf.new(src.dxfversion)
    lay = dxf.layers.get('0')
    lay.set_color(2)
    if os.path.isfile(target):
        if ezdxf.is_dxf_file(target):
            dxf = ezdxf.readfile(target)
    target_msp = dxf.modelspace()
    source_msp = src.modelspace()

    # for lay in src.layers:
    for e in source_msp:
        if e.dxf.layer in ignoreLayers:
            # Skip this entity
            continue
        t = '{}'.format(e.dxftype)
        e_lay = e.dxf.layer
        if e_lay in renameLayers:
            e_lay = renameLayers[e_lay]
        if t[14:17] == 'Arc':
            addLayer(e_lay, dxf, src)
            c = tuple(map(operator.add, e.dxf.center, move))
            target_msp.add_arc(c, e.dxf.radius, e.dxf.start_angle, e.dxf.end_angle, dxfattribs={'layer': e_lay})
        elif t[14:20] == 'Circle':
            addLayer(e_lay, dxf, src)
            c = tuple(map(operator.add, e.dxf.center, move))
            target_msp.add_circle(c, e.dxf.radius, dxfattribs={'layer': e_lay})
        elif t[14:19] == 'Point':
            addLayer(e_lay, dxf, src)
            loc = tuple(map(operator.add, e.dxf.location, move))
            target_msp.add_point(loc, dxfattribs={'layer': e_lay})
        elif t[14:18] == 'Text':
            addLayer(e_lay, dxf, src)
            c = (e.dxf.insert[0]+move[0],e.dxf.insert[1]+move[1], e.dxf.insert[2])
            target_msp.add_text(e.dxf.text, dxfattribs={
                'insert': c,
                'height': e.dxf.height,
                'rotation': e.dxf.rotation,
                'style': e.dxf.style,
                'width': e.dxf.width,
                'halign': e.dxf.halign,
                'valign': e.dxf.valign,
                'layer': e_lay
            })
        elif t[14:19] == 'MText':
            # print('MTEXT: {}'.format(e.get_text()))
            addLayer(e_lay, dxf, src)
            c = (e.dxf.insert[0] + move[0], e.dxf.insert[1] + move[1], e.dxf.insert[2])
            target_msp.add_mtext(e.get_text(), dxfattribs={
                'insert': c,
                'char_height': e.dxf.char_height,
                'width': e.dxf.width,
                'attachment_point': e.dxf.attachment_point,
                'flow_direction': e.dxf.flow_direction,
                'style': e.dxf.style,
                'rotation': e.dxf.rotation,
                'line_spacing_style': e.dxf.line_spacing_style,
                'line_spacing_factor': e.dxf.line_spacing_factor,
                'layer': e_lay
            })
        elif t[14:18] == 'Line':
            addLayer(e_lay, dxf, src)
            start = tuple(map(operator.add, e.dxf.start, move))
            end = tuple(map(operator.add, e.dxf.end, move))
            target_msp.add_line(start, end, dxfattribs={'layer': e_lay})
        # elif t[14:22] == 'Polyline':
        #     addLayer(e_lay, dxf, src)
        #     points = e.points()
        #     newPoints = []
        #     for p in points:
        #         newPoints.append((p[0] + move[0], p[1] + move[1]))
        #     poly = target_msp.add_polyline(newPoints, dxfattribs={
        #         'layer': e_lay,
        #         'flags': e.dxf.flags
        #     })
        #     poly.closed = e.closed
        elif t[14:20] == 'LWPoly':
            addLayer(e_lay, dxf, src)
            points = e.get_points()
            newPoints = []
            for p in points:
                newPoints.append( (p[0] + move[0], p[1] + move[1], p[2], p[3], p[4]) )
            poly = target_msp.add_lwpolyline(newPoints, dxfattribs={
                'layer': e_lay,
                'flags': e.dxf.flags
            })
            poly.closed = e.closed
        elif t[14:20] == 'Spline':
            addLayer(e_lay, dxf, src)
            points = e.get_fit_points()
            newPoints = []
            for p in points:
                newPoints.append( (p[0] + move[0], p[1] + move[1], p[2]) )
            spline = target_msp.add_spline(newPoints, dxfattribs={
                'layer': e_lay,
                'flags': e.dxf.flags
            })

            points = e.get_control_points()
            newPoints = []
            for p in points:
                newPoints.append( (p[0] + move[0], p[1] + move[1], p[2]) )
            spline.set_control_points(newPoints)

            spline.set_knot_values(e.get_knot_values())
            spline.set_weights(e.get_weights())

            spline.closed = e.closed
        elif t[14:20] == 'Modern':
            # addLayer(e.dxf.layer, dxf, src)
            # target_msp.add_entity(e)
            ignore = 1
        else:
            print t[14:]
            print e_lay
            # target_msp.add_entity(e)
        # source_msp.unlink_entity(e)
        # target_msp.add_entity(e)

    dxf.saveas(target)
    return True

def mergeFiles(target, sources):
    if os.path.isfile(target):
        os.remove(target)
    for source, dic in sources.iteritems():
        if isinstance(dic, dict):
            move = (0.0, 0.0)
            ignoreLayers = None
            renameLayers = None
            if 'move' in dic:
                move = dic['move']
            if 'ignoreLayers' in dic:
                ignoreLayers = dic['ignoreLayers']
            if 'renameLayers' in dic:
                renameLayers = dic['renameLayers']
            mergeDXF(target, source, move=move, ignoreLayers=ignoreLayers, renameLayers=renameLayers)
        elif isinstance(dic, tuple):
            mergeDXF(target, source, dic)
        else:
            print('Instruction error!!!')

if __name__ == "__main__":
    mergeFiles('../dxf/6mm_plywood_cut_left_right.dxf', {
        '../dxf/blocks/6mm_les_izrez_levo - LM8UU.dxf': {'move': (0.0, 0.0), 'ignoreLayers': ['HOLES_PLEXI'], 'renameLayers': {'IZREZ_PLEXI': 'IZREZ'}},
        '../dxf/blocks/6mm_les_izrez_desno - LM8UU.dxf': {'move': (0.0, 0.0), 'ignoreLayers': ['HOLES_PLEXI'], 'renameLayers': {'IZREZ_PLEXI': 'IZREZ'}}
    })

    mergeFiles('../dxf/6mm_plywood_cut_front_back.dxf', {
        '../dxf/blocks/6mm_les_izrez_spredaj - LM8UU.dxf': {'move': (0.0, 0.0), 'ignoreLayers': ['HOLES_PLEXI'], 'renameLayers': {'IZREZ_PLEXI': 'IZREZ'}},
        '../dxf/blocks/6mm_les_izrez_zadaj - LM8UU.dxf': (0.0, 0.0)
    })

    mergeFiles('../dxf/6mm_plywood_cut_top_bottom.dxf', {
        '../dxf/blocks/6mm_les_izrez_gor - LM8UU.dxf': {'move': (-206.0, 205.0), 'ignoreLayers': ['HOLES_PLEXI'], 'renameLayers': {'IZREZ_PLEXI': 'IZREZ'}},
        '../dxf/blocks/6mm_les_izrez_dol - LM8UU.dxf': (206.0, 205.0)
    })

    mergeFiles('../dxf/6mm_plexi_cut_windows.dxf', {
        '../dxf/blocks/6mm_les_izrez_gor - LM8UU.dxf': {'move': (0.0, 0.0), 'ignoreLayers': ['HOLES', 'IZREZ'], 'renameLayers': {'IZREZ_PLEXI': 'IZREZ', 'HOLES_PLEXI': 'HOLES'}}
    })
