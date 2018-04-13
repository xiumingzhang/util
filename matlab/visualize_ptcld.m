function visualize_ptcld(pts, varargin)
% Visualize a point cloud
%
% Args:
%     pts: N-by-3 or 3-by-N array of floats
%     ss: scatter size; optional (default: 5)

% Inputs
if isempty(varargin)
    ss = 5;
else
    if length(varargin) == 1
        ss = varargin{1};
    else
        error('Only one optional parameter (ss) is accepted');
    end
end

% Standardize dimensions
if size(pts, 2) == 3
    disp('Assuming N-by-3');
elseif size(pts, 1) == 3
    disp('Assuming 3-by-N');
    pts = pts.';
else
    error('One of the two dimensions must be 3');
end

scatter3(pts(:, 1), pts(:, 2), pts(:, 3), ss, 'filled');

axis equal;

xlabel('x');
ylabel('y');
zlabel('z');

view(45, 45);