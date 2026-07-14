#!/usr/bin/env bash
set -e

echo "==> Installing Python dependencies..."
pip install -r server/requirements.txt

echo "==> Installing Playwright browsers (Firefox + Chromium) with system deps..."
python -m playwright install --with-deps firefox 2>&1
python -m playwright install --with-deps chromium 2>&1

echo "==> Build complete!"
