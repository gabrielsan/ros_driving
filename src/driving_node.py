#!/usr/bin/env python
import rospy
import roslib
import sys
import serial
import time
from geometry_msgs.msg import Twist
from ds4_driver.msg import Status
from sound_play.libsoundplay import SoundClient
from std_msgs.msg import Float64
from std_msgs.msg import String
from os.path import join, isfile



# configure the serial connection
try:
    ser = serial.Serial('/dev/frontbridge', 115200)

    ser.isOpen()
    print 'Connected to front bridge'

except IOError: # if port is already opened, close it and open it again and print message
    print ("port was already open, closing....")  
    ser.close()
    ser.open() 
    print 'Connected to front bridge'

time.sleep(1)


class Driving_pluto:

    # Intializes everything
    def __init__(self, script_path):

        #  rospy.init_node('Driving')
        rospy.init_node('driving', anonymous=True)

        rospy.on_shutdown(self.cleanup)



        # Set the default TTS voice to use
        self.voice = rospy.get_param("~voice", "voice_don_diphone")
        
        # Set the wave file path if used
        self.wavepath = rospy.get_param("~wavepath", script_path + "/../sounds")
        
        # Create the sound client object
        self.soundhandle = SoundClient()
        
        # Wait a moment to let the client connect to the
        # sound_play server
        rospy.sleep(1)
        
        # Make sure any lingering sound_play processes are stopped.
        self.soundhandle.stopAll()
        
        # Announce that we are ready for input
        self.soundhandle.playWave(self.wavepath + "/R2D2a.wav")
        rospy.sleep(1)
        self.soundhandle.say("Ready", self.voice)

        # publishing to "cmd_vel"

        global pub_vel
      #  global pub_dance
        pub_vel = rospy.Publisher('cmd_vel', Twist, queue_size=2)
      #  pub_dance = rospy.Publisher('dance', String, queue_size=10)
    

        # subscribed to joystick inputs on topic "joy"
        rospy.Subscriber('status', Status, self.callback, queue_size=1)

        rospy.Subscriber("plutotalk", String, self.talk_callback, queue_size=1)

        # starts the node
        rospy.spin()

    def cleanup(self):
        twist = Twist()
        twist.linear.x = 0
        twist.angular.z = 0
        pub_vel.publish(twist)
        rospy.loginfo("Stopping wheels...")

        self.soundhandle.stopAll()
        rospy.loginfo("Shutting down talkback node...")

    def talk_callback(self, data):
        rospy.loginfo('Saying: {}'.format(data.data))
        path = '{}.mp3'.format(join(self.wavepath, 'talk', data.data))
        if isfile(path):
            self.soundhandle.playWave(path)
        else:
            self.soundhandle.say(data.data)

    def callback(self, data):
        twist = Twist()
        linear_factor = 0.35
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
  
        # CROSS say "Excuse me"
        if (data.button_cross == 1):
            self.soundhandle.say("Excuse me", self.voice)
        
        
        # CIRCLE lights ON
        if (data.button_cross == 1):
            ser.write('o\r\n')
            time.sleep(1)

        # TRIANGLE
        if (data.button_triangle == 1):
            ser.write('f\r\n')
            time.sleep(0.5)

         # L1 - kill sound
        if (data.button_l1 == 1):
            self.soundhandle.stopAll()      

        # R1 - stop wheels
        if (data.button_r1 == 1):
            twist.linear.x = 0
            twist.angular.z = 0
            pub_vel.publish(twist)
 

        #Left button PAD by itself

        #PAD - LEFT play "Popcorn"
        if (data.button_dpad_left == 1) and (data.button_square == 0):
            self.soundhandle.playWave(self.wavepath + "/popcorn.mp3")

        #PAD - RIGHT play "Irene Cara - Flashdance"
        if (data.button_dpad_right == -1) and (data.button_square == 0):
            self.soundhandle.playWave(self.wavepath + "/flashdance.mp3")

        #PAD - TOP play "Bee Gees - Stayin Alive"
        if (data.button_dpad_up == 1) and (data.button_square == 0):
            self.soundhandle.playWave(self.wavepath + "/stayin.mp3")

        #PAD - BOTTOM play "The Nolans - I'm in the mood for dancing"
        if (data.button_dpad_down == -1) and (data.button_square == 0):
            self.soundhandle.playWave(self.wavepath + "/dancing.mp3")


        #Left button PAD + SQUARE

        #PAD - LEFT + SQUARE say "Why was the robot angry? Because somebody kept pushing his buttons"
        if (data.button_dpad_left == 1) and (data.button_square == 1):
            self.soundhandle.say("Why was the robot angry? Because somebody kept pushing his buttons", self.voice)

        #PAD - RIGHT + SQUARE say "Hello my name is PLUTO, I'm a Prevas robot"
        if (data.button_dpad_right == 1) and (data.button_square == 1):
            self.soundhandle.say("Hello my name is plutoe,    I'm a Prayvas robot", self.voice)

        #PAD - TOP + SQUARE say ""
        if (data.button_dpad_up == 1) and (data.button_square == 1):
            self.soundhandle.say("Excuse me", self.voice)
                 
        #PAD - BOTTOM + SQUARE say ""
        if (data.button_dpad_down == -1) and (data.buttons[0] == 1):
            self.soundhandle.playWave(self.wavepath + "/oxygene.mp3")

if __name__ == '__main__':

    try:
        Driving_pluto(sys.path[0])
        rospy.spin()
    except rospy.ROSInterruptException:
        rospy.loginfo("Driving node terminated.")

