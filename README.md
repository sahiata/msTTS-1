# **Piper Text-to-Speech (TTS) Project Setup**

This repository contains setup instructions, model files, and training guidance for running and fine-tuning **Piper TTS**.

## **⬇️ Download the model**

The trained model files are not stored in the repository. They are attached to the [v1.0.0 release](https://github.com/sahiata/msTTS-1/releases/tag/v1.0.0):

| File | Size |
|---|---|
| `model.onnx` | ~61 MB |
| `model.onnx.json` | ~8 KB |

```bash
mkdir -p models
wget -P models https://github.com/sahiata/msTTS-1/releases/download/v1.0.0/model.onnx
wget -P models https://github.com/sahiata/msTTS-1/releases/download/v1.0.0/model.onnx.json
```

## **📁 Directory Structure**

After downloading, the model files should be inside the `models/` folder in the repository root:

```text
msTTS-1/
│
├── models/                     <-- Download from Releases (see "Download the model")
│   ├── model.onnx              <-- Piper ONNX neural model
│   └── model.onnx.json         <-- Piper voice configuration file
│
├── README.md                   <-- Project overview and usage
├── training.md                 <-- Model training & fine-tuning guide
├── INSTALLATION.md             <-- Setup & dependency installation
├── requirements.txt            <-- Python dependencies
└── VERSION.md                  <-- Project version tracking
```

## **🚀 Quick Start**

### **1. Get the model files**

Download `model.onnx` and `model.onnx.json` from the [v1.0.0 release](https://github.com/sahiata/msTTS-1/releases/tag/v1.0.0) into the `models/` folder:

```bash
mkdir -p models
wget -P models https://github.com/sahiata/msTTS-1/releases/download/v1.0.0/model.onnx
wget -P models https://github.com/sahiata/msTTS-1/releases/download/v1.0.0/model.onnx.json
```

### **2. Running Inference**

Once the model files are in `models/`, you can run Piper TTS from the command line:

```bash
echo "Hello world, this is a test using Piper TTS." | piper \
  --model models/model.onnx \
  --config models/model.onnx.json \
  --output_file output.wav
```

## **📄 File Overview**

* **INSTALLATION.md**: Complete guide for setting up Python environments, C++ binaries, and system dependencies.
* **training.md**: Step-by-step instructions for dataset preparation and model training with Piper.
* **requirements.txt**: Python dependencies.
* **VERSION.md**: Version specification file.
