#!/usr/bin/env python
import rospy
import roslib
import dynamixel_controllers
import serial
import time
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Joy
from std_msgs.msg import Float64

    # configure the serial connection
try:
       ser = serial.Serial('/dev/ttyUSB0', 115200)

       ser.isOpen()
       print 'Connected to rangefinder'

except IOError: # if port is already opened, close it and open it again and print message
       print ("port was already open, closing....")  
       ser.close()
       ser.open() 
       print 'Connected to rangefinder'

time.sleep(1)

def callback(data):
    twist = Twist()
    linear_factor = 1
    angular_factor = 1.5
    speed_factor = 1
    forward_cntrl = 1
    reverse_cntrl = 1
    dist_reading = 1


    ser.write('d\r\n')
    out = ''

    rospy.sleep(0.05)

    while ser.inWaiting() > 0:
       out += ser.read(1)

    if out !='':
       print repr(out)
       dist_reading =float(out)/200
       print "Distance : " + str (dist_reading)
  
    # vertical left stick axis = linear rate

    if (data.buttons[6]) == 1:
       reverse_cntrl = (data.axes[3])

    if (data.buttons[7]) == 1:
       forward_cntrl = (data.axes[4])

    print "axis3:  " + str(reverse_cntrl) + "         axis4:  " + str(forward_cntrl)
    
    twist.linear.x = (forward_cntrl - reverse_cntrl)*-linear_factor*dist_reading

    # horizontal left stick axis = turn rate
    twist.angular.z = (angular_factor*data.axes[0])*(1-abs((data.axes[4] - data.axes[3])/speed_factor))

  
    print "Angular velocity:  " + str(twist.angular.z) + "         Linear velocity:  " + str(twist.linear.x)

    pub_vel.publish(twist)
    pub_head_pan.publish(data.axes[2])
    pub_head_tilt.publish((data.axes[5])*-2)
#    pub_head_pan.publish((data.axes[9])*2)
#    pub_head_tilt.publish((data.axes[7])*2)


# Intializes everything

def start():




    # publishing to "cmd_vel"
    global pub_vel, pub_head_pan, pub_head_tilt
    pub_vel = rospy.Publisher('cmd_vel', Twist, queue_size=10)
    pub_head_pan = rospy.Publisher('head_pan_joint/command', Float64, queue_size=10)
    pub_head_tilt = rospy.Publisher('head_tilt_joint/command', Float64, queue_size=10)

    #  rospy.init_node('Driving')
    rospy.init_node('driving', anonymous=True)

    # subscribed to joystick inputs on topic "joy"
    rospy.Subscriber("joy", Joy, callback, queue_size=1)
    # starts the node
    rospy.spin()

if __name__ == '__main__':
    start()

