#!/usr/bin/env bash
set -e

echo "==> Installing Python dependencies..."
pip install -r server/requirements.txt

echo "==> Installing Playwright browsers..."
python -m playwright install firefox 2>&1 || true
python -m playwright install chromium 2>&1 || true

echo "==> Build complete!"
