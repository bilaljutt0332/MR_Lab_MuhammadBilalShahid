
#====================================================
# Task-1:-
#====================================================


# import rclpy
# from rclpy.node import Node
# from geometry_msgs.msg import Twist
# import time

# class VelocityPublisher(Node):
#     def __init__(self, pattern):
#         super().__init__('velocity_publisher')
#         self.publisher_ = self.create_publisher(Twist, 'turtle1/cmd_vel', 10)
#         self.pattern = pattern
#         # The timer will trigger the selected pattern logic
#         self.timer = self.create_timer(1.0, self.timer_callback)
#         self.executed = False

#     def timer_callback(self):
#         if self.executed and self.pattern != '3':
#             return # Only run once for shapes; circles keep going
            
#         msg = Twist()

#         if self.pattern == '1': # Square 
#             self.get_logger().info('Executing Square Pattern')
#             for _ in range(4):
#                 self.move_forward(msg, 2.0, 2)
#                 self.turn(msg, 1.57, 1) # 90 degrees
#             self.executed = True

#         elif self.pattern == '2': # Triangle
#             self.get_logger().info('Executing Triangular Pattern')
#             for _ in range(3):
#                 self.move_forward(msg, 2.0, 2)
#                 self.turn(msg, 2.09, 1) # 120 degrees
#             self.executed = True

#         elif self.pattern == '3': # Circle
#             msg.linear.x = 2.0
#             msg.angular.z = 1.0
#             self.publisher_.publish(msg)
#             self.get_logger().info('Moving in a Circle...')

#     def move_forward(self, msg, speed, duration):
#         msg.linear.x = speed
#         msg.angular.z = 0.0
#         self.publisher_.publish(msg)
#         time.sleep(float(duration))

#     def turn(self, msg, angle, duration):
#         msg.linear.x = 0.0
#         msg.angular.z = angle
#         self.publisher_.publish(msg)
#         time.sleep(float(duration))

# def main(args=None):
#     print("--- Turtle Pattern Controller ---")
#     print("1: Square")
#     print("2: Triangle")
#     print("3: Circle")
#     choice = input("Enter the number of the pattern you want: ")

#     rclpy.init(args=args)
#     velocity_publisher = VelocityPublisher(choice)
    
#     try:
#         rclpy.spin(velocity_publisher)
#     except KeyboardInterrupt:
#         pass
        
#     velocity_publisher.destroy_node()
#     rclpy.shutdown()

# if __name__ == '__main__':
#     main()




#====================================================
# Task-2:-
#====================================================



# import rclpy
# from rclpy.node import Node
# from geometry_msgs.msg import Twist
# from turtlesim.srv import Spawn
# import time

# class MultiTurtleController(Node):
#     def __init__(self, choices):
#         super().__init__('multi_turtle_controller')
#         self.choices = choices
#         self.count = 0  # To track movement steps
        
#         # 1. Setup Service Client to spawn turtles 
#         self.spawner = self.create_client(Spawn, 'spawn')
#         while not self.spawner.wait_for_service(timeout_sec=1.0):
#             self.get_logger().info('Waiting for spawn service...')
        
#         # Spawn Turtle 2 and Turtle 3 at specific locations [cite: 162, 163]
#         self.spawn_turtle(2.0, 2.0, 0.0, 'turtle2')
#         self.spawn_turtle(8.0, 8.0, 0.0, 'turtle3')

#         # 2. Create Publishers [cite: 125]
#         self.pub1 = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
#         self.pub2 = self.create_publisher(Twist, '/turtle2/cmd_vel', 10)
#         self.pub3 = self.create_publisher(Twist, '/turtle3/cmd_vel', 10)

#         # 3. Timer for movement - set to 1 second intervals for clear steps [cite: 127]
#         self.timer = self.create_timer(1.0, self.timer_callback)
#         self.get_logger().info('Multi-Turtle Controller Started')

#     def spawn_turtle(self, x, y, theta, name):
#         request = Spawn.Request()
#         request.x = x
#         request.y = y
#         request.theta = theta
#         request.name = name
#         self.spawner.call_async(request)

#     def timer_callback(self):
#         # Apply patterns to each turtle
#         self.execute_logic(self.pub1, self.choices[0])
#         self.execute_logic(self.pub2, self.choices[1])
#         self.execute_logic(self.pub3, self.choices[2])
#         self.count += 1

#     def execute_logic(self, publisher, choice):
#         msg = Twist()
        
#         if choice == '1': # SQUARE logic: Move straight on even counts, turn on odd [cite: 132, 135]
#             if self.count % 2 == 0:
#                 msg.linear.x = 2.0
#                 msg.angular.z = 0.0
#             else:
#                 msg.linear.x = 0.0
#                 msg.angular.z = 1.57 # 90 degrees
                
#         elif choice == '2': # TRIANGLE logic [cite: 161]
#             if self.count % 2 == 0:
#                 msg.linear.x = 2.0
#                 msg.angular.z = 0.0
#             else:
#                 msg.linear.x = 0.0
#                 msg.angular.z = 2.09 # 120 degrees
                
#         elif choice == '3': # CIRCLE logic: Constant curve [cite: 161]
#             msg.linear.x = 2.0
#             msg.angular.z = 1.0
        
#         publisher.publish(msg)

# def main(args=None):
#     print("--- Multi-Turtle Pattern Menu ---")
#     print("1: Square | 2: Triangle | 3: Circle")
#     t1 = input("Pattern for Turtle 1: ")
#     t2 = input("Pattern for Turtle 2: ")
#     t3 = input("Pattern for Turtle 3: ")

#     rclpy.init(args=args)
#     node = MultiTurtleController([t1, t2, t3])
#     try:
#         rclpy.spin(node)
#     except KeyboardInterrupt:
#         pass
#     node.destroy_node()
#     rclpy.shutdown()

# if __name__ == '__main__':
#     main()



#====================================================
# Task-3:-
#====================================================



import rclpy
from rclpy.node import Node
from turtlesim.srv import TeleportAbsolute
import sys

class TurtleTeleporter(Node):
    def __init__(self):
        super().__init__('turtle_teleporter')
        # Create a client for the absolute teleportation service 
        self.client = self.create_client(TeleportAbsolute, '/turtle1/teleport_absolute')
        
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Teleport service not available, waiting...')

    def send_request(self, x, y, theta):
        request = TeleportAbsolute.Request()
        request.x = float(x)
        request.y = float(y)
        request.theta = float(theta)
        
        # Call the service asynchronously
        self.future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, self.future)
        return self.future.result()

def main(args=None):
    # Get user input for the specific location 
    print("--- Move Turtle to Specific Location ---")
    pos_x = input("Enter X coordinate (0.0 to 11.0): ")
    pos_y = input("Enter Y coordinate (0.0 to 11.0): ")
    angle = input("Enter Orientation/Theta (0.0 to 6.28): ")

    rclpy.init(args=args)
    teleporter = TurtleTeleporter()
    
    response = teleporter.send_request(pos_x, pos_y, angle)
    
    if response is not None:
        print(f"Successfully moved turtle to X: {pos_x}, Y: {pos_y}")
    
    teleporter.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()