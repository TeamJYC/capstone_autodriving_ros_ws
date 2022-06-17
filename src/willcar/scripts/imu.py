#!/usr/bin/env python

from termios import VSWTCH
import rospy
import smbus
import math
from math import sin, cos, pi
import time
import tf


from atexit import register
from bitstring import Bits
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Point, Pose, Quaternion, Twist, Vector3



bus = smbus.SMBus(1)
DEV_ADDR = 0x68




def read_data(register) : 
    high = bus.read_byte_data(DEV_ADDR, register)
    low = bus.read_byte_data(DEV_ADDR, register+1)
    val = (high << 8) + low
    return val

def twocomplements(val) : 
    s = Bits(uint=val, length=16)
    return s.int 

def dist(a,b):
    return math.sqrt((a*a)+(b*b))

def gyro_dps(val) :
    sensitive_gyro = 131.0
    return twocomplements(val)/sensitive_gyro

def get_yaw(x,y,z):
    radians = math.atan(z/dist(x,y))
    return radians
def listener():
    rospy.init_node('imu_node', anonymous=True)
    odom_pub = rospy.Publisher("odom",Odometry, queue_size=50)
    odom_broadcaster = tf.TransformBroadcaster()



    register_gyro_xout_h = 0x43
    register_gyro_yout_h = 0x45
    register_gyro_zout_h = 0x47    

    register_accel_xout_h = 0x3B
    register_accel_yout_h = 0x3D
    register_accel_zout_h = 0x3F

    pos_x = 0.0
    pos_y = 0.0
    pos_th = 0.0

    vX = 0.1
    vY = -0.1
    vth = 0.1

    PI = 3.14

    gyro_x_ = 0.0
    gyro_y_ = 0.0
    gyro_z_ = 0.0
    
 


    while not rospy.is_shutdown() :
            last = rospy.Time.now()
            current = rospy.Time.now()

            dt = (current - last).to_sec()

            bus.write_byte_data(DEV_ADDR, 0x6B, 0b00000000)
    
            x = read_data(register_accel_xout_h)/16384.0
            y = read_data(register_accel_yout_h)/16384.0

            gyro_x = read_data(register_gyro_xout_h)
            gyro_y = read_data(register_gyro_yout_h)
            gyro_z = read_data(register_gyro_zout_h)
            vth = vth + (PI*(gyro_dps(gyro_z)*dt)/180)

            print(vth)

            gyro_x_ = gyro_x_ + gyro_x  
            gyro_y_ = gyro_y_ + gyro_y  
            gyro_z_ = gyro_z_ + gyro_z  
        

            rospy.loginfo(x)
            rospy.loginfo(dt)
            rospy.loginfo(vX)

            vX = vX + x*dt
            
            delta_x = (vX * cos(pos_th) - vY * sin(pos_th)) * dt
            delta_y = (vX * sin(pos_th) + vY * cos(pos_th)) * dt
            delta_th = vth * dt

            pos_x = pos_x + delta_x
            pos_y = pos_y + delta_y
            th = th + delta_th
 
            odom_quat = tf.transformations.quaternion_from_euler(gyro_x_, gyro_y_, gyro_z_)
            current_time = rospy.Time.now()
            

            odom_broadcaster.sendTransform(
                    (pos_x, pos_y, 0),
                    odom_quat,
                    current_time,
                    "base_footprint",
                    "odom"
            )


            odom = Odometry()
            odom.header.stamp = current_time
            odom.header.frame_id = "odom"

            odom.pose.pose = Pose(Point(pos_x,pos_y,0.), Quaternion(*odom_quat))

            odom.child_frame_id = "base_footprint"
            odom.twist.twist = Twist(Vector3(vX, vY, 0), Vector3(0, 0, vth))

            odom_pub.publish(odom)
            
    rospy.spin()
if __name__ == '__main__':
    listener()
