import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist 
from cv_bridge import CvBridge
import cv2
import numpy as np
from tflite_runtime.interpreter import Interpreter
import time
import os

class ImageSubscriber(Node):
    def __init__(self):
        super().__init__('subscriber')

        self.subscription = self.create_subscription(Image,'/color/preview/image', self.listener_callback, 10)
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.br = CvBridge()

    def listener_callback(self, data):

        self.get_logger().info('Receiving video frame')
        current_frame = self.br.imgmsg_to_cv2(data)

        # Get path to current working directory
        CWD_PATH = os.getcwd()
        
        # Path to .tflite file, which contains the model that is used for object detection
        PATH_TO_CKPT = os.path.join(CWD_PATH,'./custom_model_lite','detect.tflite') #change dir /home/ay93/sparky_ws
        interpreter = Interpreter(model_path=PATH_TO_CKPT)
        interpreter.allocate_tensors()

        # Get model details
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        height = input_details[0]['shape'][1]
        width = input_details[0]['shape'][2]
        floating_model = (input_details[0]['dtype'] == np.float32)
        input_mean = 127.5
        input_std = 127.5

        # Grab frame from video stream
        frame1 = current_frame
        # Acquire frame and resize to expected shape [1xHxWx3]
        frame = frame1.copy()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (width, height))
        input_data = np.expand_dims(frame_resized, axis=0)

        # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
        if floating_model:
            input_data = (np.float32(input_data) - input_mean) / input_std

        # Perform the actual detection by running the model with the image as input
        interpreter.set_tensor(input_details[0]['index'],input_data)
        interpreter.invoke()

        # Retrieve detection results
        #boxes = interpreter.get_tensor(output_details[boxes_idx]['index'])[0] # Bounding box coordinates of detected objects
        scores = interpreter.get_tensor(output_details[0]['index'])[0] # Confidence of detected objects

        # Print the values of boxes, classes, and scores
        #print("Box: ", boxes[0])
        print("Score: ", scores[0])

        if scores[0] < 0.9:
            twist = Twist()
            twist.linear.x = 0.0
            twist.angular.z = 1.0

            self.publisher_.publish(twist)

        else:
            twist = Twist()
            twist.linear.x = 0.0
            twist.angular.z = 0.0

            time.sleep(1.0)

            self.publisher_.publish(twist)

        #Show video feed
        cv2.imshow("camera", current_frame)
        cv2.waitKey(1)

def main(args=None):

    rclpy.init(args=args)
    sparky_node = ImageSubscriber()
    rclpy.spin(sparky_node)
    sparky_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()