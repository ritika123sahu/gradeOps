import torch
import time
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor, TextStreamer
from qwen_vl_utils import process_vision_info
from PIL import Image

# Allow processing of large images from high-res scans
Image.MAX_IMAGE_PIXELS = None


class QwenVLModel:
    def __init__(self, model_id="Qwen/Qwen2-VL-2B-Instruct"):
        self.device = "mps" if torch.backends.mps.is_available() else "cpu"
        print(f"Using device: {self.device}")

        self.processor = AutoProcessor.from_pretrained(model_id)

        # float16 is generally very stable on MPS
        print(f"Loading model {model_id}...")
        self.model = Qwen2VLForConditionalGeneration.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if self.device == "mps" else torch.float32,
            low_cpu_mem_usage=True,
        ).to(self.device).eval()
        print("Model loaded successfully.")

    def transcribe(
        self,
        image_path: str,
        prompt: str = "Transcribe the handwritten text in this image accurately. If there is no text, say 'No text detected'."
    ) -> str:
        start_time = time.time()
        # Load image using PIL to ensure compatibility
        try:
            image = Image.open(image_path).convert("RGB")
            
            # Reduce size further to speed up inference on MPS
            max_size = 896
            if max(image.size) > max_size:
                image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                print(f"Resized image to {image.size}")
                
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            raise RuntimeError(f"Could not load image at {image_path}: {e}")

        # Qwen2-VL standard message structure
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": prompt},
                ],
            }
        ]

        # Preparation for inference
        text = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        image_inputs, video_inputs = process_vision_info(messages)

        inputs = self.processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        ).to(self.device)

        # Inference with streamer to show progress
        print(f"Starting OCR inference for {image_path}...")
        streamer = TextStreamer(self.processor.tokenizer, skip_prompt=True, skip_special_tokens=True)
        inf_start = time.time()
        with torch.inference_mode():
            generated_ids = self.model.generate(
                **inputs, 
                max_new_tokens=300,
                do_sample=False, 
                repetition_penalty=1.1,
                streamer=streamer
            )
        print(f"\nInference completed in {time.time() - inf_start:.2f}s")

        # Trim the prompt tokens out of the generated response
        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]

        response = self.processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )
        
        output = response[0] if response else ""
        print(f"Total transcription time: {time.time() - start_time:.2f}s")
        return output

    def chat(self, prompt: str) -> str:
        print("Starting grading chat...")
        start_time = time.time()
        messages = [{"role": "user", "content": [
            {"type": "text", "text": prompt}]}]
        text = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True)

        inputs = self.processor(
            text=[text], return_tensors="pt").to(self.device)

        streamer = TextStreamer(self.processor.tokenizer, skip_prompt=True, skip_special_tokens=True)
        with torch.inference_mode():
            generated_ids = self.model.generate(
                **inputs, 
                max_new_tokens=400, 
                temperature=0.1, 
                do_sample=False,
                streamer=streamer
            )

        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        response = self.processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True)
        
        output = response[0] if response else ""
        print(f"\nGrading completed in {time.time() - start_time:.2f}s")
        return output
