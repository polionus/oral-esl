import os

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

import pytesseract
from PIL import Image
import torch
from dataclasses import dataclass
import tyro
import google.generativeai as genai

# Initialize the client (API key from .env)
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GEMIMI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

# 1. Point to the Tesseract executable (Homebrew default path on macOS; Linux uses PATH)
_tesseract_path = r'/opt/homebrew/bin/tesseract'
if os.path.exists(_tesseract_path):
    pytesseract.pytesseract.tesseract_cmd = _tesseract_path


SYSTEM_PROMOPT_ENGLISH = '''

### Task
The following is a text snippet from inside an image. Make it an actionable simple sentence in English.

TEXT: 
'''

SYSTEM_PROMOPT_ROHINGIYALLISH = '''

Translate this to Rohingyian, using the rohyingian alphabet. Only write the English Transliteration. Don't write anything else. Be very precise

'''

@dataclass
class Config:

    input_image_path: str = 'text.png'


def call_gemini(text:str, system_prompt: str):
    
    final_text = system_prompt + text
    return model.generate_content(final_text)

def extract_prompt(text: str):

    return text.split('[/SUMMARY]')[0].split('[SUMMARY]')[1]

def perform_ocr(image_path):
    try:
        # 2. Load the image using Pillow
        img = Image.open(image_path)

        # 3. Convert image to string
        text = pytesseract.image_to_string(img)
        
        return text
    except Exception as e:
        return f"An error occurred: {e}"
    
def generate_image_from_text(prompt: str, output_filename: str = "./output.png"):
    """
    Takes a text prompt and generates an image using Stable Diffusion.
    """
    model_id = "runwayml/stable-diffusion-v1-5"
    print(f"Downloading and loading {model_id}...")
    
    # Determine the best available hardware and appropriate data type
    if torch.cuda.is_available():
        device = "cuda"
        dtype = torch.float16
        print("Using NVIDIA GPU (CUDA)")
    elif torch.backends.mps.is_available():
        device = "mps"
        dtype = torch.float16
        print("Using Apple Silicon GPU (MPS)")
    else:
        device = "cpu"
        dtype = torch.float32 
        print("Using CPU (Generation will be slow)")

    # Load the pipeline
    pipe = StableDiffusionPipeline.from_pretrained(
        model_id, 
        torch_dtype=dtype
    )
    pipe = pipe.to(device)

    # Generate the image
    print(f"Generating image for prompt: '{prompt}'")
    image = pipe(prompt).images[0]
    
    # Save the output
    image.save(output_filename)
    print(f"Success! Image saved to {output_filename}")
    
    return image

if __name__ == "__main__":
    
    # Parse configuration
    cfg = tyro.cli(Config)
    
    # 1. Extract text via OCR
    print("--- Extracting Text ---")
    text = perform_ocr(cfg.input_image_path)
    print(text)
    
    # 2. Pass text to Ollama
    print("\n--- Asking Llama for Image Prompts ---")
    english_summary = call_gemini(text, SYSTEM_PROMOPT_ENGLISH).text
    response = call_gemini(english_summary, SYSTEM_PROMOPT_ROHINGIYALLISH).text
    
    # CRITICAL FIX: Extract the actual text string from the Ollama response dictionary
    print(response)
    print(f'English Equivalent: {english_summary}')