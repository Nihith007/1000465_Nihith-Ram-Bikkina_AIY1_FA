"""
Smart Farming Assistant - Streamlit Application (Pure Python Version)
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

# =============================================================================
# CONFIGURATION - USING STREAMLIT SECRETS
# =============================================================================
try:
    app_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=app_key)
except Exception as e:
    st.error("⚠️ **Gemini API Key Not Found!**")
    st.info("""
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
    model_name="gemini-2.5-flash",
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
def get_ai_response(user_message, feature=None, _chat_history=None):
    """Generate AI response using Gemini API"""
    try:
        conversation = []
        
        system_prompt = generate_system_prompt(feature)
        conversation.append({
            "role": "user",
            "parts": [system_prompt]
        })
        conversation.append({
            "role": "model",
            "parts": ["I understand. I'm AgroNova, your agricultural assistant. I'll provide practical, region-specific farming advice with clear formatting and actionable steps."]
        })
        
        if _chat_history:
            for msg in _chat_history[-6:]:
                role = "user" if msg["role"] == "user" else "model"
                conversation.append({
                    "role": role,
                    "parts": [msg["content"]]
                })
        
        chat = model.start_chat(history=conversation)
        response = chat.send_message(user_message)
        
        return response.text
        
    except Exception as e:
        error_msg = f"""**Error Processing Request**

I encountered an issue generating a response. This could be due to:
- API key not configured properly
- Network connectivity issues
- API rate limits

**Please ensure:**
1. Your Gemini API key is correctly set in Streamlit secrets
2. You have an active internet connection
3. Your API key has sufficient quota

Error details: {str(e)}"""
        return error_msg


# =============================================================================
# UI COMPONENTS (PURE PYTHON)
# =============================================================================

def render_header():
    """Render the header using native Streamlit components"""
    # Create a colored container using columns and containers
    header_container = st.container()
    with header_container:
        st.markdown("# 🌾 AgroNova")
        st.markdown("#### Smart Farming Assistant powered by Gemini AI")
        st.markdown("---")

def render_sidebar():
    """Render the sidebar with features"""
    with st.sidebar:
        st.markdown("### 📋 Features")
        st.caption("Select a feature to get specialized advice:")
        
        for feature in FEATURES:
            is_selected = st.session_state.selected_feature == feature["id"]
            
            # Create a container for each feature
            with st.container():
                if st.button(
                    feature['title'],
                    key=feature["id"],
                    use_container_width=True,
                    type="primary" if is_selected else "secondary",
                    help=feature['description']
                ):
                    st.session_state.selected_feature = feature["id"]
                    st.rerun()
                
                if is_selected:
                    st.success(feature['description'])
                else:
                    st.caption(feature['description'])
        
        if st.session_state.selected_feature:
            st.markdown("")
            if st.button("🔄 Clear Selection", use_container_width=True):
                st.session_state.selected_feature = None
                st.rerun()
        
        st.divider()
        
        st.markdown("### 🌍 Global Coverage")
        st.info("Get region-specific advice for farming practices worldwide. Supporting farmers in India, Kenya, Brazil, Italy, and more!")
        
        st.divider()
        
        st.markdown("### ℹ️ About")
        st.caption("Supporting UN SDG 2 (Zero Hunger) & SDG 13 (Climate Action)")
        st.caption("Built with Streamlit & Gemini AI")

def render_sample_prompts():
    """Render sample prompts using native Streamlit components"""
    st.markdown("### ✨ Try These Sample Questions")
    
    if st.session_state.selected_feature:
        prompts = SAMPLE_PROMPTS.get(st.session_state.selected_feature, [])
    else:
        prompts = []
        for prompt_list in SAMPLE_PROMPTS.values():
            prompts.extend(prompt_list[:2])
    
    cols = st.columns(2)
    for idx, prompt in enumerate(prompts[:8]):
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
    
    # Display chat messages using native Streamlit chat components
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant", avatar="🌾"):
                    st.write(message["content"])
    
    # Chat input
    st.divider()
    
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
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.spinner("🤔 Thinking..."):
            response = get_ai_response(
                user_input,
                st.session_state.selected_feature,
                st.session_state.messages
            )
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
    
    # Sample prompts
    st.divider()
    render_sample_prompts()
    
    # Clear chat button
    if len(st.session_state.messages) > 1:
        st.divider()
        if st.button("🗑️ Clear Chat History", type="secondary"):
            st.session_state.messages = [st.session_state.messages[0]]
            st.rerun()

if __name__ == "__main__":
    main()
