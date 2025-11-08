#!/bin/bash
set -e

echo "=============================="
echo "🟦 Updating system packages..."
echo "=============================="
sudo apt update && sudo apt upgrade -y

echo "=============================="
echo "🟩 Installing core dependencies..."
echo "=============================="
sudo apt install -y python3-pip python3-venv npm ffmpeg git tmux curl

# Ensure correct Node.js version (>=18)
echo "=============================="
echo "🟨 Setting up Node.js (v18 LTS)..."
echo "=============================="
sudo apt remove -y nodejs libnode-dev npm || true
sudo apt autoremove -y || true
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

echo "Node version: $(node -v)"
echo "NPM version:  $(npm -v)"

PROJECT_DIR=~/indian-sign-language-translator
BACKEND_DIR=$PROJECT_DIR/backend
FRONTEND_DIR=$PROJECT_DIR/frontend/react_app

echo "=============================="
echo "🟪 Setting up Python virtual environment..."
echo "=============================="
cd $BACKEND_DIR
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

# Install backend dependencies
echo "=============================="
echo "🧩 Installing Python dependencies..."
echo "=============================="
pip install -r requirements.txt

# Add missing core packages explicitly
pip install openai-whisper ffmpeg-python SpeechRecognition fastapi uvicorn

echo "=============================="
echo "🟨 Building React frontend..."
echo "=============================="
cd $FRONTEND_DIR
npm install
npm audit fix --force || true
sudo npm install framer-motion lottie-react react-spinners react-icons react-audio-visualize
sudo npm install -g react-scripts
sudo npm run build

echo "=============================="
echo "🟪 Linking frontend build with FastAPI..."
echo "=============================="
cd $PROJECT_DIR

# Confirm build exists
if [ ! -d "$FRONTEND_DIR/build" ]; then
  echo "❌ React build not found! Please check npm build logs."
  exit 1
fi

echo "=============================="
echo "🟩 Starting FastAPI backend in tmux..."
echo "=============================="
tmux kill-session -t speechapp || true
tmux new-session -d -s speechapp "bash -c 'cd $PROJECT_DIR && source backend/venv/bin/activate && exec uvicorn backend.api:app --host 0.0.0.0 --port 8000'"

echo "=============================="
echo "✅ Deployment complete!"
echo "🌍 Visit your app at: http://$(curl -s ifconfig.me):8000"
echo "🧠 To view logs: tmux attach -t speechapp"
echo "=============================="
uvicorn backend.api:app --host 0.0.0.0 --port 8000
