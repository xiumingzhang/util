from sys import argv
from shlex import split
from subprocess import check_output, Popen, PIPE, DEVNULL
from multiprocessing import Pool
from collections import OrderedDict
from operator import itemgetter
from tqdm import tqdm

import logging
import logging_colorer # noqa: F401 # pylint: disable=unused-import
logging.basicConfig(level=logging.INFO)


def ping_ok(machine_name):
    cmd = 'timeout 0.5 ping -c1 %s' % machine_name
    child = Popen(split(cmd), stdout=DEVNULL, stderr=DEVNULL)
    _, _ = child.communicate()
    return child.returncode == 0


def on_this_machine(machine_name):
    return machine_name == check_output('hostname').decode().strip('\n')


def get_pids(machine_name, user, job_name):
    cmd = ('ssh -o PasswordAuthentication=no -o LogLevel=QUIET -t %s '
           '"ps ax -u %s | grep -e %s -e exec_client"') % (machine_name, user, job_name)
    ps = Popen(split(cmd), stdout=PIPE).communicate()[0].decode()
    pids = []
    for p in ps.split('\n'):
        if len(p) < 2:
            # Skip '', '\r', etc.
            continue
        p_list = p.split(None, 4)
        if p_list[1] == '?':
            # Not attached to any pseudoterminal
            pids.append(p_list[0])
    return pids


def ssh_kill_process(machine_name, pid):
    cmd = ('ssh -o PasswordAuthentication=no -o LogLevel=QUIET -t %s '
           'kill -9 %s') % (machine_name, pid)
    child = Popen(split(cmd), stdout=DEVNULL, stderr=DEVNULL)
    _, _ = child.communicate()
    return child.returncode == 0


def kill_machine(args):
    machine_name, user, job_name = args

    msgs = OrderedDict()
    msg_id = 0
    msg_prefix = "%s: " # to be formatted as machine name

    if on_this_machine(machine_name):
        msgs[(msg_id, 'info')] = msg_prefix + "Skip killing, since you are on it"
        msg_id += 1
        return (machine_name, msgs)

    if not ping_ok(machine_name):
        msgs[(msg_id, 'error')] = msg_prefix + "Can't ping"
        msg_id += 1
    else:
        pids = get_pids(machine_name, user, job_name)
        pids_killed = []
        for pid in pids:
            if ssh_kill_process(machine_name, pid):
                pids_killed.append(pid)
        pids_unkilled = [x for x in pids if x not in pids_killed]
        if not pids:
            msgs[(msg_id, 'info')] = msg_prefix + "No clients found"
            msg_id += 1
        if pids_killed:
            msgs[(msg_id, 'info')] = msg_prefix + "%s killed" % pids_killed
            msg_id += 1
        if pids_unkilled:
            msgs[(msg_id, 'warning')] = msg_prefix + "%s NOT killed" % pids_unkilled
            msg_id += 1
    return (machine_name, msgs)


def fix_messed_up_terminal():
    cmd = 'stty sane'
    child = Popen(split(cmd), stdout=DEVNULL, stderr=DEVNULL)
    _, _ = child.communicate()


def main(user, job_name, where):
    cpu_machines = ['vision%02d' % e for e in range(1, 39)]
    gpu_machines = ['visiongpu%02d' % e for e in range(1, 40)]
    if where == 'cgpu':
        machine_names = cpu_machines + gpu_machines
    elif where == 'cpu':
        machine_names = cpu_machines
    elif where == 'gpu':
        machine_names = gpu_machines
    else:
        raise NotImplementedError(where)

    args = []
    for m in machine_names:
        args.append((m, user, job_name))

    pool = Pool()
    results = list(tqdm(pool.imap_unordered(kill_machine, args), total=len(args)))
    pool.close()
    pool.join()

    fix_messed_up_terminal()

    # Results returned out-of-order
    for machine_name, msgs in sorted(results, key=itemgetter(0)):
        for (_, level), msg in msgs.items():
            logging_print = getattr(logging, level)
            logging_print(msg, machine_name)


if __name__ == '__main__':
    main(*argv[1:])
