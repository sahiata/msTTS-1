# **Piper TTS Installation Guide**

Follow these instructions to set up Piper TTS on your operating system.

## **Prerequisites**

> * Python 3.9 or higher  
> * pip package manager  
> * Optionally, an NVIDIA GPU with CUDA support for accelerated inference

## **1\. Python Package Installation**

The fastest way to install Piper is via pip:  
`pip install piper-tts`

## **2\. Pre-built Binary Installation (Standalone)**

If you prefer using standalone C++ binaries instead of Python:

> 1. Go to the [Piper GitHub Releases](https://github.com/rhasspy/piper/releases) page.  
> 2. Download the archive matching your platform (e.g., piper\_amd64.tar.gz for Linux or piper\_windows\_amd64.zip for Windows).  
> 3. Extract the archive:  
>    `tar -xvf piper_amd64.tar.gz`

> 4. Verify installation by checking version/help output:  
>    `./piper --help`

## **3\. Verifying Your Setup**

Ensure your model.onnx and model.onnx.json files are placed inside the models/ directory, then execute:  
`echo "Piper installation successful." | piper \`  
  `--model models/model.onnx \`  
  `--config models/model.onnx.json \`  
  `--output_file test.wav`  
