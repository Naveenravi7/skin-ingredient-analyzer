import streamlit as st
import pandas as pd
import plotly.express as px
from src.analyzer import IngredientAnalyzer
import os

st.set_page_config(page_title="The Maester's Analyzer", page_icon="⚔️", layout="wide")

def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Lora:ital,wght@0,400;1,400&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Lora', serif;
        background-color: #1a1a1a;
        color: #e5e5e5;
    }
    
    /* Main area background */
    .stApp {
        background-color: #121212;
        background-image: radial-gradient(circle at center, #2a2a2a 0%, #121212 100%);
    }
    
    h1, h2, h3 {
        font-family: 'Cinzel', serif;
        color: #d4af37; /* Gold */
        text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
    }
    
    .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: #2c2c2c !important;
        color: #d4af37 !important;
        border: 1px solid #8b0000 !important; /* Crimson */
        border-radius: 5px;
        font-family: 'Lora', serif;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #8b0000;
        color: #d4af37;
        border: 2px solid #d4af37;
        font-family: 'Cinzel', serif;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #d4af37;
        color: #8b0000;
        border-color: #8b0000;
    }
    
    /* Cards */
    .card {
        background-color: rgba(30, 30, 30, 0.8);
        padding: 20px;
        border-radius: 5px;
        border: 1px solid #444;
        box-shadow: inset 0 0 10px #000;
        margin-bottom: 20px;
    }
    .card-success {
        border-left: 5px solid #d4af37; /* Gold for good */
    }
    .card-warning {
        border-left: 5px solid #8b0000; /* Crimson for danger */
    }
    
    hr {
        border-color: #d4af37;
    }
    </style>
    """, unsafe_allow_html=True)

load_css()

# Initialize Analyzer
@st.cache_resource
def get_analyzer():
    db_path = 'data/ingredients_db.csv'
    if not os.path.exists(db_path):
        db_path = os.path.join(os.path.dirname(__file__), 'data', 'ingredients_db.csv')
    
    # If the file exists but has < 300 ingredients, delete it so it regenerates
    if os.path.exists(db_path):
        try:
            if len(pd.read_csv(db_path)) < 300:
                os.remove(db_path)
        except Exception as e:
            print("Error checking db size:", e)
            
    return IngredientAnalyzer(db_path=db_path)

analyzer = get_analyzer()

st.title("⚔️ The Maester's Skin Elixir Analyzer")
st.markdown("*\"A wise ruler knows the contents of their potions.\"* - Read the ingredients, protect the realm of your skin.")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Consult the Oracle")
    skin_type = st.selectbox(
        "Declare Your House (Skin Type):",
        ("All", "Dry", "Oily", "Acne", "Sensitive", "Aging")
    )
    
    st.markdown("### Provide the Parchment")
    tab1, tab2, tab3 = st.tabs(["✍️ Write Inscription", "📜 Upload Scroll (Image)", "📸 Capture with Device"])
    
    ingredients_input = ""
    extracted_text = ""
    
    with tab1:
        text_input = st.text_area(
            "Transcribe the ingredients (comma-separated):",
            height=150,
            placeholder="Water (Tears of Lys), Glycerin, Dragonbone extract..."
        )
        
    with tab2:
        st.markdown("*Note: Requires Tesseract-OCR to be installed on your machine.*")
        uploaded_file = st.file_uploader("Upload an image of the potion's label", type=['png', 'jpg', 'jpeg'])
        if uploaded_file is not None:
            st.image(uploaded_file, caption="The Scroll", use_column_width=True)
            with st.spinner("Decoding the ancient runes (OCR)..."):
                extracted_text = analyzer.extract_text_from_image(uploaded_file)
                if extracted_text:
                    st.success("Runes deciphered!")
                    st.text_area("Extracted Text (Edit if needed):", value=extracted_text, height=100, key="ocr_text_upload")
                else:
                    st.error("The runes are illegible. Tesseract-OCR may not be installed or the image is too blurry.")
                    
    with tab3:
        st.markdown("*Use your device's camera to capture the potion label directly.*")
        camera_photo = st.camera_input("Capture Label")
        if camera_photo is not None:
            with st.spinner("Decoding the captured runes (OCR)..."):
                extracted_text = analyzer.extract_text_from_image(camera_photo)
                if extracted_text:
                    st.success("Runes deciphered!")
                    st.text_area("Extracted Text (Edit if needed):", value=extracted_text, height=100, key="ocr_text_camera")
                else:
                    st.error("The runes are illegible. Make sure the text is clear.")
                
    if text_input:
        ingredients_input = text_input
    elif uploaded_file and "ocr_text_upload" in st.session_state:
        ingredients_input = st.session_state.ocr_text_upload
    elif camera_photo and "ocr_text_camera" in st.session_state:
        ingredients_input = st.session_state.ocr_text_camera
    elif (uploaded_file or camera_photo) and extracted_text:
        ingredients_input = extracted_text
        
    analyze_btn = st.button("Unveil the Truth 🔍", use_container_width=True)

with col2:
    st.subheader("The Maester's Verdict")
    if analyze_btn and ingredients_input:
        with st.spinner("Consulting the Grand Library..."):
            cleaned_list = analyzer.clean_ingredient_list(ingredients_input)
            matched_df, unmatched = analyzer.match_ingredients(cleaned_list)
            
            if matched_df.empty:
                st.warning("These elements are unknown to the Citadel. Check your spelling or provide clearer runes.")
            else:
                analysis = analyzer.analyze_for_skin_type(matched_df, skin_type)
                
                # Metrics
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Elements", len(cleaned_list))
                m2.metric("Known to Citadel", len(matched_df))
                m3.metric("Shadow Elements", len(unmatched))
                
                st.markdown("---")
                
                if skin_type != "All":
                    st.markdown(f"### 🛡️ House **{skin_type}** Compatibility")
                    
                    if analysis['good']:
                        st.markdown('<div class="card card-success">', unsafe_allow_html=True)
                        st.markdown("#### 👑 Noble Allies (Beneficial)")
                        for row in analysis['good']:
                            st.markdown(f"- **{row['Ingredient']}**: *{row['Description']}*")
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.info(f"No noble allies found for House {skin_type}.")
                    
                    if analysis['bad']:
                        st.markdown('<div class="card card-warning">', unsafe_allow_html=True)
                        st.markdown("#### 🗡️ Treacherous Foes (Harmful)")
                        for row in analysis['bad']:
                            st.markdown(f"- **{row['Ingredient']}**: Known to betray {skin_type} skin.")
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                col_c, col_i = st.columns(2)
                with col_c:
                    if analysis['comedogenic']:
                        st.markdown('<div class="card card-warning">', unsafe_allow_html=True)
                        st.markdown("#### 🕳️ The Abyss (Pore-Clogging)")
                        for row in analysis['comedogenic']:
                            st.markdown(f"- **{row['Ingredient']}** (Danger Level: {row['Comedogenic Rating']}/5)")
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.success("No dark abysses found!")
                        
                with col_i:
                    if analysis['irritants']:
                        st.markdown('<div class="card card-warning">', unsafe_allow_html=True)
                        st.markdown("#### 🔥 Wildfire (Irritants)")
                        for row in analysis['irritants']:
                            st.markdown(f"- **{row['Ingredient']}** (Burn Level: {row['Irritancy']}/5)")
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.success("No wildfire detected!")
                        
                st.markdown("---")
                st.markdown("### The Alchemist's Breakdown")
                
                if 'Function' in matched_df.columns:
                    func_counts = matched_df['Function'].value_counts().reset_index()
                    func_counts.columns = ['Function', 'Count']
                    fig = px.pie(func_counts, values='Count', names='Function', 
                                 hole=0.4,
                                 color_discrete_sequence=['#8b0000', '#d4af37', '#666666', '#333333', '#e5e5e5'])
                    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#d4af37')
                    st.plotly_chart(fig, use_container_width=True)
                    
                with st.expander("Read the Full Scroll (Matched Data)"):
                    st.dataframe(matched_df[['Ingredient', 'Function', 'Comedogenic Rating', 'Irritancy']], use_container_width=True)
                    
                if unmatched:
                    with st.expander("View Shadow Elements (Unknowns)"):
                        st.write(", ".join(unmatched))
                        
    elif analyze_btn and not ingredients_input:
        st.warning("The parchment is blank. Please write or upload the runes.")
    else:
        st.info("👈 Present your potion to the Maester to begin.")
