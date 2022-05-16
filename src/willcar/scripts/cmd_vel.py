#!/usr/bin/env python


import rospy
import smbus
import math
import time
from geometry_msgs.msg import Twist

PI = 3.1415926535897

class YB_Pcb_Car(object):

    def get_i2c_device(self, address, i2c_bus):
        self._addr = address
        if i2c_bus is None:
            return smbus.SMBus(1)
        else:
            return smbus.SMBus(i2c_bus)

    def __init__(self):
        # Create I2C device.
        self._device = self.get_i2c_device(0x16, 1)

    def write_u8(self, reg, data):
        try:
            self._device.write_byte_data(self._addr, reg, data)
        except:
            print ('write_u8 I2C error')

    def write_reg(self, reg):
        try:
            self._device.write_byte(self._addr, reg)
        except:
            print ('write_u8 I2C error')

    def write_array(self, reg, data):
        try:
            # self._device.write_block_data(self._addr, reg, data)
            self._device.write_i2c_block_data(self._addr, reg, data)
        except:
            print ('write_array I2C error')

    def Ctrl_Car(self, l_dir, l_speed, r_dir, r_speed):
        try:
            reg = 0x01
            data = [l_dir, l_speed, r_dir, r_speed]
            self.write_array(reg, data)
        except:
            print ('Ctrl_Car I2C error')
            
    def Control_Car(self, speed1, speed2):
        try:
            if speed1 < 0:
                dir1 = 0
            else:
                dir1 = 1
            if speed2 < 0:
                dir2 = 0
            else:
                dir2 = 1 
            
            self.Ctrl_Car(dir1, int(math.fabs(speed1)), dir2, int(math.fabs(speed2)))
        except:
            print ('Ctrl_Car I2C error')


    def Car_Run(self, speed1, speed2):
        try:
            self.Ctrl_Car(1, speed1, 1, speed2)
        except:
            print ('Car_Run I2C error')

    def Car_Stop(self):
        try:
            reg = 0x02
            self.write_u8(reg, 0x00)
        except:
            print ('Car_Stop I2C error')

    def Car_Back(self, speed1, speed2):
        try:
            self.Ctrl_Car(0, speed1, 0, speed2)
        except:
            print ('Car_Back I2C error')

    def Car_Left(self, speed1, speed2):
        try:
            self.Ctrl_Car(0, speed1, 1, speed2)
        except:
            print ('Car_Spin_Left I2C error')

    def Car_Right(self, speed1, speed2):
        try:
            self.Ctrl_Car(1, speed1, 0, speed2)
        except:
            print ('Car_Spin_Left I2C error')

    def Car_Spin_Left(self, speed1, speed2):
        try:
            self.Ctrl_Car(0, speed1, 1, speed2)
        except:
            print ('Car_Spin_Left I2C error')

    def Car_Spin_Right(self, speed1, speed2):
        try:
            self.Ctrl_Car(1, speed1, 0, speed2)
        except:
            print ('Car_Spin_Right I2C error')

    def Ctrl_Servo(self, id, angle):
        try:
            reg = 0x03
            data = [id, angle]
            if angle < 0:
                angle = 0
            elif angle > 180:
                angle = 180
            self.write_array(reg, data)
        except:
            print ('Ctrl_Servo I2C error')

def subscribe_topic_message(data):
    car = YB_Pcb_Car()

    linear_pwm_X = int(data.linear.x * 100) # 0.5m/s = 50 pwm [Hz]
    angle_pwm = int(data.angular.z*360/(2*PI))

    if linear_pwm_X <= 30 and linear_pwm_X >= 10:
        linear_pwm_X = 30
        car.Car_Run(linear_pwm_X, linear_pwm_X)
        time.sleep(2)
        car.Car_Stop()

        print("linear_pwm_X")
        print(linear_pwm_X)

    elif linear_pwm_X > 30 :
        car.Car_Run(linear_pwm_X, linear_pwm_X)
        time.sleep(2)
        car.Car_Stop()

        print("linear_pwm_X")
        print(linear_pwm_X)
        

    if angle_pwm <= 180 and angle_pwm >= 30 :
        angle_pwm = 50
        car.Car_Right(angle_pwm, 0)
        time.sleep(2)
        car.Car_Stop()

        print("angle_pwm")
        print(angle_pwm)

    if angle_pwm >= 210 and angle_pwm <= 360 :
        angle_pwm = 50
        car.Car_Left(0, angle_pwm)
        time.sleep(2)
        car.Car_Stop()

        print("angle_pwm")
        print(angle_pwm)

   
    
    

    # Car_Run 
    # car.Car_Run(linear_pwm_X, linear_pwm_X)
    # time.sleep(2)
    # car.Car_Stop()

    # Car_Back
    #car.Car_Back(150, 150) 
    #time.sleep(2)
    #car.Car_Stop()

    # Car_left
    # car.Car_Left(0, angle_pwm_X)
    # time.sleep(2)
    # car.Car_Stop()

    # Car_Right

    # Car_Spin_Left
    #car.Car_Spin_Left(150, 150)
    #time.sleep(2)
    #car.Car_Stop()

    # Car_Spin_Right
    #car.Car_Spin_Right(150, 150)
    #time.sleep(2)
    #car.Car_Stop()

def listener():
    rospy.init_node('cmd_vel_node', anonymous=True)
    rospy.Subscriber('/cmd_vel', Twist, subscribe_topic_message)
    rospy.spin()

if __name__ == '__main__':
    listener()
