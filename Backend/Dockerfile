FROM python:3.10-slim

WORKDIR /app
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

# -------------------------
# Copy only requirements first (for caching)
COPY requirements_cpu.txt requirements_cpu.txt
COPY requirements_gpu.txt requirements_gpu.txt

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# -------------------------
# Install dependencies
# By default, CPU
RUN pip install --no-cache-dir -r requirements_cpu.txt

# ⚡ Optional GPU users:
# 1. Run check_gpu.py to confirm CUDA version (12.1 recommended)

# 2. If GPU compatible, comment the line above and uncomment below:
# RUN pip install --no-cache-dir -r requirements_gpu.txt
# -------------------------

# Copy backend code
COPY . .

# Ensure temp folder exists
RUN mkdir -p temp

# Expose FastAPI port
EXPOSE 8000

# Start server
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]