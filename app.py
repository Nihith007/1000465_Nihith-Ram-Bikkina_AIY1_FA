"""
Smart Farming Assistant - Python Flask Application
Powered by Google Gemini AI

Installation:
pip install flask google-generativeai python-dotenv

Usage:
1. Add your Gemini API key in the code where it says app_key
2. Run: python app.py
3. Open browser: http://localhost:5000
"""

from flask import Flask, render_template_string, request, jsonify
import google.generativeai as genai
from datetime import datetime
import os
import json

app = Flask(__name__)

# =============================================================================
# CONFIGURATION - ADD YOUR API KEY HERE
# =============================================================================
app_key = "YOUR_GEMINI_API_KEY_HERE"  # Replace with your actual API key
genai.configure(api_key=app_key)

# Configure the Gemini model
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 2048,
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# =============================================================================
# DATA STRUCTURES
# =============================================================================

FEATURES = [
    {
        "id": "crop-recommendation",
        "title": "Crop Recommendation",
        "description": "Get suggestions for crops based on your location, season, and soil type",
        "icon": "🌾",
        "color": "bg-green-100"
    },
    {
        "id": "pest-disease",
        "title": "Pest & Disease Management",
        "description": "Identify and treat crop diseases and pest infestations",
        "icon": "🐛",
        "color": "bg-red-100"
    },
    {
        "id": "weather-alerts",
        "title": "Weather-Based Alerts",
        "description": "Get weather forecasts and farming advice based on conditions",
        "icon": "🌦️",
        "color": "bg-blue-100"
    },
    {
        "id": "soil-fertilizer",
        "title": "Soil & Fertilizer Advice",
        "description": "Receive recommendations for soil treatment and fertilization",
        "icon": "🌱",
        "color": "bg-amber-100"
    },
    {
        "id": "sustainable-farming",
        "title": "Sustainable Farming Tips",
        "description": "Learn eco-friendly and organic farming practices",
        "icon": "♻️",
        "color": "bg-emerald-100"
    }
]

SAMPLE_PROMPTS = {
    "crop-recommendation": [
        "Suggest crops to plant in July in Tamil Nadu",
        "What should I grow in acidic soil in Odisha in September?",
        "Best crops for monsoon season in Kerala",
        "Crop recommendation for sandy soil in Rajasthan"
    ],
    "pest-disease": [
        "White fungus on wheat leaves in Haryana – treatment?",
        "How to treat aphids on tomato plants organically?",
        "Yellow spots on rice leaves - what is it?",
        "Pest control for cotton crops in Maharashtra"
    ],
    "weather-alerts": [
        "Rain prediction and farming advice for Punjab this week?",
        "Weather forecast for harvesting season in Karnataka",
        "Should I irrigate my crops this week in Gujarat?",
        "Best time to apply fertilizer based on weather in UP"
    ],
    "soil-fertilizer": [
        "What should I grow in slightly acidic soil in Kenya?",
        "NPK fertilizer ratio for wheat cultivation",
        "How to improve clay soil for vegetable farming?",
        "Organic fertilizer recommendations for sugarcane"
    ],
    "sustainable-farming": [
        "Give eco-friendly pest control methods for grapes in Italy",
        "Organic farming practices for small-scale farmers",
        "Water conservation techniques for paddy fields",
        "Companion planting guide for vegetables"
    ]
}

# =============================================================================
# AI RESPONSE GENERATION
# =============================================================================

def generate_system_prompt(feature=None):
    """Generate system prompt based on selected feature"""
    base_prompt = """You are AgroNova, an expert AI agricultural assistant helping farmers worldwide. 
You provide practical, actionable farming advice based on scientific principles and regional best practices.

Your expertise includes:
- Crop recommendations based on location, season, soil type, and climate
- Pest and disease identification and management (organic and chemical solutions)
- Weather-based farming advice and planning
- Soil health and fertilizer recommendations
- Sustainable and organic farming practices

Always provide:
1. Clear, structured responses with practical steps
2. Region-specific advice when location is mentioned
3. Both organic and conventional solutions when applicable
4. Safety warnings for chemical applications
5. Preventive measures alongside treatments

Format your responses with:
- Clear headings using **bold** for main points
- Bullet points for lists
- Emojis for visual appeal (🌾 🐛 💧 🌱 etc.)
- Specific measurements and timings
- Action-oriented language

Keep responses concise but comprehensive, typically 200-400 words unless detailed technical information is requested."""

    feature_contexts = {
        "crop-recommendation": "\n\nFocus on: Suggesting appropriate crops based on soil type, climate, season, water availability, and market demand. Include planting times, expected yields, and care requirements.",
        "pest-disease": "\n\nFocus on: Identifying pests and diseases from descriptions, providing both organic and chemical treatment options, preventive measures, and application guidelines.",
        "weather-alerts": "\n\nFocus on: Providing weather-based farming advice, irrigation scheduling, harvest timing, and crop protection strategies during different weather conditions.",
        "soil-fertilizer": "\n\nFocus on: Soil health assessment, pH management, nutrient deficiency identification, fertilizer recommendations (NPK ratios), and organic soil improvement methods.",
        "sustainable-farming": "\n\nFocus on: Eco-friendly pest control, organic farming practices, companion planting, water conservation, biodiversity, and certification guidance."
    }
    
    if feature and feature in feature_contexts:
        return base_prompt + feature_contexts[feature]
    return base_prompt

