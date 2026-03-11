import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'

# 1. ALWAYS import paddle first
import paddle
print(f"Paddle GPU works: {paddle.device.is_compiled_with_cuda()}")

# 2. Then import torch/ultralytics
import torch
from ultralytics import YOLO
print(f"YOLO GPU works: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"Using GPU: {torch.cuda.get_device_name(0)}")

# 3. Test OCR Initialization
from paddleocr import PaddleOCR
try:
    ocr = PaddleOCR(use_gpu=True, lang='en', show_log=False)
    print("OCR Engine: Ready on GPU")
except Exception as e:
    print(f"OCR Error: {e}")