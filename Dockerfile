FROM pytorch/pytorch:2.3.1-cuda12.1-cudnn8-runtime

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /workspace

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    satlaspretrain-models \
    numpy \
    pandas \
    pillow \
    matplotlib \
    scikit-learn \
    opencv-python-headless \
    ruff \
    mlflow \
    tqdm

RUN <<EOF
python3 - <<'PYCODE'
import torch
print("PyTorch version:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())
PYCODE
EOF

CMD ["bash"]
