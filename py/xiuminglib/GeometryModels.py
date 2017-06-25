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

    def __init__(self, name=None, v=None, f=None, vn=None, fn=None, vt=None, ft=None, s=False):
        """
        Class constructor

        Args:
            name: Object name
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
        """
        self.name = name

        # Vertices
        if v is not None:
            assert (len(v.shape) == 2 and v.shape[1] == 3), "'v' must be *-by-3"
        if vn is not None:
            assert (len(vn.shape) == 2 and vn.shape[1] == 3), "'vn' must be *-by-3"
        if vt is not None:
            assert (len(vt.shape) == 2 and vt.shape[1] == 2), "'vt' must be *-by-2"
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

        # Group smoothing
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
        thisfunc = thisfile + '->load_file()'

        # Stats
        fid = open(obj_file, 'r')
        lines = [l.strip('\n') for l in fid.readlines()]
        n_o = len([l for l in lines if l[0] == 'o'])
        if n_o > 1:
            raise ValueError(".obj file containing multiple objects is not supported -- consider using 'assimp' instead")
        n_v = len([l for l in lines if l[:2] == 'v '])
        n_vt = len([l for l in lines if l[:3] == 'vt '])
        n_vn = len([l for l in lines if l[:3] == 'vn '])
        lines_f = [l for l in lines if l[:2] == 'f ']
        n_f = len(lines_f)
        n_slashes = lines_f[0].split(' ')[1].count('/')
        if n_slashes == 0: # just f
            n_fn, n_ft = 0, 0
        elif n_slashes == 1: # f and ft
            n_fn = 0
            n_ft = n_f
        elif n_slashes == 2:
            if lines_f[0].split(' ')[1].count('//') == 1: # f and fn
                n_fn = n_f
                n_ft = 0
            else: # all
                n_fn, n_ft = n_f, n_f

        logging.info("%s: -----------------------------------", thisfunc)
        logging.info("%s: # geometric vertices:      %d", thisfunc, n_v)
        logging.info("%s: # texture vertices         %d", thisfunc, n_vt)
        logging.info("%s: # vertex normals:          %d", thisfunc, n_vn)
        logging.info("%s: # geometric faces:         %d", thisfunc, n_f)
        logging.info("%s: # texture faces:           %d", thisfunc, n_ft)
        logging.info("%s: # normal faces:            %d", thisfunc, n_fn)
        logging.info("%s: -----------------------------------", thisfunc)

        # Initialize arrays
        v = np.zeros((n_v, 3))
        vt = np.zeros((n_vt, 2))
        vn = np.zeros((n_vn, 3))
        f = [None] * n_f
        ft = [None] * n_ft
        fn = [None] * n_fn

        # Load data line by line
        i_v, i_vt, i_vn, i_f, i_ft, i_fn = 0, 0, 0, 0, 0, 0
        for i, l in enumerate(lines):
            if l[0] == '#': # comment
                pass
            elif l[:2] == 'o ': # object name
                name = l[2:]
            elif l[:2] == 'v ': # geometric vertex
                v[i_v, :] = [float(x) for x in l[2:].split(' ')]
                i_v += 1
            elif l[:3] == 'vt ': # texture vertex
                vt[i_vt, :] = [float(x) for x in l[3:].split(' ')]
                i_vt += 1
            elif l[:3] == 'vn ': # normal vector
                vn[i_vn, :] = [float(x) for x in l[3:].split(' ')]
                i_vn += 1
            elif l[:2] == 'f ': # face
                if n_ft == 0 and n_fn == 0: # 1 2 3
                    f[i_f] = [int(x) for x in l[2:].split(' ')]
                    i_f += 1
                elif n_ft > 0 and n_fn == 0: # 1/1 2/2 3/3
                    f[i_f] = [int(x.split('/')[0]) for x in l[2:].split(' ')]
                    i_f += 1
                    ft[i_ft] = [int(x.split('/')[1]) for x in l[2:].split(' ')]
                    i_ft += 1
                elif n_ft == 0 and n_fn > 0: # 1//1 2//2 3//3
                    f[i_f] = [int(x.split('//')[0]) for x in l[2:].split(' ')]
                    i_f += 1
                    fn[i_fn] = [int(x.split('//')[1]) for x in l[2:].split(' ')]
                    i_fn += 1
                else: # 1/1/1 2/2/2 3/3/3
                    f[i_f] = [int(x.split('/')[0]) for x in l[2:].split(' ')]
                    i_f += 1
                    ft[i_ft] = [int(x.split('/')[1]) for x in l[2:].split(' ')]
                    i_ft += 1
                    fn[i_fn] = [int(x.split('/')[2]) for x in l[2:].split(' ')]
                    i_fn += 1
            elif l[:2] == 's ': # group smoothing
                s = True if l[2:] == 'on' else False
            else:
                raise ValueError("Unidentified line type at line %d" % (i + 1))

        # Update self
        self.name = name
        self.v = v
        self.vt = vt if vt.shape[0] > 0 else None
        self.vn = vn if vn.shape[0] > 0 else None
        self.f = f
        self.ft = ft if len(ft) > 0 else None
        self.fn = fn if len(fn) > 0 else None
        self.s = s
        return self

    # Print model info
    def print_info(self):
        thisfunc = thisfile + '->print_info()'

        # Basic stats
        name = self.name
        n_v = self.v.shape[0] if self.v is not None else 0
        n_vt = self.vt.shape[0] if self.vt is not None else 0
        n_vn = self.vn.shape[0] if self.vn is not None else 0
        n_f = len(self.f) if self.f is not None else 0
        n_ft = len(self.ft) if self.ft is not None else 0
        n_fn = len(self.fn) if self.fn is not None else 0
        s = self.s

        logging.info("%s: --------------------------------------------", thisfunc)
        logging.info("%s: Object name 'o':               %s", thisfunc, name)
        logging.info("%s: # geometric vertices 'v':      %d", thisfunc, n_v)
        logging.info("%s: # texture vertices 'vt':       %d", thisfunc, n_vt)
        logging.info("%s: # normal vectors 'vn':         %d", thisfunc, n_vn)
        logging.info("%s: # geometric faces 'f x/o/o':   %d", thisfunc, n_f)
        logging.info("%s: # texture faces 'f o/x/o':     %d", thisfunc, n_ft)
        logging.info("%s: # normal faces 'f o/o/x':      %d", thisfunc, n_fn)
        logging.info("%s: Group smoothing 's':           %r", thisfunc, s)

        # How many triangles, quads, etc.
        if n_f > 0:
            logging.info("%s:", thisfunc)
            logging.info("%s: Among %d faces:", thisfunc, n_f)
            vert_counts = [len(x) for x in self.f]
            for c in np.unique(vert_counts):
                howmany = vert_counts.count(c)
                logging.info("%s:   - %d are formed by %d vertices", thisfunc, howmany, c)
        logging.info("%s: --------------------------------------------", thisfunc)

    # Set vn and fn according to v and f
    def set_face_normals(self):
        """
        Set face normals according to geometric vertices and their orders in forming faces

        Returns:
            vn: Normal vectors
                n-by-3 numpy arrays, where n is 'self.f.shape[0]'
            fn: Normal faces
                List of lists of integers starting from 1
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

        name = self.name
        v, vt, vn = self.v, self.vt, self.vn
        f, ft, fn = self.f, self.ft, self.fn
        s = self.s

        # Validate inputs
        assert (v is not None and len(v.shape) == 2 and v.shape[1] == 3), "'v' must be *-by-3 and not be None"
        assert (f is not None), "'f' can't be None"
        if ft is not None:
            assert (len(f) == len(ft)), "'ft' and 'f' must have the same length"
        if fn is not None:
            assert (len(f) == len(fn)), "'fn' and 'f' must have the same length"
        assert isinstance(s, bool), "'s' must be Boolean"

        # mkdir if necessary
        outdir = dirname(objpath)
        if not exists(outdir):
            makedirs(outdir)

        # Write .obj
        with open(objpath, 'w') as fid:
            fid.write('o %s\n' % name)

            # Vertices
            for i in range(v.shape[0]):
                fid.write('v %f %f %f\n' % tuple(v[i, :]))
            if vt is not None:
                for i in range(vt.shape[0]):
                    fid.write('vt %f %f\n' % tuple(vt[i, :]))
            if vn is not None:
                for i in range(vn.shape[0]):
                    fid.write('vn %f %f %f\n' % tuple(vn[i, :]))

            # Group smoothing
            if s:
                fid.write('s on\n')
            else:
                fid.write('s off\n')

            # Faces
            if ft is None and fn is None: # just f
                for v_id in f:
                    fid.write(('f' + ' %d' * len(v_id) + '\n') % tuple(v_id))
            elif ft is not None and fn is None: # f and ft
                for i, v_id in enumerate(f):
                    vt_id = ft[i]
                    assert (len(v_id) == len(vt_id)), "'f[%d]' and 'ft[%d]' are of different lengths" % (i, i)
                    fid.write(('f' + ' %d/%d' * len(v_id) + '\n') %
                              tuple([x for pair in zip(v_id, vt_id) for x in pair]))
            elif ft is None and fn is not None: # f and fn
                for i, v_id in enumerate(f):
                    vn_id = fn[i]
                    assert (len(v_id) == len(vn_id)), "'f[%d]' and 'fn[%d]' are of different lengths" % (i, i)
                    fid.write(('f' + ' %d//%d' * len(v_id) + '\n') %
                              tuple([x for pair in zip(v_id, vn_id) for x in pair]))
            elif ft is not None and fn is not None: # all
                for i, v_id in enumerate(f):
                    vt_id = ft[i]
                    vn_id = fn[i]
                    assert (len(v_id) == len(vt_id)), "'f[%d]' and 'ft[%d]' are of different lengths" % (i, i)
                    assert (len(v_id) == len(vn_id)), "'f[%d]' and 'fn[%d]' are of different lengths" % (i, i)
                    fid.write(('f' + ' %d/%d/%d' * len(v_id) + '\n') %
                              tuple([x for triple in zip(v_id, vt_id, vn_id) for x in triple]))
        logging.info("%s: Done writing to %s", thisfunc, objpath)


# Test
if __name__ == '__main__':
    objf = '/data/vision/billf/mooncam/output/xiuming/planets/moon_icosphere/moon.obj'
    obj = Obj()
    obj.print_info()
    obj.load_file(objf)
    obj.set_face_normals()
    obj.print_info()
    objf_mod = '/data/vision/billf/mooncam/output/xiuming/planets/moon_icosphere/moon_mod.obj'
    obj.write_file(objf_mod)
