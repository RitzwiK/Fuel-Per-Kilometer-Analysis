import time
import re
import os
import base64
import requests
import numpy as np
import pandas as pd
import pickle as pk
import streamlit as st
from streamlit_lottie import st_lottie
import feedparser
import plotly.express as px
from io import BytesIO

loaded_model = pk.load(open("trained_model_lr.sav", "rb"))
scaled_data  = pk.load(open("scaled_data.sav", "rb"))

st.set_page_config(page_title="FuelSense Analysis", page_icon="⛽", layout="wide")

DARK_DASHBOARD_IMAGES = [
    "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=400&h=400&fit=crop&q=80",
    "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=400&h=400&fit=crop&q=80",
    "https://images.unsplash.com/photo-1605559424843-9e4c228bf1c2?w=400&h=400&fit=crop&q=80",
    "https://images.unsplash.com/photo-1494976688754-90f4743b2d1e?w=400&h=400&fit=crop&q=80",
    "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=400&h=400&fit=crop&q=80",
]

BACKGROUND_TEXTURE_URL = "https://images.unsplash.com/photo-1617886903355-9354bb57751f?w=1920&h=1080&fit=crop&q=80"

@st.cache_data
def fetch_image_as_base64_with_mime(url, timeout=8):
    try:
        response = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200 and response.content:
            ctype = response.headers.get("Content-Type", "").lower()
            if "png" in ctype:
                mime = "image/png"
            elif "svg" in ctype:
                mime = "image/svg+xml"
            elif "jpeg" in ctype or "jpg" in ctype:
                mime = "image/jpeg"
            else:
                mime = "image/jpeg"
            b64 = base64.b64encode(response.content).decode()
            return b64, mime
    except Exception:
        pass
    return None

def create_dark_automotive_svg(width=120, height=120):
    svg_content = f"""<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' viewBox='0 0 {width} {height}'>
        <defs>
            <radialGradient id='dashGrad' cx='50%' cy='50%' r='50%'>
                <stop offset='0%' style='stop-color:#2a2a2a;stop-opacity:1' />
                <stop offset='100%' style='stop-color:#0f0f0f;stop-opacity:1' />
            </radialGradient>
            <linearGradient id='needleGrad' x1='0%' y1='0%' x2='100%' y2='100%'>
                <stop offset='0%' style='stop-color:#ffffff;stop-opacity:0.8' />
                <stop offset='100%' style='stop-color:#cccccc;stop-opacity:0.6' />
            </linearGradient>
        </defs>
        <rect width='100%' height='100%' fill='url(#dashGrad)' rx='12'/>
        <circle cx='{width//2}' cy='{height//2}' r='{width//3}' fill='none' stroke='#333' stroke-width='2'/>
        <circle cx='{width//2}' cy='{height//2}' r='{width//4}' fill='none' stroke='#444' stroke-width='1'/>
        <line x1='{width//2}' y1='{height//2}' x2='{width//2 + width//4}' y2='{height//2 - height//8}' stroke='url(#needleGrad)' stroke-width='3' stroke-linecap='round'/>
        <circle cx='{width//2}' cy='{height//2}' r='4' fill='url(#needleGrad)'/>
        <text x='{width//2}' y='{height - 15}' text-anchor='middle' fill='#888' font-family='Arial' font-size='10' font-weight='bold'>FUEL</text>
    </svg>"""
    return base64.b64encode(svg_content.encode()).decode(), "image/svg+xml"

def load_lottie(url):
    try:
        r = requests.get(url, timeout=8)
        return r.json() if r.status_code == 200 else None
    except:
        return None

