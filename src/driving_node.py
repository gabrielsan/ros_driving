#!/usr/bin/env python
import rospy
import roslib
import sys
import serial
import time
from geometry_msgs.msg import Twist
from ds4_driver.msg import Status
from std_msgs.msg import Float64
from std_msgs.msg import String
from os.path import join, isfile


time.sleep(1)


class Driving_pluto:

    # Intializes everything
    def __init__(self, script_path):

        #  rospy.init_node('Driving')
        rospy.init_node('driving', anonymous=True)

        rospy.on_shutdown(self.cleanup)


        global pub_vel
        pub_vel = rospy.Publisher('cmd_vel', Twist, queue_size=2)
      #  pub_dance = rospy.Publisher('dance', String, queue_size=10)
    

        # subscribed to joystick inputs on topic "joy"
        rospy.Subscriber('status', Status, self.callback, queue_size=1)

        # starts the node
        rospy.spin()

    def cleanup(self):
        twist = Twist()
        twist.linear.x = 0
        twist.angular.z = 0
        pub_vel.publish(twist)
        rospy.loginfo("Stopping wheels...")
        rospy.loginfo("Shutting down talkback node...")

    def callback(self, data):
        twist = Twist()
        linear_factor = 0.2
        angular_factor = 0.5
        speed_factor = 1
        forward_cntrl = 1
        reverse_cntrl = 1
 
        reverse_cntrl = (data.axis_l2)
        forward_cntrl = (data.axis_r2)
        twist.linear.x = (forward_cntrl - reverse_cntrl)*linear_factor
        #twist.linear.x = (data.axis_left_y)*linear_factor
        twist.angular.z = (angular_factor*data.axis_left_x)
        
        pub_vel.publish(twist)
  
        # R1 - stop wheels
        if (data.button_r1 == 1):
            twist.linear.x = 0
            twist.angular.z = 0
            pub_vel.publish(twist)

if __name__ == '__main__':
    try:
        Driving_pluto(sys.path[0])
        rospy.spin()
    except rospy.ROSInterruptException:
        rospy.loginfo("Driving node terminated.")

