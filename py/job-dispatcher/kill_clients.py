from sys import argv
from shlex import split
from subprocess import check_output, Popen, PIPE, DEVNULL

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
            # Not attached any pseudoterminal
            pids.append(p_list[0])
    return pids


def _kill(machine_name, pid):
    cmd = ('ssh -o PasswordAuthentication=no -o LogLevel=QUIET -t %s '
           'kill -9 %s') % (machine_name, pid)
    child = Popen(split(cmd), stdout=DEVNULL, stderr=DEVNULL)
    _, _ = child.communicate()
    return child.returncode == 0


def kill(machine_name, user, job_name):
    if on_this_machine(machine_name):
        return
    if not ping_ok(machine_name):
        logging.warning("%s: unresponsive", machine_name)
    else:
        pids = get_pids(machine_name, user, job_name)
        logging.info("%s: %s found", machine_name, pids)
        for pid in pids:
            killed = _kill(machine_name, pid)
            if killed:
                logging.info("%s: %s killed", machine_name, pid)
            else:
                logging.warning("%s: %s NOT killed", machine_name, pid)


def main(user, job_name):
    cpu_machines = ['vision%02d' % e for e in range(1, 39)]
    gpu_machines = ['visiongpu%02d' % e for e in range(1, 21)]
    machine_names = cpu_machines + gpu_machines

    for m in machine_names:
        kill(m, user, job_name)


if __name__ == '__main__':
    main(*argv[1:])
