import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np


class ColorSegmentation(Node):
    """Task 2: Convert the image to HSV and perform color segmentation for multiple colors."""

    def __init__(self):
        super().__init__('color_segmentation')
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10)
        self.bridge = CvBridge()

        # --- HSV Thresholds ---
        # RED (Wraps around hue 0 and 180) — high saturation to reject noise
        self.lower_red1 = np.array([0, 150, 70])
        self.upper_red1 = np.array([10, 255, 255])
        self.lower_red2 = np.array([160, 150, 70])
        self.upper_red2 = np.array([180, 255, 255])

        # GREEN
        self.lower_green = np.array([40, 50, 50])
        self.upper_green = np.array([80, 255, 255])

        # GREY (Low saturation, medium value - tightening to avoid the light grey floor)
        self.lower_grey = np.array([0, 0, 80])
        self.upper_grey = np.array([180, 40, 150])

        # BLACK (Very low value)
        self.lower_black = np.array([0, 0, 0])
        self.upper_black = np.array([180, 255, 30])

        self.get_logger().info('Task 2 node started -> Segmenting Red, Green, Grey, and Black...')

    def image_callback(self, msg):
        # Convert ROS Image → OpenCV BGR
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        # Apply Gaussian blur to reduce pixel noise before color detection
        blurred = cv2.GaussianBlur(frame, (5, 5), 0)

        # Convert BGR → HSV
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        # Create individual masks
        mask_red1 = cv2.inRange(hsv, self.lower_red1, self.upper_red1)
        mask_red2 = cv2.inRange(hsv, self.lower_red2, self.upper_red2)
        mask_red = cv2.bitwise_or(mask_red1, mask_red2)

        mask_green = cv2.inRange(hsv, self.lower_green, self.upper_green)
        mask_grey = cv2.inRange(hsv, self.lower_grey, self.upper_grey)
        mask_black = cv2.inRange(hsv, self.lower_black, self.upper_black)

        # Combine all masks into one (bitwise OR)
        combined_mask = mask_red | mask_green | mask_grey | mask_black

        # Clean up the combined mask with morphological operations
        kernel = np.ones((7, 7), np.uint8)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)

        # Apply the mask to the original frame to see the detected colors!
        color_result = cv2.bitwise_and(frame, frame, mask=combined_mask)

        # Resize to 50% so windows don't fill the screen
        frame_small = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        result_small = cv2.resize(color_result, (0, 0), fx=0.5, fy=0.5)

        # Display both windows
        cv2.imshow('Camera View', frame_small)
        cv2.imshow('Detected Colors', result_small)
        cv2.waitKey(1)


def main(args=None):
    rclpy.init(args=args)
    node = ColorSegmentation()
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
