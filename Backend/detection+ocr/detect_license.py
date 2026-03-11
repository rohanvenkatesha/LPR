import cv2
from ultralytics import YOLO

# ----------------------------
# 1️⃣ Load YOLOv8 model
# ----------------------------
model = YOLO("production_models/license_plate_best.pt")  # path to your best.pt

# ----------------------------
# 2️⃣ Open input video
# ----------------------------
input_video_path = "E:\\GitHub\\LPR\\temp.mp4"       # replace with your video
output_video_path = "output_video.mp4"

cap = cv2.VideoCapture(input_video_path)
fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Video writer
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

# ----------------------------
# 3️⃣ Process video frames
# ----------------------------
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Run YOLO detection on frame
    results = model.predict(frame, verbose=False)

    # Draw boxes on frame
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            cls = int(box.cls[0])

            # Draw rectangle and label
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"Plate {conf:.2f}"
            cv2.putText(frame, label, (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Write frame to output video
    out.write(frame)

# ----------------------------
# 4️⃣ Release resources
# ----------------------------
cap.release()
out.release()
cv2.destroyAllWindows()
print(f"✅ Video saved: {output_video_path}")