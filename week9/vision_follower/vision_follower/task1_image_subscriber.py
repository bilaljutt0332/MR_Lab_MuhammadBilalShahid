import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2


class ImageSubscriber(Node):
    """Task 1: Subscribe to /camera/image_raw and display the image using OpenCV."""

    def __init__(self):
        super().__init__('image_subscriber')
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10)
        self.bridge = CvBridge()
        self.get_logger().info('Task 1->image_subscriber node started, waiting for camera images...')

    def image_callback(self, msg):
        # Convert ROS Image message to OpenCV BGR frame
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        # Resize to 50% so window doesn't fill the screen
        frame_small = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

        # Display the raw camera feed
        cv2.imshow('Camera View', frame_small)
        cv2.waitKey(1)


def main(args=None):
    rclpy.init(args=args)
    node = ImageSubscriber()
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
