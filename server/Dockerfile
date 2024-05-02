FROM python:3.12.3

WORKDIR /app

ADD . /app

# Install dependencies
RUN apt update && DEBIAN_FRONTEND=noninteractive apt install -y \
    bash git make vim wget g++ ffmpeg
RUN pip install --no-cache-dir -r requirements.txt

# Build whisper.cpp and download the model
WORKDIR /app/whisper.cpp
RUN make clean 
RUN ./models/download-ggml-model.sh base.en 
RUN UNAME_M=arm64 UNAME_P=arm WHISPER_NO_METAL=1 make -j server
WORKDIR /app

# Server runs on port 8000
EXPOSE 8000

CMD ["python", "run.py", "docker-config.toml"]