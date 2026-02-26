import rclpy
from rclpy.node import Node
import os

class SimpleNode(Node):
    def __init__(self):
        super().__init__('simple_node')
        
        # --- Task 3: Add a ROS Parameter ---
        # Declares 'student_name' with a default message if not set
        self.declare_parameter('student_name', 'student_name not set')
        student_name = self.get_parameter('student_name').get_parameter_value().string_value

        # --- Task 2: Implement a Persistent Counter ---
        # Path to store the count on your HP Notebook
        count_file_path = os.path.expanduser('~/ros_run_count.txt')
        
        if os.path.exists(count_file_path):
            with open(count_file_path, 'r') as f:
                try:
                    count = int(f.read().strip()) + 1
                except ValueError:
                    count = 1
        else:
            count = 1
            
        with open(count_file_path, 'w') as f:
            f.write(str(count))

        # --- Task 1: Customized Log Message ---
        # Requirements: 'Welcome to Mobile Robotics Lab'
        self.get_logger().info('Welcome to Mobile Robotics Lab')
        self.get_logger().info(f'Run count: {count}')
        self.get_logger().info(f'Student: {student_name}')


def main(args=None):
    rclpy.init(args=args)
    node = SimpleNode()

    # spin_once allows the node to initialize and log before exiting
    rclpy.spin_once(node, timeout_sec=0.1)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
