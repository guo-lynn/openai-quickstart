from flask import Flask, request, jsonify
from translator import PDFTranslator
from model import OpenAIModel
from utils import ConfigLoader

app = Flask(__name__)

@app.route('/translate', methods=['POST'])
def translate():
    data = request.json
    file_path = data.get('file_path')
    file_format = data.get('file_format') or 'PDF'
    target_language = data.get('target_language') or '中文'
    model_name = data.get('model_name', 'gpt-3.5-turbo')
    if not file_path:
        return jsonify({'error': 'Missing required parameters'}), 400
    model = getModel(model_name)
    
    translator = PDFTranslator(model)
    try:
        translation_result = translator.translate_pdf(file_path, file_format, target_language)
        return jsonify({'translation_result': translation_result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def getModel(model_name:str):
    config_loader = ConfigLoader("d:/workspace/openai-quickstart/guoly/openai-quickstart/openai-translator/config.yaml")
    config = config_loader.load_config()
    api_key = config['OpenAIModel']['api_key']
    model = OpenAIModel(model= model_name , api_key=api_key)
    return model

if __name__ == '__main__':
    app.run(debug=True) 