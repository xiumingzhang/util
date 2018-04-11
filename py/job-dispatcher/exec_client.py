from multiprocessing import Pool
from subprocess import call
from socket import gethostname
from os.path import exists
from argparse import ArgumentParser
from tqdm import tqdm
import logging
import logging_colorer # noqa: F401 # pylint: disable=unused-import

logging.basicConfig(level=logging.INFO)


def wrapper(cmd):
    s = call(cmd.strip(), shell=True)
    return [s, cmd]


def main(args):
    with open(args.cmds_file) as f:
        cmds_all = f.readlines()
    with open(args.expects_file) as f:
        expects_all = f.readlines()

    if args.t < 0:
        p = Pool()
    else:
        p = Pool(args.t)

    if args.c > 0:
        cmds_all = cmds_all[0:args.c]
    cmds = []
    for i, x in enumerate(cmds_all):
        for f in expects_all[i].strip().split(' '):
            if not exists(f):
                cmds.append(x)
                break

    hostname = gethostname()
    log_file = args.cmds_file.replace('.cmds', '.cmds.log')
    with open(log_file, 'a') as f:
        f.write("Host: %s\n\n" % hostname)

    if args.d:
        for x in cmds:
            logging.info("(%s) %s", hostname, x)
        return

    with tqdm(total=int(len(cmds) / args.e), desc=hostname) as pbar:
        cnt = 0
        for i, s in enumerate(p.imap_unordered(wrapper, cmds)):
            if s[0] != 0:
                with open(log_file, 'a') as f:
                    f.write('{}: {}\n'.format(s[1], s[0]))
            cnt += 1
            if cnt % args.e == 0:
                pbar.update()

    pbar.close()
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
