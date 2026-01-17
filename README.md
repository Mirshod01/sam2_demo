# SAM2 Demo with YOLO Export

SAM2 (Segment Anything Model 2) video segmentation demo with automatic YOLO format export functionality.

## Features

- Video object segmentation and tracking
- Export tracking results to YOLO format
- Automatic deployment via GitHub Actions
- Docker support for easy deployment

## YOLO Export

After tracking objects in a video, click "Export YOLO Format" button to download a ZIP file containing:

```
session_{id}/
├── classes.txt          # Object class names (object_0, object_1, ...)
├── labels/              # YOLO format annotations
│   ├── frame_0000.txt   # Format: class_id center_x center_y width height
│   ├── frame_0001.txt
│   └── ...
└── metadata.json        # Session metadata
```

## Local Development

### Prerequisites

- Python 3.10+
- Node.js 18+
- CUDA-capable GPU (recommended)

### Backend Setup

```bash
cd demo/backend/server

# Install dependencies
pip install flask flask-cors strawberry-graphql[flask] torch opencv-python numpy pycocotools dataclasses-json

# Run server
python app.py
```

### Frontend Setup

```bash
cd demo/frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

## Deployment to Vast.ai

### Initial Setup

1. **Create a Vast.ai instance** with GPU support

2. **Connect to your instance via SSH**
   ```bash
   ssh root@<vast-ai-ip> -p <port>
   ```

3. **Clone the repository**
   ```bash
   cd /workspace
   git clone git@github.com:Mirshod01/sam2_demo.git
   cd sam2_demo
   ```

4. **Run initial deployment**
   ```bash
   ./deploy.sh
   ```

### Automatic Deployment via GitHub Actions

1. **Add GitHub Secrets** (Settings → Secrets → Actions):
   - `VASTAI_HOST`: Your Vast.ai instance IP
   - `VASTAI_USERNAME`: SSH username (usually `root`)
   - `VASTAI_SSH_KEY`: Your SSH private key
   - `VASTAI_PORT`: SSH port (from Vast.ai dashboard)

2. **Setup SSH Key on Vast.ai**
   ```bash
   # On your local machine, copy your SSH public key
   cat ~/.ssh/id_rsa.pub

   # On Vast.ai server, add it to authorized_keys
   echo "your-public-key" >> ~/.ssh/authorized_keys
   ```

3. **Enable Auto-deployment**

   Now, every time you push to `main` branch:
   ```bash
   git add .
   git commit -m "Update features"
   git push origin main
   ```

   GitHub Actions will automatically:
   - Pull latest code on Vast.ai server
   - Install/update dependencies
   - Rebuild frontend
   - Restart services

### Docker Deployment (Alternative)

```bash
# Build and run with Docker Compose
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Configuration

### Environment Variables

Create `.env` file in `demo/backend/server/`:

```bash
MODEL_SIZE=base_plus  # Options: tiny, small, base_plus, large
FLASK_ENV=production
PORT=5000
```

### Service Management Options

#### Option 1: Systemd Service

Create `/etc/systemd/system/sam2-backend.service`:

```ini
[Unit]
Description=SAM2 Backend Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/workspace/sam2_demo/demo/backend/server
ExecStart=/usr/bin/python3 app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable sam2-backend
sudo systemctl start sam2-backend
```

#### Option 2: PM2 (Process Manager)

```bash
# Install PM2
npm install -g pm2

# Start service
pm2 start demo/backend/server/app.py --name sam2-backend --interpreter python3

# Save PM2 configuration
pm2 save

# Setup PM2 to start on boot
pm2 startup
```

## Monitoring

### Check Deployment Status

Visit your repository → Actions tab to see deployment logs

### Check Server Status

```bash
# SSH into Vast.ai
ssh root@<vast-ai-ip> -p <port>

# Check service status
systemctl status sam2-backend  # if using systemd
pm2 status                      # if using pm2
docker-compose ps               # if using docker
```

### View Logs

```bash
# Systemd logs
journalctl -u sam2-backend -f

# PM2 logs
pm2 logs sam2-backend

# Docker logs
docker-compose logs -f
```

## Troubleshooting

### Deployment fails with SSH error
- Verify SSH key is added to GitHub Secrets
- Check SSH key is in Vast.ai `~/.ssh/authorized_keys`
- Ensure correct port in GitHub Secrets

### Backend won't start
- Check Python dependencies: `pip list`
- Verify GPU availability: `nvidia-smi`
- Check logs for errors

### Frontend build fails
- Clear node_modules: `rm -rf node_modules && npm install`
- Check Node.js version: `node --version` (should be 18+)

## API Endpoints

- `POST /export_session` - Export tracking results to YOLO format
  ```json
  {
    "session_id": "abc-123",
    "extract_frames": false
  }
  ```

- `POST /propagate_in_video` - Start video tracking
- `POST /graphql` - GraphQL API for all other operations

## License

Copyright (c) Meta Platforms, Inc. and affiliates.

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
