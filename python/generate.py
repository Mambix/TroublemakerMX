import ezdxf
import os

def addLayer(layerName, dxf, srcDxf):
    if layerName not in dxf.layers:
        lay = srcDxf.layers.get(layerName)
        dxf.layers.new(name=lay.dxf.name, dxfattribs={'linetype': lay.dxf.linetype, 'color': lay.dxf.color, 'line_weight': lay.dxf.line_weight})

def mergeDXF(target, source, move = None):
    if not os.path.isfile(source):
        return False
    if not ezdxf.is_dxf_file(source):
        return False
    src = ezdxf.readfile(source)
    dxf = ezdxf.new(src.dxfversion)
    if os.path.isfile(target):
        if ezdxf.is_dxf_file(target):
            dxf = ezdxf.readfile(target)
    target_msp = dxf.modelspace()
    source_msp = src.modelspace()

    # for lay in src.layers:
    for e in source_msp:
        t = '{}'.format(e.dxftype)
        if t[14:20] == 'Circle':
            addLayer(e.dxf.layer, dxf, src)
            target_msp.add_circle(e.dxf.center, e.dxf.radius, dxfattribs={'layer': e.dxf.layer})
        elif t[14:19] == 'Point':
            addLayer(e.dxf.layer, dxf, src)
            target_msp.add_point(e.dxf.location, dxfattribs={'layer': e.dxf.layer})
        elif t[14:18] == 'Text':
            addLayer(e.dxf.layer, dxf, src)
            target_msp.add_text(e.dxf.text, dxfattribs={
                'insert': e.dxf.insert,
                'height': e.dxf.height,
                'rotation': e.dxf.rotation,
                'style': e.dxf.style,
                'width': e.dxf.width,
                'halign': e.dxf.halign,
                'valign': e.dxf.valign,
                'layer': e.dxf.layer
            })
        elif t[14:19] == 'MText':
            addLayer(e.dxf.layer, dxf, src)
            target_msp.add_mtext(e.get_text(), dxfattribs={
                'insert': e.dxf.insert,
                'char_height': e.dxf.char_height,
                'width': e.dxf.width,
                'attachment_point': e.dxf.attachment_point,
                'flow_direction': e.dxf.flow_direction,
                'style': e.dxf.style,
                'rotation': e.dxf.rotation,
                'line_spacing_style': e.dxf.line_spacing_style,
                'line_spacing_factor': e.dxf.line_spacing_factor,
                'layer': e.dxf.layer
            })
        elif t[14:18] == 'Line':
            addLayer(e.dxf.layer, dxf, src)
            target_msp.add_line(e.dxf.start, e.dxf.end, dxfattribs={'layer': e.dxf.layer})
        elif t[14:20] == 'LWPoly':
            print e.dxf.flags
            addLayer(e.dxf.layer, dxf, src)
            target_msp.add_lwpolyline(e.get_points(), dxfattribs={
                'layer': e.dxf.layer,
                'flags': e.dxf.flags
            })
        # elif t[14:20] == 'Modern':
        #     addLayer(e.dxf.layer, dxf, src)
        #     target_msp.add_entity(e)
        else:
            print t[14:]
            print e.dxf.layer
        # source_msp.unlink_entity(e)
        # target_msp.add_entity(e)

    dxf.saveas(target)
    return True

if __name__ == "__main__":
    if os.path.isfile('../dxf/6mm_plywood_cut_left_right.dxf'):
        os.remove('../dxf/6mm_plywood_cut_left_right.dxf')
    mergeDXF('../dxf/6mm_plywood_cut_left_right.dxf', '../dxf/blocks/6mm_les_izrez_levo - LM8UU.dxf')
    mergeDXF('../dxf/6mm_plywood_cut_left_right.dxf', '../dxf/blocks/6mm_les_izrez_desno - LM8UU.dxf')

# dwg = '../dxf/blocks/6mm_les_izrez_dol - LM8UU.dxf'
# msp = dwg.modelspace()
#
# dxf_cuts = msp.query('*[layer=="IZREZ"]')
# dxf_holes = msp.query('*[layer=="HOLES"]')