def get_ai_response(user_message, feature=None, chat_history=None):
    """Generate AI response using Gemini API"""
    try:
        # Build conversation history
        conversation = []
        
        # Add system context
        system_prompt = generate_system_prompt(feature)
        conversation.append({
            "role": "user",
            "parts": [system_prompt]
        })
        conversation.append({
            "role": "model",
            "parts": ["I understand. I'm AgroNova, your agricultural assistant. I'll provide practical, region-specific farming advice with clear formatting and actionable steps."]
        })
        
        # Add chat history if provided
        if chat_history:
            for msg in chat_history[-6:]:  # Keep last 6 messages for context
                role = "user" if msg["role"] == "user" else "model"
                conversation.append({
                    "role": role,
                    "parts": [msg["content"]]
                })
        
        # Start chat and send message
        chat = model.start_chat(history=conversation)
        response = chat.send_message(user_message)
        
        return response.text
        
    except Exception as e:
        error_msg = f"Error generating response: {str(e)}"
        print(error_msg)
        return f"""**Error Processing Request**

I encountered an issue generating a response. This could be due to:
- API key not configured properly
- Network connectivity issues
- API rate limits

**Please ensure:**
1. Your Gemini API key is correctly set in the code (app_key variable)
2. You have an active internet connection
3. Your API key has sufficient quota

Error details: {str(e)}"""

