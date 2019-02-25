from shlex import split
from subprocess import Popen
from random import shuffle
from os import makedirs
from os.path import exists, join, dirname, realpath, basename, splitext
from shutil import rmtree
from argparse import ArgumentParser
from configparser import ConfigParser
from xiuminglib import general as xg

exec_client = join(dirname(realpath(__file__)), 'exec_client.py')


def send_jobs(machine_list, curr_dir, pool_dir, prefix,
              dry_run=False, exec_args=''):
    # Generate SSH commands
    cmds = []
    for i, x in enumerate(machine_list):
        cmds_file = join(pool_dir, '{}_{:09d}.cmds'.format(prefix, i))
        expects_file = join(pool_dir, '{}_{:09d}.expects'.format(prefix, i))
        cmd = 'ssh -f vision{} "cd {}; python {} {} {} {}"'.format(
            x, curr_dir, exec_client, exec_args, cmds_file, expects_file
        )
        cmds.append(cmd)
    with open(join(pool_dir, 'ssh.cmds'), 'w') as f:
        for x in cmds:
            f.write(x + '\n')
    # Dry run or "wet" run
    if dry_run:
        for x in cmds:
            print(x)
    else:
        for x in cmds:
            child = Popen(split(x)) # stdout and stderr handled in client
            _, _ = child.communicate()


def split_jobs(cmds, cmd_expects, n_machines, pool_dir, prefix):
    # Init
    machine_cmds, machine_expects = [], []
    for _ in range(n_machines):
        machine_cmds.append([])
        machine_expects.append([])
    #
    m_id = 0
    for i, x in enumerate(cmds):
        machine_cmds[m_id].append(x)
        machine_expects[m_id].append(cmd_expects[i])
        m_id += 1
        if m_id >= n_machines:
            m_id = 0
    for mi, thismachine_cmds in enumerate(machine_cmds):
        outf = join(pool_dir, '{}_{:09d}.cmds'.format(prefix, mi))
        with open(outf, 'w') as f:
            for cmd in thismachine_cmds:
                f.write(cmd + '\n')
        outf = join(pool_dir, '{}_{:09d}.expects'.format(prefix, mi))
        with open(outf, 'w') as f:
            for es in machine_expects[mi]:
                f.write(' '.join(es) + '\n')


def gen_exec_args(args):
    exec_args = ''
    if args.exec_seg > 0:
        exec_args += '-s {} '.format(args.exec_seg)
    if args.exec_thread > 0:
        exec_args += '-t {} '.format(args.exec_thread)
    if args.exec_cap > 0:
        exec_args += '-c {} '.format(args.exec_cap)
    if args.exec_dryrun:
        exec_args += '-d '
    return exec_args


def gen_full_cmds(cmd_prefix, params_file, expect_file):
    with open(params_file) as f:
        params = f.readlines()
    if expect_file is None:
        expects = None
    else:
        with open(expect_file) as f:
            expects = f.readlines()
        assert len(params) == len(expects), \
            "Lines of `expect_file` and `params_file` must correspond"
    cmds, cmd_expects = [], []
    for i, x in enumerate(params):
        cmds.append('%s %s' % (cmd_prefix, x.strip()))
        if expects is None:
            cmd_expects.append(['a-nonexistent-placeholder-file'])
        else:
            cmd_expects.append(expects[i].strip().split(' '))
    return cmds, cmd_expects


def main(args):
    # Absolute paths
    config = ConfigParser(inline_comment_prefixes='#')
    config.read(args.config_file)
    curr_dir = config['ENVIRONMENT']['curr_dir']
    job_file = join(curr_dir, config['JOB']['job_file'])
    job_name = splitext(basename(job_file))[0]
    cmd_prefix = '%s %s' % (config['JOB']['bin'], job_file)
    params_file = join(curr_dir, config['JOB']['params_file'])
    pool_dir = join(curr_dir, config['JOB']['pool_dir'])
    rmtree(pool_dir, ignore_errors=True)
    makedirs(pool_dir)
    if 'expect_file' in config['OPTIONAL']:
        expect_file = join(curr_dir, config['OPTIONAL']['expect_file'])
        if not exists(expect_file):
            xg.ask_to_proceed("`expect_file` provided, but non-existent.")
            expect_file = None
    else:
        expect_file = None

    # Machines
    cpu_machines = [x for x in eval(config['MACHINES']['cpu'])]
    gpu_machines = [x for x in eval(config['MACHINES']['gpu'])]
    shuffle(cpu_machines) # in-place
    shuffle(gpu_machines)
    machine_list = []
    for x in cpu_machines:
        machine_list.append('%02d' % x)
    for x in gpu_machines:
        machine_list.append('gpu%02d' % x)

    cmds, cmd_expects = gen_full_cmds(cmd_prefix, params_file, expect_file)

    exec_args = gen_exec_args(args)

    split_jobs(cmds, cmd_expects, len(machine_list), pool_dir, job_name)

    msg = "The first job will be:\n" + \
        "\n".join(['\t' + x for x in split(cmds[0])])
    xg.ask_to_proceed(msg, level='info')

    send_jobs(machine_list, curr_dir, pool_dir, job_name,
              dry_run=args.dryrun, exec_args=exec_args)


if __name__ == '__main__':
    parser = ArgumentParser(description="Dispatch jobs to machines")
    parser.add_argument('config_file', type=str,
                        help="path to the configuration file")
    parser.add_argument('--dryrun', action='store_true',
                        help="print commands without executing them")
    parser.add_argument('--exec_seg', type=int,
                        help="for exec_client: segment number for updating progress", default=-1)
    parser.add_argument('--exec_thread', type=int,
                        help="for exec_client: thread number", default=-1)
    parser.add_argument('--exec_cap', type=int,
                        help="for exec_client: cap the task list to test on small batches", default=-1)
    parser.add_argument('--exec_dryrun', action='store_true',
                        help="for exec_client: print commands without executing")
    main(parser.parse_args())
