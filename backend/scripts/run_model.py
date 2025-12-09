#!/usr/bin/env python3
"""Run llama-server with a HuggingFace model."""

import subprocess
import sys


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python run_model.py <user>/<model-repo>/<filename.gguf>")
        print("Example: python run_model.py unsloth/DeepSeek-R1-Distill-Qwen-7B-GGUF/DeepSeek-R1-Distill-Qwen-7B-Q4_K_M.gguf")
        sys.exit(1)

    model_path = sys.argv[1]

    # Parse the path: user/repo/filename.gguf
    parts = model_path.split("/")
    if len(parts) == 3:
        hf_repo = f"{parts[0]}/{parts[1]}"
        hf_file = parts[2]
    elif len(parts) == 2:
        # Format: user/model[:quant] - use directly
        hf_repo = model_path
        hf_file = None
    else:
        print(f"Invalid model path format: {model_path}")
        print("Expected: <user>/<model-repo>/<filename.gguf> or <user>/<model>[:quant]")
        sys.exit(1)

    cmd = [
        "llama-server",
        "--hf-repo", hf_repo,
        "--port", "8080",
        "--host", "127.0.0.1",
        "--ctx-size", "0",
        "-ub", "2048",
        "-b", "2048",
        "--jinja",  # Required for tool/function calling support
    ]

    if hf_file:
        cmd.extend(["--hf-file", hf_file])

    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
