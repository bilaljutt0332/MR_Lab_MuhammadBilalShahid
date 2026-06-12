import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
import numpy as np


class ProportionalControl(Node):
    """Task 4: Use centroid error to steer the robot toward the detected object via proportional control."""

    def __init__(self):
        super().__init__('proportional_control')
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10)
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.bridge = CvBridge()

        # --- HSV Thresholds (RED only) ---
        self.lower_red1 = np.array([0, 150, 70])
        self.upper_red1 = np.array([10, 255, 255])
        self.lower_red2 = np.array([160, 150, 70])
        self.upper_red2 = np.array([180, 255, 255])

        # --- Control Parameters ---
        self.kp = 0.0005             # proportional gain for angular velocity
        self.center_threshold = 3  # pixels — if error < this, object is "centered"
        self.min_contour_area = 500 # minimum area to consider a valid detection
        self.search_speed = 0.3     # angular speed (rad/s) when searching for red object

        self.get_logger().info('Task 4 -> proportional_control node started (tracking RED only)...')
        self.get_logger().info(f'  kp = {self.kp}, center_threshold = {self.center_threshold} px')

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        h, w, _ = frame.shape
        image_center_x = w // 2

        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(frame, (5, 5), 0)

        # Convert BGR -> HSV
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        # Create mask for RED only
        mask_red1 = cv2.inRange(hsv, self.lower_red1, self.upper_red1)
        mask_red2 = cv2.inRange(hsv, self.lower_red2, self.upper_red2)
        mask = cv2.bitwise_or(mask_red1, mask_red2)

        # Clean up with morphological operations
        kernel = np.ones((7, 7), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        twist = Twist()

        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)

            if area > self.min_contour_area:
                # Compute centroid
                M = cv2.moments(largest_contour)
                if M['m00'] > 0:
                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])

                    # Compute horizontal error (positive = object is to the right)
                    error_x = cx - image_center_x

                    # Proportional angular control
                    # Negative sign: if object is to the RIGHT (positive error),
                    # we turn CLOCKWISE (negative angular.z)
                    if abs(error_x) > self.center_threshold:
                        twist.angular.z = -self.kp * float(error_x)
                        status = f'TURNING  | error={error_x}px  angular.z={twist.angular.z:.3f}'
                    else:
                        twist.angular.z = 0.0
                        status = f'CENTERED | error={error_x}px'

                    # Draw visualization
                    cv2.drawContours(frame, [largest_contour], -1, (0, 255, 0), 2)
                    cv2.circle(frame, (cx, cy), 8, (0, 0, 255), -1)
                    # Draw center line
                    cv2.line(frame, (image_center_x, 0), (image_center_x, h), (255, 255, 0), 1)
                    # Draw error line from center to centroid
                    cv2.line(frame, (image_center_x, cy), (cx, cy), (0, 255, 255), 2)
                    cv2.putText(frame, status, (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                    self.get_logger().info(status, throttle_duration_sec=0.5)
            else:
                # Object too small -> keep searching
                twist.angular.z = self.search_speed
                cv2.putText(frame, 'SEARCHING (object too small)...', (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
                self.get_logger().info('Object too small -> searching...', throttle_duration_sec=2.0)
        else:
            # No red object detected -> keep rotating to search
            twist.angular.z = self.search_speed
            cv2.putText(frame, 'SEARCHING FOR RED...', (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            self.get_logger().info('No red object -> searching...', throttle_duration_sec=2.0)

        # Publish velocity command
        self.publisher.publish(twist)

        # Resize and display
        frame_small = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        cv2.imshow('Proportional Control', frame_small)
        cv2.waitKey(1)


def main(args=None):
    rclpy.init(args=args)
    node = ProportionalControl()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Stop the robot on exit
        twist = Twist()
        node.publisher.publish(twist)
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