def show_enhanced_loading_animation():
    loading_placeholder = st.empty()
    with loading_placeholder.container():
        st.markdown("""
            <div style='display:flex;flex-direction:column;align-items:center;justify-content:center;height:45vh;'>
                <div style='position:relative;margin-bottom:1.2rem;'>
                    <div style='font-size:5.5rem;animation: pumpPulse 2s ease-in-out infinite;color:#ffffff;filter:drop-shadow(0 0 10px rgba(255,255,255,0.3));'>⛽</div>
                    <div style='position:absolute;top:-10px;right:-5px;font-size:1.5rem;animation: sparkle 1.5s ease-in-out infinite alternate;'>✨</div>
                </div>
                <h2 style='color:#fff;font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display",Inter, sans-serif;font-weight:600;margin-bottom:1rem;letter-spacing:0.5px;'>ANALYZING FUEL DATA</h2>
                <div style='width:320px;height:6px;background:rgba(255,255,255,0.08);border-radius:4px;overflow:hidden;box-shadow:inset 0 2px 4px rgba(0,0,0,0.3);'>
                    <div style='width:100%;height:100%;background:linear-gradient(90deg, #333, #666, #999, #666, #333);animation: fuelFlow 2.5s linear infinite;'></div>
                </div>
                <p style='color:#bbb;font-size:0.9rem;margin-top:1rem;'>Preparing your personalized insights...</p>
            </div>
            <style>
                @keyframes pumpPulse { 0%, 100% { transform: scale(1) } 50% { transform: scale(1.08) } }
                @keyframes sparkle { 0% { opacity: 0.4; transform: rotate(0deg) } 100% { opacity: 1; transform: rotate(15deg) } }
                @keyframes fuelFlow { 0% { transform: translateX(-100%);} 25% { transform: translateX(-50%);} 50% { transform: translateX(0%);} 75% { transform: translateX(50%);} 100% { transform: translateX(100%);} }
            </style>
        """, unsafe_allow_html=True)
    time.sleep(2.2)
    loading_placeholder.empty()

show_enhanced_loading_animation()

bg_texture_result = fetch_image_as_base64_with_mime(BACKGROUND_TEXTURE_URL)
bg_texture_b64 = bg_texture_result[0] if bg_texture_result else None

if bg_texture_b64:
    bg_css = f"""
    background-image: url('data:image/jpeg;base64,{bg_texture_b64}'), linear-gradient(180deg, rgba(0,0,0,0.88) 0%, rgba(8,8,10,0.92) 100%) !important;
    background-size: cover, cover !important;
    background-position: center, center !important;
    background-repeat: no-repeat, no-repeat !important;
    background-attachment: fixed, fixed !important;
    background-blend-mode: overlay !important;
    """
