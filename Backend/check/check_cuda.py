import torch

print("CUDA available:", torch.cuda.is_available())
print("GPU:", torch.cuda.get_device_name(0))
print("Number of GPUs:", torch.cuda.device_count())
print(torch.version.cuda)
