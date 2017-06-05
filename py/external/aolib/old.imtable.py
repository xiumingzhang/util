  
# def make_video(out_fname, ims, fps, tmp_ext = '.ppm', sound = None):
#   assert tmp_ext.startswith('.')
#   in_dir = ut.make_temp_dir_big()
#   # for i, x in enumerate(ims):
#   #   # pad to be even
#   #   if x.shape[0] % 2 == 1 or x.shape[1] % 2 == 1:
#   #     x = ig.pad_corner(x, x.shape[1] % 2, x.shape[0] % 2)
#   #   ig.save(ut.pjoin(in_dir, 'ao-video-frame%05d%s' % (i, tmp_ext)), x)

#   ut.parmap(make_video_helper, 
#             [(i, x, in_dir, tmp_ext) for i, x in enumerate(ims)])
    
#   #cmd = 'ffmpeg -loglevel warning -f image2 -r %f -i %s/ao-video-frame%%05d%s -pix_fmt yuv420p -vcodec h264 -acodec aac -strict 2 -y %s' % (fps, in_dir, tmp_ext, out_fname)
  
#   if sound is None:
#     sound_flags = ''
#   else:
#     sound_flags = '-i "%s"' % sound

#   cmd = ('ffmpeg -loglevel warning -f image2 -r %f -i %s/ao-video-frame%%05d%s %s '
#          '-pix_fmt yuv420p -vcodec h264 -acodec aac -strict -2 -y %s') % (fps, in_dir, tmp_ext, sound_flags, out_fname)

#   # try to make it work well in keynote (hack)
#   #cmd = 'ffmpeg -r %f -i %s/ao-video-frame%%05d%s -y -qscale:v 0 %s' % (fps, in_dir, tmp_ext, out_fname)
#   print cmd
#   #print cmd
#   os.system(cmd)
  
#   #os.system('ffmpeg -f image2 -r %f -i %s/ao-video-frame%%05d%s -pix_fmt yuv420p -vcodec h264 -acodec aac -strict 2 -y %s' % (fps, in_dir, tmp_ext, out_fname))
#   #os.system('ffmpeg -f image2 -r %f -i %s/ao-video-frame%%05d%s -pix_fmt yuv420p -vcodec h264 -acodec aac -strict 2 -y %s' % (fps, in_dir, tmp_ext, out_fname))

#   if 0:
#     print 'HACK'
#   else:
#     for x in glob.glob(ut.pjoin(in_dir, 'ao-video-frame*%s' % tmp_ext)):
#       os.remove(x)
#     os.rmdir(in_dir)
  
#   #os.system('ffmpeg -f image2 -r %f -i %s/ao-video-frame%%05d.png -vcodec mpeg4 -y %s' % (fps, in_dir, out_fname))
#   #os.system('ffmpeg -i %s/ao-video-frame%%05d.png -b 1500k -vcodec libx264 -vpre slow -vpre baseline -g 30 "%s"' % (in_dir, out_fname))
#   #os.system('ffmpeg -f image2 -r %f -i %s/ao-video-frame%%05d.png -b 1500k -vcodec libx264  -g 30 "%s"' % (fps, in_dir, out_fname))
#   #os.system('ffmpeg -f image2 -r %f -i %s/ao-video-frame%%05d.png -vcodec libx264 -y %s' % (fps, in_dir, out_fname))

#   # convert to another video format first for some reason
#   #tmp_fname = ut.make_temp('.mp4')
#   #tmp_fname = ut.make_temp('.mkv')
#   #os.system('ffmpeg -f image2 -r %f -i %s/ao-video-frame%%05d.png -vcodec mpeg4 -y %s' % (fps, in_dir, tmp_fname))
#   #os.system('ffmpeg -i %s -vcodec libx264 -y %s' % (tmp_fname, out_fname))
#   #os.system('ffmpeg -i %s -qscale 0 -vcodec libx264 -y %s' % (tmp_fname, out_fname))
#   # os.system(('ffmpeg -f image2 -r %f -i %s/ao-video-frame%%05d.png -vcodec mpeg4 '\
#   #            + '-mbd rd -flags +mv4+aic -trellis 2 -cmp 2 -subcmp 2 -g 300  -y %s') % (fps, in_dir, tmp_fname))
#   # os.system('ffmpeg -i %s -qscale 0 -vcodec libx264 -mbd rd -flags +mv4+aic -trellis 2 -cmp 2 -subcmp 2 -g 300 -y %s' % (tmp_fname, out_fname))

#   #os.system(('ffmpeg -f image2 -r %f -i %s/ao-video-frame%%05d.png -vcodec mpeg4 -crf 0 %s') % (fps, in_dir, tmp_fname))
#   #os.system(('ffmpeg -f image2 -r %f -i %s/ao-video-frame%%05d.png -vcodec huffyuv -y %s') % (fps, in_dir, tmp_fname))
#   #tmp_fname = '/tmp/ao_s0olXg.mkv'
#   #os.system('ffmpeg -i %s -vcodec libx264 -crf 0 -y %s' % (tmp_fname, out_fname))
#   #os.system('ffmpeg -i %s -vcodec libx264 -crf -b 250k -bt 50k -acodec libfaac -ab 56k -ac 2 -y %s' % (tmp_fname, out_fname))

#   # if 0:
#   #   # needs -pix_fmt yuv420p flag
#   #   os.system('ffmpeg -i %s -pix_fmt yuv420p -vcodec h264 -acodec aac -strict 2 -y %s' % (tmp_fname, out_fname))

#   # os.system('ffmpeg -f image2 -r %f -i %s/ao-video-frame%%05d.png -pix_fmt yuv420p -vcodec h264 -acodec aac -strict 2 -y %s' % (fps, in_dir, out_fname))

#   # print tmp_fname
#   # if 0:
#   #   os.remove(tmp_fname)
