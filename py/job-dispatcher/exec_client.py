from multiprocessing import Pool
from subprocess import call
import sys
import socket
import argparse
import re
from tqdm import tqdm
hostname = ''
count = None
total = None


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def wrapper(task):
    try:
        s = call(task.strip(), shell=True)
        return [s, task]
    except Exception as e:
        print(str(e))
        sys.std.flush()
        return [str(e), task]


'''
def init(args1, args2):
    global count
    count = args1
    global total
    total = args2
    global hostname
'''


def main(args):
    name = re.search(r'(\w+)\.txt', args.job_file)[1]
    log_file = re.sub(r'\w+\.txt', '{}.log'.format(name), args.job_file)
    if args.full_file:
        tasks = args.job_file
    else:
        with open(args.job_file) as j:
            tasks = j.readlines()
    if args.thread < 0:
        p = Pool()
    else:
        p = Pool(args.thread)
    if args.cap > 0:
        tasks = tasks[0:args.cap]
    max_ = len(tasks)
    hostname = socket.gethostname()
    with open(log_file, 'a') as f:
        f.write(hostname + '\n')
    seg = args.seg
    if args.dryrun:
        for k in tasks:
            print("{}: {}".format(hostname, k))
        return
    try:
        with tqdm(total=int(max_ / seg), desc=hostname) as pbar:
            count = 0
            for i, s in enumerate(p.imap_unordered(wrapper, tasks)):
                if s[0] != 0:
                    with open(log_file, 'a') as f:
                        f.write('{}:  {}\n'.format(s[1], s[0]))
                count += 1
                if count % seg == 0:
                    print('\n')
                    pbar.update()
    except Exception as e:
        pbar.close()
        p.close()
        p.join()
        print(str(e))
        sys.stdout.flush()
        return
    pbar.close()
    p.close()
    p.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('job_file', type=str, help='path to joblist')
    parser.add_argument('-t', '--thread', type=int,
                        help='Number of thread', default=-1)
    parser.add_argument('-s', '--seg', type=int,
                        help="segment number for updating progress bar", default=1)
    parser.add_argument('-c', '--cap', type=int,
                        help="cap the task list to test on small batch.", default=-1)
    parser.add_argument('-d', '--dryrun', action='store_true',
                        help="print command but do not execute.")
    parser.add_argument('-f', '--full_file', action='store_true',
                        help="send the path to job_file as arguement to command. This is for programs that has long start-up/ quit time, such as matlab.")
    args = parser.parse_args()
    main(args)

'''
    with open(sys.argv[1]) as j:
        tasks = j.readlines()
    total = Value('i', len(tasks))
    count = Value('i', 0)
    p = Pool(initializer=init, initargs=(count, total,))
    max_ = len(tasks)
    hostname = socket.gethostname()
    seg = 50
    with tqdm(total=int(max_ / seg), desc=hostname) as pbar:
        count = 0
        for i, _ in enumerate(p.imap_unordered(wrapper, tasks)):
            count += 1
            if count % seg == 0:
                pbar.update()
                print('\n')
    pbar.close()
    p.close()
    p.join()
'''
