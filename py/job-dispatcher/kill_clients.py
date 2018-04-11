from subprocess import call, check_output, Popen, PIPE

cpu_machines = ['vision%02d' % e for e in range(1, 39)]
gpu_machines = ['visiongpu%02d' % e for e in range(1, 21)]
machine_names = cpu_machines + gpu_machines


def kill(machine_name):
    if machine_name == check_output('hostname').decode().strip('\n'):
        # Can't kill this machine
        return
    if call('timeout 0.5 ping -c1 %s' % machine_name, shell=True) == 0:
        is_found = False
        ps = Popen('ssh -o PasswordAuthentication=no -t %s "ps a -u xiuming x | grep exec_client"' %
                   machine_name, stdout=PIPE, shell=True).communicate()[0].decode()
        ps = ps.split('\n')
        print(ps)
        for p in ps:
            if len(p) < 3:
                continue
            status = p.split(None, 5)
            print(status)
            if status[1] == '?' and 'S' in status[2]:
                pid = status[0]
                is_found = True
                break
        if is_found:
            print("found client!")
            call('ssh -o PasswordAuthentication=no -t %s kill -9 %s' %
                 (machine_name, pid), shell=True)


if __name__ == '__main__':
    for x in machine_names:
        kill(x)
