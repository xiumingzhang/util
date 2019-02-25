from os.path import exists
from shlex import split
from multiprocessing import Pool
from subprocess import Popen, PIPE
from socket import gethostname
from argparse import ArgumentParser
from tqdm import tqdm

sepline = ''.join(["*"] * 50)


def wrapper(cmd):
    child = Popen(split(cmd.strip()), stdout=PIPE, stderr=PIPE)
    out, err = child.communicate()
    out = out.decode()
    err = err.decode()
    if out is not None:
        out = [x + "\n" for x in out.split('\n')]
    if err is not None:
        err = [x + "\n" for x in err.split('\n')]
    return (cmd, out, err)


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
    cmds = []
    for i, x in enumerate(cmds_all):
        for f in expects_all[i].strip().split(' '):
            if not exists(f):
                cmds.append(x)
                # Found one file missing, need to re-run this job
                break

    # Dry run?
    hostname = gethostname()
    if args.d:
        for x in cmds:
            print("(%s) %s" % (hostname, x))
        return

    # Log files
    out_log = args.cmds_file.replace('.cmds', '.cmds.out')
    err_log = args.cmds_file.replace('.cmds', '.cmds.err')
    with open(out_log, 'w') as oh, open(err_log, 'w') as eh:
        oh.write("Host: %s\n\n" % hostname)
        eh.write("Host: %s\n\n" % hostname)

    # Send jobs to p
    with tqdm(total=int(len(cmds) / args.e), desc=hostname) as pbar:
        cnt = 0
        for i, (cmd, out, err) in enumerate(
                p.imap_unordered(wrapper, cmds)
        ):
            with open(out_log, 'a') as oh, open(err_log, 'a') as eh:
                oh.write(sepline + "\n\n")
                eh.write(sepline + "\n\n")
                oh.write(cmd + "\n")
                eh.write(cmd + "\n")
                oh.writelines(out)
                eh.writelines(err)
                oh.write("\n\n" + sepline + "\n\n")
                eh.write("\n\n" + sepline + "\n\n")
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
