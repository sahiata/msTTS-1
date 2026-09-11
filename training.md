# **Piper TTS Training & Fine-Tuning Guide**

This document provides a comprehensive step-by-step guide for preparing your dataset, preprocessing data, training a voice model, and exporting the trained model to ONNX format for Piper TTS.

## ---

**1\. Environment Setup & Prerequisites**

Training requires Linux (Ubuntu 20.04/22.04 recommended) and an NVIDIA GPU with CUDA support.  
`# Clone the official Piper repository`  
`git clone https://github.com/rhasspy/piper.git`  
`cd piper/src/python`

`# Create and activate a Python virtual environment`  
`python3 -m venv .venv`  
`source .venv/bin/activate`

`# Upgrade pip and install training dependencies`  
`pip install --upgrade pip`  
`pip install -e .[train]`

## ---

**2\. Dataset Preparation**

Piper expects a dataset formatted in the standard **LJSpeech** format:

> * **wavs/**: A directory containing 22050Hz or 16000Hz mono 16-bit PCM WAV audio files.  
> * **metadata.csv**: A pipe-separated file mapping audio file IDs to their respective transcriptions.

### **Directory Layout**

`dataset/`  
`├── wavs/`  
`│   ├── sample_0001.wav`  
`│   ├── sample_0002.wav`  
`│   └── sample_0003.wav`  
`└── metadata.csv`

### **metadata.csv Example**

`sample_0001|This is the first sentence recorded for the voice dataset.`  
`sample_0002|Here is another example sentence.`  
`sample_0003|Piper TTS delivers fast and realistic speech synthesis.`

## ---

**3\. Data Preprocessing**

Before training, preprocess the audio files and text transcriptions into phonemes and features suitable for the VITS architecture.

### **Command**

`python3 -m piper_train.preprocess \`  
  `--language en-us \`  
  `--input-dir ./dataset \`  
  `--output-dir ./preprocessed \`  
  `--dataset-format ljspeech \`  
  `--single-speaker`

### **Parameter Explanations**

| Parameter | Description   |
| :---- | :---- |
| \--language | Language code (e.g., en-us, sr, de, fr). |
| \--input-dir | Path to your dataset folder containing wavs/ and metadata.csv. |
| \--output-dir | Target directory where preprocessed feature files will be saved. |
| \--dataset-format | Dataset format (typically ljspeech). |
| \--single-speaker | Flag for single-speaker voice models (use \--multi-speaker for multi-speaker datasets). |

## ---

**4\. Model Training**

Train the neural network using PyTorch Lightning. Monitor training loss and check checkpoint outputs regularly.

### **Command**

`python3 -m piper_train \`  
  `--dataset-dir ./preprocessed \`  
  `--accelerator gpu \`  
  `--devices 1 \`  
  `--batch-size 32 \`  
  `--validation-split 0.05 \`  
  `--max-epochs 1000 \`  
  `--checkpoint-epochs 50 \`  
  `--precision 32`

### **Parameter Explanations**

| Parameter | Description   |
| :---- | :---- |
| \--dataset-dir | Directory containing the preprocessed data output from step 3\. |
| \--accelerator | Hardware accelerator to use (gpu or cpu). |
| \--devices | Number of GPU devices allocated for training. |
| \--batch-size | Number of audio samples per training step (lower to 16 or 8 if CUDA out-of-memory errors occur). |
| \--validation-split | Fraction of the dataset reserved for validation (e.g., 0.05 \= 5%). |
| \--max-epochs | Total number of training epochs to run. |
| \--checkpoint-epochs | Frequency (in epochs) at which model checkpoints (.ckpt) are automatically saved. |
| \--precision | Calculation precision (32 or 16-mixed for faster training on modern GPUs). |

## ---

**5\. Exporting to ONNX**

Once training achieves satisfactory loss levels, export your PyTorch Lightning checkpoint (.ckpt) into the lightweight **ONNX** format required by the Piper runtime.

### **Command**

`python3 -m piper_train.export_onnx \`  
  `/path/to/checkpoint.ckpt \`  
  `/path/to/output/model.onnx`

### **Deploying to Your Project**

After exporting, copy the resulting model files into your repository's models/ folder:  
`cp /path/to/output/model.onnx models/`  
`cp /path/to/output/model.onnx.json models/`  
