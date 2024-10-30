1. Install Ollama
2. install Pytorch

```
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

3. install SBERT ONNX

```
pip install -U "sentence-transformers[onnx-gpu] @ git+https://github.com/UKPLab/sentence-transformers.git"
```