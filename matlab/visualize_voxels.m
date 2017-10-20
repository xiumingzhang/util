function visualize_voxels(voxels)

ind = find(voxels == 1);
[xs, ys, zs] = ind2sub(size(voxels), ind);
scatter3(xs, ys, zs, 'filled');

axis equal;
xlabel('x');
ylabel('y');
zlabel('z');