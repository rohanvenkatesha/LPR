# 🚗 License Plate Recognition System

A full-stack **License Plate Recognition (LPR)** system built with **Computer Vision, FastAPI, and Next.js**.
It detects license plates from uploaded videos, extracts plate text using OCR, streams detections live via **WebSockets**, and provides downloadable processed videos and CSV logs.

---

# 🐳 Docker Deployment (Recommended)

We provide Docker files for **easy deployment**. By default, it runs on **CPU**.

If you have a GPU and compatible CUDA, you can enable GPU support (optional).

## Steps

1. **Check your GPU (optional)**

```bash
python Backend/check/check_gpu.py
```

2. **CPU users:** No changes needed. Docker will install CPU dependencies.

3. **GPU users:** If CUDA version is compatible (e.g., 12.1), uncomment the GPU line in `Backend/Dockerfile` and comment the CPU line.

4. **Build and run with Docker Compose:**

```bash
docker-compose up --build
```

5. **Access the services:**

| Service            | URL                                            |
| ------------------ | ---------------------------------------------- |
| Backend (FastAPI)  | [http://localhost:8000](http://localhost:8000) |
| Frontend (Next.js) | [http://localhost:3000](http://localhost:3000) |

---

# 📌 Features

* Upload vehicle videos
* YOLO-based license plate detection
* PaddleOCR text recognition
* Live plate detection via WebSockets
* CSV log of detected plates
* Download processed video
* GPU support (optional)
* Modular backend and modern Next.js frontend

---

# 🧠 Tech Stack

## Backend

* Python 3.10
* FastAPI + Uvicorn
* OpenCV
* YOLO (license plate detection)
* PaddleOCR (text recognition)
* WebSockets

## Frontend

* Next.js 14+
* React 18+
* Tailwind CSS

---

# 🏗 Project Structure

```text
project-root
│
├── Backend
│   ├── server.py
│   ├── requirements_cpu.txt
│   ├── requirements_gpu.txt
│   ├── models/ai_models.py
│   ├── production_models/license_plate_best.pt
│   ├── production_models/paddle_ocr_models/
│   ├── routes/upload_routes.py
│   ├── services/video_service.py
│   ├── utils/plate_utils.py
│   ├── check/check_cpu.py
│   ├── check/check_gpu.py
│   ├── check/check_cuda.py
│   └── temp/
│       ├── input_video.mp4
│       ├── detected_output.mp4
│       └── plates_log.csv
│
├── Frontend
│   ├── .env.local
│   ├── package.json
│   ├── next.config.js
│   ├── app/
│   ├── components/
│   └── public/ui-preview.png
│
└── docker-compose.yml
```

---

# 🧠 Model Training

Dataset and training notebook available on Kaggle:

[Indian License Plates Dataset](https://www.kaggle.com/datasets/rohanvenkatesha/indian-license-plates)

Trained models used for inference are stored in:

```
Backend/production_models/
```

---

# ⚙️ Manual Backend Setup (FastAPI)

1. Navigate to backend:

```bash
cd Backend
```

2. Create virtual environment:

```bash
python -m venv venv
```

Activate environment:

* Windows:

```bash
venv\Scripts\activate
```

* Mac/Linux:

```bash
source venv/bin/activate
```

3. Install dependencies (CPU default):

```bash
pip install -r requirements_cpu.txt
```

GPU users:

* Verify CUDA version (`check_gpu.py`)
* If compatible, install GPU dependencies instead:

```bash
pip install -r requirements_gpu.txt
```

4. Run server:

```bash
uvicorn server:app --reload
```

Backend will run at: `http://localhost:8000`

---

# ⚙️ Manual Frontend Setup (Next.js)

1. Navigate to frontend:

```bash
cd Frontend
```

2. Install dependencies:

```bash
npm install
# or
yarn install
```

3. Run development server:

```bash
npm run dev
```

Frontend will run at: `http://localhost:3000`

---

# 🔑 Frontend Environment Variables

Create `.env.local` in **Frontend** root:

```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

Production example:

```env
NEXT_PUBLIC_BACKEND_URL=https://your-backend.com
NEXT_PUBLIC_WS_URL=wss://your-backend.com/ws
```

---

# 🔌 API Endpoints

## Health Check

```
GET /
```

Response:

```json
{
 "status": "ok",
 "message": "License Plate Recognition API is running"
}
```

## Upload Video

```
POST /upload-video
```

Supported formats: `.mp4`, `.mov`, `.avi`, `.mkv`

## WebSocket (Live Plate Detection)

```
ws://localhost:8000/ws
```

Example message:

```json
{
 "plate": "KA01AB1234",
 "timestamp": "2026-03-10 14:23:12"
}
```

Video processing complete:

```json
{
 "type": "video_complete"
}
```

---

# ⚡ GPU Support (Optional)

* PyTorch GPU:

```bash
pip install torch==2.5.1+cu121 torchvision==0.20.1+cu121 torchaudio==2.5.1+cu121 --index-url https://download.pytorch.org/whl/cu121
```

* PaddlePaddle GPU:

```bash
pip install paddlepaddle-gpu==2.6.2.post121 -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html
```

* Enable GPU in `Backend/models/ai_models.py`:

```python
ocr = PaddleOCR(
    use_angle_cls=True,
    lang="en",
    use_gpu=True
)
```

If GPU unavailable, code will **automatically fall back to CPU**.

---

# 🖥 Hardware Check Utilities

Located in:

```
Backend/check/
```

Scripts:

* `check_cpu.py` → CPU check
* `check_gpu.py` → GPU check
* `check_cuda.py` → CUDA check

---

# 🖥 UI Preview

![UI Preview](Frontend/public/ui-preview.png)

---

# 📂 Temporary Files

Stored in:

```
Backend/temp/
```

Includes:

```
input_video.mp4
detected_output.mp4
plates_log.csv
```

---

# 📜 License

MIT License

---

# 👨‍💻 Author

**[Rohan Venkatesha](https://rohanvenkatesha.vercel.app/)**
Software Engineer

---
