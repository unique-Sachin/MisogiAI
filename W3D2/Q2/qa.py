from flask import Blueprint, request, jsonify
import google.generativeai as genai
from PIL import Image
import requests
from io import BytesIO
import os

qa_bp = Blueprint('qa', __name__)

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

def get_gemini_response(image, question):
    """
    Get response from Gemini Pro Vision model
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        if image is not None:
            response = model.generate_content([question, image])
        else:
            response = model.generate_content([question])
        return response.text
    except Exception as e:
        raise Exception(f"Gemini API error: {str(e)}")

@qa_bp.route('/qa', methods=['POST'])
def handle_qa():
    """
    Handle multimodal question answering requests
    Supports both file upload and URL-based image input
    """
    try:
        # Check if request contains form data (file upload) or JSON (URL)
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Handle file upload
            if 'image' not in request.files:
                return jsonify({'error': 'No image file provided'}), 400
            
            file = request.files['image']
            if file.filename == '':
                return jsonify({'error': 'No image file selected'}), 400
            
            question = request.form.get('question', '').strip()
            if not question:
                return jsonify({'error': 'No question provided'}), 400
            
            try:
                # Open and process the uploaded image
                image = Image.open(file.stream)
                
                # Get response from Gemini
                answer = get_gemini_response(image, question)
                
                return jsonify({'answer': answer})
                
            except Exception as e:
                return jsonify({'error': f'Error processing image: {str(e)}'}), 400
                
        else:
            # Handle JSON request (URL-based)
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            image_url = data.get('imageUrl', '').strip()
            question = data.get('question', '').strip()
            
            if not image_url:
                return jsonify({'error': 'No image URL provided'}), 400
            
            if not question:
                return jsonify({'error': 'No question provided'}), 400
            
            try:
                # Download image from URL
                response = requests.get(image_url, timeout=10)
                response.raise_for_status()
                
                # Open and process the image
                image = Image.open(BytesIO(response.content))
                
                # Get response from Gemini
                answer = get_gemini_response(image, question)
                
                return jsonify({'answer': answer})
                
            except requests.RequestException as e:
                return jsonify({'error': f'Error downloading image: {str(e)}'}), 400
            except Exception as e:
                return jsonify({'error': f'Error processing image: {str(e)}'}), 400
                
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

