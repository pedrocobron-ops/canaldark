#!/usr/bin/env bash
# Prepara o editor: dependências Python e modelo de voz Kokoro.
set -e
cd "$(dirname "$0")"
pip install -q -r requirements.txt
mkdir -p models
base=https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0
[ -f models/kokoro-v1.0.int8.onnx ] || curl -sSL -o models/kokoro-v1.0.int8.onnx $base/kokoro-v1.0.int8.onnx
[ -f models/voices-v1.0.bin ] || curl -sSL -o models/voices-v1.0.bin $base/voices-v1.0.bin
echo "ok: editor pronto"
