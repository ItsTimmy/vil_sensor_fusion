#!/usr/bin/env python3

"""
The KITTI dataset uses the Velodyne HDL-64E. This project uses the VLP-16 (Or simulated equivalent).

This node takes in a PointCloud2 message, downsamples the points (just discards some points, no interpolation is done),
and outputs a new PointCloud2 message.

Subscriptions:
 - ~input: PointCloud2 raw data

Publications:
 - ~output: PointCloud2 downsampled

Params:
 - ~channels: Number of channels from the input lidar data
 - ~vert_downsample: Keep only every this many points in the vertical (channel) direction. E.g., vert_downsample=4
                     keeps only 1 out of every 4 channels
 - ~horiz_downsample: Keep only every this many points in the horizontal (spinning) direction
"""

import rospy
import numpy as np
import message_filters
from sensor_msgs.msg import PointCloud2


class PointcloudDownsampler:

    def __init__(self, node_name="pointcloud_downsampler"):
        rospy.init_node(node_name)

        # Default values for downsampling Velodyne HDL-64E from KITTI to VLP-16
        self.channels = rospy.get_param("~channels", default=64)
        self.vert_downsample = rospy.get_param("~vert_downsample", default=4)
        self.horiz_downsample = rospy.get_param("~horiz_downsample", default=2)
        self.time_downsample = rospy.get_param("~time_downsample", default=1)
        self.transpose = rospy.get_param("~transpose", default=False)

        self.input = rospy.Subscriber("~input", PointCloud2, callback=self.callback)
        self.output = rospy.Publisher("~output", PointCloud2, queue_size=1)

    def callback(self, msg: PointCloud2):
        if msg.header.seq % self.time_downsample == 0:
            point_length = msg.point_step // 4
            data = np.reshape(np.fromstring(msg.data, dtype=np.float32), [-1, point_length])
            # Truncate data to round to a multiple of 64 points
            num_points = self.channels * (data.shape[0] // self.channels)
            data = data[0:num_points, :]
            if self.transpose:
                data = np.reshape(data, [-1, self.channels, point_length])
                data = data.transpose((1, 0, 2))
                # msg.header.stamp = rospy.Time.now()
            else:
                data = np.reshape(data, [self.channels, -1, point_length])

            # print("Height: {}, Width: {}, Shape: {}".format(msg.height, msg.width, data.shape))
            downsampled_data = data[::self.vert_downsample, ::self.horiz_downsample, :]
            downsampled_data = np.reshape(downsampled_data, [-1, point_length])
            msg.data = downsampled_data.tostring()
            msg.width = downsampled_data.shape[0]
            self.output.publish(msg)


if __name__ == "__main__":
    node = PointcloudDownsampler()
    rospy.spin()
