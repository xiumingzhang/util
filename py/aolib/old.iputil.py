# todo: rewrite 
from IPython import parallel 
import util as ut, os, sys, time
from IPython.parallel.util import interactive
import subprocess

if 0:
  import dill
  from types import FunctionType
  from IPython.utils.pickleutil import can_map
  can_map.pop(FunctionType, None)
  import pickle
  from IPython.kernel.zmq import serialize
  serialize.pickle = pickle

ip_parallel = parallel

default_config_file = '/data/vision/billf/aho-billf/ipcluster_profile/security/ipcontroller-client.json'

p = None
part_info = None
builtin_map = __builtins__['map']

def relative_module(m):
  return hasattr(m, '__file__') \
         and ((not m.__file__.startswith('/')) \
              or m.__file__.startswith(os.getcwd()))

def safe_reload(m):
  if relative_module(m) and (not hasattr(m, '__no_autoreload__')):
    print 'reloading'
    reload(m)

def run_reload():
  excludes = set(['__main__', 'autoreload'])
  for name, m in list(sys.modules.iteritems()):
    if m and relative_module(m) and (name not in excludes) and (not hasattr(m, '__no_autoreload__')):
      reload(m)

class Parallel:
  def __init__(self, config = None, rc = None, view = None):
    self.config = config
    self._rc = rc
    self._view = view

  def init_rc(self, reset = False):
    if reset or (self._rc is None):
      if self.config is None:
        self._rc = ip_parallel.Client()
      else:
        self._rc = ip_parallel.Client(self.config)
      self._view = self._rc.direct_view()
      #self._view = self._rc.load_balanced_view()

  def view(self):
    self.init_rc()
    return self._view
  
  def rc(self):
    self.init_rc()
    return self._rc
      
  def per_machine_subset(self, n_per_machine):
    targets = self.targets_by_hostname()
    target_subset = ut.flatten([ut.sample_at_most(ts, n_per_machine) \
                                for ts in targets.values()])
    return Parallel(self.config, self.rc(), self.rc()[target_subset])

  def partition(self, n, i):
    target_subset = [j for j in self.rc()[:].targets if j % n == i]
    return Parallel(self.config, self.rc(), self.rc()[target_subset])
    
  def targets_by_hostname(self):
    # initialize parallel_rc
    self.import_modules(['subprocess'], False)
    targets_by_hostname = {}
    for t in self.rc()[:].targets:
      v = self.rc()[[t]]
      [hostname] = v.map_sync(interactive(lambda x: subprocess.Popen('hostname', shell=True, stdout=subprocess.PIPE).stdout.read().rstrip()), [1])
      if hostname not in targets_by_hostname:
        targets_by_hostname[hostname] = []
      targets_by_hostname[hostname].append(t)
    return targets_by_hostname

  def execute(self, code):
    r = self.view().execute(code)
    r.wait()
    if not r.successful():
      print 'iputil.execute error:'
      print r.result
    assert r.successful()

  def list_machines(self):
    self.view().execute('import subprocess, os').wait()
    res = self.view().map_sync(interactive(lambda x : subprocess.Popen('hostname', shell=True,
                                                                  stdout=subprocess.PIPE).stdout.read().rstrip()), range(200))
    print 'Running on:'
    ut.prn_lines(set(res))

  def send_var(self, var_name, val):
    res = self.view().push({var_name : val})
    res.wait()
    assert res.successful()

  def import_modules(self, packages, reload = False):
    packages = ['aolib.iputil'] + list(packages)
    import_cmd = ''
    reload_cmd = ''
    for p in packages:
      if len(import_cmd) != 0:
        import_cmd += ', '
        reload_cmd += '; '
      if type(p) == type((1,)):
        import_cmd += '%s as %s' % p
        reload_cmd += 'aolib.iputil.safe_reload(%s)' % p[1]
      else:
        import_cmd += p
        reload_cmd += 'aolib.iputil.safe_reload(%s)' % p
        
    if reload:
      cmd = 'import %s; %s' % (import_cmd, reload_cmd)
    else:
      cmd = 'import %s' % import_cmd
    self.execute(cmd)

  def reload_modules(self):
    #self.execute('from aolib import iputil, areload; iputil.run_reload()')
    self.execute('from aolib import iputil, areload; iputil.run_reload()')

  def send_var_fs(self, var_name, val):
    fname = ut.make_temp_nfs('.pk')
    ut.save(fname, val)
    res = self.view().execute('import util as ut; ut.wait_for_file("%s", 30); %s = ut.load("%s")' % (fname, var_name, fname))
    res.wait()
    assert res.successful()
    os.remove(fname)

  def clear(self):
    self.view().results.clear()
    self.rc().results.clear()
    self.rc().metadata.clear()
    
  # def maybe_map_sync(self, parallel, f, xs, imports = []):
  #   if parallel:
  #     return self.map_sync(f, xs, imports)
  #   else:
  #     # assume imports have already been loaded if not parallel
  #     if type(xs) == type((1,)):
  #       return map(f, *xs)
  #     else:
  #       return map(f, xs)

  # def maybe_map_sync(self, parallel, f, xs, imports = [], vars = {}):
  #   if parallel:
  #     return self.map_sync(f, xs, imports)
  #   else:
  #     # todo: is it better to save these temporarily? or would it only make it more confusing?
  #     f.func_globals.update(vars)
  #     # assume imports have already been loaded if not parallel
  #     if type(xs) == type((1,)):
  #       return map(f, *xs)
  #     else:
  #       return map(f, xs)

  def maybe_map_sync(self, parallel, f, xs, vars = {}, imports = []):
    if parallel:
      return self.map_sync(f, xs, vars, imports)
    else:
      # todo: is it better to save these temporarily? or would it only make it more confusing?
      if len(vars):
        f.func_globals.update(vars)
      # assume imports have already been loaded if not parallel
      if type(xs) == type((1,)):
        return builtin_map(f, *xs)
      else:
        return builtin_map(f, xs)

  def map(self, parallel, f, xs, vars = {}, imports = []):
    return self.maybe_map_sync(parallel, f, xs, vars, imports)
  
  def map_sync(self, f, xs, vars = {}, imports = []):
    self.import_modules(imports, True)
    self.reload_modules()
    
    # res = self.view().push(vars)
    # res.wait()
    # assert res.successful()

    if len(xs) == 0:
      return []
    
    # interpret tuple as multiple args
    if type(xs) == type((1,)):
      res = self.view().map_sync(f, *xs)
    else:
      res = self.view().map_sync(f, xs)
      
    self.clear()

    return res

  def abort(self):
    #self._rc.abort()
    self.view().abort()

  def test(self, do = True, max_wait = 30):
    if do:
      a = self.view().map_async(lambda x: x, range(100))
      start = time.time()
      while time.time() - start <= max_wait:
        if a.ready():
          return True
        else:
          time.sleep(1)
      raise RuntimeError('test() timed out after %s seconds!' % max_wait)
    
__no_autoreload__ = True

def init(do=True, local = False):
  if do:
    global p, part_info
    if local or not os.path.exists(default_config_file):
      config_file = None
    else:
      config_file = default_config_file

    p = Parallel(config_file)
    if part_info is not None:
      print 'iputil partition:', part_info
      p = p.partition(*part_info)
    for f in dir(p):
      if not f.startswith('_') and hasattr(getattr(p, f), '__call__'):
        globals()[f] = getattr(p, f)
    
init()  

# def restart():
#   os.system('./cluster.sh')
#   init()


def global_partition(n=None, i=None):
  global p, part_info
  if n is None:
    part_info = None
  else:
    part_info = (n, i)
  init()

def test_partition():
  def f(x):
    import iputil
    return sum(iputil.partition(2, 1).map_sync(lambda x: x, range(10)))
  import iputil
  iputil.map_sync(lambda x:x, range(10000))
  assert sum(iputil.partition(2, 0).map_sync(f, range(1000))) == 1000*sum(range(10))

def reset(parallel=True):
  init(parallel)
  test(parallel)

