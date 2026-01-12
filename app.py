"""
Smart Farming Assistant - Streamlit Application
Powered by Google Gemini AI

Installation:
pip install streamlit google-generativeai

Usage:
1. Add your Gemini API key to Streamlit secrets (.streamlit/secrets.toml)
2. Run: streamlit run app.py

Streamlit Secrets Setup:
Create .streamlit/secrets.toml file with:
GEMINI_API_KEY = "your_api_key_here"
"""

import streamlit as st
import google.generativeai as genai
from datetime import datetime

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="AgroNova - Smart Farming Assistant",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    .feature-card {
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #e5e7eb;
        cursor: pointer;
        transition: all 0.3s;
        margin-bottom: 0.5rem;
    }
    .feature-card:hover {
        border-color: #10b981;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .feature-card-selected {
        border-color: #059669;
        background-color: #ecfdf5;
    }
    .user-message {
        background-color: #059669;
        color: white;
        padding: 1rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
    }
    .assistant-message {
        background-color: #f3f4f6;
        color: #1f2937;
        padding: 1rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
    }
    .sample-prompt-btn {
        background-color: white;
        border: 1px solid #d1d5db;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        margin: 0.25rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    .sample-prompt-btn:hover {
        border-color: #10b981;
        background-color: #ecfdf5;
    }
    .stButton>button {
        background-color: #059669;
        color: white;
    }
    .stButton>button:hover {
        background-color: #047857;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# CONFIGURATION - USING STREAMLIT SECRETS
# =============================================================================
try:
    # Access API key from Streamlit secrets
    app_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=app_key)
