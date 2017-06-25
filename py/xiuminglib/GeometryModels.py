"""
Classes of Common 3D Geometry Models

Xiuming Zhang, MIT CSAIL
June 2017
"""

import logging
from os import makedirs
from os.path import abspath, dirname, exists
import numpy as np

logging.basicConfig(level=logging.INFO)
thisfile = abspath(__file__)


class Obj(object):
    """
    Wavefront .obj format
    """

    def __init__(self, o=None, v=None, f=None, vn=None, fn=None, vt=None, ft=None, s=False, mtllib=None, usemtl=None):
        """
        Class constructor

        Args:
            o: Object name
                String
                Optional; defaults to None
            v: Vertex coordinates
                *-by-3 numpy array of floats
                Optional; defaults to None
            f: Faces' vertex indices
                List of lists of integers starting from 1, e.g., '[[1, 2, 3], [4, 5, 6], [7, 8, 9, 10], ...]'
                Optional; defaults to None
            vn: Vertex normals
                *-by-3 numpy array of floats, normalized or unnormalized
                Optional; defaults to None
            fn: Faces' vertex normal indices
                Same type and length as 'f', e.g., '[[1, 1, 1], [], [2, 2, 2, 2], ...]'
                Optional; defaults to None
            vt: Vertex texture coordinates
                *-by-2 numpy array of floats in [0, 1]
                Optional; defaults to None
            ft: Faces' texture vertex indices
                Same type and length as 'f', e.g., '[[1, 2, 3], [4, 5, 6], [], ...]'
                Optional; defaults to None
            s: Group smoothing
                Boolean
                Optional; defaults to False
            mtllib: Material file name
                String, e.g., 'cube.mtl'
                Optional; defaults to None
            usemtl: Material name (defined in .mtl file)
                String
                Optional; defaults to None
        """
        self.mtllib = mtllib
        self.o = o

        # Vertices
        if v is not None:
            assert (len(v.shape) == 2 and v.shape[1] == 3), "'v' must be *-by-3"
        if vt is not None:
            assert (len(vt.shape) == 2 and vt.shape[1] == 2), "'vt' must be *-by-2"
        if vn is not None:
            assert (len(vn.shape) == 2 and vn.shape[1] == 3), "'vn' must be *-by-3"
        self.v = v
        self.vt = vt
        self.vn = vn

        # Faces
        if f is not None:
            if ft is not None:
                assert (len(ft) == len(f)), "'ft' must be of the same length as 'f' (use '[]' to fill)"
            if fn is not None:
                assert (len(fn) == len(f)), "'fn' must be of the same length as 'f' (use '[]' to fill)"
        self.f = f
        self.ft = ft
        self.fn = fn

        self.usemtl = usemtl
        self.s = s

    # Populate attributes with contents read from file
    def load_file(self, obj_file):
        """
        Load a (basic) .obj file as an object

        Args:
            obj_file: Path to .obj file
                String

        Returns:
            self: updated object
        """
        fid = open(obj_file, 'r')
        lines = [l.strip('\n') for l in fid.readlines()]
        lines = [l for l in lines if len(l) > 0] # remove empty lines

        # Check if there's only one object
        n_o = len([l for l in lines if l[0] == 'o'])
        if n_o > 1:
            raise ValueError(".obj file containing multiple objects is not supported -- consider using 'assimp' instead")

        # Count for array initializations
        n_v = len([l for l in lines if l[:2] == 'v '])
        n_vt = len([l for l in lines if l[:3] == 'vt '])
        n_vn = len([l for l in lines if l[:3] == 'vn '])
        lines_f = [l for l in lines if l[:2] == 'f ']
        n_f = len(lines_f)

        # Initialize arrays
        mtllib = None
        o = None
        v = np.zeros((n_v, 3))
        vt = np.zeros((n_vt, 2))
        vn = np.zeros((n_vn, 3))
        usemtl = None
        s = False
        f = [None] * n_f
        # If there's no 'ft' or 'fn' for a 'f', a '[]' is inserted as a placeholder
        # This guarantees 'f[i]' always corresponds to 'ft[i]' and 'fn[i]'
        ft = [None] * n_f
        fn = [None] * n_f

        # Load data line by line
        n_ft, n_fn = 0, 0
        i_v, i_vt, i_vn, i_f = 0, 0, 0, 0
        for l in lines:
            if l[0] == '#': # comment
                pass
            elif l[:7] == 'mtllib ': # mtl file
                mtllib = l[7:]
            elif l[:2] == 'o ': # object name
                o = l[2:]
            elif l[:2] == 'v ': # geometric vertex
                v[i_v, :] = [float(x) for x in l[2:].split(' ')]
                i_v += 1
            elif l[:3] == 'vt ': # texture vertex
                vt[i_vt, :] = [float(x) for x in l[3:].split(' ')]
                i_vt += 1
            elif l[:3] == 'vn ': # normal vector
                vn[i_vn, :] = [float(x) for x in l[3:].split(' ')]
                i_vn += 1
            elif l[:7] == 'usemtl ': # material name
                usemtl = l[7:]
            elif l[:2] == 's ': # group smoothing
                if l[2:] == 'on':
                    s = True
            elif l[:2] == 'f ': # face
                n_slashes = l[2:].split(' ')[0].count('/')
                if n_slashes == 0: # just f (1 2 3)
                    f[i_f] = [int(x) for x in l[2:].split(' ')]
                    ft[i_f] = []
                    fn[i_f] = []
                elif n_slashes == 1: # f and ft (1/1 2/2 3/3)
                    f[i_f] = [int(x.split('/')[0]) for x in l[2:].split(' ')]
                    ft[i_f] = [int(x.split('/')[1]) for x in l[2:].split(' ')]
                    fn[i_f] = []
                    n_ft += 1
                elif n_slashes == 2:
                    if l[2:].split(' ')[0].count('//') == 1: # f and fn (1//1 2//1 3//1)
                        f[i_f] = [int(x.split('//')[0]) for x in l[2:].split(' ')]
                        ft[i_f] = []
                        fn[i_f] = [int(x.split('//')[1]) for x in l[2:].split(' ')]
                        n_fn += 1
                    else: # f, ft and fn (1/1/1 2/2/1 3/3/1)
                        f[i_f] = [int(x.split('/')[0]) for x in l[2:].split(' ')]
                        ft[i_f] = [int(x.split('/')[1]) for x in l[2:].split(' ')]
                        fn[i_f] = [int(x.split('/')[2]) for x in l[2:].split(' ')]
                        n_ft += 1
                        n_fn += 1
                i_f += 1
            else:
                raise ValueError("Unidentified line type: %s" % l)

        # Update self
        self.mtllib = mtllib
        self.o = o
        self.v = v
        self.vt = vt if vt.shape[0] > 0 else None
        self.vn = vn if vn.shape[0] > 0 else None
        self.f = f
        self.ft = ft if any(len(x) > 0 for x in ft) else None
        self.fn = fn if any(len(x) > 0 for x in fn) else None
        self.usemtl = usemtl
        self.s = s

    # Print model info
    def print_info(self):
        thisfunc = thisfile + '->print_info()'

        # Basic stats
        mtllib = self.mtllib
        o = self.o
        n_v = self.v.shape[0] if self.v is not None else 0
        n_vt = self.vt.shape[0] if self.vt is not None else 0
        n_vn = self.vn.shape[0] if self.vn is not None else 0
        usemtl = self.usemtl
        s = self.s
        n_f = len(self.f) if self.f is not None else 0
        if self.ft is not None:
            n_ft = sum(len(x) > 0 for x in self.ft)
        else:
            n_ft = 0
        if self.fn is not None:
            n_fn = sum(len(x) > 0 for x in self.fn)
        else:
            n_fn = 0

        logging.info("%s: -------------------------------------------------------", thisfunc)
        logging.info("%s: Object name            'o'            %s", thisfunc, o)
        logging.info("%s: Material file          'mtllib'       %s", thisfunc, mtllib)
        logging.info("%s: Material               'usemtl'       %s", thisfunc, usemtl)
        logging.info("%s: Group smoothing        's'            %r", thisfunc, s)
        logging.info("%s: # geometric vertices   'v'            %d", thisfunc, n_v)
        logging.info("%s: # texture vertices     'vt'           %d", thisfunc, n_vt)
        logging.info("%s: # normal vectors       'vn'           %d", thisfunc, n_vn)
        logging.info("%s: # geometric faces      'f x/o/o'      %d", thisfunc, n_f)
        logging.info("%s: # texture faces        'f o/x/o'      %d", thisfunc, n_ft)
        logging.info("%s: # normal faces         'f o/o/x'      %d", thisfunc, n_fn)

        # How many triangles, quads, etc.
        if n_f > 0:
            logging.info("%s:", thisfunc)
            logging.info("%s: Among %d faces:", thisfunc, n_f)
            vert_counts = [len(x) for x in self.f]
            for c in np.unique(vert_counts):
                howmany = vert_counts.count(c)
                logging.info("%s:   - %d are formed by %d vertices", thisfunc, howmany, c)
        logging.info("%s: -------------------------------------------------------", thisfunc)

    # Set vn and fn according to v and f
    def set_face_normals(self):
        """
        Set face normals according to geometric vertices and their orders in forming faces

        Returns:
            vn: Normal vectors
                'len(f)'-by-3 numpy arrays
            fn: Normal faces
                'len(f)'-long list of lists of integers starting from 1
                Each member list consists of the same integer, e.g., '[[1, 1, 1], [2, 2, 2, 2], ...]'
        """
        thisfunc = thisfile + '->set_face_normals()'

        n_f = len(self.f)
        vn = np.zeros((n_f, 3))
        fn = [None] * n_f

        # For each face
        for i, verts_id in enumerate(self.f):
            # Vertices must be coplanar to be valid, so we can just pick the first three
            ind = [x - 1 for x in verts_id[:3]] # in .obj, index starts from 1, not 0
            verts = self.v[ind, :]
            p1p2 = verts[1, :] - verts[0, :]
            p1p3 = verts[2, :] - verts[0, :]
            normal = np.cross(p1p2, p1p3)
            vn[i, :] = normal / np.linalg.norm(normal) # normalize
            fn[i] = [i + 1] * len(verts_id)

        # Set normals and return
        self.vn = vn
        self.fn = fn
        logging.info("%s: Face normals recalculated with 'v' and 'f' -- 'vn' and 'fn' updated", thisfunc)
        return vn, fn

    # Output object to a .obj file
    def write_file(self, objpath):
        """
        Write the current model to a .obj file (and possibly an accompanying .mtl)
        """
        thisfunc = thisfile + '->write_file()'

        mtllib = self.mtllib
        o = self.o
        v, vt, vn = self.v, self.vt, self.vn
        usemtl = self.usemtl
        s = self.s
        f, ft, fn = self.f, self.ft, self.fn

        # mkdir if necessary
        outdir = dirname(objpath)
        if not exists(outdir):
            makedirs(outdir)

        # Write .obj
        with open(objpath, 'w') as fid:
            # Material file
            if mtllib is not None:
                fid.write('mtllib %s\n' % mtllib)

            # Object name
            fid.write('o %s\n' % o)

            # Vertices
            for i in range(v.shape[0]):
                fid.write('v %f %f %f\n' % tuple(v[i, :]))
            if vt is not None:
                for i in range(vt.shape[0]):
                    fid.write('vt %f %f\n' % tuple(vt[i, :]))
            if vn is not None:
                for i in range(vn.shape[0]):
                    fid.write('vn %f %f %f\n' % tuple(vn[i, :]))

            # Material name
            if usemtl is not None:
                fid.write('usemtl %s\n' % usemtl)

            # Group smoothing
            if s:
                fid.write('s on\n')
            else:
                fid.write('s off\n')

            # Faces
            if ft is None and fn is None: # just f (1 2 3)
                for v_id in f:
                    fid.write(('f' + ' %d' * len(v_id) + '\n') % tuple(v_id))
            elif ft is not None and fn is None: # f and ft (1/1 2/2 3/3 or 1 2 3)
                for i, v_id in enumerate(f):
                    vt_id = ft[i]
                    if len(vt_id) == len(v_id):
                        fid.write(('f' + ' %d/%d' * len(v_id) + '\n') %
                                  tuple([x for pair in zip(v_id, vt_id) for x in pair]))
                    elif len(vt_id) == 0:
                        fid.write(('f' + ' %d' * len(v_id) + '\n') % tuple(v_id))
                    else:
                        raise ValueError("'ft[%d]', not empty, doesn't match length of 'f[%d]'" % (i, i))
            elif ft is None and fn is not None: # f and fn (1//1 2//1 3//1 or 1 2 3)
                for i, v_id in enumerate(f):
                    vn_id = fn[i]
                    if len(vn_id) == len(v_id):
                        fid.write(('f' + ' %d//%d' * len(v_id) + '\n') %
                                  tuple([x for pair in zip(v_id, vn_id) for x in pair]))
                    elif len(vn_id) == 0:
                        fid.write(('f' + ' %d' * len(v_id) + '\n') % tuple(v_id))
                    else:
                        raise ValueError("'fn[%d]', not empty, doesn't match length of 'f[%d]'" % (i, i))
            elif ft is not None and fn is not None: # f, ft and fn (1/1/1 2/2/1 3/3/1 or 1/1 2/2 3/3 or 1//1 2//1 3//1 or 1 2 3)
                for i, v_id in enumerate(f):
                    vt_id = ft[i]
                    vn_id = fn[i]
                    if len(vt_id) == len(v_id) and len(vn_id) == len(v_id):
                        fid.write(('f' + ' %d/%d/%d' * len(v_id) + '\n') %
                                  tuple([x for triple in zip(v_id, vt_id, vn_id) for x in triple]))
                    elif len(vt_id) == len(v_id) and len(vn_id) == 0:
                        fid.write(('f' + ' %d/%d' * len(v_id) + '\n') %
                                  tuple([x for pair in zip(v_id, vt_id) for x in pair]))
                    elif len(vt_id) == 0 and len(vn_id) == len(v_id):
                        fid.write(('f' + ' %d//%d' * len(v_id) + '\n') %
                                  tuple([x for pair in zip(v_id, vn_id) for x in pair]))
                    elif len(vt_id) == 0 and len(vn_id) == 0:
                        fid.write(('f' + ' %d' * len(v_id) + '\n') % tuple(v_id))
                    else:
                        raise ValueError("If not empty, 'ft[%d]' or 'fn[%d]' doesn't match length of 'f[%d]'" % (i, i, i))
        logging.info("%s: Done writing to %s", thisfunc, objpath)


# Test
if __name__ == '__main__':
    objf = '/data/vision/billf/mooncam/output/xiuming/planets/moon_icosphere/icosphere2.obj'
    # objf = './example-obj-mtl/cube.obj'
    obj = Obj()
    obj.print_info()
    obj.load_file(objf)
    obj.print_info()
    objf_reproduce = objf.replace('.obj', '_reproduce.obj')
    obj.write_file(objf_reproduce)
    obj.set_face_normals()
    obj.print_info()
