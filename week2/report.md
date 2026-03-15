Part 1: The Difference Between Topics and Services
	Based on the observations from the Turtlesim exercise, here is the technical distinction:
	ROS 2 Topics (Continuous Stream):

	Observation: When running ros2 topic echo /turtle1/pose, the terminal displayed a constant, high-speed stream of data (x, y, theta) 	even when the turtle wasn't moving.

Definition: Topics use a Publisher/Subscriber model. They are intended for continuous data streams where the sender doesn't need to know if anyone is listening.

Analogy: Like a radio station broadcasting music 24/7; anyone can tune in at any time to hear the current status.

ROS 2 Services (One-time Request):

Observation: When using /spawn or /reset in rqt, nothing happened until I clicked "Call." Once clicked, a single action occurred (a new turtle appeared or the screen cleared), and the service provided a single confirmation response.

Definition: Services use a Client/Server (Request/Response) model. They are intended for "remote procedures" or discrete actions that happen only when specifically triggered.

Analogy: Like a doorbell; nothing happens until someone presses the button, and the ringer provides an immediate, one-time reaction.

Part 2: Steps Taken to Control the Second Turtle Independently
To successfully control turtle2 without affecting turtle1, the following sequence was performed:

Spawning the Turtle:

Opened rqt and navigated to the Service Caller plugin.

Selected the /spawn service.

Entered parameters: x: 5.0, y: 5.0, theta: 0.0, and named it "turtle2".

Clicked Call, which successfully generated a new turtle icon in the center of the turtlesim window.

Identifying the Unique Topic:

Ran ros2 topic list in the terminal.

Observed that a new set of topics was created automatically: /turtle2/cmd_vel and /turtle2/pose. This confirmed that ROS 2 separates robot controls by "namespaces."

Sending Independent Commands:

Instead of using the keyboard (which defaults to turtle1), I used the command line to send a specific movement command to the second turtle's topic:

ros2 topic pub /turtle2/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 2.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 1.0}}"
Observation: Only turtle2 began moving in a circle, while turtle1 remained stationary. This proved that by targeting the specific /turtle2/cmd_vel topic, we can control multiple robots independently within the same environment.
