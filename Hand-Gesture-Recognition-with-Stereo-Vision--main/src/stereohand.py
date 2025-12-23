import cv2
from undistort import calibrator
import mediapipe as mp
import os
import sys
from stereovision import Stereo

# ==========================================
# بخش حیاتی: حل مشکل ایمپورت MediaPipe
# ==========================================
print(">> Attempting to load MediaPipe...")
try:
    # روش ۱: تلاش برای دسترسی مستقیم به فایل‌های پایتون (برای رفع باگ نسخه ۳.۱۱)
    from mediapipe.python.solutions import drawing_utils as mp_drawing
    from mediapipe.python.solutions import drawing_styles as mp_drawing_styles
    from mediapipe.python.solutions import hands as mp_hands
    print(">> Success: MediaPipe loaded via 'mediapipe.python.solutions' (Explicit Mode)")
except ImportError:
    try:
        # روش ۲: روش استاندارد
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles
        mp_hands = mp.solutions.hands
        print(">> Success: MediaPipe loaded via 'mp.solutions' (Standard Mode)")
    except AttributeError:
        print("!! CRITICAL ERROR: Could not load MediaPipe solutions.")
        print("!! Check if 'protobuf' is installed correctly.")
        sys.exit()
# ==========================================

class StereoHand:
    def __init__(self, Stereo_Object:Stereo):
        print(">> Initializing StereoHand...")
        
        # 1. مسیردهی فایل‌های کالیبراسیون
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        calib_path1 = os.path.join(project_root, "calibration objects", "cam1_calib.pkl")
        calib_path2 = os.path.join(project_root, "calibration objects", "cam2_calib.pkl")

        # 2. لود کالیبراسیون
        if os.path.exists(calib_path1) and os.path.exists(calib_path2):
            self.calib = [calibrator(calib_path1), calibrator(calib_path2)]
            print(">> Calibration files loaded.")
        else:
            print(f"!! WARNING: Calibration files missing.")
            self.calib = None

        # 3. ساخت مدل‌های دست (با استفاده از ماژول‌هایی که بالا لود کردیم)
        self.mp_drawing = mp_drawing
        self.mp_drawing_styles = mp_drawing_styles
        self.mp_hands = mp_hands

        self.hands = [
            self.mp_hands.Hands(model_complexity=1, min_detection_confidence=0.5, min_tracking_confidence=0.5), 
            self.mp_hands.Hands(model_complexity=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)
        ]
        
        # 4. باز کردن دوربین‌ها (واقعی)
        # اگر دوربین لپ‌تاپ مزاحم است، اعداد را [1, 2] بگذارید
        camera_indices = [1, 2]
        print(f">> Opening cameras {camera_indices}...")
        
        self.caps = [cv2.VideoCapture(camera_indices[0], cv2.CAP_DSHOW), 
                     cv2.VideoCapture(camera_indices[1], cv2.CAP_DSHOW)]
        
        # چک کردن باز شدن دوربین‌ها
        if not self.caps[0].isOpened() or not self.caps[1].isOpened():
            print("\n" + "!"*40)
            print(f"!! ERROR: Failed to open cameras {camera_indices}")
            print("!! Try changing 'camera_indices' in stereohand.py line 62")
            print("!"*40 + "\n")
            sys.exit()
        else:
            print(">> Cameras started successfully.")

        self.successes = [False, False]
        self.images = [None, None]
        self.results = [None, None]
        self.stereo_object = Stereo_Object 
    
    def get_hand(self):
        self.successes[0], self.images[0] = self.caps[0].read()
        self.successes[1], self.images[1] = self.caps[1].read()

        if not self.successes[0] or not self.successes[1]:
            # اگر فریمی نیامد، رد می‌کنیم
            return False, [(0, 0, 0)]
                
        self.cam_points = [[], []]
        
        for index, image in enumerate(self.images):
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            self.results[index] = self.hands[index].process(image)
            
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # نمایش لندمارک‌ها
            if self.results[index].multi_hand_landmarks:
                for hand_landmarks in self.results[index].multi_hand_landmarks:
                    self.mp_drawing.draw_landmarks(
                        image,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style())
            
            cv2.imshow(f'Camera {index}', cv2.flip(image, 1))
            if cv2.waitKey(1) & 0xFF == 27:
                break
        
        hands_found_in_both = True
        for i in range(2):
            if not self.results[i].multi_hand_landmarks: 
                hands_found_in_both = False

        if not hands_found_in_both:
            return False, [(0, 0, 0)]
        
        for i in range(2):
            self.main_hand = self.results[i].multi_hand_landmarks[0]
            h, w, _ = self.images[i].shape
            self.points = []
            for landmark in self.main_hand.landmark: 
                px = landmark.x * w
                py = landmark.y * h
                self.points.append((px, py))
            self.cam_points[i] = self.points
        
        points3d = []
        for i in range(21):
            p3d = self.stereo_object.locate(self.cam_points[0][i], self.cam_points[1][i]) 
            points3d.append(p3d) 
        
        return True, points3d