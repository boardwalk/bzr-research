
class Plane(object):
    def __init__(self, x, y, z, d):
        self.x = x
        self.y = y
        self.z = z
        self.d = d

    def __str__(self):
        return 'Plane(x={:.2f} y={:.2f} z={:.2f} d={:.2f})'.format(self.x, self.y, self.z, self.d)

class Sphere(object):
    def __init__(self, x, y, z, r):
        self.x = x
        self.y = y
        self.z = z
        self.r = r

    def __str__(self):
        return 'Sphere(x={:.2f} y={:.2f} z={:.2f} r={:.2f})'.format(self.x, self.y, self.z, self.r)

class BSPNode(object):
    def __init__(self, r, tree_type):
        self.node_type = r.readformat('4s')[::-1]
        if self.node_type == b'LEAF':
            self.unpack_leaf(r, tree_type)
        elif self.node_type == b'PORT':
            self.unpack_portal(r, tree_type)
        else:
            self.unpack_node(r, tree_type)

    def unpack_leaf(self, r, tree_type):
        self.leaf_index = r.readint()

        if tree_type != 1:
            return

        self.solid = (r.readint() != 0)
        self.bounds = Sphere(*r.readformat('4f'))

        trianglecount = r.readint()
        self.triangles = [r.readshort() for i in range(trianglecount)]

        if not self.solid:
            del self.bounds
            del self.triangles

    def unpack_portal(self, r, tree_type):
        self.partition = Plane(*r.readformat('4f'))

        self.front_child = BSPNode(r, tree_type)
        self.back_child = BSPNode(r, tree_type)

        if tree_type != 0:
            return

        self.bounds = Sphere(*r.readformat('4f'))

        trianglecount = r.readint()
        polycount = r.readint()

        self.triangles = [r.readshort() for i in range(trianglecount)]
        self.polys = [r.readformat('2H') for i in range(polycount)]

    def unpack_node(self, r, tree_type):
        self.partition = Plane(*r.readformat('4f'))

        if self.node_type == b'BPnn' or self.node_type == b'BPIn':
            self.front_child = BSPNode(r, tree_type)
        elif self.node_type == b'BpIN' or self.node_type == b'BpnN':
            self.back_child = BSPNode(r, tree_type)
        elif self.node_type == b'BPIN' or self.node_type == b'BPnN':
            self.front_child = BSPNode(r, tree_type)
            self.back_child = BSPNode(r, tree_type)
        else:
            pass

        if tree_type == 0 or tree_type == 1:
            self.bounds = Sphere(*r.readformat('4f'))

        if tree_type != 0:
            return

        trianglecount = r.readint()
        self.triangles = [r.readshort() for i in range(trianglecount)]

    def __str__(self):
        return self.to_str(0)

    def to_str(self, indent):
        result = '  ' * indent + 'Node {}\n'.format(self.node_type)

        if hasattr(self, 'leaf_index'):
            result += '  ' * indent + 'Leaf index: {}\n'.format(self.leaf_index)

        if hasattr(self, 'partition'):
            result += '  ' * indent + 'Partition: {}\n'.format(self.partition)

        if hasattr(self, 'bounds'):
            result += '  ' * indent + 'Bounds: {}\n'.format(self.bounds)

        if hasattr(self, 'front_child'):
            result += '  ' * indent + 'Front child:\n' + self.front_child.to_str(indent + 1)

        if hasattr(self, 'back_child'):
            result += '  ' * indent + 'Back child:\n' + self.back_child.to_str(indent + 1)

        if hasattr(self, 'triangles'):
            result += '  ' * indent + 'Triangles: {}\n'.format(self.triangles)

        if hasattr(self, 'polys'):
            result += '  ' * indent + 'Polys: {}\n'.format(self.polys)

        if hasattr(self, 'solid'):
            result += '  ' * indent + 'Solid: {}\n'.format(self.solid)

        return result

