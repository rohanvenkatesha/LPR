import os
import cv2
import re
import warnings

# --- 1. ENVIRONMENT SETUP ---
warnings.filterwarnings("ignore", module="requests")
os.environ['FLAGS_use_onednn'] = '0'
os.environ['FLAGS_enable_pir_api'] = '0'
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

# import torch
from ultralytics import YOLO
# import paddle
from paddleocr import PaddleOCR

# --- 2. INITIALIZE MODELS ---
print("Loading YOLOv8 Tracker on RTX 4060...")
# Using tracking-capable model
yolo_model = YOLO("production_models/license_plate_best.pt") 

print("Loading PaddleOCR on CPU...")
ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False, show_log=False)

# --- 3. CONFIGURATION & TRACKING STORE ---
input_video_path = r"E:\GitHub\LPR\temp.mp4"
output_video_path = "output_tracked_lpr.mp4"
output_txt_file = "database_ready_logs.txt"

# Memory to store {track_id: "CLEAN_LICENSE_PLATE"}
# This persists for the duration of the video
tracked_plates = {} 

states = ["AN","AP","AR","AS","BR","CH","DN","DD","DL","GA","GJ","HR",
          "HP","JK","KA","KL","LD","MP","MH","MN","ML","MZ","NL","OR",
          "PY","PN","RJ","SK","TN","TR","UP","WR"]

special_characters = ['.','!','#','$','%','&','@','[',']','_',' ']

# --- 4. VIDEO INITIALIZATION ---
cap = cv2.VideoCapture(input_video_path)
fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))

f = open(output_txt_file, "w")

print("Processing video with Tracking...")

# --- 5. MAIN PROCESSING LOOP ---
while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break

    frame = cv2.rotate(frame, cv2.ROTATE_180)

    # .track() keeps IDs consistent across frames using BoT-SORT
    # persist=True is mandatory for video tracking
    # results = yolo_model.track(frame, conf=0.5, persist=True, verbose=False, device=0)
    # results = yolo_model.track(frame, conf=0.25, persist=True, verbose=False, tracker="bytetrack.yaml")
    # results = yolo_model.track(frame, conf=0.25, persist=True, verbose=False, device=0)
    results = yolo_model.track(
        source=frame, 
        persist=True, 
        conf=0.5,      # Stricter confidence prevents the warning
        iou=0.5,       # Helps handle overlapping detections
        tracker="botsort.yaml", # This is the "normal" default
        verbose=False,
        # device=0
    )
    for result in results:
        if result.boxes is None or result.boxes.id is None:
            continue
            
        # Extract boxes and track IDs
        boxes = result.boxes.xyxy.cpu().numpy().astype(int)
        track_ids = result.boxes.id.cpu().numpy().astype(int)

        for box, track_id in zip(boxes, track_ids):
            x1, y1, x2, y2 = box
            
            # --- LOGIC: If we already have a high-quality read for this ID, skip OCR ---
            if track_id in tracked_plates:
                license_number = tracked_plates[track_id]
            else:
                # Perform OCR only on new IDs or IDs we haven't read yet
                cropped_plate = frame[max(0, y1):min(height, y2), max(0, x1):min(width, x2)]
                if cropped_plate.size == 0: continue

                ocr_result = ocr.ocr(cropped_plate)
                license_number = None

                if ocr_result and ocr_result[0] is not None:
                    txt_cleaned = []
                    for line in ocr_result[0]:
                        txt_pred, txt_conf = line[1][0], line[1][1]
                        
                        if "IND" not in txt_pred.upper() and txt_conf > 0.5:
                            clean_text = txt_pred.upper()
                            for ch in special_characters:
                                clean_text = clean_text.replace(ch, '')
                            txt_cleaned.append(clean_text)

                    # Pattern Matching for Indian Plates
                    full_str = "".join(txt_cleaned)
                    if any(full_str.startswith(st) for st in states):
                        pattern = r"^[A-Z]{2}\d{2}[A-Z]{1,2}\d{1,4}$"
                        if re.match(pattern, full_str) and len(full_str) >= 7:
                            license_number = full_str
                            
                            # SAVE TO "DATABASE" (Text file for now)
                            tracked_plates[track_id] = license_number
                            f.write(f"ID:{track_id} | Plate:{license_number} | Status:Logged\n")
                            f.flush()
                            print(f"✅ ID {track_id} Registered: {license_number}")

            # --- VISUALIZATION ---
            if license_number:
                # Green for successfully identified plates
                color = (0, 255, 0)
                label = f"ID:{track_id} {license_number}"
            else:
                # Yellow for tracking but no OCR read yet
                color = (0, 255, 255)
                label = f"ID:{track_id} Reading..."

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    out.write(frame)

# --- 6. CLEANUP ---
cap.release()
out.release()
f.close()
cv2.destroyAllWindows()
print(f"Finished. Unique vehicles logged: {len(tracked_plates)}")