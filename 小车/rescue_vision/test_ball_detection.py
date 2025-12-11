import cv2
import numpy as np
import math
from config import CAMERA_CONFIG, COLOR_RANGES, TARGET_CONFIG, VISION_CONFIG
from object_detection import ObjectDetector

class BallDetectionTester:
    def __init__(self):
        # Initialize camera
        self.cap = cv2.VideoCapture(0)  # 0 represents default camera
        self.cap.set(3, CAMERA_CONFIG["resolution"][0])
        self.cap.set(4, CAMERA_CONFIG["resolution"][1])
        
        # Create object detector
        self.detector = ObjectDetector()
        
        # Configure parameters
        self.team_color = "red"  # Can be changed to "blue" or other colors
        self.fov_horizontal = CAMERA_CONFIG.get("horizontal_fov", 60)  # Horizontal field of view
        self.fov_vertical = CAMERA_CONFIG.get("vertical_fov", 45)  # Vertical field of view
        self.img_center_x = CAMERA_CONFIG["resolution"][0] / 2  # Image center x-coordinate
        self.img_center_y = CAMERA_CONFIG["resolution"][1] / 2  # Image center y-coordinate
        
        # Distance calculation parameters
        self.pixel_distance_scale = VISION_CONFIG.get("ball_distance_scale", 15000)
        self.pixel_distance_offset = VISION_CONFIG.get("ball_distance_offset", 0)
        
        print("Ball detection test program started")
        print("Press 'q' to quit")
        print("Press 'r' to switch to red ball detection")
        print("Press 'b' to switch to blue ball detection")
        print("Press 'k' to switch to black ball detection")
        print("Press 'y' to switch to yellow ball detection")
    
    def calculate_angle(self, cx, cy):
        """Calculate horizontal and vertical angles relative to image center"""
        # Horizontal angle calculation
        horizontal_offset = cx - self.img_center_x
        angle_per_pixel_horizontal = self.fov_horizontal / CAMERA_CONFIG["resolution"][0]
        horizontal_angle = horizontal_offset * angle_per_pixel_horizontal
        
        # Vertical angle calculation
        vertical_offset = self.img_center_y - cy  # Up is positive, down is negative
        angle_per_pixel_vertical = self.fov_vertical / CAMERA_CONFIG["resolution"][1]
        vertical_angle = vertical_offset * angle_per_pixel_vertical
        
        return horizontal_angle, vertical_angle
    
    def run(self):
        show_vertical_angle = False  # Control whether to show vertical angle
        
        while True:
            # Read camera frame
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to read camera frame")
                break
            
            # Detect balls
            balls, mask = self.detector.detect_color(frame, self.team_color)
            
            # Process detection results
            if balls:
                # Find the closest ball
                closest_ball = balls[0]  # balls are already sorted by distance
                cx, cy, distance = closest_ball
                
                # Calculate angles
                horizontal_angle, vertical_angle = self.calculate_angle(cx, cy)
                
                # Convert units
                distance_cm = distance / 10.0
                
                # Draw results on the image
                # Draw ball center
                cv2.circle(frame, (int(cx), int(cy)), 5, (0, 255, 0), -1)  # Center point
                
                # Calculate ball diameter in pixels (inverse of distance relationship)
                distance_adjusted = distance - self.pixel_distance_offset
                if distance_adjusted <= 0:
                    distance_adjusted = 1  # Avoid division by zero
                ball_diameter_pixels = int(self.pixel_distance_scale / distance_adjusted)
                if ball_diameter_pixels < 5:
                    ball_diameter_pixels = 5
                
                # Draw ball bounding box
                half_diameter = ball_diameter_pixels // 2
                x = int(cx - half_diameter)
                y = int(cy - half_diameter)
                w = h = ball_diameter_pixels
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)  # Yellow bounding box
                
                # Display distance and angle information
                if show_vertical_angle:
                    info_text = f"Color: {self.team_color} Dist: {distance_cm:.1f}cm H-Angle: {horizontal_angle:.1f}° V-Angle: {vertical_angle:.1f}°"
                else:
                    info_text = f"Color: {self.team_color} Dist: {distance_cm:.1f}cm Angle: {horizontal_angle:.1f}°"
                cv2.putText(frame, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Draw image center lines
                cv2.line(frame, (int(self.img_center_x), 0), (int(self.img_center_x), frame.shape[0]), (0, 255, 255), 2)
                cv2.line(frame, (0, int(self.img_center_y)), (frame.shape[1], int(self.img_center_y)), (0, 255, 255), 2)
                
                # Draw line from center to ball
                cv2.line(frame, (int(self.img_center_x), int(self.img_center_y)), (int(cx), int(cy)), (255, 0, 0), 2)
                
                # Display ball diameter in pixels
                ball_diameter_pixels = max(w, h)
                diameter_text = f"Diameter: {ball_diameter_pixels}px"
                cv2.putText(frame, diameter_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            else:
                # No ball detected
                cv2.putText(frame, f"No {self.team_color} ball detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            # Display mask image (optional)
            mask_rgb = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
            
            # Combine original image and mask for display
            combined = np.hstack((frame, mask_rgb))
            
            # Display window
            cv2.imshow("Ball Detection Test - Press q to quit", combined)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                self.team_color = "red"
                print("Switched to red ball detection")
            elif key == ord('b'):
                self.team_color = "blue"
                print("Switched to blue ball detection")
            elif key == ord('k'):
                self.team_color = "black"
                print("Switched to black ball detection")
            elif key == ord('y'):
                self.team_color = "yellow"
                print("Switched to yellow ball detection")
        
        # Release resources
        self.cap.release()
        cv2.destroyAllWindows()
        print("Program exited")

if __name__ == "__main__":
    tester = BallDetectionTester()
    tester.run()