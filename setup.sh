#!/bin/bash
set -e

echo "🟦 Updating system..."
sudo apt update && sudo apt upgrade -y

echo "🟩 Installing dependencies..."
sudo apt install -y python3-pip python3-venv npm ffmpeg git tmux

# Optional: install build tools if Whisper needs them
sudo apt install -y build-essential

# -------------------------------------------------
# 🔹 Set project root
# -------------------------------------------------
PROJECT_DIR=~/indian-sign-language-translator
BACKEND_DIR=$PROJECT_DIR/backend
FRONTEND_DIR=$PROJECT_DIR/frontend/react_app

# -------------------------------------------------
# 🧠 Python / FastAPI setup
# -------------------------------------------------
echo "🟦 Setting up Python environment..."
cd $BACKEND_DIR
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# -------------------------------------------------
# 💻 React frontend build
# -------------------------------------------------
echo "🟨 Building React frontend..."
cd $FRONTEND_DIR

# Make sure public/index.html exists
if [ ! -f "public/index.html" ]; then
  echo "⚠️ Missing public/index.html — creating default..."
  mkdir -p public
  cat <<'EOF' > public/index.html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta
      name="description"
      content="Speech to Indian Sign Language Translator"
    />
    <title>Speech to ISL Translator</title>
  </head>
  <body class="bg-gray-100">
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
EOF
fi

npm install
npm audit fix --force || true
npm run build

# -------------------------------------------------
# 🧩 Link frontend with backend
# -------------------------------------------------
cd $BACKEND_DIR
if ! grep -q "StaticFiles" api.py; then
  echo "⚠️ Ensure api.py includes StaticFiles mount for frontend"
fi

# -------------------------------------------------
# 🚀 Start the application
# -------------------------------------------------
echo "🟩 Starting FastAPI..."
tmux new-session -d -s speechapp "cd $BACKEND_DIR && source venv/bin/activate && uvicorn api:app --host 0.0.0.0 --port 8000"

echo "✅ Application deployed!"
EC2_IP=$(curl -s http://checkip.amazonaws.com)
echo "🌐 Visit: http://$EC2_IP:8000"
