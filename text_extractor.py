import os 
import easyocr
import cv2
import json
from dotenv import load_dotenv  
from typing import List 
from google import genai
from google.genai import types
import numpy as np
from PIL import Image, ImageDraw, ImageFont

load_dotenv('.env')
 
LANGUAGE = {
    "hi" : "hindi",
    "en" : "english"
}

def translate_texts_array(text_array: List[str], source_lang: str = "hindi", target_lang: str = "english") -> List[str]: 
    prompt = (
        f"Translate this exact text from {source_lang} to {target_lang} also do correction of grammar and spelling in the translation in every word and sentence of each language if possible. "
        f"Like in hindi translate this exact text to english. also hindi word should be a hindi word. also do correction of grammar and spelling in the translation in every word and sentence of each language if possible. "
        f"Preserve all numbers, names, and technical terms. "
        f"Return ONLY the translation, no explanations. "
        f"Return ONLY [original_text, translated_text] array of text. and length of the array should be same as text_array. Do not return any other text.\n\n"
        f"Response SHOULD be in json format which consists ARRAY of [original_text, translated_text].\n\n"
        f"Also remove ```json ``` from the response.\n\n"
        f"TextArray: {json.dumps(text_array)}\n"
        f"TranslationArray:"
    )  
    client = genai.Client(api_key=os.getenv("API_KEY"))
    model = os.getenv("MODEL_ID")
    contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]
    tools = [types.Tool(googleSearch=types.GoogleSearch())]
    generate_content_config = types.GenerateContentConfig(thinking_config=types.ThinkingConfig(thinking_budget=0), tools=tools) 
    response = client.models.generate_content(model=model, contents=contents, config=generate_content_config) 
    return list(json.loads(response.text.replace("```json", "").replace("```", "")))  

def draw_text(img_data, detection_boxes, translations_texts, length, output_path="output.png"):
    pil_image = Image.fromarray(cv2.cvtColor(img_data, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_image)
    for i in range(length):
        bbox = detection_boxes[i]
        text = translations_texts[i][1] if translations_texts[i][1] else " " 
        draw.rectangle([(bbox[0][0], bbox[0][1]), (bbox[2][0], bbox[2][1])], fill=(255, 255, 255))
        x = bbox[0][0]
        y = bbox[0][1]
        w = bbox[2][0] - bbox[0][0]
        h = bbox[2][1] - bbox[0][1]   
        font = ImageFont.truetype("FreeSans.otf", h/2)
        draw.text((x, y), text, font=font, fill=(0, 0, 0))
    cv2.imwrite(output_path, cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR))

def extract_text_from_image(input_path="input.png", output_path="output.png", languages=['hi', 'en'], draw_texts=True) -> List[str]: 
    image_path = input_path
    img_data = cv2.imread(image_path)
    reader = easyocr.Reader(lang_list=languages, gpu=False)
    # detection_results = reader.readtext(img_data, text_threshold=0.01, link_threshold=0.01, width_ths=1.0, add_margin=0.1, contrast_ths=0.01, adjust_contrast=0.01) 
    detection_results = reader.readtext(img_data) 
    detection_texts = [detection[1] for detection in detection_results] 
    print("detection_texts", len(detection_texts))
    if draw_texts: 
        detection_boxes = [detection[0] for detection in detection_results]
        translations_texts = translate_texts_array(detection_texts, source_lang=LANGUAGE[languages[0]], target_lang=LANGUAGE[languages[1]]) 
        print("translations_texts", len(translations_texts))
        draw_text(img_data, detection_boxes, translations_texts, len(translations_texts), output_path)
        print(f"Text extracted and saved to {output_path}!")
        return translations_texts
    return detection_texts

# if __name__ == "__main__": 
    # detection_texts = extract_text_from_image("input.png", "output.png", ['en', 'hi'], False)
    # print(detection_texts)
    # translation_texts = extract_text_from_image("input.png", "output.png", ['en', 'hi'], True) 
    # print(translation_texts)
