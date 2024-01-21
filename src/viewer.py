from logging import getLogger

import matplotlib.pyplot as plt
import tensorflow as tf
from matplotlib.patches import Rectangle
from mpl_toolkits.mplot3d import Axes3D

from src.logger import LoggingClass


class Vizualizer(LoggingClass):
    def __init__(self, logger: getLogger = None, **kw_args):
        super().__init__(logger, **kw_args)

    def vizualize(self, image, detections, poses3d, poses2d, edges):
        image = tf.image.decode_jpeg(tf.io.read_file(image))
        fig = plt.figure(figsize=(10, 5.2))
        image_ax = fig.add_subplot(1, 2, 1)
        image_ax.imshow(image)
        for x, y, w, h in detections[:, :4]:
            image_ax.add_patch(Rectangle((x, y), w, h, fill=False))

        pose_ax = fig.add_subplot(1, 2, 2, projection='3d')
        pose_ax.view_init(5, -85)
        pose_ax.set_xlim3d(-1500, 1500)
        pose_ax.set_zlim3d(-1500, 1500)
        pose_ax.set_ylim3d(0, 3000)

        # Matplotlib plots the Z axis as vertical, but our poses have Y as the vertical axis.
        # Therefore, we do a 90° rotation around the X axis:
        poses3d[..., 1], poses3d[..., 2] = poses3d[..., 2], -poses3d[..., 1]
        for pose3d, pose2d in zip(poses3d, poses2d):
            for i_start, i_end in edges:
                image_ax.plot(*zip(pose2d[i_start], pose2d[i_end]), marker='o', markersize=2)
                pose_ax.plot(*zip(pose3d[i_start], pose3d[i_end]), marker='o', markersize=2)
            image_ax.scatter(*pose2d.T, s=2)
            pose_ax.scatter(*pose3d.T, s=2)

        fig.tight_layout()
        plt.show()
        return fig
