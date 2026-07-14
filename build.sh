#!/usr/bin/env bash
set -e

echo "==> Installing Python dependencies..."
pip install -r server/requirements.txt

echo "==> Installing Playwright browsers..."
python -m playwright install firefox 2>&1
python -m playwright install chromium 2>&1

echo "==> Installing system dependencies for Playwright..."
apt-get update -qq 2>&1
apt-get install -y -qq \
  libnss3 libnspr4 libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64 \
  libdrm2 libdbus-1-3 libxkbcommon0 libxcomposite1 libxdamage1 \
  libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 \
  libasound2t64 libatspi2.0-0t64 2>&1

echo "==> Build complete!"