else:
    bg_css = "background: linear-gradient(180deg, #000000 0%, #0a0a0a 50%, #050505 100%), radial-gradient(circle at 20% 30%, rgba(255,255,255,0.015), transparent 25%), radial-gradient(circle at 80% 70%, rgba(255,255,255,0.01), transparent 20%) !important;"

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  * {{
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", Inter, sans-serif !important;
    -webkit-font-smoothing: antialiased !important;
    -moz-osx-font-smoothing: grayscale !important;
    color: #f5f5f5 !important;
  }}

  /* background from Python variable */
  .stApp {{ {bg_css} }}
  .main {{ {bg_css} }}
  [data-testid="stAppViewContainer"] {{ {bg_css} }}

  [data-testid="stHeader"] {{ background: transparent !important; }}
  .block-container {{ background: transparent !important; }}

  /* Reduced top padding for the header area - minimizes open space */
  .header-compact {{
    padding: 8px 0 6px 0 !important;
    margin-bottom: 6px !important;
  }}

  /* Tiny textured strip style (no external images used) */
  .header-texture {{
    width: 100%;
    height: 58px;
    border-radius: 10px;
    margin: 0 auto 6px auto;
    max-width: 900px;
    background: linear-gradient(180deg, rgba(10,10,12,0.85), rgba(20,20,22,0.7));
    box-shadow: 0 6px 28px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.02);
    display:flex;
    align-items:center;
    justify-content:center;
    overflow:hidden;
    position:relative;
  }}

  /* subtle pattern overlay (CSS-only) */
  .header-texture::before {{
    content: '';
    position: absolute;
    inset: 0;
    background-image:
      linear-gradient(90deg, rgba(255,255,255,0.005) 1px, transparent 1px),
      linear-gradient(180deg, rgba(255,255,255,0.01) 1px, transparent 1px);
    background-size: 40px 40px, 40px 40px;
    opacity: 0.04;
    pointer-events: none;
  }}

  /* Big, bold title — correct class name: .fuel-main-title */
  .fuel-main-title {{
    font-size: 4.8rem !important;
    font-weight: 900 !important;
    line-height: 1.02 !important;
    margin: 10px 0 8px 0 !important;
    letter-spacing: -0.02em !important;
    text-shadow: 0 3px 8px rgba(0,0,0,0.45) !important;
    background: linear-gradient(135deg, #ffffff 0%, #e0e0e0 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
  }}

  /* --- Make Streamlit sliders match the FuelSense title tone --- */
  :root {{
    --fuel-title-color: #e0e0e0;
    --fuel-title-gradient: linear-gradient(90deg, #ffffff, #e0e0e0);
  }}

  /* generic range input override (modern browsers) */
  input[type="range"] {{
    accent-color: var(--fuel-title-color) !important;
  }}

  /* webkit track + thumb */
  input[type="range"]::-webkit-slider-runnable-track {{
    background: var(--fuel-title-gradient) !important;
    height: 6px !important;
    border-radius: 10px !important;
  }}
  input[type="range"]::-webkit-slider-thumb {{
    -webkit-appearance: none !important;
    appearance: none !important;
    width: 18px !important;
    height: 18px !important;
    border-radius: 6px !important;
    background: var(--fuel-title-color) !important;
    border: 2px solid rgba(255,255,255,0.08) !important;
    margin-top: -6px !important; /* center the thumb on the track */
    box-shadow: 0 4px 14px rgba(0,0,0,0.45) !important;
  }}

  /* Firefox */
  input[type="range"]::-moz-range-track {{
    background: var(--fuel-title-gradient) !important;
    height: 6px !important;
    border-radius: 10px !important;
  }}
  input[type="range"]::-moz-range-thumb {{
    background: var(--fuel-title-color) !important;
    width: 18px !important;
    height: 18px !important;
    border: 2px solid rgba(255,255,255,0.08) !important;
    border-radius: 6px !important;
  }}

  /* Streamlit rc-slider specific overrides */
  .stSlider .rc-slider-rail {{
    background: rgba(255,255,255,0.08) !important;
    height: 6px !important;
    border-radius: 10px !important;
  }}
  .stSlider .rc-slider-track {{
    background: var(--fuel-title-gradient) !important;
    height: 6px !important;
    border-radius: 10px !important;
  }}
  .stSlider .rc-slider-handle {{
    background: var(--fuel-title-color) !important;
    border: 2px solid rgba(255,255,255,0.08) !important;
    box-shadow: 0 6px 18px rgba(0,0,0,0.45) !important;
  }}

  /* Subheading under title */
  p.sub-head {{
    text-align: center;
    color: #c5c5c5;
    font-size: 1.12rem;
    margin-bottom: 30px;
    font-weight: 500;
    letter-spacing: 0.3px;
    line-height: 1.4;
  }}

  /* Preserve all original interactive element styling below */
  .glass-card {{
    background: linear-gradient(180deg, rgba(15,15,15,0.85), rgba(8,8,8,0.9)) !important;
    backdrop-filter: blur(20px) saturate(120%) !important;
    border: 1px solid rgba(255,255,255,0.04) !important;
    border-radius: 20px !important;
    padding: 32px !important;
    margin: 24px 0 !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.05) !important;
  }}

  /* keep responsive title scaling */
  @media (max-width: 1100px) {{
    .fuel-main-title {{ font-size: 3.6rem !important; }}
  }}
  @media (max-width: 768px) {{
    .fuel-main-title {{ font-size: 2.4rem !important; }}
    .header-texture {{ height: 44px; }}
  }}
 .stButton button {{
  display: block !important;
  margin: 10px auto !important;
  width: 100%;
  max-width: 600px;
}}

.stTextInput {{
  margin: 10px auto !important;
  display: block !important;
}}

</style>
""", unsafe_allow_html=True)

st.markdown("<div class='header-compact' style='text-align:center;'>", unsafe_allow_html=True)

st.markdown("<div class='header-texture' aria-hidden='true'></div>", unsafe_allow_html=True)

st.markdown("""
    <h1 class='fuel-main-title' style='text-align: center;'>
        FuelSense Analysis
    </h1>
    <p class='sub-head'>Advanced fuel forecasts, predictive insights & clear recommendations</p>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

with st.expander("🔧 VEHICLE CONFIGURATION & LATEST NEWS", expanded=False):
    st.markdown("""
        <div style='text-align: center; margin-bottom: 28px;'>
            <h3 style='color: #ffffff; font-size: 1.7rem; font-weight: 700; margin-bottom: 8px; 
                          text-shadow: 0 1px 2px rgba(0,0,0,0.3);'>Configure Your Vehicle</h3>
            <p style='color: #c0c0c0; font-size: 1.02rem; line-height: 1.5;'>
                Fine-tune your vehicle specifications for accurate fuel predictions
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    vehicle_map = {
        '🏎️ Two-Seater': 'Two-seater',
        '🚙 Compact': 'Compact', 
        '🚗 Subcompact': 'Subcompact',
        '🚐 Minivan': 'Minivan',
        '🚙 SUV Small': 'SUV: Small',
        '🚚 Pickup Standard': 'Pickup truck: Standard'
    }

    trans_map = {
        '🔄 Automatic': 'A',
        '⚙️ Manual': 'M',
        '🔄 CVT': 'AV',
        '🔀 Auto-Manual': 'AM',
        '⚙️ Auto-Shift': 'AS'
    }

    fuel_map = {
        '⛽ Diesel': 'D',
        '🌱 Ethanol': 'E', 
        '⛽ Gasoline': 'X',
        '⚡ Electric': 'Z'
    }

    col1, col2 = st.columns(2, gap="large")

    with col1:
        veh_choice = st.selectbox("🚗 Vehicle Class", list(vehicle_map.keys()), key="vehicle")
        engine = st.slider("🔧 Engine Size (Liters)", 1, 7, 3, key="engine")
        cyl = st.slider("⚙️ Number of Cylinders", 1, 16, 4, key="cylinders")

    with col2:
        trans_choice = st.selectbox("🔄 Transmission Type", list(trans_map.keys()), key="transmission")
        co2 = st.slider("🌍 CO₂ Emission Rating (1-10)", 1, 10, 5, key="co2")
        fuel_choice = st.selectbox("⛽ Fuel Type", list(fuel_map.keys()), key="fuel")

    st.markdown("<div style='display: flex; justify-content: center; margin: 32px 0;'>", unsafe_allow_html=True)

    if st.button("✨ Calculate Fuel Consumption", key="calculate", help="Get AI-powered fuel consumption prediction"):
        with st.spinner("🧠 AI is analyzing your vehicle configuration..."):
            time.sleep(1.5)

            inp = [
                vehicle_map[veh_choice], engine, cyl,
                trans_map[trans_choice], co2, fuel_map[fuel_choice]
            ]

            vcl = list(vehicle_map.values())
            t = list(trans_map.values())
            f = list(fuel_map.values())

            lst = [vcl.index(inp[0]), inp[1], inp[2], t.index(inp[3]), inp[4]]
            oh = [0] * 4
            oh[f.index(inp[5])] = 1
            lst.extend(oh)
            lst.extend([0, 0, 0])

            arr = np.array(lst).reshape(1, -1)
            pred = loaded_model.predict(scaled_data.transform(arr))[0]

            st.success(f"🎯 **Predicted Fuel Consumption:** {pred:.2f} L/100 km")

            if pred < 5:
                efficiency = "🌟 Exceptional Efficiency"
                color = "#a8e6a3"
                advice = "Your vehicle configuration shows outstanding fuel economy. Perfect for long-distance travel!"
            elif pred < 7:
                efficiency = "✅ Excellent Efficiency"
                color = "#c5e8c1"
                advice = "Great fuel economy! This configuration balances performance and efficiency well."
            elif pred < 9:
                efficiency = "👍 Good Efficiency"
                color = "#e2e2e2"
                advice = "Solid fuel consumption. Consider hybrid options for better efficiency."
            elif pred < 12:
                efficiency = "⚠️ Average Consumption"
                color = "#f0d794"
                advice = "Higher than average consumption. Consider smaller engine or hybrid alternatives."
            else:
                efficiency = "🔺 High Consumption"
                color = "#f5b7b1"
                advice = "Significantly high fuel consumption. Review your vehicle configuration for better efficiency."

            st.markdown(
                f"""
                <div style='text-align: center; padding: 24px; 
                            background: linear-gradient(135deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01)); 
                            border-radius: 16px; margin: 20px 0;
                            border: 1px solid rgba(255,255,255,0.05);
                            box-shadow: 0 4px 16px rgba(0,0,0,0.2);'>
                    <h4 style='color: {color}; margin: 0 0 8px 0; font-size: 1.3rem; font-weight: 600;'>{efficiency}</h4>
                    <p style='color: #bbb; font-size: 0.95rem; margin: 0; line-height: 1.4;'>{advice}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style='height: 1px; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent); 
                margin: 32px 0;'></div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style='text-align: center; margin: 24px 0 16px 0;'>
            <h3 style='color: #f0f0f0; font-size: 1.4rem; font-weight: 700; margin-bottom: 8px;
                          text-shadow: 0 1px 2px rgba(0,0,0,0.3);'>
                📰 Latest Automotive & Fuel News
            </h3>
            <p style='color: #aaa; font-size: 0.92rem;'>Stay updated with the latest industry trends</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        with st.spinner("🔄 Fetching latest automotive news..."):
            feed = feedparser.parse("https://feeds.bbci.co.uk/news/topics/cpzpydkymr4t/rss.xml")
            keywords = ['fuel', 'mileage', 'electric', 'efficiency', 'car', 'auto', 'vehicle', 'hybrid', 'gasoline', 'diesel']
            arts = [e for e in feed.entries if any(k in e.title.lower() or k in e.summary.lower() for k in keywords)][:6]

            if arts:
                for i, entry in enumerate(arts):
                    title = entry.title.strip()
                    summary = re.sub(r'<[^>]+>', '', entry.summary).strip()[:120] + "..."
                    pub_date = entry.get('published', 'Unknown date')
                    link = entry.get('link', '#')
                    
                    st.markdown(f"""
                    <div class='news-item'>
                        <h5 style='color: #fff; font-size: 1.1rem; font-weight: 600; margin: 0 0 8px 0; line-height: 1.3;'>
                            <a href='{link}' target='_blank' style='color: inherit; text-decoration: none;'>{title}</a>
                        </h5>
                        <p style='color: #bbb; font-size: 0.9rem; margin: 0 0 6px 0; line-height: 1.4;'>{summary}</p>
                        <p style='color: #888; font-size: 0.8rem; margin: 0;'>{pub_date}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
            else:
                st.markdown("""
                <div style='text-align: center; padding: 20px; color: #999; font-style: italic;'>
                    No automotive news found at the moment. Please try again later.
                </div>
                """, unsafe_allow_html=True)
                
    except Exception as e:
        st.markdown("""
        <div style='text-align: center; padding: 20px; color: #999; font-style: italic;'>
            Unable to fetch news at the moment. Please check your internet connection.
        </div>
        """, unsafe_allow_html=True)

# ----------------------------------
# FUEL INSIGHTS & ANALYTICS DASHBOARD 
# ----------------------------------
with st.expander("📊 FUEL INSIGHTS & ANALYTICS DASHBOARD", expanded=False):
    st.markdown("""
        <div style='text-align: center; margin-bottom: 28px;'>
            <h3 style='color: #ffffff; font-size: 1.7rem; font-weight: 700; margin-bottom: 8px; 
                          text-shadow: 0 1px 2px rgba(0,0,0,0.3);'>Advanced Analytics Dashboard</h3>
            <p style='color: #c0c0c0; font-size: 1.02rem; line-height: 1.5;'>
                Comprehensive fuel consumption analysis and market insights
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    sample_data = pd.DataFrame({
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'Fuel Consumption': [8.2, 7.8, 8.5, 7.9, 8.1, 7.6],
        'Cost (USD)': [120, 115, 125, 118, 121, 112],
        'Efficiency Rating': [85, 88, 82, 87, 84, 89]
    })

    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig1 = px.line(sample_data, x='Month', y='Fuel Consumption', 
                      title='Monthly Fuel Consumption Trend',
                      color_discrete_sequence=['#ffffff'])
        fig1.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#ffffff',
            title_font_color='#ffffff',
            title_font_size=16
        )
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig2 = px.bar(sample_data, x='Month', y='Efficiency Rating',
                     title='Monthly Efficiency Ratings',
                     color_discrete_sequence=['#666666'])
        fig2.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#ffffff',
            title_font_color='#ffffff',
            title_font_size=16
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style='height: 1px; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent); 
                margin: 24px 0;'></div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style='text-align: center; padding: 16px; background: linear-gradient(135deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01)); 
                    border-radius: 12px; border: 1px solid rgba(255,255,255,0.05);'>
            <h4 style='color: #a8e6a3; margin: 0; font-size: 1.8rem; font-weight: 700;'>7.85</h4>
            <p style='color: #bbb; margin: 0; font-size: 0.9rem;'>Avg L/100km</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 16px; background: linear-gradient(135deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01)); 
                    border-radius: 12px; border: 1px solid rgba(255,255,255,0.05);'>
            <h4 style='color: #c5e8c1; margin: 0; font-size: 1.8rem; font-weight: 700;'>85%</h4>
            <p style='color: #bbb; margin: 0; font-size: 0.9rem;'>Efficiency</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div style='text-align: center; padding: 16px; background: linear-gradient(135deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01)); 
                    border-radius: 12px; border: 1px solid rgba(255,255,255,0.05);'>
            <h4 style='color: #f0d794; margin: 0; font-size: 1.8rem; font-weight: 700;'>$118</h4>
            <p style='color: #bbb; margin: 0; font-size: 0.9rem;'>Avg Cost</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown("""
        <div style='text-align: center; padding: 16px; background: linear-gradient(135deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01)); 
                    border-radius: 12px; border: 1px solid rgba(255,255,255,0.05);'>
            <h4 style='color: #e2e2e2; margin: 0; font-size: 1.8rem; font-weight: 700;'>12%</h4>
            <p style='color: #bbb; margin: 0; font-size: 0.9rem;'>Improvement</p>
        </div>
        """, unsafe_allow_html=True)


