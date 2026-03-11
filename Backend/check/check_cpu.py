import torch
from ultralytics import YOLO
import paddle
from paddleocr import PaddleOCR

# Test YOLO
try:
    model = YOLO("yolov8n.pt")
    print("✅ YOLOv8: Success (Running on GPU)")
except Exception as e:
    print(f"❌ YOLOv8 Error: {e}")

# Test Paddle
try:
    # Bare minimum init for stable 2.7.x
    ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False, show_log=False)
    print("✅ PaddleOCR: Success (Running on CPU)")
except Exception as e:
    print(f"❌ PaddleOCR Error: {e}")