function extract_frames(videof, out_dir, step_size, out_len, zero_idx)
% Extract frames from a video
%
% Args:
%     videof: video path
%     out_dir: output directory
%     step_size: step size for extracting frames (default: 1)
%     out_len: length of output names (zero padding; default: 9)
%     zero_idx: whether to use zero indexing for output names (default: true)

if ~exist('step_size', 'var')
    step_size = 1;
end
if ~exist('out_len', 'var')
    out_len = 9;
end
if ~exist('zero_idx', 'var')
    zero_idx = true;
end

if ~exist(out_dir, 'dir')
    mkdir(out_dir);
end

v = VideoReader(videof);

fi = 1;
if zero_idx
    fname = fi - 1;
else
    fname = fi;
end

fmt = sprintf('%%0%dd', out_len);

while hasFrame(v)
    frame = readFrame(v);
    fpath = fullfile(out_dir, [sprintf(fmt, fname) '.png']);
    if mod(fi, step_size) == 0
        imwrite(frame, fpath);
        fname = fname+1;
    end
    fi = fi+1;
end