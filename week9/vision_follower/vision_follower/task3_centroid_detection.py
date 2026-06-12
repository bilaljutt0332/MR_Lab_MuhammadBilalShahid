import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np


class CentroidDetection(Node):
    """Task 3: Detect colored objects via HSV segmentation and compute separate centroids per color."""

    def __init__(self):
        super().__init__('centroid_detection')
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10)
        self.bridge = CvBridge()

        # Minimum contour area to consider (filters out tiny noise blobs)
        self.min_contour_area = 500

        # Morphological kernel for cleaning masks
        self.kernel = np.ones((7, 7), np.uint8)

        # Each color entry: (label, hsv_ranges_list, BGR_draw_color)
        # hsv_ranges_list is a list of (lower, upper) tuples (red needs 2 ranges)
        self.colors = [
            ('RED', [
                (np.array([0, 150, 70]),   np.array([10, 255, 255])),
                (np.array([160, 150, 70]), np.array([180, 255, 255])),
            ], (0, 0, 255)),       # drawn in red BGR

            ('GREEN', [
                (np.array([40, 50, 50]), np.array([80, 255, 255])),
            ], (0, 255, 0)),       # drawn in green BGR

            ('BLUE', [
                (np.array([100, 100, 50]), np.array([130, 255, 255])),
            ], (255, 0, 0)),       # drawn in blue BGR

            ('GREY', [
                (np.array([0, 0, 80]), np.array([180, 40, 150])),
            ], (180, 180, 180)),   # drawn in light grey BGR

            ('BLACK', [
                (np.array([0, 0, 0]), np.array([180, 255, 30])),
            ], (100, 100, 100)),   # drawn in dark grey BGR
        ]

        self.get_logger().info('Task 3 -> centroid_detection node started (per-color centroids)...')

    def process_color(self, hsv, frame, label, hsv_ranges, draw_color):
        """Process a single color: create mask, find largest contour, draw centroid.
        Returns (cx, cy, area) if found, else None."""

        # Build mask from one or more HSV ranges (e.g., red needs two)
        mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        for lower, upper in hsv_ranges:
            mask = cv2.bitwise_or(mask, cv2.inRange(hsv, lower, upper))

        # Clean up the mask
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel)

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return None

        # Select the largest contour
        largest = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest)

        if area < self.min_contour_area:
            return None

        # Compute centroid using image moments
        M = cv2.moments(largest)
        if M['m00'] == 0:
            return None

        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])

        # Draw contour outline, centroid dot, and label on the frame
        cv2.drawContours(frame, [largest], -1, draw_color, 2)
        cv2.circle(frame, (cx, cy), 8, draw_color, -1)
        cv2.putText(frame, f'{label} ({cx},{cy})',
                    (cx + 12, cy - 12), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, draw_color, 2)

        return (cx, cy, area)

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(frame, (5, 5), 0)

        # Convert BGR -> HSV
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        # Process each color separately
        detections = []
        for label, hsv_ranges, draw_color in self.colors:
            result = self.process_color(hsv, frame, label, hsv_ranges, draw_color)
            if result:
                cx, cy, area = result
                detections.append((label, cx, cy, area))

        # Log detections
        if detections:
            for label, cx, cy, area in detections:
                self.get_logger().info(
                    f'{label}: centroid=({cx},{cy})  area={area}',
                    throttle_duration_sec=1.0)
        else:
            self.get_logger().info('No objects detected', throttle_duration_sec=2.0)

        # Resize and display
        frame_small = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        cv2.imshow('Camera View + Centroids', frame_small)
        cv2.waitKey(1)


def main(args=None):
    rclpy.init(args=args)
    node = CentroidDetection()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

