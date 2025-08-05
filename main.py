import easyocr
import cv2
from typing import List, Tuple 
import argostranslate.package
import argostranslate.translate

def initialize_reader(languages: List[str] = ['en']) -> easyocr.Reader: 
    return easyocr.Reader(languages, gpu=False)  # Set gpu=True if available

def extract_text_line_by_line(image_path: str, reader: easyocr.Reader) -> List[Tuple[str, float]]: 
    # Read the image
    img = cv2.imread(image_path) 
    # Get text detection results
    detection_results = reader.readtext(img, text_threshold=0.01, link_threshold=0.01, width_ths=1.0, add_margin=0.1, contrast_ths=0.01, adjust_contrast=0.01) 
    # Group by y-coordinate to identify lines
    lines = {}
    for (bbox, text, confidence) in detection_results:
        cv2.rectangle(img, (bbox[0][0], bbox[0][1]), (bbox[2][0], bbox[2][1]), (0, 255, 0), 2)
        # Use the middle y-coordinate of the bounding box as line identifier
        y_center = (bbox[0][1] + bbox[2][1]) / 2 
        # Round to nearest 10 pixels to group nearby text as same line
        line_key = round(y_center / 10) * 10 
        if line_key not in lines:
            lines[line_key] = []
        lines[line_key].append((bbox, text, confidence)) 
    # Display the image with bounding boxes
    cv2.imwrite("output.png", img) 
    # Sort lines by y-position (top to bottom)
    sorted_lines = sorted(lines.items(), key=lambda x: x[0]) 
    # Process each line (left to right)
    line_results = []
    for y_pos, line_data in sorted_lines:
        # Sort elements in the line by x-position
        line_data.sort(key=lambda x: x[0][0][0]) 
        # Combine text in the line
        line_text = ' '.join([item[1] for item in line_data])
        avg_confidence = sum([item[2] for item in line_data]) / len(line_data) 
        line_results.append((line_text, avg_confidence)) 
    return line_results 
  
def translate_argo(text, source_lang="hi", target_lang="en"):
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()
    package_to_install = next(
        filter(
            lambda x: x.from_code == source_lang and x.to_code == target_lang, available_packages
        )
    )
    argostranslate.package.install_from_path(package_to_install.download())
    translatedText = argostranslate.translate.translate(text, source_lang, target_lang)
    return translatedText

if __name__ == "__main__": 
    reader = initialize_reader(['en', 'hi'])
    image_path = "input.png"
    line_results = extract_text_line_by_line(image_path, reader) 
    print([line[0] for line in line_results])
    translated_lines = [translate_argo(line[0], "hi", "en") for line in line_results]
    print(translated_lines)