import streamlit.components.v1 as components  # safe to add here

contact_html = """
<style>
/* compact contact row styling */
.contact-row {
  text-align: center;
  margin-top: 18px;
  margin-bottom: 8px;
  color: #cfcfcf;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", Inter, sans-serif;
}
.contact-row .built-by {
  margin: 0;
  color: #bbb;
  font-size: 0.95rem;
}
.contact-row .name {
  color: #ffffff;
  font-weight: 700;
  letter-spacing: 0.4px;
}
.contact-row .one-liner {
  margin: 6px 0 12px 0;
  color: #aaa;
  font-size: 0.92rem;
}

/* icons */
.contact-icons {
  display:flex;
  justify-content:center;
  gap:18px;
  align-items:center;
}
.contact-icons a {
  display:inline-flex;
  align-items:center;
  justify-content:center;
  width:40px;
  height:40px;
  border-radius:8px;
  text-decoration:none;
  transition: transform 0.12s ease, box-shadow 0.12s ease;
}
.contact-icons a svg {
  width:24px;
  height:24px;
  display:block;
}
.contact-icons a:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 18px rgba(255,255,255,0.04);
}
/* ensure svg strokes/fills are visible on hover */
.contact-icons a:hover svg * {
  stroke: #ffffff !important;
  fill: #ffffff !important;
}
</style>

<div class="contact-row" aria-label="Built by and contact">
  <p class="built-by">Built by <span class="name">RITWIK</span></p>
  <p class="one-liner">Less fuel, more miles.</p>

<div class="contact-icons" role="list" style="display:flex; gap:15px; justify-content:center; margin-top:20px;">
  
  <!-- LinkedIn -->
  <a role="listitem" title="Open LinkedIn" href="https://www.linkedin.com/in/ritwik-k-68537a285/" 
     target="_blank" rel="noopener noreferrer">
    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" width="28" height="28">
      <rect x="2" y="3" width="20" height="18" rx="2" stroke="#c5c5c5" stroke-width="1.2" fill="none"/>
      <path d="M7 10.5V18" stroke="#c5c5c5" stroke-width="1.2" stroke-linecap="round"/>
      <circle cx="7" cy="7.5" r="1.1" fill="#c5c5c5"/>
      <path d="M11.5 18V13.5c0-1.1.9-2 2-2s2 .9 2 2V18" 
            stroke="#c5c5c5" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  </a>

  <!-- GitHub -->
  <a role="listitem" title="Open GitHub" href="https://github.com/RitzwiK" 
     target="_blank" rel="noopener noreferrer">
    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" width="28" height="28">
      <path d="M12 .6C5.9.6.9 5.6.9 11.7c0 4.9 3.2 9 7.6 10.5.6.1.8-.3.8-.6v-2.1c-3.1.7-3.7-1.4-3.7-1.4-.5-1.2-1.3-1.6-1.3-1.6-1-.7.1-.7.1-.7 1.1.1 1.7 1.1 1.7 1.1 1 .1 1.7-.8 2.1-1.3-.8-.1-1.7-.4-1.7-1.9 0-.4.1-.8.3-1.1-.3-.1-1.1-.5-.1-1 0 0 .8-.2 2.2.9.6-.2 1.2-.3 1.9-.3s1.3.1 1.9.3c1.4-1.1 2.2-.9 2.2-.9.9.5.2.9.1 1-0.2.3-.3.7-.3 1.1 0 1.5-.9 1.8-1.7 1.9.4.4.8 1.1.8 2.2v3.2c0 .3.2.7.8.6 4.4-1.5 7.6-5.7 7.6-10.5C23.1 5.6 18.1.6 12 .6z"
            stroke="#c5c5c5" stroke-width="0.3" fill="#c5c5c5"/>
    </svg>
  </a>

  <!-- Email -->
  <a role="listitem" title="Send Email" href="mailto:kritwik495@gmail.com" 
     target="_blank" rel="noopener noreferrer">
    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" width="28" height="28">
      <rect x="2.5" y="4" width="19" height="16" rx="2" stroke="#c5c5c5" stroke-width="1.2" fill="none"/>
      <path d="M3.5 7.5l7.5 5 7.5-5" stroke="#c5c5c5" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  </a>
 </div>
</div>
"""

components.html(contact_html, height=160, scrolling=False)
# ----------------------------------
# FOOTER 
# ----------------------------------
st.markdown("""
<div style='text-align: center; padding: 40px 0 20px 0; margin-top: 40px; 
            border-top: 1px solid rgba(255,255,255,0.05);'>
    <p style='color: #888; font-size: 0.9rem; margin: 0;'>
        FuelSense Analysis • Advanced Automotive Intelligence Platform
    </p>
    <p style='color: #666; font-size: 0.8rem; margin: 8px 0 0 0;'>
        Powered by Machine Learning & Real-time Data Analytics
    </p>
</div>
""", unsafe_allow_html=True)
