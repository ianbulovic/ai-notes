FROM python:3.12.3

WORKDIR /app

# Add only requirements.txt first to leverage Docker caching for dependencies
ADD requirements.txt /app/

# Install dependencies
RUN apt update && DEBIAN_FRONTEND=noninteractive apt install -y \
    bash git make vim wget g++ ffmpeg && \
    pip install --no-cache-dir -r requirements.txt

# Add the rest of the application files
ADD . /app

# Build whisper.cpp and download the model
WORKDIR /app/whisper.cpp
RUN make clean && \
    ./models/download-ggml-model.sh base.en && \
    UNAME_M=arm64 UNAME_P=arm WHISPER_NO_METAL=1 make -j server

# Move back to app directory
WORKDIR /app

# Server runs on port 8000
EXPOSE 8000

CMD ["python", "run.py", "docker-config.toml"]
