import cv2
from ultralytics import YOLO
from paddleocr import PaddleOCR
import re

# --- Initialize models ---
yolo_model = YOLO("E:\\GitHub\\LPR\\Backend\\production_models\\license_plate_best.pt")
ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False, show_log=False)

# --- Configuration ---
image_path = r"E:\\GitHub\\LPR\\test_image.jpg"
states = ["AN","AP","AR","AS","BR","CH","DN","DD","DL","GA","GJ","HR",
          "HP","JK","KA","KL","LD","MP","MH","MN","ML","MZ","NL","OR",
          "PY","PN","RJ","SK","TN","TR","UP","WR"]
special_characters = ['.','!','#','$','%','&','@','[',']','_',' ']

# Load image
frame = cv2.imread(image_path)
height, width = frame.shape[:2]

# --- Detect & Track (tracking optional for single image) ---
results = yolo_model.predict(frame, conf=0.25, verbose=False, device=0)

# For storing OCR results
tracked_plates = {}

for result in results:
    if result.boxes is None:
        continue
    
    boxes = result.boxes.xyxy.cpu().numpy().astype(int)
    track_ids = result.boxes.id.cpu().numpy().astype(int)

    for box, track_id in zip(boxes, track_ids):
        x1, y1, x2, y2 = box
        cropped_plate = frame[max(0, y1):min(height, y2), max(0, x1):min(width, x2)]
        if cropped_plate.size == 0: 
            continue

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

            full_str = "".join(txt_cleaned)
            if any(full_str.startswith(st) for st in states):
                pattern = r"^[A-Z]{2}\d{2}[A-Z]{1,2}\d{1,4}$"
                if re.match(pattern, full_str) and len(full_str) >= 7:
                    license_number = full_str
                    tracked_plates[track_id] = license_number
                    print(f"✅ ID {track_id} Detected Plate: {license_number}")

        # --- Visualization ---
        color = (0, 255, 0) if license_number else (0, 255, 255)
        label = f"ID:{track_id} {license_number}" if license_number else f"ID:{track_id} Reading..."
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

# Show the result
cv2.imshow("License Plate Detection", frame)
cv2.waitKey(0)
cv2.destroyAllWindows()