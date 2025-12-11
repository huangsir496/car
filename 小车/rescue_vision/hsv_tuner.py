import cv2
import numpy as np
import json
import os
from config import COLOR_RANGES, CAMERA_CONFIG

class HSVTuner:
    def __init__(self):
        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, CAMERA_CONFIG["resolution"][0])
        self.cap.set(4, CAMERA_CONFIG["resolution"][1])
        
        # Current color to tune
        self.current_color = "red"
        self.is_red_second_range = False  # For red color's second range
        
        # Get HSV range from config
        self.color_ranges = COLOR_RANGES.copy()
        
        # Create windows
        cv2.namedWindow("HSV Tuner")
        cv2.namedWindow("Mask")
        
        # Load initial values
        self.load_current_hsv()
        
        # Create sliders with initial values
        self.create_sliders()
        
        print("HSV Tuner started")
        print("Keyboard Controls:")
        print("r - Switch to red color")
        print("b - Switch to blue color")
        print("k - Switch to black color")
        print("y - Switch to yellow color")
        print("w - Switch to white color")
        print("2 - Toggle between red's first/second range")
        print("s - Save current settings to config.py")
        print("q - Quit")
        
    def create_sliders(self):
        """Create HSV sliders"""
        cv2.createTrackbar("H Min", "HSV Tuner", self.h_min, 179, self.on_h_min_change)
        cv2.createTrackbar("H Max", "HSV Tuner", self.h_max, 179, self.on_h_max_change)
        cv2.createTrackbar("S Min", "HSV Tuner", self.s_min, 255, self.on_s_min_change)
        cv2.createTrackbar("S Max", "HSV Tuner", self.s_max, 255, self.on_s_max_change)
        cv2.createTrackbar("V Min", "HSV Tuner", self.v_min, 255, self.on_v_min_change)
        cv2.createTrackbar("V Max", "HSV Tuner", self.v_max, 255, self.on_v_max_change)
        
    def load_current_hsv(self):
        """Load current HSV values for the selected color"""
        color_range = self.color_ranges[self.current_color]
        
        if self.current_color == "red":
            if self.is_red_second_range:
                # Second range (indices 6-11)
                self.h_min = color_range[6]
                self.s_min = color_range[7]
                self.v_min = color_range[8]
                self.h_max = color_range[9]
                self.s_max = color_range[10]
                self.v_max = color_range[11]
            else:
                # First range (indices 0-5)
                self.h_min = color_range[0]
                self.s_min = color_range[1]
                self.v_min = color_range[2]
                self.h_max = color_range[3]
                self.s_max = color_range[4]
                self.v_max = color_range[5]
        else:
            # For other colors
            if len(color_range) == 2:
                # Tuple format [(h_min,s_min,v_min),(h_max,s_max,v_max)]
                lower, upper = color_range
                self.h_min, self.s_min, self.v_min = lower
                self.h_max, self.s_max, self.v_max = upper
            elif len(color_range) == 6:
                # List format [h_min,s_min,v_min,h_max,s_max,v_max]
                self.h_min, self.s_min, self.v_min, self.h_max, self.s_max, self.v_max = color_range
        
        # Update sliders only if they exist
        try:
            self.update_sliders()
        except cv2.error:
            pass
        
    def update_sliders(self):
        """Update sliders with current HSV values"""
        cv2.setTrackbarPos("H Min", "HSV Tuner", self.h_min)
        cv2.setTrackbarPos("H Max", "HSV Tuner", self.h_max)
        cv2.setTrackbarPos("S Min", "HSV Tuner", self.s_min)
        cv2.setTrackbarPos("S Max", "HSV Tuner", self.s_max)
        cv2.setTrackbarPos("V Min", "HSV Tuner", self.v_min)
        cv2.setTrackbarPos("V Max", "HSV Tuner", self.v_max)
        
    def on_h_min_change(self, value):
        self.h_min = value
    def on_h_max_change(self, value):
        self.h_max = value
    def on_s_min_change(self, value):
        self.s_min = value
    def on_s_max_change(self, value):
        self.s_max = value
    def on_v_min_change(self, value):
        self.v_min = value
    def on_v_max_change(self, value):
        self.v_max = value
        
    def update_config(self):
        """Update current color's HSV values in the config"""
        if self.current_color == "red":
            # Red has two ranges
            if self.color_ranges["red"] is None or len(self.color_ranges["red"]) != 12:
                self.color_ranges["red"] = [0]*12
                
            if self.is_red_second_range:
                # Update second range
                self.color_ranges["red"][6] = self.h_min
                self.color_ranges["red"][7] = self.s_min
                self.color_ranges["red"][8] = self.v_min
                self.color_ranges["red"][9] = self.h_max
                self.color_ranges["red"][10] = self.s_max
                self.color_ranges["red"][11] = self.v_max
            else:
                # Update first range
                self.color_ranges["red"][0] = self.h_min
                self.color_ranges["red"][1] = self.s_min
                self.color_ranges["red"][2] = self.v_min
                self.color_ranges["red"][3] = self.h_max
                self.color_ranges["red"][4] = self.s_max
                self.color_ranges["red"][5] = self.v_max
        else:
            # For other colors, use 6-value list format
            self.color_ranges[self.current_color] = [
                self.h_min, self.s_min, self.v_min, 
                self.h_max, self.s_max, self.v_max
            ]
            
    def save_to_config(self):
        """Save current HSV settings to config.py"""
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, "config.py")
        
        # Read current config.py
        with open(config_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # Find COLOR_RANGES section
        start_idx = None
        end_idx = None
        for i, line in enumerate(lines):
            if "COLOR_RANGES = {" in line:
                start_idx = i
            elif start_idx is not None and line.strip() == "}":
                end_idx = i
                break
        
        if start_idx is None or end_idx is None:
            print("Failed to find COLOR_RANGES section in config.py")
            return
        
        # Generate new COLOR_RANGES lines
        new_lines = ["COLOR_RANGES = {\n"]
        for color, values in self.color_ranges.items():
            # Format the values with proper spacing
            values_str = ", ".join(map(str, values))
            new_lines.append(f"    \"{color}\": [{values_str}],  # {color}目标，配置方法：在实际环境下调整H值\n")
        new_lines.append("}\n")
        
        # Replace the old section with new section
        new_file_content = lines[:start_idx] + new_lines + lines[end_idx+1:]
        
        # Write back to config.py
        with open(config_path, "w", encoding="utf-8") as f:
            f.writelines(new_file_content)
        
        print("HSV settings saved to config.py")
        
    def run(self):
        """Main loop"""
        while True:
            # Read frame
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to read camera frame")
                break
            
            # Convert to HSV
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Create mask
            lower = np.array([self.h_min, self.s_min, self.v_min])
            upper = np.array([self.h_max, self.s_max, self.v_max])
            mask = cv2.inRange(hsv, lower, upper)
            
            # Show original frame with HSV info
            info = f"Color: {self.current_color}"
            if self.current_color == "red":
                info += f" Range: {'Second' if self.is_red_second_range else 'First'}"
            info += f" HSV: [{self.h_min}, {self.s_min}, {self.v_min}] - [{self.h_max}, {self.s_max}, {self.v_max}]"
            
            cv2.putText(frame, info, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            cv2.imshow("HSV Tuner", frame)
            cv2.imshow("Mask", mask)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                self.current_color = "red"
                self.is_red_second_range = False
                self.load_current_hsv()
            elif key == ord('b'):
                self.current_color = "blue"
                self.load_current_hsv()
            elif key == ord('k'):
                self.current_color = "black"
                self.load_current_hsv()
            elif key == ord('y'):
                self.current_color = "yellow"
                self.load_current_hsv()
            elif key == ord('w'):
                self.current_color = "white"
                self.load_current_hsv()
            elif key == ord('2') and self.current_color == "red":
                self.is_red_second_range = not self.is_red_second_range
                self.load_current_hsv()
            elif key == ord('s'):
                self.update_config()
                self.save_to_config()
        
        # Cleanup
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    tuner = HSVTuner()
    tuner.run()
