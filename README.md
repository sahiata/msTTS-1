# **Piper Text-to-Speech (TTS) Project Setup**

This repository contains setup instructions, model files, and training guidance for running and fine-tuning **Piper TTS**.

## **📁 Directory Structure**

Place your trained model files inside the models/ folder in the repository root:  
`my-piper-project/`  
`│`  
`├── models/                     <-- Place your model files here!`  
`│   ├── model.onnx              <-- Piper ONNX neural model`  
`│   └── model.onnx.json         <-- Piper voice configuration file`  
`│`  
`├── README.md                   <-- Project overview and usage`  
`├── training.md                 <-- Model training & fine-tuning guide`  
`├── INSTALLATION.md             <-- Setup & dependency installation`  
`└── VERSION                     <-- Project version tracking`

## **🚀 Quick Start**

### **1\. Model Directory Setup**

Create a models/ directory in the project root and place both your .onnx model and its corresponding .onnx.json config file inside it:  
`mkdir -p models`  
`# Copy your model.onnx and model.onnx.json into models/`

### **2\. Running Inference**

Once your model files are placed in models/, you can run Piper TTS via the command line:  
`echo "Hello world, this is a test using Piper TTS." | piper \`  
  `--model models/model.onnx \`  
  `--config models/model.onnx.json \`  
  `--output_file output.wav`

## **📄 File Overview**

> * **INSTALLATION.md**: Complete guide for setting up Python environments, C++ binaries, and system dependencies.  
> * **training.md**: Step-by-step instructions for dataset preparation and model training with Piper.  
> * **VERSION**: Version specification file.