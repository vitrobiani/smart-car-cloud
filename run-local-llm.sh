#!/usr/bin/env bash

exec llama-server \
  -m "./models/gemma-4-E4B-it-qat-UD-Q4_K_XL.gguf" \
  --mmproj "./models/mmproj-F16.gguf" \
  -ngl 99 \
  -c 16384 \
  -np 1 \
  --flash-attn on \
  --host 127.0.0.1 --port 8880 \
  "$@"
