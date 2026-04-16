import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist
import math

class FollowerNode(Node):
    def __init__(self):
        super().__init__('follower_node')
        self.turtle1_pose = None
        self.turtle2_pose = None

        self.sub_turtle1 = self.create_subscription(Pose, '/turtle1/pose', self.turtle1_callback, 10)
        self.sub_turtle2 = self.create_subscription(Pose, '/turtle2/pose', self.turtle2_callback, 10)
        self.pub_cmd_vel = self.create_publisher(Twist, '/turtle2/cmd_vel', 10)

        self.timer = self.create_timer(0.1, self.control_loop)

    def turtle1_callback(self, msg):
        self.turtle1_pose = msg

    def turtle2_callback(self, msg):
        self.turtle2_pose = msg

    def control_loop(self):
        if self.turtle1_pose is None or self.turtle2_pose is None:
            return

        # Calculate distance and angle errors
        dx = self.turtle1_pose.x - self.turtle2_pose.x
        dy = self.turtle1_pose.y - self.turtle2_pose.y
        distance = math.sqrt(dx**2 + dy**2)
        angle_to_goal = math.atan2(dy, dx)

        msg = Twist()
        # Proportional control loop
        if distance > 0.5: # Maintain a small distance so they don't collide
            msg.linear.x = 1.5 * distance
            angle_diff = angle_to_goal - self.turtle2_pose.theta
            # Normalize angle between -pi and pi
            angle_diff = math.atan2(math.sin(angle_diff), math.cos(angle_diff))
            msg.angular.z = 4.0 * angle_diff
        else:
            msg.linear.x = 0.0
            msg.angular.z = 0.0

        self.pub_cmd_vel.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = FollowerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
