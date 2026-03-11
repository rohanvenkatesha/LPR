from ultralytics import YOLO
from paddleocr import PaddleOCR

yolo_model = None
ocr_model = None

def load_models():
    global yolo_model, ocr_model

    print("Loading YOLOv8 Tracker...")
    yolo_model = YOLO("production_models/license_plate_best.pt")

    print("Loading PaddleOCR...")
    ocr_model = PaddleOCR(
        use_angle_cls=True,
        lang='en',
        use_gpu=False,
        show_log=False
    )
    print("Models loaded!")

def get_models():
    return yolo_model, ocr_model