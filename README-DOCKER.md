# Deep-Live-Cam - Docker Deployment Guide

This guide will help you run Deep-Live-Cam using Docker, eliminating the need for manual Python environment setup.

## 🚀 Quick Start

### Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (included with Docker Desktop)
- At least 8GB RAM available
- Required model files (see below)

### Step 1: Download Required Models

Before running the container, download these model files and place them in the `./models` directory:

1. **GFPGANv1.4.pth** (348 MB)
   ```bash
   wget -P ./models https://huggingface.co/hacksider/deep-live-cam/resolve/main/GFPGANv1.4.pth
   ```

2. **inswapper_128_fp16.onnx** (256 MB)
   ```bash
   wget -P ./models https://huggingface.co/hacksider/deep-live-cam/resolve/main/inswapper_128_fp16.onnx
   ```

Or download manually from:
- [GFPGANv1.4.pth](https://huggingface.co/hacksider/deep-live-cam/resolve/main/GFPGANv1.4.pth)
- [inswapper_128_fp16.onnx](https://huggingface.co/hacksider/deep-live-cam/resolve/main/inswapper_128_fp16.onnx)

### Step 2: Build the Docker Image

```bash
docker-compose build
```

Or build directly:
```bash
docker build -t deep-live-cam:cpu .
```

### Step 3: Prepare Your Files

Create input and output directories:
```bash
mkdir -p input output temp
```

Place your source face image and target image/video in the `./input` directory.

### Step 4: Run Deep-Live-Cam

#### Using Docker Compose (Recommended)

Process an image:
```bash
docker-compose run --rm deep-live-cam \
  -s /app/input/source_face.jpg \
  -t /app/input/target_image.jpg \
  -o /app/output/result.jpg \
  --execution-provider cpu
```

Process a video:
```bash
docker-compose run --rm deep-live-cam \
  -s /app/input/source_face.jpg \
  -t /app/input/target_video.mp4 \
  -o /app/output/result.mp4 \
  --execution-provider cpu \
  --keep-fps \
  --keep-audio
```

#### Using Docker Run

```bash
docker run --rm \
  -v $(pwd)/models:/app/models:ro \
  -v $(pwd)/input:/app/input:ro \
  -v $(pwd)/output:/app/output:rw \
  deep-live-cam:cpu \
  -s /app/input/source_face.jpg \
  -t /app/input/target_video.mp4 \
  -o /app/output/result.mp4 \
  --execution-provider cpu
```

## 📁 Directory Structure

```
Deep-Live-Cam/
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── docker/
│   └── entrypoint.sh
├── models/                    # Mount point for model files
│   ├── GFPGANv1.4.pth        # Download separately
│   └── inswapper_128_fp16.onnx
├── input/                     # Place your source and target files here
│   ├── source_face.jpg
│   └── target_video.mp4
├── output/                    # Processed results will appear here
│   └── result.mp4
└── temp/                      # Temporary processing files
```

## ⚙️ Command Line Options

All standard Deep-Live-Cam options are available:

| Option | Description | Example |
|--------|-------------|---------|
| `-s, --source` | Source face image | `-s /app/input/face.jpg` |
| `-t, --target` | Target image/video | `-t /app/input/video.mp4` |
| `-o, --output` | Output file | `-o /app/output/result.mp4` |
| `--execution-provider` | Use CPU | `--execution-provider cpu` |
| `--keep-fps` | Keep original FPS | `--keep-fps` |
| `--keep-audio` | Keep original audio | `--keep-audio` |
| `--many-faces` | Process all faces | `--many-faces` |
| `--video-quality` | Quality (0-51) | `--video-quality 18` |

## 🔧 Advanced Usage

### Custom Resource Limits

Edit `docker-compose.yml` to adjust CPU and memory limits:

```yaml
deploy:
  resources:
    limits:
      cpus: '8'      # Use up to 8 CPU cores
      memory: 16G    # Use up to 16GB RAM
```

### Environment Variables

- `OMP_NUM_THREADS`: Number of OpenMP threads (default: 4)
- `TF_CPP_MIN_LOG_LEVEL`: TensorFlow logging level (default: 2)

Set in docker-compose.yml or via `-e` flag:
```bash
docker run -e OMP_NUM_THREADS=8 ...
```

### Interactive Shell

Access the container shell for debugging:
```bash
docker-compose run --rm --entrypoint /bin/bash deep-live-cam
```

## 🐛 Troubleshooting

### Models Not Found Error

**Error:** `Model not found: /app/models/inswapper_128_fp16.onnx`

**Solution:** Ensure model files are downloaded and placed in `./models/` on your host machine.

### Permission Denied on Output

**Error:** Cannot write to `/app/output`

**Solution:** Ensure the output directory has write permissions:
```bash
chmod -R 777 ./output ./temp
```

### Out of Memory

**Error:** Container killed or crashes during video processing

**Solution:** 
1. Reduce video resolution before processing
2. Increase Docker memory limit in Docker Desktop settings
3. Process shorter video segments

### Slow Performance

**Expected:** CPU-only processing is significantly slower than GPU processing.

**Tips:**
- For long videos, consider processing overnight
- Use `--video-quality` to balance quality vs speed
- Reduce resolution of input videos
- Expected speed: ~1-5 FPS on modern CPUs for 1080p video

## 📊 Performance Expectations

CPU-only performance (approximate):

| Task | Resolution | Speed |
|------|-----------|-------|
| Image | 1920x1080 | 2-5 seconds |
| Video | 1920x1080 | 1-3 FPS |
| Video | 1280x720 | 3-5 FPS |
| Video | 640x480 | 5-10 FPS |

*Speeds vary based on CPU model and available cores*

## 🔒 Security Notes

- Models are mounted as read-only (`:ro`)
- Input files are mounted as read-only (`:ro`)
- Only output directory has write access
- Container runs as non-root user where possible

## 📝 License

This Docker implementation follows the same license as Deep-Live-Cam. Please use responsibly and ethically.

## 🆘 Support

For issues specific to Docker deployment, please check:
1. Docker logs: `docker-compose logs`
2. Container status: `docker ps -a`
3. Model file checksums match official versions

For application issues, refer to the main [README.md](README.md).

