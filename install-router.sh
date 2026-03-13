#!/bin/bash

ROUTER_NAME=$1
PORT=$2

if [ -z "$ROUTER_NAME" ] || [ -z "$PORT" ]; then
  echo "Usage: bash install-router.sh router-name port"
  exit
fi

echo "Installing $ROUTER_NAME on port $PORT..."

sudo apt update
sudo apt install -y python3 python3-venv python3-pip git curl

mkdir -p /home/aman/routers
cd /home/aman/routers

# remove old router if exists
if [ -d "$ROUTER_NAME" ]; then
  echo "Existing router found, removing..."
  rm -rf $ROUTER_NAME
fi

echo "Downloading router from GitHub..."

git clone https://github.com/technicalboy2023/$ROUTER_NAME

cd $ROUTER_NAME

echo "Creating virtual environment..."

python3 -m venv venv
source venv/bin/activate

echo "Installing dependencies..."

pip install fastapi uvicorn requests python-dotenv

echo "Creating .env file..."

cat <<EOF > .env
HF_KEY_1=
HF_KEY_2=
HF_KEY_3=
HF_KEY_4=
HF_KEY_5=
HF_KEY_6=
HF_KEY_7=
HF_KEY_8=
HF_KEY_9=
HF_KEY_10=
EOF

echo ".env file created"

echo "Creating systemd service..."

sudo bash -c "cat > /etc/systemd/system/$ROUTER_NAME.service" <<EOF
[Unit]
Description=$ROUTER_NAME
After=network.target

[Service]
User=aman
WorkingDirectory=/home/aman/routers/$ROUTER_NAME
ExecStart=/home/aman/routers/$ROUTER_NAME/venv/bin/uvicorn router:app --host 0.0.0.0 --port $PORT
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "Reloading systemd..."

sudo systemctl daemon-reload

echo "Starting router..."

sudo systemctl enable $ROUTER_NAME
sudo systemctl restart $ROUTER_NAME

echo "-----------------------------------"
echo "$ROUTER_NAME installed successfully"
echo "Port: $PORT"
echo "Folder: /home/aman/routers/$ROUTER_NAME"
echo ""
echo "Add API keys here:"
echo "nano /home/aman/routers/$ROUTER_NAME/.env"
echo "-----------------------------------"
