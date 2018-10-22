#!/usr/bin/env python3

from os.path import join


params_h = open('./para/job.params', 'w')
expects_h = open('./para/job.expects', 'w')

out_dir = ''

for i in range(10):
    for j in range(10):
        params_h.write('%d %d\n' % (i, j))

        expects_h.write('%s %s\n' % (
            join(out_dir, '%d_%d_output1.png' % (i, j)),
            join(out_dir, '%d_%d_output2.png' % (i, j)),
        ))

params_h.close()
expects_h.close()
