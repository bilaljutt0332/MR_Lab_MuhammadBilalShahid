import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import numpy as np

class LidarNavigator(Node):
    def __init__(self):
        super().__init__('lidar_navigator')

        # Subscriber: LiDAR scan data
        self.subscription = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, 10)

        # Publisher: velocity commands
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)

        # ── Thresholds (tune these values) ──────────────────────
        self.front_threshold = 0.5   # metres — stop if < this
        self.side_threshold  = 0.4   # metres — wall follow distance
        self.wall_target     = 0.4   # metres — desired wall distance
        self.kp              = 1.5   # proportional gain for wall follow

        self.get_logger().info('LidarNavigator node started.')

    def scan_callback(self, msg):
        ranges = np.array(msg.ranges)

        # ── TODO 1: Clean data (replace inf/nan with large value) ─
        ranges = np.where(np.isfinite(ranges), ranges, 10.0)

        total = len(ranges)

        # ── TODO 2: Define directional regions ────────────────────
        # Front: indices near 0° (first and last few degrees)
        front_size = total // 12          # ~30° sector
        front = np.concatenate([
            ranges[:front_size],
            ranges[total - front_size:]
        ])

        # Left: indices around 90°
        left_start = total // 4 - total // 12
        left_end   = total // 4 + total // 12
        left  = ranges[left_start : left_end]

        # Right: indices around 270°
        right_start = 3 * total // 4 - total // 12
        right_end   = 3 * total // 4 + total // 12
        right = ranges[right_start : right_end]

        # Compute minimum distance in each region
        front_dist = float(np.min(front))
        left_dist  = float(np.min(left))
        right_dist = float(np.min(right))

        # Debug logging
        self.get_logger().info(
            f'Front: {front_dist:.2f}  Left: {left_dist:.2f}  Right: {right_dist:.2f}'
        )

        twist = Twist()

        # ── TODO 3: Obstacle avoidance logic ──────────────────────
        if front_dist < self.front_threshold:   # obstacle in front

            # ── TODO 4: Choose turn direction ─────────────────────
            if left_dist > right_dist:           # left side clearer
                twist.angular.z =  0.5           # turn left (+z)
            else:                                # right side clearer
                twist.angular.z = -0.5           # turn right (-z)

            twist.linear.x = 0.0                 # stop forward motion

        else:
            # ── TODO 5: Wall following (proportional control) ─────
            # Use left wall distance; error = actual - target
            error = left_dist - self.wall_target

            # Clamp angular correction
            angular_correction = self.kp * error
            angular_correction = max(-0.8, min(0.8, angular_correction))

            twist.linear.x  = 0.15               # forward speed
            twist.angular.z = -angular_correction # steer toward wall

        self.publisher.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = LidarNavigator()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()