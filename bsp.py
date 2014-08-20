__all__ = ['unpack_bsp']

indent = 0

def unpack_bsp(r, tree_type):
    global indent
    indent += 1
    bsp_type = r.readint()
    #print(' ' * indent + '{:08x}'.format(bsp_type))
    if bsp_type == 0x4c454146: # LEAF
        #print(' ' * indent + "LEAF ENTER")
        unpack_bsp_leaf(r, tree_type)
        #print(' ' * indent + "LEAF LEAVE")
    elif bsp_type == 0x504f5254: # PORT
        #print(' ' * indent + "PORT ENTER")
        unpack_bsp_portal(r, tree_type)
        #print(' ' * indent + "PORT LEAVE")
    else:
        #print(' ' * indent + "NODE ENTER")
        unpack_bsp_node(r, tree_type, bsp_type)
        #print(' ' * indent + "NODE LEAVE")
    indent -= 1

def unpack_bsp_leaf(r, tree_type):
    r.readint()

    if tree_type != 1:
        return

    notempty = r.readint()

    x, y, z, radius = r.readformat('4I')

    index_count = r.readint()
    for i in range(index_count):
        r.readshort()

    if notempty:
        assert x != 0xcdcdcdcd
        assert y != 0xcdcdcdcd
        assert z != 0xcdcdcdcd
        assert radius != 0xcdcdcdcd
        assert index_count != 0
    else:
        pass
        #assert x == 0xcdcdcdcd
        #assert y == 0xcdcdcdcd
        #assert z == 0xcdcdcdcd
        #assert radius == 0xcdcdcdcd
        #assert index_count == 0

def unpack_bsp_portal(r, tree_type):
    x, y, z, d = r.readformat('4f')

    unpack_bsp(r, tree_type)
    unpack_bsp(r, tree_type)

    if tree_type != 0:
        return

    x, y, z, radius = r.readformat('4f')

    tricount = r.readint()
    polycount = r.readint()

    for i in range(tricount):
        r.readshort()

    for i in range(polycount):
        r.readshort()
        r.readshort()

def unpack_bsp_node(r, tree_type, node_type):
    x, y, z, dist = r.readformat('4f')
    #print(' ' * indent + "plane: {}, {}, {}, {}".format(x, y, z, dist))

    if node_type == 0x42506e6e or node_type == 0x4250496e: # BPnn, BPIn
        #print(' ' * indent + "(BPnn, BPIn)")
        unpack_bsp(r, tree_type)
    elif node_type == 0x4270494e or node_type == 0x42706e4e: # BpIN, BpnN
        #print(' ' * indent * "(BpIN, BpnN)")
        unpack_bsp(r, tree_type)
    elif node_type == 0x4250494e or node_type == 0x42506e4e: # BPIN, BPnN
        #print(' ' * indent + "(BPIN, BPnN)")
        unpack_bsp(r, tree_type)
        unpack_bsp(r, tree_type)
    else:
        #print("node_type = {:08x}".format(node_type))
        pass

    if tree_type == 0 or tree_type == 1:
        x, y, z, radius = r.readformat('4f')
        #print(' ' * indent + "bounds: {}, {}, {}, {}".format(x, y, z, radius))

    if tree_type != 0:
        return

    index_count = r.readint()
    for i in range(index_count):
        r.readshort()
