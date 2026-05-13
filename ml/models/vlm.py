import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from PIL import Image
import os

class QwenVLModel:
    def __init__(self, model_id="Qwen/Qwen-VL-Chat"):
        self.device = "mps" if torch.backends.mps.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id, 
            device_map=self.device, 
            trust_remote_code=True,
            torch_dtype=torch.float16 if self.device == "mps" else torch.float32
        ).eval()

    def transcribe(self, image_path: str, prompt: str = "Transcribe the handwritten text in this image.") -> str:
        query = self.tokenizer.from_list_format([
            {'image': image_path},
            {'text': prompt},
        ])
        inputs = self.tokenizer(query, return_tensors='pt').to(self.device)
        out = self.model.generate(**inputs)
        response = self.tokenizer.decode(out[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
        return response
