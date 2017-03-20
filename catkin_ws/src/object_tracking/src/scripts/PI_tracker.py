#!/usr/bin/env python

# publisher + subscriber that reads position msgs from
# camera and calculates movement

# Intro to Robotics - EE5900 - Spring 2017
#          Assignment #6

#       Project #6 Group #2
#            prithvi
#            Aswin
#        Akhil (Team Lead)
#
# Revision: v1.2

# define imports
import rospy
import std_msgs

from geometry_msgs.msg import Twist
from geometry_msgs.msg import Vector3
from object_tracking.msg import position

# global variables
global ang_control
global lin_control
global val_recieved

ang_control = 0.0
lin_control = 0.0
val_recieved = False


# define controller class
class Controller:

    # define init
    def __init__(self):
        # Detect position from OpenCV
        rospy.Subscriber('custom_chatter', position, self.callback)
        rospy.spin()

    # define callback
    def callback(self, data):
        global ang_control
        global lin_control
        global val_recieved

        # set value recieved flag
        val_recieved = True

        #reference = 0
        #P = 0.001

        ref_pos  = rospy.get_param("/P_control/ref_pos") #needs a point and a size
        ref_size = rospy.get_param("/P_control/ref_size")
        P_ang = rospy.get_param("/P_control/P_ang") #angular proportional controller
        P_lin = rospy.get_param("/P_control/P_lin") #linear proportional controller

        #Employ hysterisis for both controllers
        err_ang = ref_pos - data.x # 100 pix deadzone +-50 each side
        err_lin = ref_size - data.radius # <50 move forward, >70 move back

        # define publisher
        pub = rospy.Publisher('cmd_vel', Twist, queue_size=10)
        rospy.loginfo('ref_pos: %s ref_size: %s err_lin: %s err_ang: %s data.x: %s data.radius: %s', ref_pos, ref_size, err_lin, err_ang, data.x, data.radius)

        #Angular control hysterisis
        if err_ang < -50.00:
            err_ang = err_ang + 50.00
        elif err_ang > 50.00:
            err_ang = err_ang - 50.00
        else:
            err_ang = 0

        #Linear control hysterisis
        if err_lin < -10.00:
            err_lin = err_lin + 10.00
        elif err_lin > 10.00:
            err_lin = err_lin - 10.00
        else:
            err_lin = 0

        #Implement controller saturation limits if needed using ROS params
        ang_control = P_ang*err_ang
        lin_control = 4*P_lin*err_lin
        rospy.loginfo('ref_pos: %s ref_size: %s err_lin: %s err_ang: %s', ref_pos, ref_size, err_lin, err_ang)

        #Publish Velocities
        linear  = Vector3(lin_control, 0.0, 0.0)
        angular = Vector3(0.0, 0.0, ang_control)
        message = Twist(linear, angular)
        pub.publish(message)


# standard boilerplate
if __name__ == '__main__':
    while not rospy.is_shutdown():
        rospy.init_node('jackal_move', anonymous=True)
        try:
            c = Controller()
        except rospy.ROSInterruptException:
            pass
