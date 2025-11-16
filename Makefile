IMAGE_NAME      ?= satlas-gpu
GPU             ?= all
MODEL_ID        ?= Sentinel2_SwinB_SI_RGB
CHECKPOINT      ?= "/workspace/training_inference/models/satlas/sentinel2_swinb_si_rgb.pth"

PROJECT_DIR     ?= $(PWD)
DATA_DIR        ?= $(PROJECT_DIR)/data

MLFLOW_DIR      ?= $(PROJECT_DIR)/mlruns
MLFLOW_EXPERIMENT ?= initial_test

DOCKER_RUN_GPU  = docker run --rm -it --gpus $(GPU)

.PHONY: build train inference shell mlflow-ui

build:
	docker build -t $(IMAGE_NAME) .

train: build
	$(DOCKER_RUN_GPU) \
	  -v $(PROJECT_DIR):/workspace \
	  $(IMAGE_NAME) \
	  bash -lc "cd /workspace && ruff format ."

	# Train + MLflow UI (http://localhost:5000)
	$(DOCKER_RUN_GPU) -p 5000:5000 \
	  -v $(PROJECT_DIR):/workspace \
	  -v $(DATA_DIR):/data \
	  -v $(MLFLOW_DIR):/mlruns \
	  -e MODEL_ID=$(MODEL_ID) \
	  -e MLFLOW_TRACKING_URI=file:/mlruns \
	  -e MLFLOW_EXPERIMENT_NAME=$(MLFLOW_EXPERIMENT) \
	  $(IMAGE_NAME) \
	  bash -lc 'cd /workspace && \
	    echo "Starting MLflow UI on http://localhost:5000" && \
	    mlflow ui --host 0.0.0.0 --port 5000 & \
	    cd /workspace/training_inference && \
	    python train.py'

inference: build
	$(DOCKER_RUN_GPU) \
	  -v $(PROJECT_DIR):/workspace \
	  $(IMAGE_NAME) \
	  bash -lc "cd /workspace && ruff format ."

	$(DOCKER_RUN_GPU) \
	  -v $(PROJECT_DIR):/workspace \
	  -v $(DATA_DIR):/data \
	  -e MODEL_ID=$(MODEL_ID) \
	  -e CHECKPOINT=$(CHECKPOINT) \
	  $(IMAGE_NAME) \
	  bash -lc 'cd /workspace && python ./training_inference/inference.py'

shell: build
	$(DOCKER_RUN_GPU) \
	  -v $(PROJECT_DIR):/workspace \
	  -v $(DATA_DIR):/data \
	  -e MODEL_ID=$(MODEL_ID) \
	  $(IMAGE_NAME) \
	  bash
