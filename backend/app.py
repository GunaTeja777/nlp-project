from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
from nlp_processor import NLPProcessor
from config import Config

app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.config.from_object(Config)
CORS(app, origins=Config.CORS_ORIGINS)

# Initialize NLP processor
nlp_processor = NLPProcessor()

@app.route('/')
def index():
    """Serve the frontend"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'AI Answer Generation System is running'
    })

@app.route('/api/answer', methods=['POST'])
def get_answer():
    """Main endpoint to get answer with NLP processing"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        # Get answer from AI API
        answer_text = fetch_ai_answer(question)
        
        if not answer_text:
            return jsonify({'error': 'Failed to fetch answer'}), 500
        
        # Process with NLP - analyze both question and answer
        result = nlp_processor.process_question_and_answer(question, answer_text)
        
        return jsonify({
            'success': True,
            'question': question,
            'result': result
        })
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

def fetch_ai_answer(question):
    """Fetch answer from AI API (Anthropic Claude)"""
    try:
        # Try Anthropic Claude API
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if api_key:
            headers = {
                'Content-Type': 'application/json',
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01'
            }
            
            payload = {
                'model': 'claude-3-sonnet-20240229',
                'max_tokens': Config.MAX_TOKENS,
                'messages': [{
                    'role': 'user',
                    'content': f'Answer this question in a clear, informative way (200-300 words): {question}'
                }]
            }
            
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                json=payload,
                timeout=Config.API_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                return data['content'][0]['text']
        
        # Fallback to OpenAI
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {openai_key}'
            }
            
            payload = {
                'model': 'gpt-3.5-turbo',
                'messages': [{
                    'role': 'user',
                    'content': f'Answer this question in a clear, informative way (200-300 words): {question}'
                }],
                'max_tokens': Config.MAX_TOKENS
            }
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=Config.API_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content']
        
        # If no API keys, return demo answer
        return generate_demo_answer(question)
    
    except Exception as e:
        print(f"API Error: {str(e)}")
        return generate_demo_answer(question)

def generate_demo_answer(question):
    """Generate a demo answer when APIs are not available"""
    import random
    
    # Extract topic from question
    topic = question.lower().replace('what is', '').replace('how does', '').replace('explain', '').strip('?').strip()
    
    # Create varied responses with different complexity levels
    templates = [
        # Beginner level (short, simple)
        f"""{topic.capitalize()} is an important concept in modern technology. It helps us solve problems efficiently. Many experts study this field.
        
The basic idea is straightforward. {topic.capitalize()} works by processing information systematically. This makes tasks easier and faster.
        
People use {topic} every day. It has practical applications in many areas. Learning about it can be very useful.""",
        
        # Intermediate level (medium complexity)
        f"""Understanding {topic} requires knowledge of several fundamental principles. This concept has evolved significantly over recent years through continuous research and development.
        
The implementation involves multiple sophisticated techniques and methodologies. Researchers have discovered that {topic} demonstrates remarkable efficiency when applied to complex problem-solving scenarios. Various algorithms and frameworks have been developed to optimize performance.
        
Contemporary applications of {topic} span numerous domains including computational systems, data analysis, and automated processing. Organizations increasingly recognize its transformative potential for enhancing operational effectiveness.
        
Future developments in {topic} promise even greater capabilities. Emerging technologies continue to expand possibilities, enabling more innovative approaches to traditional challenges.""",
        
        # Advanced level (complex, technical)
        f"""The theoretical foundations of {topic} encompass multidisciplinary paradigms integrating computational methodologies with sophisticated analytical frameworks. Contemporary implementations leverage hierarchical architectures characterized by interconnected processing units exhibiting emergent computational capabilities.
        
Advanced algorithmic approaches utilize stochastic gradient optimization techniques coupled with backpropagation mechanisms to facilitate iterative parameter refinement. The mathematical underpinnings involve complex differential equations, probabilistic graphical models, and information-theoretic principles governing representational learning.
        
Cutting-edge research investigates neural architectural innovations including attention mechanisms, transformer-based architectures, and meta-learning strategies. These developments demonstrate unprecedented performance across benchmark evaluations, particularly in domains requiring contextual understanding and generalization capabilities.
        
Practitioners confront substantial challenges regarding computational scalability, interpretability constraints, and ethical considerations surrounding autonomous decision-making systems. Ongoing investigations explore regularization techniques, adversarial robustness, and uncertainty quantification methodologies.
        
The interdisciplinary nature of {topic} necessitates collaborative efforts spanning computer science, neuroscience, mathematics, and domain-specific expertise, collectively advancing both theoretical understanding and practical implementations with transformative societal implications."""
    ]
    
    # Randomly select a template to vary difficulty
    return random.choice(templates)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)