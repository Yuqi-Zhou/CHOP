import os
from PIL import Image
from io import BytesIO
import ast
import logging
from fastapi import FastAPI, HTTPException, File, UploadFile, Body
import torch
from transformers import AutoModelForCausalLM, AutoProcessor

app = FastAPI()

model_path = ""

model = AutoModelForCausalLM.from_pretrained(
    model_path,
    device_map="auto",
    torch_dtype=torch.bfloat16,
    trust_remote_code=True,
)

processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True)

@app.post("/generate_click_location/")
async def generate_click_location(file: UploadFile = File(...), data: str = Body(...)):
    try:
        img = Image.open(BytesIO(await file.read())).convert("RGB")

        query = data

        messages = [
            {
                "role": "user",
                "content": [
                    {"text": None, "type": "image"},
                    {"text": query, "type": "text"},
                ],
            }
        ]

        text = processor.apply_chat_template(messages, add_generation_prompt=True)
        inputs = processor(text=text, images=img, return_tensors="pt")
        inputs["pixel_values"] = inputs["pixel_values"].to(model.dtype)
        inputs = {k: v.to(model.device) for k, v in inputs.items()}

        with torch.inference_mode(), torch.amp.autocast("cuda", dtype=torch.bfloat16):
            output = model.generate(
                **inputs,
                max_new_tokens=50,
                stop_strings=["<|im_end|>"],
                tokenizer=processor.tokenizer,
            )

        output_ids = output[0][inputs["input_ids"].shape[1]:]
        response = processor.decode(output_ids, skip_special_tokens=True)
        print(response)
        coords = ast.literal_eval(response.replace("<|im_end|>", "").replace("```", "").replace(" ", "").strip())

        del inputs
        del output
        torch.cuda.empty_cache()
        return {"click_coordinates": coords}

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
