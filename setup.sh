#!/bin/bash
set -e

echo "=============================="
echo "🚀 Speech-to-Sign Setup Script"
echo "=============================="

# -----------------------------
# 🟦 Update system
# -----------------------------
echo "🟦 Updating system..."
sudo apt update -y && sudo apt upgrade -y

# -----------------------------
# 🟩 Install base dependencies
# -----------------------------
echo "🟩 Installing core dependencies..."
sudo apt install -y python3-pip python3-venv ffmpeg git tmux curl build-essential

# -----------------------------
# 🔹 Fix Node.js version (install Node 18 LTS cleanly)
# -----------------------------
echo "🟨 Installing Node.js 18 LTS..."
sudo apt remove -y nodejs libnode-dev npm || true
sudo apt autoremove -y || true
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

echo "Node version: $(node -v)"
echo "NPM version:  $(npm -v)"

# -----------------------------
# 🔹 Define directories
# -----------------------------
PROJECT_DIR=~/indian-sign-language-translator
BACKEND_DIR=$PROJECT_DIR/backend
FRONTEND_DIR=$PROJECT_DIR/frontend/react_app

# -----------------------------
# 🧠 Setup Python backend
# -----------------------------
echo "🟦 Setting up Python environment..."
cd $BACKEND_DIR
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# -----------------------------
# 💻 Setup React frontend
# -----------------------------
echo "🟨 Building React frontend..."
cd $FRONTEND_DIR

# Ensure public/index.html exists
if [ ! -f "public/index.html" ]; then
  echo "⚠️  Creating missing public/index.html..."
  mkdir -p public
  cat <<'EOF' > public/index.html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="Speech to Indian Sign Language Translator" />
    <title>Speech to ISL Translator</title>
  </head>
  <body class="bg-gray-100">
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
EOF
fi

# Install React dependencies & build
rm -rf node_modules package-lock.json
npm install
npm audit fix --force || true
npm run build

# -----------------------------
# 🔗 Link frontend with backend
# -----------------------------
cd $BACKEND_DIR
if ! grep -q "StaticFiles" api.py; then
  echo "⚠️  Ensure api.py mounts StaticFiles for serving React build!"
fi

# -----------------------------
# 🚀 Launch FastAPI in tmux
# -----------------------------
echo "🟩 Starting FastAPI backend in tmux..."
tmux kill-session -t speechapp || true
tmux new-session -d -s speechapp "cd $BACKEND_DIR && source venv/bin/activate && uvicorn api:app --host 0.0.0.0 --port 8000"

# -----------------------------
# 🌐 Show access URL
# -----------------------------
EC2_IP=$(curl -s http://checkip.amazonaws.com)
echo "✅ Deployment complete!"
echo "🌍 Visit your app at: http://$EC2_IP:8000"
echo "🧠 To reattach the server: tmux attach -t speechapp"