# =============================================================================
# HTML TEMPLATE
# =============================================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AgroNova - Smart Farming Assistant</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        .prose { max-width: none; }
        .prose p { margin-bottom: 0.5rem; }
        .prose ul, .prose ol { margin-left: 1.5rem; margin-bottom: 0.5rem; }
        .prose li { margin-bottom: 0.25rem; }
        .prose strong { font-weight: 600; color: #111827; }
        .prose h1, .prose h2, .prose h3 { color: #111827; font-weight: bold; }
        .chat-container { height: calc(100vh - 280px); min-height: 500px; }
        .loading-dots::after {
            content: '...';
            animation: loading 1.5s infinite;
        }
        @keyframes loading {
            0%, 20% { content: '.'; }
            40% { content: '..'; }
            60%, 100% { content: '...'; }
        }
    </style>
</head>
<body class="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50">
    <!-- Header -->
    <header class="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                    <div class="bg-green-600 p-2 rounded-lg">
                        <i data-lucide="sprout" class="w-6 h-6 text-white"></i>
                    </div>
                    <div>
                        <h1 class="text-xl sm:text-2xl font-bold text-gray-900">AgroNova</h1>
                        <p class="text-xs sm:text-sm text-gray-600">Smart Farming Assistant</p>
                    </div>
                </div>
                <div class="hidden sm:flex items-center gap-2">
                    <span class="bg-green-50 text-green-700 border border-green-300 px-3 py-1 rounded-full text-sm">
                        Powered by Gemini AI
                    </span>
                </div>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <!-- Sidebar - Features -->
            <aside class="lg:col-span-3 space-y-4">
                <div class="bg-white rounded-lg shadow-md p-4">
                    <h2 class="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                        <span class="text-green-600">📋</span>
                        Features
                    </h2>
                    <div id="features-container" class="space-y-2">
                        <!-- Features will be inserted here -->
                    </div>
                    <button id="clear-feature" class="w-full mt-3 px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded hidden">
                        Clear Selection
                    </button>
                </div>

                <div class="bg-gradient-to-br from-green-50 to-blue-50 border border-green-200 rounded-lg p-4">
                    <h3 class="font-semibold text-gray-900 mb-2 text-sm">🌍 Global Coverage</h3>
                    <p class="text-xs text-gray-700 leading-relaxed">
                        Get region-specific advice for farming practices worldwide. Supporting farmers in India, Kenya, Brazil, Italy, and more!
                    </p>
                </div>
            </aside>

            <!-- Main Chat Area -->
            <main class="lg:col-span-9 space-y-4">
                <!-- Chat Messages -->
                <div class="bg-white shadow-lg rounded-lg overflow-hidden flex flex-col chat-container">
                    <div id="chat-messages" class="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
                        <div class="flex gap-3">
                            <div class="flex-shrink-0 w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
                                <i data-lucide="bot" class="w-6 h-6 text-green-600"></i>
                            </div>
                            <div class="max-w-[85%] sm:max-w-[80%] rounded-2xl px-4 py-3 bg-gray-100 text-gray-800">
                                <div class="prose prose-sm">
                                    <p>Welcome to <strong>AgroNova Smart Farming Assistant</strong>! 🌾</p>
                                    <p>I'm here to help farmers worldwide with AI-powered agricultural advice. Ask me about crops, pests, weather, soil, or sustainable farming practices in your region.</p>
                                    <p><strong>Select a feature below or ask me anything!</strong></p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Input Area -->
                    <div class="border-t border-gray-200 p-4 bg-gray-50">
                        <div class="flex gap-2">
                            <textarea 
                                id="user-input" 
                                placeholder="Ask about crops, pests, weather, soil, or sustainable farming..."
                                class="flex-1 min-h-[60px] max-h-[120px] resize-none bg-white border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-green-500"
                                rows="2"
                            ></textarea>
                            <button 
                                id="send-btn"
                                class="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg self-end disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                <i data-lucide="send" class="w-5 h-5"></i>
                            </button>
                        </div>
                        <p class="text-xs text-gray-500 mt-2">Press Enter to send, Shift + Enter for new line</p>
                    </div>
                </div>

                <!-- Sample Prompts -->
                <div class="bg-white rounded-lg p-4">
                    <div class="flex items-center gap-2 mb-3">
                        <i data-lucide="sparkles" class="w-4 h-4 text-green-600"></i>
                        <h3 class="font-semibold text-gray-900 text-sm">Try These Sample Questions</h3>
                    </div>
                    <div id="sample-prompts" class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        <!-- Sample prompts will be inserted here -->
                    </div>
                </div>
            </main>
        </div>
    </div>

    <!-- Footer -->
    <footer class="bg-white border-t border-gray-200 mt-8">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <p class="text-center text-xs sm:text-sm text-gray-600">
                🌾 Supporting UN SDG 2 (Zero Hunger) & SDG 13 (Climate Action) | Built with Python Flask & Gemini AI
            </p>
        </div>
    </footer>

    <script>
        // Initialize Lucide icons
        lucide.createIcons();

        // State management
        let selectedFeature = null;
        let chatHistory = [];
        let isLoading = false;

        // Features data
        const features = {{ features | tojson }};
        const samplePrompts = {{ sample_prompts | tojson }};

        // Initialize features
        function initFeatures() {
            const container = document.getElementById('features-container');
            features.forEach(feature => {
                const card = document.createElement('div');
                card.className = 'p-3 cursor-pointer transition-all hover:shadow-md border-2 border-gray-200 hover:border-green-300 rounded-lg';
                card.innerHTML = `
                    <div class="flex items-start gap-3">
                        <div class="${feature.color} p-2 rounded-lg text-2xl flex-shrink-0">${feature.icon}</div>
                        <div class="flex-1 min-w-0">
                            <h3 class="font-semibold text-sm text-gray-900 mb-1">${feature.title}</h3>
                            <p class="text-xs text-gray-600 line-clamp-2">${feature.description}</p>
                        </div>
                    </div>
                `;
                card.addEventListener('click', () => selectFeature(feature.id, card));
                container.appendChild(card);
            });
        }

        // Select feature
        function selectFeature(featureId, element) {
            const allCards = document.querySelectorAll('#features-container > div');
            allCards.forEach(card => {
                card.className = 'p-3 cursor-pointer transition-all hover:shadow-md border-2 border-gray-200 hover:border-green-300 rounded-lg';
            });
            
            selectedFeature = featureId;
            element.className = 'p-3 cursor-pointer transition-all hover:shadow-md border-2 border-green-600 bg-green-50 shadow-md rounded-lg';
            document.getElementById('clear-feature').classList.remove('hidden');
        }

        // Clear feature selection
        document.getElementById('clear-feature').addEventListener('click', () => {
            selectedFeature = null;
            const allCards = document.querySelectorAll('#features-container > div');
            allCards.forEach(card => {
                card.className = 'p-3 cursor-pointer transition-all hover:shadow-md border-2 border-gray-200 hover:border-green-300 rounded-lg';
            });
            document.getElementById('clear-feature').classList.add('hidden');
        });

        // Initialize sample prompts
        function initSamplePrompts() {
            const container = document.getElementById('sample-prompts');
            Object.values(samplePrompts).flat().forEach(prompt => {
                const btn = document.createElement('button');
                btn.className = 'text-left h-auto py-2 px-3 border border-gray-300 rounded-lg text-xs sm:text-sm hover:bg-green-50 hover:border-green-300 whitespace-normal';
                btn.textContent = prompt;
                btn.addEventListener('click', () => sendMessage(prompt));
                container.appendChild(btn);
            });
        }

        // Add message to chat
        function addMessage(role, content) {
            const messagesContainer = document.getElementById('chat-messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `flex gap-3 ${role === 'user' ? 'justify-end' : ''}`;
            
            if (role === 'user') {
                messageDiv.innerHTML = `
                    <div class="max-w-[85%] sm:max-w-[80%] rounded-2xl px-4 py-3 bg-green-600 text-white">
                        <div class="whitespace-pre-wrap text-sm sm:text-base">${escapeHtml(content)}</div>
                    </div>
                    <div class="flex-shrink-0 w-10 h-10 rounded-full bg-green-600 flex items-center justify-center">
                        <i data-lucide="user" class="w-6 h-6 text-white"></i>
                    </div>
                `;
            } else {
                const htmlContent = marked.parse(content);
                messageDiv.innerHTML = `
                    <div class="flex-shrink-0 w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
                        <i data-lucide="bot" class="w-6 h-6 text-green-600"></i>
                    </div>
                    <div class="max-w-[85%] sm:max-w-[80%] rounded-2xl px-4 py-3 bg-gray-100 text-gray-800">
                        <div class="prose prose-sm">${htmlContent}</div>
                    </div>
                `;
            }
            
            messagesContainer.appendChild(messageDiv);
            lucide.createIcons();
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        // Show loading indicator
        function showLoading() {
            const messagesContainer = document.getElementById('chat-messages');
            const loadingDiv = document.createElement('div');
            loadingDiv.id = 'loading-indicator';
            loadingDiv.className = 'flex items-center gap-2 text-gray-500';
            loadingDiv.innerHTML = `
                <i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i>
                <span class="text-sm">Thinking<span class="loading-dots"></span></span>
            `;
            messagesContainer.appendChild(loadingDiv);
            lucide.createIcons();
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        // Remove loading indicator
        function removeLoading() {
            const loadingDiv = document.getElementById('loading-indicator');
            if (loadingDiv) loadingDiv.remove();
        }

        // Send message
        async function sendMessage(customMessage = null) {
            if (isLoading) return;
            
            const input = document.getElementById('user-input');
            const message = customMessage || input.value.trim();
            
            if (!message) return;
            
            // Add user message
            addMessage('user', message);
            chatHistory.push({ role: 'user', content: message });
            
            if (!customMessage) input.value = '';
            
            isLoading = true;
            document.getElementById('send-btn').disabled = true;
            showLoading();
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: message,
                        feature: selectedFeature,
                        history: chatHistory
                    })
                });
                
                const data = await response.json();
                removeLoading();
                
                if (data.error) {
                    addMessage('assistant', `Error: ${data.error}`);
                } else {
                    addMessage('assistant', data.response);
                    chatHistory.push({ role: 'assistant', content: data.response });
                }
            } catch (error) {
                removeLoading();
                addMessage('assistant', `Error: ${error.message}`);
            }
            
            isLoading = false;
            document.getElementById('send-btn').disabled = false;
        }

        // Event listeners
        document.getElementById('send-btn').addEventListener('click', () => sendMessage());
        
        document.getElementById('user-input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // Utility function
        function escapeHtml(text) {
            const map = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            };
            return text.replace(/[&<>"']/g, m => map[m]);
        }

        // Initialize on load
        document.addEventListener('DOMContentLoaded', () => {
            initFeatures();
            initSamplePrompts();
        });
    </script>
</body>
</html>
"""

# =============================================================================
# ROUTES
# =============================================================================

@app.route('/')
def index():
    """Render main page"""
    return render_template_string(
        HTML_TEMPLATE, 
        features=FEATURES,
        sample_prompts=SAMPLE_PROMPTS
    )

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.json
        user_message = data.get('message', '')
        feature = data.get('feature')
        history = data.get('history', [])
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Generate AI response
        ai_response = get_ai_response(user_message, feature, history)
        
        return jsonify({
            'response': ai_response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("🌾 AgroNova Smart Farming Assistant")
    print("=" * 70)
    print(f"\n✅ Server starting...")
    print(f"🌐 Open your browser and go to: http://localhost:5000")
    print(f"\n⚠️  Important: Make sure to add your Gemini API key in the code!")
    print(f"   Look for: app_key = 'YOUR_GEMINI_API_KEY_HERE'")
    print(f"\n📝 Press Ctrl+C to stop the server")
    print("=" * 70)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
