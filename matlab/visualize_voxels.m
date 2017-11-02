function visualize_voxels(voxels, varargin)
% Visualize voxels
%
% Args:
%     voxels: X-by-Y-by-Z array of 0's and 1's or floats
%     thres: threshold; optional (default: 0.5)

% Inputs
if isempty(varargin)
    thres = 0.5;
else
    if length(varargin) == 1
        thres = varargin{1};
    else
        error('Only one optional parameter (thres) is accepted');
    end
end

% Standardize dimensions
if ndims(voxels) ~= 3
    error('Input voxels must be 3D');
end

ind = find(voxels > thres);
[xs, ys, zs] = ind2sub(size(voxels), ind);
scatter3(xs, ys, zs, 'filled');
axis equal;
xlabel('x');
ylabel('y');
zlabel('z');
view(-90, 0);