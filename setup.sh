#!/bin/bash
set -e

echo "🟦 Updating system..."
sudo apt update && sudo apt upgrade -y

echo "🟩 Installing dependencies..."
sudo apt install -y python3-pip python3-venv npm ffmpeg git tmux

echo "🟦 Setting up Python environment..."
cd ~/speech_to_sign/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "🟨 Building React frontend..."
cd ../frontend/react_app
npm install
npm run build

echo "🟪 Linking frontend build with backend..."
cd ../../backend

# Ensure FastAPI serves React build
if ! grep -q "StaticFiles" api.py; then
  echo "⚠️ Ensure api.py includes StaticFiles mount for frontend"
fi

echo "🟩 Starting FastAPI..."
tmux new-session -d -s speechapp "source venv/bin/activate && uvicorn api:app --host 0.0.0.0 --port 8000"

echo "✅ Application deployed!"
echo "Visit http://<your-ec2-ip>:8000"
