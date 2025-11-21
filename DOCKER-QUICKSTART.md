# Docker Quick Start Guide

## ✅ What Was Created

The following Docker deployment files have been added to your Deep-Live-Cam project:

1. **Dockerfile** - Multi-stage build configuration (CPU-only)
2. **.dockerignore** - Excludes unnecessary files from Docker image
3. **docker-compose.yml** - Service orchestration configuration
4. **docker/entrypoint.sh** - Container startup script with model validation
5. **requirements-docker.txt** - CPU-only Python dependencies
6. **README-DOCKER.md** - Comprehensive documentation
7. **docker-build.sh** - Automated build script

## 🚀 Getting Started (3 Steps)

### Step 1: Download Models
```bash
# Create models directory
mkdir -p models

# Download required models (600MB total)
wget -P ./models https://huggingface.co/hacksider/deep-live-cam/resolve/main/GFPGANv1.4.pth
wget -P ./models https://huggingface.co/hacksider/deep-live-cam/resolve/main/inswapper_128_fp16.onnx
```

### Step 2: Build Docker Image
```bash
# Use the automated build script
./docker-build.sh

# Or manually with docker-compose
docker-compose build
```

Build time: ~10-15 minutes (depending on internet speed)

### Step 3: Run Deep-Live-Cam

#### Image Processing Example
```bash
# 1. Place your files in the input directory
mkdir -p input output
cp /path/to/source_face.jpg ./input/
cp /path/to/target_image.jpg ./input/

# 2. Run the container
docker-compose run --rm deep-live-cam \
  -s /app/input/source_face.jpg \
  -t /app/input/target_image.jpg \
  -o /app/output/result.jpg \
  --execution-provider cpu

# 3. Find your result in ./output/result.jpg
```

#### Video Processing Example
```bash
# Place source and target files
cp /path/to/source_face.jpg ./input/
cp /path/to/target_video.mp4 ./input/

# Process video (this will take time on CPU)
docker-compose run --rm deep-live-cam \
  -s /app/input/source_face.jpg \
  -t /app/input/target_video.mp4 \
  -o /app/output/result.mp4 \
  --execution-provider cpu \
  --keep-fps \
  --keep-audio

# Monitor progress in terminal
```

## 📁 Directory Structure

After setup, your project structure will look like:

```
Deep-Live-Cam/
├── Dockerfile                 ← Docker image definition
├── docker-compose.yml         ← Docker orchestration
├── docker-build.sh           ← Build helper script
├── .dockerignore             ← Files to exclude from image
├── requirements-docker.txt    ← CPU-only dependencies
├── README-DOCKER.md          ← Full documentation
├── DOCKER-QUICKSTART.md      ← This file
├── docker/
│   └── entrypoint.sh         ← Container startup script
├── models/                    ← DOWNLOAD MODELS HERE
│   ├── GFPGANv1.4.pth
│   └── inswapper_128_fp16.onnx
├── input/                     ← YOUR INPUT FILES
│   ├── source_face.jpg
│   └── target_video.mp4
└── output/                    ← PROCESSED RESULTS
    └── result.mp4
```

## ⚡ Common Commands

### View Available Options
```bash
docker-compose run --rm deep-live-cam --help
```

### Process with All Faces
```bash
docker-compose run --rm deep-live-cam \
  -s /app/input/source.jpg \
  -t /app/input/target.mp4 \
  -o /app/output/result.mp4 \
  --execution-provider cpu \
  --many-faces
```

### Better Quality (Slower)
```bash
docker-compose run --rm deep-live-cam \
  -s /app/input/source.jpg \
  -t /app/input/target.mp4 \
  -o /app/output/result.mp4 \
  --execution-provider cpu \
  --video-quality 10 \
  --frame-processor face_swapper face_enhancer
```

### Interactive Shell (for debugging)
```bash
docker-compose run --rm --entrypoint /bin/bash deep-live-cam
```

## 🐛 Troubleshooting

### Issue: "Model not found"
**Solution:** Download models to `./models/` directory (see Step 1)

### Issue: "Permission denied" on output
**Solution:** 
```bash
chmod -R 777 ./output ./temp
```

### Issue: Build fails with "network timeout"
**Solution:** 
```bash
# Retry the build
docker-compose build --no-cache
```

### Issue: Container is slow
**Expected:** CPU-only processing is 10-20x slower than GPU
**Speeds:** ~1-3 FPS for 1080p video on modern CPUs

### Issue: Out of memory
**Solution:** Adjust memory limits in docker-compose.yml:
```yaml
deploy:
  resources:
    limits:
      memory: 16G  # Increase this
```

## 🎯 Performance Tips

1. **Reduce video resolution** before processing
2. **Process shorter segments** for long videos
3. **Increase CPU allocation** in docker-compose.yml (limits.cpus)
4. **Use lower quality settings** for faster preview (--video-quality 30)
5. **Close other applications** to free up system resources

## 📊 Expected Processing Times (CPU)

| Input | Resolution | Duration | Approx. Time |
|-------|-----------|----------|--------------|
| Image | 1920x1080 | N/A | 3-5 seconds |
| Video | 1920x1080 | 10 sec | 30-100 seconds |
| Video | 1920x1080 | 1 min | 5-10 minutes |
| Video | 1280x720 | 1 min | 2-5 minutes |

*Times vary based on CPU model (measured on modern 4-core CPUs)*

## 🔄 Updating

To update the Docker image after code changes:

```bash
# Rebuild the image
docker-compose build --no-cache

# Or use the build script
./docker-build.sh
```

## 🔒 Security Notes

- Models are mounted read-only (`:ro`)
- Input directory is read-only (`:ro`)
- Only output directory has write access
- Container runs with minimal privileges

## 📖 More Information

For comprehensive documentation, see:
- **README-DOCKER.md** - Full Docker documentation
- **README.md** - Main application documentation
- **CONTRIBUTING.md** - Development guidelines

## ❓ Getting Help

1. Check logs: `docker-compose logs`
2. Verify models: `ls -lh models/`
3. Test with small files first
4. Refer to README-DOCKER.md for detailed troubleshooting

---

**Ready to process your first deepfake!** 🎭

Start with Step 1 above to download the models, then follow the examples.