except Exception as e:
    st.error("""
    ⚠️ **Gemini API Key Not Found!**
    
    Please add your API key to Streamlit secrets:
    
    **For local development:**
    1. Create `.streamlit/secrets.toml` file
    2. Add: `GEMINI_API_KEY = "your_api_key_here"`
    
    **For Streamlit Cloud:**
    1. Go to App Settings → Secrets
    2. Add: `GEMINI_API_KEY = "your_api_key_here"`
    
    Get your API key at: https://makersuite.google.com/app/apikey
    """)
    st.stop()

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
        "title": "🌾 Crop Recommendation",
        "description": "Get suggestions for crops based on your location, season, and soil type",
        "color": "#d1fae5"
    },
    {
        "id": "pest-disease",
        "title": "🐛 Pest & Disease Management",
        "description": "Identify and treat crop diseases and pest infestations",
        "color": "#fee2e2"
    },
    {
        "id": "weather-alerts",
        "title": "🌦️ Weather-Based Alerts",
        "description": "Get weather forecasts and farming advice based on conditions",
        "color": "#dbeafe"
    },
    {
        "id": "soil-fertilizer",
        "title": "🌱 Soil & Fertilizer Advice",
        "description": "Receive recommendations for soil treatment and fertilization",
        "color": "#fef3c7"
    },
    {
        "id": "sustainable-farming",
        "title": "♻️ Sustainable Farming Tips",
        "description": "Learn eco-friendly and organic farming practices",
        "color": "#d1fae5"
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
# SESSION STATE INITIALIZATION
# =============================================================================

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": """Welcome to AgroNova Smart Farming Assistant! 🌾

I'm here to help farmers worldwide with AI-powered agricultural advice. Ask me about crops, pests, weather, soil, or sustainable farming practices in your region.

**Select a feature from the sidebar or ask me anything!**"""
        }
    ]

if "selected_feature" not in st.session_state:
    st.session_state.selected_feature = None

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

@st.cache_data(show_spinner=False)
def get_ai_response(user_message, feature=None, chat_history=None):
    """
    Sends a message to Gemini 1.5 and returns the AI response.
    Includes system instructions and recent chat context.
    """
    try:
        # 1️⃣ Create conversation container
        conversation = []

        # 2️⃣ Add system instructions (acts like a system prompt)
        system_prompt = generate_system_prompt(feature)
        conversation.append({
            "role": "user",
            "parts": [system_prompt]
        })

        # 3️⃣ Force Gemini to accept the role (important)
        conversation.append({
            "role": "model",
            "parts": [
                "Understood. I will act as AgroNova, an expert agricultural assistant "
                "providing clear, practical, and region-specific farming advice."
            ]
        })

        # 4️⃣ Add recent chat history (memory)
        if chat_history:
            for msg in chat_history[-6:]:  # keep last 6 messages only
                conversation.append({
                    "role": "user" if msg["role"] == "user" else "model",
                    "parts": [msg["content"]]
                })

        # 5️⃣ Start chat session with Gemini
        chat = model.start_chat(history=conversation)

        # 6️⃣ Send the new user message
        response = chat.send_message(user_message)

        # 7️⃣ Return clean text output
        return response.text

    except Exception as e:
        return f"""
❌ **Error Generating Re**


# =============================================================================
# UI COMPONENTS
# =============================================================================

def render_header():
    """Render the header"""
    st.markdown("""
    <div class="main-header">
        <h1 style="margin:0; font-size: 2rem;">🌾 AgroNova</h1>
        <p style="margin:0; opacity: 0.9;">Smart Farming Assistant powered by Gemini AI</p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render the sidebar with features"""
    with st.sidebar:
        st.markdown("### 📋 Features")
        st.markdown("Select a feature to get specialized advice:")
        
        for feature in FEATURES:
            is_selected = st.session_state.selected_feature == feature["id"]
            
            button_class = "feature-card-selected" if is_selected else ""
            
            if st.button(
                f"{feature['title']}\n{feature['description']}", 
                key=feature["id"],
                use_container_width=True,
                type="primary" if is_selected else "secondary"
            ):
                st.session_state.selected_feature = feature["id"]
                st.rerun()
        
        if st.session_state.selected_feature:
            if st.button("🔄 Clear Selection", use_container_width=True):
                st.session_state.selected_feature = None
                st.rerun()
        
        st.markdown("---")
        st.markdown("""
        ### 🌍 Global Coverage
        Get region-specific advice for farming practices worldwide. 
        Supporting farmers in India, Kenya, Brazil, Italy, and more!
        """)
        
        st.markdown("---")
        st.markdown("""
        ### ℹ️ About
        Supporting UN SDG 2 (Zero Hunger) & SDG 13 (Climate Action)
        
        Built with Streamlit & Gemini AI
        """)

def render_sample_prompts():
    """Render sample prompts"""
    st.markdown("### ✨ Try These Sample Questions")
    
    # Get prompts based on selected feature
    if st.session_state.selected_feature:
        prompts = SAMPLE_PROMPTS.get(st.session_state.selected_feature, [])
    else:
        # Show all prompts
        prompts = []
        for prompt_list in SAMPLE_PROMPTS.values():
            prompts.extend(prompt_list[:2])  # Take 2 from each category
    
    cols = st.columns(2)
    for idx, prompt in enumerate(prompts[:8]):  # Show max 8 prompts
        with cols[idx % 2]:
            if st.button(prompt, key=f"prompt_{idx}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.spinner("🤔 Thinking..."):
                    response = get_ai_response(
                        prompt, 
                        st.session_state.selected_feature,
                        st.session_state.messages
                    )
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()

# =============================================================================
# MAIN APP
# =============================================================================

def main():
    render_header()
    render_sidebar()
    
    # Chat interface
    st.markdown("### 💬 Chat with AgroNova")
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div style="text-align: right;">
                    <div class="user-message" style="display: inline-block; max-width: 80%;">
                        {message["content"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="assistant-message">
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)
    
    # Chat input
    st.markdown("---")
    user_input = st.text_area(
        "Ask me anything about farming...",
        key="user_input",
        placeholder="e.g., What crops should I grow in July in Tamil Nadu?",
        height=100
    )
    
    col1, col2 = st.columns([6, 1])
    with col2:
        send_button = st.button("Send 📤", use_container_width=True, type="primary")
    
    if send_button and user_input.strip():
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Generate AI response
        with st.spinner("🤔 Thinking..."):
            response = get_ai_response(
                user_input,
                st.session_state.selected_feature,
                st.session_state.messages
            )
        
        # Add assistant response
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Rerun to update chat
        st.rerun()
    
    # Sample prompts
    st.markdown("---")
    render_sample_prompts()
    
    # Clear chat button
    if len(st.session_state.messages) > 1:
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = [st.session_state.messages[0]]  # Keep welcome message
            st.rerun()

if __name__ == "__main__":
    main()
