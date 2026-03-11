# video_service.py
import cv2
from models.ai_models import get_models
from utils.plate_utils import clean_plate_text, validate_indian_plate
from datetime import datetime
import os
import csv

TEMP_FOLDER = "temp"
os.makedirs(TEMP_FOLDER, exist_ok=True)

CSV_FILE = os.path.join(TEMP_FOLDER, "plates_log.csv")


def save_plate_to_csv(plate, timestamp):
    """
    Append a plate and timestamp to CSV log.
    """
    file_exists = os.path.isfile(CSV_FILE)

    with open(CSV_FILE, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)

        if not file_exists:
            writer.writerow(["plate", "timestamp"])

        writer.writerow([plate, timestamp])


def process_video(video_path, websocket_callback=None):
    """
    Process a video for license plates.

    Args:
        video_path (str): Path to video file.
        websocket_callback (function, optional): Callback to send plate data live.
    """

    yolo_model, ocr_model = get_models()
    tracked_plates = {}
    results_to_return = []

    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    output_video_path = os.path.join(TEMP_FOLDER, "detected_output.mp4")

    # Clear CSV logs for new video
    open(CSV_FILE, "w").close()

    # Video writer
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Rotate frame if needed
        frame = cv2.rotate(frame, cv2.ROTATE_180)

        # YOLO tracking
        yolo_results = yolo_model.track(
            source=frame,
            persist=True,
            verbose=False,
            conf=0.5,
            tracker="botsort.yaml"
        )

        for result in yolo_results:
            if result.boxes is None or result.boxes.id is None:
                continue

            boxes = result.boxes.xyxy.cpu().numpy().astype(int)
            track_ids = result.boxes.id.cpu().numpy().astype(int)

            for box, track_id in zip(boxes, track_ids):
                x1, y1, x2, y2 = box

                if track_id in tracked_plates:
                    license_number = tracked_plates[track_id]
                else:
                    cropped_plate = frame[
                        max(0, y1):min(height, y2),
                        max(0, x1):min(width, x2)
                    ]

                    if cropped_plate.size == 0:
                        continue

                    ocr_result = ocr_model.ocr(cropped_plate)
                    license_number = None

                    if ocr_result and ocr_result[0]:
                        raw_texts = [(line[1][0], line[1][1]) for line in ocr_result[0]]
                        cleaned_texts = clean_plate_text(raw_texts)
                        full_str = "".join(cleaned_texts)

                        if validate_indian_plate(full_str):
                            license_number = full_str
                            tracked_plates[track_id] = license_number

                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                            # Save to CSV
                            save_plate_to_csv(license_number, timestamp)

                            results_to_return.append({
                                "plate": license_number,
                                "timestamp": timestamp
                            })

                            # Send live plate to frontend via WebSocket
                            if websocket_callback:
                                websocket_callback({
                                    "plate": license_number,
                                    "timestamp": timestamp
                                })

                # Draw bounding boxes
                if track_id in tracked_plates:
                    label = f"ID:{track_id} {tracked_plates[track_id]}"
                    color = (0, 255, 0)
                else:
                    label = f"ID:{track_id} Reading..."
                    color = (0, 255, 255)

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # Save annotated frame
        out.write(frame)

    cap.release()
    out.release()

    # Notify frontend that video processing is complete
    if websocket_callback:
        websocket_callback({"type": "video_complete"})

    return results_to_return