import os
import cv2
import re
import warnings

# Suppress the annoying urllib3/requests dependency warning
warnings.filterwarnings("ignore", module="requests")


# --- STEP 1: BYPASS BUGGY EXECUTORS ---
os.environ['FLAGS_use_onednn'] = '0'
os.environ['FLAGS_enable_pir_api'] = '0'
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

# --- STEP 1: INITIALIZE MODELS (GPU for YOLO, CPU for OCR) ---
# 1. Import PyTorch and YOLO (Claims the RTX 4060 safely)
import torch
from ultralytics import YOLO

# 2. Import Paddle (Running safely on CPU, no shm.dll conflicts!)
import paddle
from paddleocr import PaddleOCR

print("Initializing YOLOv8 on RTX 4060...")
yolo_model = YOLO("production_models/license_plate_best.pt")

print("Initializing PaddleOCR on CPU...")
# Notice use_gpu=False. This is the magic fix!
# ocr = PaddleOCR(use_textline_orientation=True, lang='en', device='cpu')
ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False, show_log=False)


# ----------------------------
# 2️⃣ Configuration & Paths
# ----------------------------
input_video_path = r"E:\GitHub\LPR\temp.mp4"
output_video_path = "output_video_ocr.mp4"
output_txt_file = "detected_plates.txt"

states = ["AN","AP","AR","AS","BR","CH","DN","DD","DL","GA","GJ","HR",
          "HP","JK","KA","KL","LD","MP","MH","MN","ML","MZ","NL","OR",
          "PY","PN","RJ","SK","TN","TR","UP","WR"]

special_characters = ['.','!','#','$','%','&','@','[',']','_',' ']

# ----------------------------
# 3️⃣ Video Setup
# ----------------------------
cap = cv2.VideoCapture(input_video_path)
if not cap.isOpened():
    print(f"Error: Could not open video {input_video_path}")
    exit()

fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

f = open(output_txt_file, "w")

print("Processing video frames...")

# ----------------------------
# 4️⃣ Processing Loop
# ----------------------------
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.rotate(frame, cv2.ROTATE_180)

    # YOLO detection on the full frame (GPU)
    results = yolo_model.predict(frame, conf=0.25, verbose=False, device=0) 

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            
            # Extract the license plate area
            cropped_plate = frame[y1:y2, x1:x2]
            if cropped_plate.size == 0:
                continue

            # Run OCR on the tiny crop (CPU)
            ocr_result = ocr.ocr(cropped_plate)

            if not ocr_result or ocr_result[0] is None:
                continue

            txt_cleaned = []
            for line in ocr_result[0]:
                txt_pred = line[1][0]
                txt_conf = line[1][1]
                
                # Filter out "IND" markers and lpip inow confidence
                IND_flag = any(x in txt_pred.upper() for x in ["IN", "IND"])
                if not IND_flag and txt_conf > 0.4:
                    # Clean special characters
                    clean_text = txt_pred.upper()
                    for ch in special_characters:
                        clean_text = clean_text.replace(ch, '')
                    txt_cleaned.append(clean_text)

            # Check for Indian State Code pattern
            state_flag = False
            state_index = -1
            for index, txt in enumerate(txt_cleaned):
                if any(txt.startswith(st) for st in states):
                    state_index = index
                    state_flag = True
                    break

            if state_flag:
                # Merge detected text starting from the state code
                license_number = "".join(txt_cleaned[state_index:])
                
                # Regex for Indian Standard: AA 11 AA 1111
                pattern = r"^[A-Z]{2}\d{2}[A-Z]{1,2}\d{1,4}$"
                if re.match(pattern, license_number) and len(license_number) >= 7:
                    print(f"Detected: {license_number}")
                    f.write(license_number + "\n")
                    f.flush()

                    # Draw visualization
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, license_number, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    out.write(frame)

# ----------------------------
# 5️⃣ Cleanup
# ----------------------------
cap.release()
out.release()
f.close()
cv2.destroyAllWindows()

print(f"\n✅ Done! Video saved to: {output_video_path}")
print(f"✅ Data saved to: {output_txt_file}")