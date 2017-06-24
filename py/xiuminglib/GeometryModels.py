"""
Classes of Common 3D Geometry Models

Xiuming Zhang, MIT CSAIL
June 2017
"""

import logging
from os.path import abspath
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
                List of lists of integers starting from 1
                Optional; defaults to None
            vn: Vertex normals
                *-by-3 numpy array of floats, normalized or unnormalized
                Optional; defaults to None
            fn: Faces' vertex normal indices
                Same type and size as 'f'
                Optional; defaults to None
            vt: Vertex texture coordinates
                *-by-2 numpy array of floats in [0, 1]
                Optional; defaults to None
            ft: Faces' texture vertex indices
                Same type and size as 'f'
                Optional; defaults to None
            s: Group smoothing
                Boolean
                Optional; defaults to False
        """
        self.name = name
        if v is not None:
            assert (len(v.shape) == 2 and v.shape[1] == 3), "'v' must be *-by-3"
        self.v = v
        if vn is not None:
            assert (len(vn.shape) == 2 and vn.shape[1] == 3), "'vn' must be *-by-3"
        self.vn = vn
        if vt is not None:
            assert (len(vt.shape) == 2 and vt.shape[1] == 2), "'vt' must be *-by-2"
        self.vt = vt
        self.f = f
        self.ft = ft
        self.fn = fn
        self.s = s

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
        f = open(obj_file, 'r')
        lines = [l.strip('\n') for l in f.readlines()]
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

        logging.info("%s: # geometric vertices:      %d", thisfunc, n_v)
        logging.info("%s: # texture vertex:          %d", thisfunc, n_vt)
        logging.info("%s: # vertex normals:          %d", thisfunc, n_vn)
        logging.info("%s: # geometric faces:         %d", thisfunc, n_f)
        logging.info("%s: # texture faces:           %d", thisfunc, n_ft)
        logging.info("%s: # normal faces:            %d", thisfunc, n_fn)

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


if __name__ == '__main__':
    objf = '/data/vision/billf/mooncam/output/xiuming/planets/moon_icosphere/moon.obj'
    obj = Obj()
    obj.print_info()
    obj = obj.load_file(objf)
    obj.print_info()
    import pdb; pdb.set_trace()
