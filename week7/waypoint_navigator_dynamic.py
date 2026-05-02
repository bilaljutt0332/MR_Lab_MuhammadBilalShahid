# # Task-2: Dynamic Waypoint Navigation
# # This script allows you to specify waypoints dynamically via command-line arguments.
# # Usage: python3 waypoint_navigator_dynamic.py x1 y1 w1 x2 y2 w2 ...
# # Each group of 3 values corresponds to one waypoint (x, y,

# import rclpy
# import sys
# from rclpy.node import Node
# from rclpy.action import ActionClient
# from nav2_msgs.action import FollowWaypoints
# from geometry_msgs.msg import PoseStamped

# class WaypointNavigator(Node):
#     def __init__(self):
#         super().__init__('waypoint_navigator')
#         self._client = ActionClient(self, FollowWaypoints, 'follow_waypoints')

#     def send_waypoints(self, waypoints):
#         self.get_logger().info('Waiting for FollowWaypoints server...')
#         self._client.wait_for_server()
#         goal_msg = FollowWaypoints.Goal()
#         goal_msg.poses = waypoints
#         self.get_logger().info(f'Sending {len(waypoints)} waypoints...')
#         future = self._client.send_goal_async(goal_msg)
#         rclpy.spin_until_future_complete(self, future)
#         handle = future.result()
#         if not handle.accepted:
#             self.get_logger().error('Goal rejected!')
#             return
#         result_future = handle.get_result_async()
#         rclpy.spin_until_future_complete(self, result_future)
#         self.get_logger().info('Mission complete!')

# def make_pose(x, y, yaw_w):
#     pose = PoseStamped()
#     pose.header.frame_id = 'map'
#     pose.pose.position.x = float(x)
#     pose.pose.position.y = float(y)
#     pose.pose.position.z = 0.0
#     pose.pose.orientation.z = float(yaw_w)
#     pose.pose.orientation.w = 1.0
#     return pose

# def main():
#     # Parse command-line arguments (groups of 3: x y orientation_w)
#     args = sys.argv[1:]   # skip script name
#     if len(args) == 0 or len(args) % 3 != 0:
#         print('Usage: python3 waypoint_navigator_dynamic.py x1 y1 w1 x2 y2 w2 ...')
#         print('  Each group of 3 values = one waypoint (x, y, orientation_w)')
#         sys.exit(1)

#     waypoints = []
#     for i in range(0, len(args), 3):
#         x, y, w = args[i], args[i+1], args[i+2]
#         waypoints.append(make_pose(x, y, w))
#         print(f'  Waypoint {i//3 + 1}: x={x}, y={y}, w={w}')

#     rclpy.init()
#     navigator = WaypointNavigator()
#     navigator.send_waypoints(waypoints)
#     navigator.destroy_node()
#     rclpy.shutdown()

# if __name__ == '__main__':
#     main()



# Task-5:

import sys
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import FollowWaypoints
from geometry_msgs.msg import PoseStamped

class WaypointNavigator(Node):
    def __init__(self):
        super().__init__('waypoint_navigator')
        self._client = ActionClient(self, FollowWaypoints, 'follow_waypoints')

    def feedback_callback(self, feedback_msg):
        """Receives feedback from the Nav2 Waypoint Follower server."""
        feedback = feedback_msg.feedback
        # Nav2 FollowWaypoints feedback provides 'current_waypoint' index
        self.get_logger().info(f'Executing Waypoint: {feedback.current_waypoint + 1}')

    def send_waypoints(self, waypoints):
        self.get_logger().info('Waiting for Nav2 FollowWaypoints action server...')
        self._client.wait_for_server()
        
        goal_msg = FollowWaypoints.Goal()
        goal_msg.poses = waypoints
        
        self.get_logger().info(f'Mission Started: Sending {len(waypoints)} waypoints...')
        
        # We add 'feedback_callback' here to monitor progress
        send_goal_future = self._client.send_goal_async(
            goal_msg, 
            feedback_callback=self.feedback_callback
        )
        
        rclpy.spin_until_future_complete(self, send_goal_future)
        
        goal_handle = send_goal_future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected by the Nav2 Server!')
            return

        self.get_logger().info('Goal accepted. Monitoring progress...')
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        
        self.get_logger().info('✅ All waypoints reached! Mission Complete.')

def make_pose(x, y, w):
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.pose.position.x = float(x)
    pose.pose.position.y = float(y)
    pose.pose.orientation.w = float(w)
    return pose

def main():
    rclpy.init()
    navigator = WaypointNavigator()
    
    args = sys.argv[1:]
    if len(args) % 3 != 0 or len(args) == 0:
        print("Usage: python3 script.py x1 y1 w1 x2 y2 w2 ...")
        return

    waypoints = []
    for i in range(0, len(args), 3):
        waypoints.append(make_pose(args[i], args[i+1], args[i+2]))

    try:
        navigator.send_waypoints(waypoints)
    except KeyboardInterrupt:
        print("Mission interrupted by user.")
    finally:
        navigator.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()