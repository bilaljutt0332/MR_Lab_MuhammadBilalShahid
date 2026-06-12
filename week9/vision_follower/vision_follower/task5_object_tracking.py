import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
import numpy as np
import time
import math


class ObjectTracking(Node):
    """Task 5: Track colored objects (Red > Blue > Green priority), approach, and stop at safe distance.
    If object disappears, rotate 360° to search, then stop if nothing found."""

    def __init__(self):
        super().__init__('object_tracking')
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10)
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.bridge = CvBridge()

        # --- HSV Thresholds (priority order: RED > BLUE > GREEN) ---
        self.colors = [
            ('RED', [
                (np.array([0, 150, 70]),   np.array([10, 255, 255])),
                (np.array([160, 150, 70]), np.array([180, 255, 255])),
            ], (0, 0, 255)),

            ('BLUE', [
                (np.array([100, 100, 50]), np.array([130, 255, 255])),
            ], (255, 0, 0)),

            ('GREEN', [
                (np.array([40, 50, 50]), np.array([80, 255, 255])),
            ], (0, 255, 0)),
        ]

        # --- Control Parameters ---
        self.kp = 0.0005            # proportional gain for angular velocity
        self.center_threshold = 3   # pixels — if error < this, object is "centered"
        self.min_contour_area = 500 # minimum area to consider a valid detection
        self.search_speed = 0.3     # angular speed (rad/s) when searching
        self.forward_speed = 0.15   # linear speed (m/s) when approaching
        self.stop_percent = 65.0    # stop when object fills this % of the screen

        # --- 360° Search State ---
        self.search_start_time = None   # when we started searching (after losing object)
        self.had_detection = False      # whether we ever had a detection before losing it
        self.search_exhausted = False   # True if we completed 360° without finding anything
        # Time for one full rotation: 2*pi / search_speed
        self.full_rotation_time = (2.0 * math.pi) / self.search_speed

        # Morphological kernel
        self.kernel = np.ones((7, 7), np.uint8)

        self.get_logger().info('Task 5 -> object_tracking node started...')
        self.get_logger().info(f'  Priority: RED > BLUE > GREEN')
        self.get_logger().info(f'  360° search timeout: {self.full_rotation_time:.1f}s')

    def detect_color(self, hsv, label, hsv_ranges):
        """Create mask for a single color and return (mask, largest_contour, area) or None."""
        mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        for lower, upper in hsv_ranges:
            mask = cv2.bitwise_or(mask, cv2.inRange(hsv, lower, upper))

        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None

        largest = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest)

        if area < self.min_contour_area:
            return None

        M = cv2.moments(largest)
        if M['m00'] == 0:
            return None

        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])
        return (largest, cx, cy, area, mask)

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        h, w, _ = frame.shape
        image_center_x = w // 2

        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(frame, (5, 5), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        twist = Twist()

        # Try to detect colors in priority order: RED > BLUE > GREEN
        detection = None
        detected_label = None
        detected_color = None
        for label, hsv_ranges, draw_color in self.colors:
            result = self.detect_color(hsv, label, hsv_ranges)
            if result:
                detection = result
                detected_label = label
                detected_color = draw_color
                break  # stop at the highest priority color found

        if detection:
            largest_contour, cx, cy, area, color_mask = detection

            # Calculate what % of the screen is filled by this color
            total_pixels = w * h
            color_pixels = cv2.countNonZero(color_mask)
            fill_percent = (color_pixels / total_pixels) * 100.0

            # We found something! Reset search state
            self.had_detection = True
            self.search_start_time = None
            self.search_exhausted = False

            # Compute horizontal error
            error_x = cx - image_center_x

            # --- STEERING ---
            if abs(error_x) > self.center_threshold:
                twist.angular.z = -self.kp * float(error_x)
            else:
                twist.angular.z = 0.0

            # --- APPROACH & SAFE DISTANCE ---
            if fill_percent >= self.stop_percent:
                # Screen is filled enough -> stop (safe distance)
                twist.linear.x = 0.0
                twist.angular.z = 0.0
                status = f'{detected_label} STOPPED ({fill_percent:.1f}% filled)'
                status_color = (0, 255, 0)
            elif abs(error_x) <= self.center_threshold:
                # Centered -> drive forward
                twist.linear.x = self.forward_speed
                status = f'{detected_label} APPROACHING ({fill_percent:.1f}%)'
                status_color = (255, 255, 0)
            else:
                # Off-center -> steer only
                twist.linear.x = 0.0
                status = f'{detected_label} ALIGNING | err={error_x}px'
                status_color = (0, 165, 255)

            # Draw visualization
            cv2.drawContours(frame, [largest_contour], -1, detected_color, 2)
            cv2.circle(frame, (cx, cy), 8, detected_color, -1)
            cv2.line(frame, (image_center_x, 0), (image_center_x, h), (255, 255, 0), 1)
            cv2.line(frame, (image_center_x, cy), (cx, cy), (0, 255, 255), 2)
            cv2.putText(frame, status, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)

            # Proximity bar (percentage-based)
            bar_width = min(int((fill_percent / self.stop_percent) * 300), 300)
            cv2.rectangle(frame, (10, h - 40), (10 + bar_width, h - 20), status_color, -1)
            cv2.rectangle(frame, (10, h - 40), (310, h - 20), (255, 255, 255), 1)
            cv2.putText(frame, f'Screen fill: {fill_percent:.1f}% / {self.stop_percent:.0f}%',
                        (10, h - 45), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

            self.get_logger().info(status, throttle_duration_sec=0.5)

        else:
            # No color detected
            if self.search_exhausted:
                # Already did a full 360° and found nothing -> stop
                twist.angular.z = 0.0
                twist.linear.x = 0.0
                cv2.putText(frame, 'NO OBJECT FOUND (360 done) - STOPPED', (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)
                self.get_logger().info('360° search complete -> stopped', throttle_duration_sec=2.0)

            elif self.had_detection:
                # We previously saw something but lost it -> start/continue 360° search
                if self.search_start_time is None:
                    self.search_start_time = time.time()

                elapsed = time.time() - self.search_start_time
                remaining = self.full_rotation_time - elapsed

                if elapsed >= self.full_rotation_time:
                    # Completed 360° -> give up
                    self.search_exhausted = True
                    twist.angular.z = 0.0
                else:
                    twist.angular.z = self.search_speed

                cv2.putText(frame, f'SEARCHING... {remaining:.1f}s left', (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
                self.get_logger().info(
                    f'Searching... {remaining:.1f}s remaining', throttle_duration_sec=1.0)

            else:
                # Never had a detection -> keep searching indefinitely
                twist.angular.z = self.search_speed
                cv2.putText(frame, 'SEARCHING FOR OBJECTS...', (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                self.get_logger().info('Initial search...', throttle_duration_sec=2.0)

        # Publish velocity command
        self.publisher.publish(twist)

        # Resize and display
        frame_small = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        cv2.imshow('Object Tracking', frame_small)
        cv2.waitKey(1)


def main(args=None):
    rclpy.init(args=args)
    node = ObjectTracking()
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
