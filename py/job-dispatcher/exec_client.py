from os.path import exists
from shlex import split
from multiprocessing import Pool
from subprocess import Popen
from socket import gethostname
from argparse import ArgumentParser
from tqdm import tqdm


sepline = ''.join(["*"] * 50)


def job(job_args):
    cmd, out_log, err_log = job_args
    with open(out_log, 'w') as out_h, open(err_log, 'w') as err_h:
        child = Popen(split(cmd), stdout=out_h, stderr=err_h)
    _, _ = child.communicate() # wait for finishing
    return cmd


def main(args):
    with open(args.cmds_file) as f:
        cmds_all = f.readlines()
    with open(args.expects_file) as f:
        expects_all = f.readlines()

    # Number of workers
    if not args.d:
        if args.t < 0:
            p = Pool()
        else:
            p = Pool(args.t)

    # Run only the first N jobs?
    if args.c > 0:
        cmds_all = cmds_all[0:args.c]

    # Decide which commands to run according to what to expect
    # and what already exists
    job_args = []
    for i, cmd in enumerate(cmds_all):
        cmd = cmd.strip()
        out_log = args.cmds_file + '%09d.out' % i
        err_log = args.cmds_file + '%09d.err' % i
        for f in expects_all[i].strip().split(' '):
            if not exists(f):
                job_args.append((cmd, out_log, err_log))
                # Found one file missing, need to re-run this job
                break

    # Dry run?
    hostname = gethostname()
    if args.d:
        for (cmd, _, _) in job_args:
            print("(%s) %s" % (hostname, cmd))
        return

    # Send jobs to p
    with tqdm(total=int(len(job_args) / args.e), desc=hostname) as pbar:
        cnt = 0
        for i, _ in enumerate(p.imap_unordered(job, job_args)):
            cnt += 1
            if cnt % args.e == 0:
                pbar.update()

    p.close()
    p.join()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('cmds_file', type=str, help="path to cmds_file")
    parser.add_argument('expects_file', type=str, help="path to expects_file")
    parser.add_argument('-t', type=int,
                        help="number of threads per machine", default=-1)
    parser.add_argument('-e', type=int,
                        help="every N tasks to update progress bar once", default=1)
    parser.add_argument('-c', type=int,
                        help="cap the task list to test on small batches", default=-1)
    parser.add_argument('-d', action='store_true',
                        help="print command without executing")
    main(parser.parse_args())
