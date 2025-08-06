from flask import Flask, request, jsonify, send_from_directory
import os, time, random
from text_extractor import extract_text_from_image

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

@app.route('/uploads/<path:filename>')
def serve_upload_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/outputs/<path:filename>')
def serve_output_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

@app.route('/process', methods=['POST'])
def upload_file():
    print("\nIncoming request headers:", request.headers)  # Debug
    print("Request files:", request.files)  # Debug
    print("Request form data:", request.form)  # Debug
    
    if 'file' not in request.files:
        print("No file part in request")  # Debug
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    print("Received file:", file.filename)  # Debug

    payload = request.form
    print("Received payload:", payload)  # Debug

    source_lang = payload.get('source_lang')
    target_lang = payload.get('target_lang') 
    
    if file.filename == '':
        print("Empty filename")  # Debug
        return jsonify({"error": "No selected file"}), 400
    
    try:
        # Simple save without secure_filename for testing
        current_time = int(round(time.time() * 1000)) # Get current time in milliseconds
        random_number = random.randint(1000, 9999) # Generate a random number
        file.filename = f"{current_time}_{random_number}_{file.filename}"
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], file.filename)
        file.save(save_path)
        print("File saved to:", save_path)  # Debug
        translation_texts = extract_text_from_image(input_path=save_path, output_path=output_path, languages=[source_lang, target_lang], draw_texts=True)
        print("translation_texts:", translation_texts)
        print("Text extracted and saved to:", output_path)  # Debug
        return jsonify({
            "message": "File processed successfully",
            "filename": file.filename,
            "saved_at": save_path,
            "extracted_at": output_path,
            "source_lang": source_lang,
            "target_lang": target_lang
        })
    except Exception as e:
        print("Error saving file:", str(e))  # Debug
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)