from subprocess import call
import os
import re
import ast
import argparse
import configparser
exec_client = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'exec_client.py')


def split_jobs(total_jobs, n_machines, pool_path, prefix='depth'):
    jobs = []
    for n in range(n_machines):
        jobs.append([])
    n = 0
    for k in total_jobs:
        jobs[n].append(k)
        n += 1
        if n >= n_machines:
            n = 0
    for id_job, job in enumerate(jobs):
        file_path = os.path.join(
            pool_path, '{}_{:02d}.txt'.format(prefix, id_job))
        with open(file_path, 'w') as f:
            for k in job:
                f.write('{}\n'.format(k))
        print('{}: {}'.format(id_job, len(job)))


def send_jobs(machine_list, prefix, pool_path, dry_run=False, is_python=True, exec_args_in=""):
    cmd = []
    for idk, k in enumerate(machine_list):
        job_file = os.path.join(pool_path, '{}_{:02d}.txt'.format(prefix, idk))
        if '{}' in exec_args_in:
            exec_args = exec_args_in.format(idk)
        else:
            exec_args = exec_args_in
        if is_python:
            cmd_cur = "ssh -f vision{} python {} {} {}".format(
                k, exec_client, exec_args, job_file)
        else:
            cmd_cur = "ssh -f vision{} {} {} {}".format(
                k, exec_client, exec_args, job_file)

        print(cmd_cur)
        cmd.append(cmd_cur)
    with open(os.path.join(pool_path, 'cmd_log.txt'), 'w') as f:
        for k in cmd:
            f.write('{}\n'.format(k))
    if not dry_run:
        for k in cmd:
            call(k, shell=True)


def prepare_jobs(command, args):
    jobs = []
    if '{}' in command:
        for k in args:
            jobs.append(command.format(k.strip()))
    else:
        for k in args:
            if command == '':
                jobs.append('{}{}'.format(command, k.strip()))
            else:
                jobs.append('{} {}'.format(command, k.strip()))
    return jobs


def main(args):
    config_file = args.config_file
    config = configparser.ConfigParser()
    config.read(config_file)
    name = config['Name']['name']
    global exec_client
    if 'Client' in config:
        exec_client = config['Client']['client']
    command = config['Command']['command']
    cpu_machine_list = config['Machines']['cpu']
    print(cpu_machine_list)
    cpu_machine_list = eval(cpu_machine_list)
    gpu_machine_list = config['Machines']['gpu']
    gpu_machine_list = ast.literal_eval(gpu_machine_list)
    pool_path = config['Pool']['pool_path']
    jobs_path = config['Job_list']['jobs_path']
    machine_list = []
    for k in cpu_machine_list:
        machine_list.append('%02d' % k)
    for k in gpu_machine_list:
        machine_list.append('gpu%02d' % k)
    with open(jobs_path) as f:
        total_jobs = f.readlines()
    if args.strip:
        for idx, x in enumerate(total_jobs):
            total_jobs[idx] = re.sub(r"\.\S*", "", x)
    total_jobs = prepare_jobs(command, total_jobs)
    exec_args = prepare_exec_args(args)
    if 'Client_args' in config:
        exec_args += config['Client_args']['args']
    if args.full_file:
        if args.exe_thread < 0:
            th = 10
        else:
            th = args.exe_thread
        split_jobs(total_jobs, len(machine_list) * th,
                   pool_path=pool_path, prefix=name)
    else:
        split_jobs(total_jobs, len(machine_list),
                   pool_path=pool_path, prefix=name)
    send_jobs(machine_list, name, pool_path=pool_path,
              is_python=(not args.no_python), dry_run=args.try_only, exec_args_in=exec_args)


def prepare_exec_args(args):
    exec_args = ""
    if args.exe_seg > 0:
        exec_args += "-s {} ".format(args.exe_seg)
    if args.exe_thread > 0:
        exec_args += "-t {} ".format(args.exe_thread)
    if args.exe_cap > 0:
        exec_args += "-c {} ".format(args.exe_cap)
    if args.exe_dryrun:
        exec_args += "-d "
    return exec_args


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='dispatch your jobs to machines')
    parser.add_argument('config_file', type=str,
                        help="path to configuration files")
    parser.add_argument('-s', '--strip', action="store_true",
                        help="strip extention names for file list")
    parser.add_argument('-n', '--no_python', action="store_true",
                        help="do not append python before exec_client")
    parser.add_argument('-t', '--try_only', action="store_true",
                        help=" dry run, print command with out running every thing.")
    parser.add_argument('-es', '--exe_seg', type=int,
                        help="exec client segments for updating progress", default=-1)
    parser.add_argument('-et', '--exe_thread', type=int,
                        help='exec thred number', default=-1)
    parser.add_argument('-ec', '--exe_cap', type=int,
                        help="cap the task list to test on small batch.", default=-1)
    parser.add_argument('-ed', '--exe_dryrun', action='store_true',
                        help="print command but do not execute.")
    parser.add_argument('-f', '--full_file', action='store_true',
                        help="send the path to job_file as arguement to command. This is for programs that has long start-up/ quit time, such as matlab.")
    args = parser.parse_args()
    main(args)

'''
    import sys
    filename = sys.argv[1]
    machine_list = [11, 12, 13, 15, 16, 17, 18, 19]
    with open(filename) as f:
        total_jobs = f.readlines()
    command = 'python2 /data/vision/billf/jwu-phys/shape_oneshot/ztzhang/tools/save_depth_exr.py'
    total_jobs = prepare_jobs(command, total_jobs)
    prefix = 'depth'
    split_jobs(total_jobs, len(machine_list), prefix=prefix)
    send_jobs(machine_list, prefix)
'''
