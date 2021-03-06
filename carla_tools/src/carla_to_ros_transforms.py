#!/usr/bin/env python2

from __future__ import print_function, division, absolute_import
import rospy
from sensor_msgs.msg import Imu, PointCloud2
import numpy as np
import math
import tf.transformations
from transform_helper import carla_to_ros, ros_to_rovio, ros_to_loam


class CarlaImuRovioTransform:
    def __init__(self, node_name="carla_to_ros_transforms"):
        rospy.init_node(node_name)
        self.imu_sub = rospy.Subscriber("~imu/carla", Imu, callback=self.imu_listener)
        self.rovio_pub = rospy.Publisher("~imu/rovio", Imu, queue_size=1)
        self.loam_pub = rospy.Publisher("~imu/loam", Imu, queue_size=1)
        self.ros_pub = rospy.Publisher("~imu/ros", Imu, queue_size=1)
        self.velodyne_pub = rospy.Publisher("~imu/velodyne", Imu, queue_size=1)

        self.lidar_sub = rospy.Subscriber("~lidar/carla", PointCloud2, callback=self.lidar_callback)
        self.lidar_pub = rospy.Publisher("~lidar/loam", PointCloud2, queue_size=1)




    def imu_listener(self, carla_msg):
        """
        The Carla convention is left-handed:
         x: Forward
         y: Right
         z: Up

        The ROS convention is right-handed:
         x: Forward
         y: Left
         z: Up

        The Rovio convention is right-handed:
         x: Right
         y: Down
         z: Forward

        LOAM convention is right-handed:
         x: Left
         y: Up
         z: Forward
        """

        ros_msg = self.imu_transform(carla_msg, carla_to_ros, from_left_hand=True)
        self.ros_pub.publish(ros_msg)


        rovio_msg = self.imu_transform(ros_msg, ros_to_rovio)
        self.rovio_pub.publish(rovio_msg)


        loam_msg = self.imu_transform(ros_msg, ros_to_loam)
        self.loam_pub.publish(loam_msg)



    def lidar_callback(self, msg):
        """
        Parameters
        ----------
        msg: PointCloud2
        """
        data = np.reshape(np.fromstring(msg.data, dtype=np.float32), [-1, 3])
        data = np.concatenate((-data[:, 1:2], data[:, 0:1], data[:, 2:3]), axis=1)
        #data = np.concatenate((data[:, 1:2], data[:, 2:3], data[:, 0:1]), axis=1)
        msg.data = data.tostring()
        self.lidar_pub.publish(msg)

if __name__ == "__main__":
    node = CarlaImuRovioTransform()
    rospy.spin()
