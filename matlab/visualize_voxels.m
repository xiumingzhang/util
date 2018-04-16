function visualize_voxels(voxels, varargin)
% Visualize voxels
%
% Args:
%     voxels: X-by-Y-by-Z array of 0's and 1's or floats
%     thres: threshold; optional (default: 0.2)

% Inputs
if isempty(varargin)
    thres = 0.2;
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

axes = scatter3(xs, ys, zs, 'filled');

res = size(voxels);
set(gca, 'XLimMode', 'manual', 'XLim', [1, res(1)]);
set(gca, 'YLimMode', 'manual', 'YLim', [1, res(2)]);
set(gca, 'ZLimMode', 'manual', 'ZLim', [1, res(3)]);
axis equal;

xlabel('x');
ylabel('y');
zlabel('z');

view(45, 45);