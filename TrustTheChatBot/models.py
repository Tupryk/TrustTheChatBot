from qwen_vl_utils import process_vision_info
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor, BitsAndBytesConfig


class LLM:

    def __init__(self, model_name: str, max_output_tokens: int=1024, device: str="cuda"):
    
        if model_name == "Qwen7B":

            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype="float16",
                bnb_4bit_use_double_quant=True
            )
            self.model = Qwen2VLForConditionalGeneration.from_pretrained(
                "Qwen/Qwen2-VL-7B-Instruct",
                quantization_config=bnb_config,
                torch_dtype="auto",
                device_map=device
            )
            self.processor = AutoProcessor.from_pretrained("Qwen/Qwen2-VL-7B-Instruct")
        
        else:
            raise Exception(f"Model with name '{model_name}' not implemented yet!")
        
        self.device = device
        self.max_output_tokens = max_output_tokens


    def send(self, messages: list) -> str:

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
        )
        inputs = inputs.to(self.device)

        generated_ids = self.model.generate(**inputs, max_new_tokens=self.max_output_tokens)
        generated_ids_trimmed = [
            out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        output_text = self.processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )

        return output_text[0]
