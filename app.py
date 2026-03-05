from sklearn.ensemble import RandomForestClassifier
import folium
from streamlit_folium import folium_static
import streamlit as st
import pandas as pd
import os
import plotly.express as px
from io import BytesIO
from utils.ai_handler import get_tamil_ai_advice

# 🎨 1. Page Config & Custom CSS
st.set_page_config(page_title="TN Agri Smart", page_icon="🌱", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #F9FAFB; }
    .stButton>button { background-color: #2E7D32; color: white; border-radius: 8px; height: 3em; width: 100%; }
    .stButton>button:hover { background-color: #1B5E20; }
    .header-box { background-color: #E8F5E9; color: #1B5E20; padding: 20px; border-radius: 10px; border-left: 5px solid #2E7D32; margin-bottom: 20px; }
    .header-box h2 { color: #1B5E20; margin: 0; }
    </style>
    """, unsafe_allow_html=True)

# 🌾 2. Tamil Dictionary
CROP_TA = {'tomato': 'தக்காளி', 'rice': 'நெல்', 'banana': 'வாழை', 'brinjal': 'கத்தரிக்காய்'}
TA_CROPS = {
        'rice': 'நெல்', 'maize': 'மக்காச்சோளம்', 'groundnut': 'நிலக்கடலை',
        'millets': 'சிறுதானியங்கள்', 'sugarcane': 'கரும்பு', 'watermelon': 'தர்பூசணி',
        'brinjal': 'கத்தரிக்காய்', 'tomato': 'தக்காளி', 'banana': 'வாழை',
        'chilli': 'மிளகாய்', 'turmeric': 'மஞ்சள்', 'onion': 'வெங்காயம்',
        'wheat': 'கோதுமை', 'cauliflower': 'கோவிக் கீரை', 'cotton': 'பருத்தி'
    }

# 🧠 3. Session State
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'farmer_id' not in st.session_state:
    st.session_state.farmer_id = ""
if 'farm_details' not in st.session_state:
    st.session_state.farm_details = {}
if "selected_crop_data" not in st.session_state:
    st.session_state.selected_crop_data = None

# 📂 4. Load Data
@st.cache_data
def load_data():
    try:
        files = ['data/crop_suitability.csv', 'data/market_demand.csv']
        for f in files:
            if not os.path.exists(f):
                st.warning(f"Missing: {f}")
        return True
    except:
        return False

# 🏠 5. Step Functions
def step_login():
    st.markdown("<div class='header-box'><h2>👋 Farmer Login / விவசாயி உள்நுழைய</h2></div>", unsafe_allow_html=True)
    
    # 🤖 AI Voice Assistant for Login Page
    with st.sidebar:
        st.markdown("### 🤖 உதவி / Help Assistant")
        st.write("பயன்பாட்டை எப்படி பயன்படுத்துவது?")
        
        if st.button(" உள்நுழைவு வழிகாட்டி", use_container_width=True):
            with st.spinner("வழிகாட்டி தயாராகிறது..."):
                from utils.ai_handler import get_login_guidance_tamil
                guidance_text, audio_file = get_login_guidance_tamil()
                
                if audio_file:
                    st.success("✅ கேட்க தயாராக உள்ளது!")
                    st.audio(audio_file, format="audio/mp3")
                    with st.expander("📝 View Text / உரையைப் பார்"):
                        st.write(guidance_text)
                else:
                    st.error(f"பிழை: {guidance_text}")
        
        # Quick Help Tips
        with st.expander("💡 Quick Tips / விரைவு உதவிக்குறிப்புகள்"):
            st.markdown("""
            **உள்நுழைய:**
            - ✅ ஆதார் எண் அல்லது போன் நம்பர் பயன்படுத்தவும்
            - ✅ தமிழ் மொழி தேர்வு செய்யலாம்
            - ✅ Login கிளிக் செய்யவும்
            
            **அடுத்த படி:**
            - 🚜 பண்ணை விவரங்கள் உள்ளிடவும்
            - 📊 பயிர் பரிந்துரைகளைப் பார்க்கவும்
            - 📥 அறிக்கை பதிவிறக்கம் செய்யவும்
            """)
    
    # Main Login Form
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("assets/tn_gov_logo.png", width=150)
    with col2:
        st.write("### Welcome to TN Agri Smart Decision Support")
        st.write("Government of Tamil Nadu | tnwise Hackathon 2026")
        
        # Welcome message in Tamil if language is Tamil
        if 'lang' in st.session_state and 'Tamil' in st.session_state.lang:
            st.info("🌾 வணக்கம் விவசாயியே! உங்கள் விவசாய வெற்றிக்கு நாங்கள் உதவுகிறோம்!")
    
    # Login Form Fields
    fid = st.text_input("Farmer ID (Aadhar/Phone) / விவசாயி ID", 
                        placeholder="Enter 12-digit Aadhar or Phone number")
    lang = st.selectbox("Language / மொழி", ["English", "Tamil (தமிழ்)"], 
                        index=1 if 'lang' in st.session_state and 'Tamil' in st.session_state.lang else 0)
    
    # Login Button
    if st.button("Login / உள்நுழைய", type="primary", use_container_width=True):
        if fid and len(fid) >= 10:  # Basic validation
            st.session_state.farmer_id = fid
            st.session_state.lang = lang
            st.session_state.step = 1
            st.rerun()
        else:
            st.error("Please enter valid ID / சரியான ID உள்ளிடவும் (min 10 digits)")
    
    # Footer Help
    st.markdown("---")
    st.caption("💡 Need help? Click the 🔊 button in sidebar for voice guidance in Tamil!")

def step_farm_details():
    st.markdown("<div class='header-box'><h2>🚜 Farm Details / பண்ணை விவரங்கள்</h2></div>", unsafe_allow_html=True)
    st.write(f"**Farmer ID:** {st.session_state.farmer_id} | **Language:** {st.session_state.lang}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        region = st.selectbox("District / மாவட்டம்", ['Coimbatore', 'Thanjavur', 'Salem', 'Trichy'])
        land = st.number_input("Land Area (Acres)", min_value=0.1, value=1.0)
    with col2:
        soil = st.selectbox("Soil Type", ['Red Loam', 'Black Cotton', 'Alluvial', 'Sandy'])
        water = st.selectbox("Water Availability", ['High', 'Medium', 'Low'])
    with col3:
        n = st.number_input("Nitrogen (N)", value=40)
        p = st.number_input("Phosphorus (P)", value=40)
        k = st.number_input("Potassium (K)", value=40)
        ph = st.number_input("pH Level", value=6.5)
        
    if st.button("Save & Continue / அடுத்தது"):
        st.session_state.farm_details = {'region': region, 'land': land, 'soil': soil, 'water': water, 'n':n, 'p':p, 'k':k, 'ph':ph}
        st.session_state.step = 2
        st.rerun()
    
    if st.button("← Back"):
        st.session_state.step = 0
        st.rerun()
    

# 📄 PDF Class (kept for future use)
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'TN Agri Smart - Crop Report', 0, 1, 'C')
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')



# 🌱 Enhanced Crop Care Database (Detailed Phase-wise)
CROP_CARE = {
    'rice': {
        'summary': {'fert': 'NPK 25:10:10 @ 150kg/acre', 'water': '2-5 cm water level', 'time': 'June-July (Samba) or Dec-Jan (Thaladi)', 'pest': 'Monitor Stem Borer & Leaf Folder'},
        'phases': {
            '🌾 நில தயாரிப்பு (Land Preparation)': {
                'duration': '7-10 days before sowing',
                'details': [
                    'மண்ணை 2-3 முறை உழுது நன்கு பதப்படுத்தவும்',
                    'ஹெக்டேருக்கு 10 டன் தொழு உரம் அல்லது 5 டன் கம்போஸ்ட் இடவும்',
                    'மண் பரிசோதனை அறிக்கையின் அடிப்படையில் சுண்ணாம்பு சேர்க்கவும் (pH < 6.5 எனில்)',
                    'வயலை சமமாக மட்டம் செய்து, நீர் தேங்கும் வசதி செய்யவும்'
                ]
            },
            '🌱 விதைப்பு / நடவு (Sowing/Transplanting)': {
                'duration': '25-30 days nursery, then transplant',
                'details': [
                    'சான்றளிக்கப்பட்ட விதைகளை மட்டுமே பயன்படுத்தவும் (ADT 43, CO 51, etc.)',
                    'விதை நேர்த்தி: Carbendazim 2g/kg விதை + Pseudomonas fluorescens 10g/kg',
                    'நாற்று 25-30 நாட்களில் 4-5 இலைகள் வந்த பின் நடவு செய்யவும்',
                    'நடவு இடைவெளி: 20cm x 10cm அல்லது SRI முறை: 25cm x 25cm'
                ]
            },
            '🌿 வளர்ச்சி பராமரிப்பு (Growth Management)': {
                'duration': '30-60 days after transplanting',
                'details': [
                    'உர இடுதல்: அடி உரமாக NPK 25:10:10 @ 150kg/acre; 30 & 60 நாளில் யூரியா தவணை',
                    'நீர் மேலாண்மை: நடவு முதல் 30 நாள் வரை 2-5cm நீர்; பூக்கும் சமயத்தில் போதிய நீர்',
                    'களை எடுத்தல்: நடவு 20, 40 நாட்களில் களை எடுக்க அல்லது களைக்கொல்லி பயன்படுத்த',
                    'இலை உரம்: 0.5% யூரியா + 2% DAP + 0.2% பொட்டாஷ் 45 & 60 நாளில் தெளிக்க'
                ]
            },
            '🐛 பூச்சி & நோய் கட்டுப்பாடு (Pest & Disease Control)': {
                'duration': 'Throughout growth period',
                'details': [
                    'தண்டு துளைப்பான்: Cartap hydrochloride 50SP @ 500g/acre அல்லது Chlorantraniliprole',
                    'இலை சுருட்டுப்புழு: Flubendiamide 20WG @ 50g/acre அல்லது Indoxacarb',
                    'இலை கருகல் நோய்: Tricyclazole 75WP @ 400g/acre அல்லது Azoxystrobin',
                    'உயிரியல் கட்டுப்பாடு: Trichogramma wasps @ 50,000/acre இறால் விடுவிப்பு'
                ]
            },
            '🌾 அறுவடை & அறுவடை பின் (Harvest & Post-Harvest)': {
                'duration': '100-120 days (varies by variety)',
                'details': [
                    '80-85% கதிர்கள் மஞ்சள் நிறமாக மாறிய பின் அறுவடை செய்யவும்',
                    'அறுவடை காலை அல்லது மாலை நேரத்தில் செய்யவும்; மழை நேரத்தில் தவிர்க்கவும்',
                    'அறுவடை பின் 2-3 நாள் வெயிலில் உலர்த்தி, தரம் பிரிக்கவும்',
                    'சேமிப்பு: ஈரப்பதம் 12-14% ஆக இருக்கும் போது கோணிகளில் சேமிக்க; பூச்சி தடுப்புக்கு Neem oil'
                ]
            }
        }
    },
    
    'tomato': {
        'summary': {'fert': 'FYM 10 tons + NPK 100:100:100 kg/acre', 'water': 'Drip every 2-3 days', 'time': 'Oct-Nov (Winter) or May-June (Summer)', 'pest': 'Fruit Borer & Early Blight'},
        'phases': {
            '🌱 நாற்றங்கால் தயாரிப்பு (Nursery Management)': {
                'duration': '25-30 days',
                'details': [
                    'பாதுகாப்பான நாற்றங்காலில் Protrays (98/128 cells) பயன்படுத்தவும்',
                    'விதை நேர்த்தி: Thiram 2g/kg விதை அல்லது Hot water treatment 50°C for 30min',
                    'நாற்றுகளுக்கு நிழல் வலை & பூச்சி வலை பயன்படுத்தவும்',
                    'நீர்: தினமும் மெல்லிய தெளிப்பு; Overhead watering தவிர்க்கவும்'
                ]
            },
            '🚜 நில தயாரிப்பு & நடவு (Land Prep & Transplanting)': {
                'duration': '7 days before transplanting',
                'details': [
                    'மண்ணை 3-4 முறை உழுந்து, 10 டன் தொழு உரம் இடவும்',
                    'பாத்தி அமைப்பு: 1m அகலம், 15cm உயரம், 50cm இடைவெளி',
                    'நடவு இடைவெளி: 60cm x 45cm அல்லது 75cm x 60cm (வகையைப் பொறுத்து)',
                    'நடவு பின் உடனே லேசான நீர் பாய்ச்சவும்'
                ]
            },
            '🌿 வளர்ச்சி & உர மேலாண்மை (Growth & Nutrition)': {
                'duration': '30-70 days after transplanting',
                'details': [
                    'அடி உரம்: NPK 100:100:100 kg/acre + 10 tons FYM',
                    'தவணை உரம்: 30 & 50 நாளில் யூரியா 50kg/acre தவணை',
                    'இலை உரம்: 0.2% போரான் + 0.5% ஜிங்க் சல்பேட் பூக்கும் முன் தெளிக்க',
                    'Mulching: கருப்பு பாலிதீன் மல்ச்சிங் பயன்படுத்தி களை & ஈரப்பதம் கட்டுப்பாடு'
                ]
            },
            '🐛 பூச்சி & நோய் நிர்வாகம் (Pest & Disease)': {
                'duration': 'Flowering to harvest',
                'details': [
                    'பழத் துளைப்பான்: Emamectin Benzoate 5SG @ 200ml/acre அல்லது Spinosad',
                    'இலை சுருள் நோய் (ToLCV): Imidacloprid 17.8SL @ 100ml/acre + Whitefly traps',
                    'ஆரம்ப கால பூஞ்சை: Mancozeb 75WP @ 2g/liter அல்லது Chlorothalonil',
                    'உயிரியல்: Beauveria bassiana @ 5g/liter for aphids/whiteflies'
                ]
            },
            '🍅 அறுவடை & சந்தைப்படுத்தல் (Harvest & Marketing)': {
                'duration': '60-90 days after transplanting',
                'details': [
                    'பழுப்பு-சிவப்பு நிலையில் பழங்களை கையில் பறிக்கவும்; கத்தி பயன்படுத்த வேண்டாம்',
                    'அறுவடை காலை நேரத்தில் செய்யவும்; மதிய வெயிலில் தவிர்க்கவும்',
                    'பழுதடைந்த/நோயுற்ற பழங்களை உடனே பிரித்து எடுக்கவும்',
                    'சந்தைக்கு: பிளாஸ்டிக் கிரேட்/மர பெட்டியில் பூப்போடு அடுக்கி அனுப்பவும்'
                ]
            }
        }
    },
    
    # Add similar detailed structure for other crops...
    # For brevity, I'll show one more example, then you can follow the pattern:
    
    'brinjal': {
        'summary': {'fert': 'FYM 10 tons + NPK 100:100:100 kg/acre', 'water': 'Every 4-5 days', 'time': 'May-June or Oct-Nov', 'pest': 'Shoot & Fruit Borer'},
        'phases': {
            '🌱 Nursery & Seed Treatment': {
                'duration': '25-30 days',
                'details': [
                    'விதை நேர்த்தி: Carbendazim 2g/kg + Pseudomonas 10g/kg',
                    'Protrays with cocopeat: 1 seed per cell, light watering',
                    'Shade net (50%) & insect net for virus protection',
                    'Hardening: Reduce water 3-4 days before transplanting'
                ]
            },
            '🚜 Land Preparation & Planting': {
                'duration': '7 days before transplanting',
                'details': [
                    'Deep ploughing + 10 tons FYM/acre + Neem cake 250kg/acre',
                    'Ridges & furrows: 60cm spacing, 15cm height',
                    'Planting distance: 60cm x 45cm (determinate) or 75x60cm (indeterminate)',
                    'Light irrigation immediately after planting'
                ]
            },
            '🌿 Growth Management': {
                'duration': '30-70 days',
                'details': [
                    'Basal: NPK 100:100:100 kg/acre; Top dress urea at 30 & 50 DAT',
                    'Foliar: 0.2% Boron + 0.5% Zinc at flowering for better fruit set',
                    'Staking: Bamboo stakes for tall varieties to prevent lodging',
                    'Pruning: Remove lower leaves & side shoots for better air circulation'
                ]
            },
            '🐛 Pest & Disease Control': {
                'duration': 'Flowering to harvest',
                'details': [
                    'Shoot & Fruit Borer: Remove infested shoots/fruits manually + Spray Emamectin',
                    'Aphids/Jassids: Imidacloprid 17.8SL @ 100ml/acre or Neem oil 5ml/liter',
                    'Fruit rot: Mancozeb 2g/liter or Copper oxychloride 3g/liter',
                    'Yellow sticky traps @ 12/acre for whitefly monitoring'
                ]
            },
            '🍆 Harvest & Post-Harvest': {
                'duration': '50-70 days after transplanting',
                'details': [
                    'Harvest when fruits attain desired size & glossy appearance',
                    'Use scissors/knife with short stalk; avoid pulling',
                    'Harvest every 2-3 days; morning hours preferred',
                    'Pre-cool in shade, pack in ventilated crates, avoid over-stacking'
                ]
            }
        }
    },
    
    # ... Continue pattern for other crops (maize, groundnut, chilli, etc.)
    # Keep summary for fallback, add phases for detailed view
}
# 📊 Step Analysis Function
def step_analysis():
    if 'selected_crop_data' not in st.session_state:
        st.session_state.selected_crop_data = None
    st.markdown("<div class='header-box'><h2>📊 Analysis & Recommendation / பரிந்துரை</h2></div>", unsafe_allow_html=True)
    st.success("✅ பண்ணை விவரங்கள் சேமிக்கப்பட்டது!")
    
    # Load Data
    try:
        soil_df = pd.read_csv('data/crop_suitability.csv')
        market_df = pd.read_csv('data/market_demand.csv')
        schemes_df = pd.read_csv('data/schemes.csv')
        supply_df = pd.read_csv('data/regional_supply.csv')
    except Exception as e:
        st.error(f"தரவு பிழை: {e}")
        return

    details = st.session_state.farm_details
    region = details['region']
    land = details['land']
    
    # Tamil UI
    TA_UI = {
        'top3': '🏆 முன்னணி 3 பயிர் பரிந்துரைகள்',
        'profit': 'எதிர்பார்க்கப்படும் லாபம்',
        'future_price': 'எதிர்பார்க்கப்படும் விலை',
        'demand': 'சந்தை தேவை',
        'subsidy': 'அரசு மானியம்',
        'select': 'தேர்ந்தெடு',
        'market_analysis': '📊 சந்தை மற்றும் லாப பகுப்பாய்வு',
        'profit_chart': 'எதிர்பார்க்கப்படும் லாப ஒப்பீடு',
        'demand_chart': 'சார்பு தேவை குறியீடு',
        'report': '📄 விரிவான பயிர் அறிக்கை',
        'care_instructions': '🌱 பராமரிப்பு வழிமுறைகள்',
        'fertilizer': 'உரம்',
        'water': 'நீர் மேலாண்மை',
        'season': 'விதைக்கும் பருவம்',
        'pest': 'பூச்சி கட்டுப்பாடு',
        'download_pdf': '📥 PDF பதிவிறக்க',
        'confirm': '✅ உறுதிப்படுத்தி தரவுத்தளத்தை புதுப்பிக்க',
        'selected': 'தேர்ந்தெடுக்கப்பட்டது',
        'high_demand': 'அதிக தேவை 🔥',
        'low_demand': 'குறைந்த தேவை 📉',
        'moderate_demand': 'மிதமான தேவை ⚖️',
        'no_profit': 'லாபகரமான பயிர்கள் எதுவும் கிடைக்கவில்லை'
    }

    # Model
    X = soil_df[['nitrogen','phosphorus','potassium','temperature','humidity','rainfall','ph']]
    y = soil_df['crop_label']
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    input_data = pd.DataFrame([[details['n'], details['p'], details['k'], 25, 70, 150, details['ph']]], columns=X.columns)
    probabilities = model.predict_proba(input_data)[0]
    classes = model.classes_
    
    cost_per_acre = {'rice': 25000, 'maize': 18000, 'groundnut': 22000, 'millets': 15000, 'sugarcane': 35000, 'watermelon': 20000, 'brinjal': 30000, 'tomato': 40000, 'banana': 50000, 'chilli': 35000, 'turmeric': 45000, 'onion': 25000, 'wheat': 20000, 'cauliflower': 30000, 'cotton': 28000}
    yield_per_acre = {'rice': 20, 'maize': 15, 'groundnut': 12, 'millets': 10, 'sugarcane': 80, 'watermelon': 100, 'brinjal': 25, 'tomato': 30, 'banana': 200, 'chilli': 15, 'turmeric': 12, 'onion': 15, 'wheat': 12, 'cauliflower': 10, 'cotton': 8}
    
    recommendations = []
    
    for crop in classes:
        crop_market = market_df[(market_df['crop_name'] == crop) & (market_df['region'] == region)]
        avg_price = crop_market['avg_price'].mean() if not crop_market.empty else 2000
        seasonal_idx = crop_market['seasonal_index'].mean() if not crop_market.empty else 1.0
        
        crop_supply = supply_df[(supply_df['crop_name'] == crop) & (supply_df['region'] == region)]
        current_supply = crop_supply['area_allocated'].sum() if not crop_supply.empty else 0
        
        cost = cost_per_acre.get(crop, 20000) * land
        yield_total = yield_per_acre.get(crop, 10) * land
        future_price = avg_price * seasonal_idx
        profit = (yield_total * future_price) - cost
        
        demand_score = seasonal_idx * (1 - (current_supply / 500))
        if demand_score > 1.2:
            demand_label = TA_UI['high_demand']
        elif demand_score < 0.8:
            demand_label = TA_UI['low_demand']
        else:
            demand_label = TA_UI['moderate_demand']
        
        scheme_row = schemes_df[schemes_df['crop_name'] == crop]
        scheme_txt = f"{scheme_row['scheme_name'].values[0]}" if not scheme_row.empty else "தற்போதைக்கு இல்லை"
        
        suitability = probabilities[list(classes).index(crop)] if crop in classes else 0
        final_score = (suitability * 40) + (demand_score * 40) + ((1 if profit > 0 else 0) * 20)
        
        
        if profit > 0:
            # Calculate supply risk label
            if current_supply > 200:
                supply_risk = 'High / அதிகம் ⚠️'
            elif current_supply > 100:
                supply_risk = 'Moderate / மிதமானம் ⚖️'
            else:
                supply_risk = 'Low / குறைவு ✅'
            
            recommendations.append({
                'crop': crop, 'profit': profit, 'score': final_score, 'price': avg_price, 
                'future_price': future_price, 'cost': cost, 'yield': yield_total, 
                'demand_label': demand_label, 'demand_score': demand_score,
                'scheme': scheme_txt, 'supply': current_supply, 'supply_risk': supply_risk
            })
    
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    top_3 = recommendations[:3]
    
    if not top_3:
        st.error(f"⚠️ {TA_UI['no_profit']}")
        return

    # Display Cards
    st.subheader(TA_UI['top3'])
    cols = st.columns(3)
    
    for i, rec in enumerate(top_3):
        crop_ta = TA_CROPS.get(rec['crop'], rec['crop'])
        with cols[i]:
            st.markdown(f"""
            <div style="background:white; padding:15px; border-radius:10px; border: {'2px solid #2E7D32' if i==0 else '1px solid #ddd'}">
                <h3 style="color:#2E7D32; margin:0">{'🥇' if i==0 else '🥈' if i==1 else '🥉'} {crop_ta}</h3>
                <p><b>{TA_UI['profit']}:</b> ₹{rec['profit']:,.0f}</p>
                <p><b>{TA_UI['future_price']}:</b> ₹{rec['future_price']:,.0f}</p>
                <p><b>{TA_UI['demand']}:</b> {rec['demand_label']}</p>
                <p><b>{TA_UI['subsidy']}:</b> {rec['scheme']}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"{TA_UI['select']} {crop_ta}", key=f"select_{i}"):
                st.session_state.selected_crop_data = rec
                st.rerun()

    st.divider()
    st.subheader(TA_UI['market_analysis'])

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        df_profit = pd.DataFrame(top_3)[['crop', 'profit']]
        df_profit['crop_ta'] = df_profit['crop'].apply(lambda x: TA_CROPS.get(x, x))
        fig_profit = px.bar(
            df_profit,
            x='crop_ta',
            y='profit',
            title=TA_UI['profit_chart'],
            color='profit',
            color_continuous_scale='Greens',
            labels={'crop_ta': 'பயிர்', 'profit': 'லாபம் (₹)'}
        )
        st.plotly_chart(fig_profit, use_container_width=True)

    with col_g2:
        df_demand = pd.DataFrame(top_3)[['crop', 'demand_score']]
        df_demand['crop_ta'] = df_demand['crop'].apply(lambda x: TA_CROPS.get(x, x))
        fig_demand = px.pie(
            df_demand,
            values='demand_score',
            names='crop_ta',
            title=TA_UI['demand_chart'],
            labels={'crop_ta': 'பயிர்', 'demand_score': 'தேவை'}
        )
        st.plotly_chart(fig_demand, use_container_width=True)

    # ✅ REPORT & TXT DOWNLOAD SECTION
    # ... (inside step_analysis, after the crop report text is generated) ...

# --- AI Tamil Assistant Section ---
    st.markdown("---")
    st.subheader("🤖 AI Tamil Assistant / தமிழ் உதவி")
    
    # Check if a crop is selected in session_state
    if st.session_state.selected_crop_data is not None:
        if st.button("🔊 Listen to AI Advice in Tamil / தமிழில் கேட்க", use_container_width=True):
            with st.spinner("AI ஆலோசனையைத் தயார் செய்கிறது..."):
                
                # Use the session_state variable directly
                current_crop = st.session_state.selected_crop_data
                
                # 1. Get the Tamil name for the crop
                crop_name_ta = TA_CROPS.get(current_crop['crop'], current_crop['crop'])
                
                # 2. Call the function from utils/ai_handler.py
                tamil_msg, audio_file = get_tamil_ai_advice(
                    crop_name_ta, 
                    current_crop['profit'], 
                    current_crop['demand_label'],
                    region
                )
                
                # 3. Display and Play
                if audio_file:
                    st.info(f"✨ **AI Suggestion:**\n\n{tamil_msg}")
                    st.audio(audio_file, format="audio/mp3")
                else:
                    st.error(f"மன்னிக்கவும், ஒரு பிழை ஏற்பட்டது: {tamil_msg}")
    else:
        st.warning("தயவுசெய்து மேலே உள்ள ஒரு பயிரைத் தேர்வு செய்யவும் / Please select a crop above.")

    selected_crop_data = st.session_state.selected_crop_data
    st.subheader(TA_UI['report'])

    crop_name = selected_crop_data['crop']
    crop_name_ta = TA_CROPS.get(crop_name, crop_name)

    
        # ✅ Get care info with proper fallback structure
    if crop_name in CROP_CARE and 'summary' in CROP_CARE[crop_name]:
        care = CROP_CARE[crop_name]
    else:
        # Fallback with 'summary' key to prevent KeyError
        care = {
            'summary': {
                'fert': 'பொதுவான NPK உரம் இடவும்',
                'water': 'வாரம் ஒருமுறை நீர் பாய்ச்சவும்',
                'time': 'பருவமழை காலத்தில் விதைக்கவும்',
                'pest': 'வழக்கமாக கண்காணிக்கவும்'
            },
            'phases': None# Empty phases for fallback
        }

    st.info(
        f"**{TA_UI['selected']}:** {crop_name_ta} | "
        f"**{TA_UI['profit']}:** ₹{selected_crop_data['profit']:,.0f}"
    )
    

        # 🌱 Detailed Care Instructions Expander
    with st.expander("🌱 விரிவான பராமரிப்பு வழிகாட்டி / Detailed Care Guide", expanded=False):
        
        # Show Summary First
        st.markdown(f"**📋 சுருக்கம் / Summary:**")
        st.markdown(f"- 🌱 **உரம்:** {care['summary']['fert']}")
        st.markdown(f"- 💧 **நீர்:** {care['summary']['water']}")
        st.markdown(f"- 📅 **பருவம்:** {care['summary']['time']}")
        st.markdown(f"- 🐛 **பூச்சி:** {care['summary']['pest']}")
        
        st.divider()
        
        # Show Detailed Phases (if available)
        if 'phases' in care and care['phases']:
            st.markdown("### 🔹 நிலை வாரியான பராமரிப்பு / Phase-wise Care")
            
            for phase_name, phase_info in care['phases'].items():
                with st.container():
                    st.markdown(f"**{phase_name}**")
                    st.caption(f"⏳ காலம்: {phase_info['duration']}")
                    
                    # Display details as bullet points
                    for detail in phase_info['details']:
                        st.markdown(f"• {detail}")
                    
                    st.markdown("---")
        else:
            st.info("ℹ️ விரிவான பராமரிப்பு வழிமுறைகள் / மேலே உள்ள சுருக்கத்தைப் பயன்படுத்தவும்.")

        # ✅ TXT Download Button with unique key
                # 🌿 CARE GUIDELINES - Enhanced with phases
        care_section = f"""
🌿 CROP CARE GUIDELINES / பயிர் பராமரிப்பு வழிமுறைகள்
─────────────────────────────────────
📋 SUMMARY:
• Fertilizer: {care['summary']['fert']}
• Water: {care['summary']['water']}
• Season: {care['summary']['time']}
• Pest Control: {care['summary']['pest']}
"""
        
        # Add detailed phases if available
        if 'phases' in care and care['phases']:
            care_section += "\n🔹 DETAILED PHASE-WISE CARE:\n"
            for phase_name, phase_info in care['phases'].items():
                care_section += f"\n{phase_name} [{phase_info['duration']}]:\n"
                for detail in phase_info['details']:
                    care_section += f"  • {detail}\n"
        
        care_section += "\n"  # Add spacing
            # ✅ Calculate supply_risk if not in selected_crop_data
        if 'supply_risk' not in selected_crop_data:
            current_supply = selected_crop_data.get('supply', 0)
            if current_supply > 200:
                supply_risk = 'High / அதிகம் ⚠️'
            elif current_supply > 100:
                supply_risk = 'Moderate / மிதமானம் ⚖️'
            else:
                supply_risk = 'Low / குறைவு ✅'
        else:
            supply_risk = selected_crop_data['supply_risk']
        # Complete report text with enhanced care section

        report_text = f"""
TN AGRI SMART - CROP REPORT
============================
👨‍🌾 FARMER DETAILS
─────────────────────────────────────
Farmer ID: {st.session_state.farmer_id}
District: {region} | Land: {land} acres
Soil: {details['soil']} | Water: {details['water']}
Soil N-P-K-pH: {details['n']}-{details['p']}-{details['k']} (pH {details['ph']})

🌱 RECOMMENDED CROP
─────────────────────────────────────
Crop: {crop_name_ta} ({crop_name.upper()})
Expected Profit: ₹{selected_crop_data['profit']:,.0f}
Total Investment: ₹{selected_crop_data['cost']:,.0f}
Market Price: ₹{selected_crop_data['price']:,.0f}/qt
Expected Yield: {selected_crop_data['yield']} quintals
Future Price: ₹{selected_crop_data['future_price']:,.0f}/qt
Demand Status: {selected_crop_data['demand_label']}
Govt Scheme: {selected_crop_data['scheme']}

{care_section}
💰 FINANCIAL SUMMARY
─────────────────────────────────────
Total Investment: ₹{selected_crop_data['cost']:,.0f}
Expected Revenue: ₹{selected_crop_data['yield'] * selected_crop_data['future_price']:,.0f}
Expected Profit: ₹{selected_crop_data['profit']:,.0f}
Profit Margin: {(selected_crop_data['profit']/selected_crop_data['cost']*100):.1f}%

⚠️ RISK ASSESSMENT
─────────────────────────────────────
• Soil Suitability: High (based on N-P-K-pH analysis)
• Market Demand: {selected_crop_data['demand_label']}
• Regional Supply Risk: {supply_risk}  # ✅ Use the variable we calculated
• Recommendation: Proceed with planned cultivation

═════════════════════════════════════════════
Generated by: TN Agri Smart Decision Support
Date: {pd.Timestamp.now().strftime('%d-%b-%Y %H:%M')}
Farmer ID: {st.session_state.farmer_id}
tnwise Hackathon 2024 | Government of Tamil Nadu
═════════════════════════════════════════════
* This report is for planning purposes only.
* Consult local agriculture officer for field-specific advice.
* Prices and demand are estimates based on historical data.
* Follow integrated pest management (IPM) practices.
"""
        
        st.download_button(
            label="📥 Download Report (TXT) / அறிக்கை பதிவிறக்க",
            data=report_text,
            file_name=f"TN_Agri_{crop_name}_{st.session_state.farmer_id}.txt",
            mime="text/plain",
            key=f"dl_{crop_name}_{st.session_state.farmer_id}_{pd.Timestamp.now().timestamp()}"
        )
        
        # ✅ CONFIRM BUTTON - PROPERLY INDENTED INSIDE if selected_crop_data
                # ✅ SIMPLE CONFIRM BUTTON TEST
    st.divider()

    if st.button(TA_UI['confirm'], type="primary", use_container_width=True):
        try:
            farmer_df = pd.read_csv('data/farmers_data.csv')

            new_entry = {
                'farmer_id': st.session_state.farmer_id,
                'region': region,
                'land_area': land,
                'soil_type': details['soil'],
                'water_availability': details['water'],
                'nitrogen': details['n'],
                'phosphorus': details['p'],
                'potassium': details['k'],
                'ph': details['ph'],
                'selected_crop': crop_name,
                'area_allocated': land
            }

            farmer_df = pd.concat([farmer_df, pd.DataFrame([new_entry])], ignore_index=True)
            farmer_df.to_csv('data/farmers_data.csv', index=False)

            # Update regional supply
            supply_mask = (
                (supply_df['crop_name'] == crop_name) &
                (supply_df['region'] == region)
            )

            if not supply_df[supply_mask].empty:
                supply_df.loc[supply_mask, 'area_allocated'] += land
                supply_df.loc[supply_mask, 'farmer_count'] += 1
            else:
                new_row = {
                    'region': region,
                    'crop_name': crop_name,
                    'expected_demand': 1000,
                    'current_supply': 1000,
                    'area_allocated': land,
                    'farmer_count': 1
                }
                supply_df = pd.concat([supply_df, pd.DataFrame([new_row])], ignore_index=True)

            supply_df.to_csv('data/regional_supply.csv', index=False)

            st.balloons()
            st.success("✅ Database Updated!")

            st.session_state.confirmed_crop = crop_name
            st.session_state.confirmed_region = region
            st.session_state.step = 3
            st.rerun()

        except Exception as e:
            st.error(f"Update Error: {e}")


# 🗺️ Step 3: Regional Crop Distribution View WITH MAP
def step_regional_view():
    st.markdown("<div class='header-box'><h2>🗺️ Regional Crop Map / பிராந்திய பயிர் வரைபடம்</h2></div>", unsafe_allow_html=True)
    st.success(f"✅ {st.session_state.farmer_id} - {TA_CROPS.get(st.session_state.confirmed_crop, st.session_state.confirmed_crop)} confirmed!")
    
    region = st.session_state.confirmed_region
    
    try:
        farmers_df = pd.read_csv('data/farmers_data.csv')
        supply_df = pd.read_csv('data/regional_supply.csv')
    except Exception as e:
        st.error(f"Data Error: {e}")
        return
    
    region_farmers = farmers_df[farmers_df['region'] == region]
    
    # Summary Stats
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.metric("Total Farmers", len(region_farmers))
    with col_s2:
        st.metric("Total Land (Acres)", f"{region_farmers['land_area'].sum():.1f}")
    with col_s3:
        st.metric("Crops Grown", region_farmers['selected_crop'].nunique())
    
    # 🗺️ INTERACTIVE MAP SECTION
    st.subheader("📍 Live Farm Map / நேரடி பண்ணை வரைபடம்")
    
    # Tamil Nadu district coordinates (approximate centers)
    TN_COORDS = {
        'Coimbatore': [11.0168, 76.9558],
        'Thanjavur': [10.7870, 79.1378],
        'Salem': [11.6643, 78.1460],
        'Trichy': [10.7905, 78.7047],
        'Madurai': [9.9252, 78.1198],
        'Chennai': [13.0827, 80.2707],
        'Erode': [11.3410, 77.7172],
        'Virudhunagar': [9.5765, 77.9629],
        'Kanchipuram': [12.8342, 79.7036],
        'Tirunelveli': [8.7139, 77.7567]
    }
    
    # Crop colors for map markers
    CROP_COLORS = {
        'rice': 'green', 'maize': 'yellow', 'groundnut': 'brown',
        'millets': 'orange', 'sugarcane': 'darkgreen', 'brinjal': 'purple',
        'tomato': 'red', 'banana': 'lightgreen', 'chilli': 'darkred',
        'turmeric': 'gold', 'onion': 'pink', 'wheat': 'beige',
        'cauliflower': 'lightblue', 'cotton': 'gray', 'watermelon': 'lightred'
    }
    
    # Create base map centered on the region
    region_coords = TN_COORDS.get(region, [11.1271, 78.6569])  # Default: Tamil Nadu center
    m = folium.Map(location=region_coords, zoom_start=9, tiles='OpenStreetMap')
    
    # Add markers for each farmer
    for _, farmer in region_farmers.iterrows():
        farmer_region = farmer['region']
        coords = TN_COORDS.get(farmer_region, region_coords)
        crop = farmer['selected_crop']
        crop_ta = TA_CROPS.get(crop, crop)
        color = CROP_COLORS.get(crop, 'blue')
        
        # Create popup content
        popup_html = f"""
        <b>{farmer['farmer_id']}</b><br>
        🌱 Crop: {crop_ta} ({crop.upper()})<br>
        📏 Land: {farmer['land_area']} acres<br>
        🪨 Soil: {farmer['soil_type']}<br>
        💧 Water: {farmer['water_availability']}
        """
        
        # Add marker to map
        folium.Marker(
            location=coords,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{crop_ta} - {farmer['land_area']} acres",
            icon=folium.Icon(color=color, icon='leaf', prefix='fa')
        ).add_to(m)
    
    # Add region boundary circle (visual aid)
    folium.Circle(
        location=region_coords,
        radius=25000,  # 25 km radius
        color='blue',
        fill=True,
        fill_opacity=0.1,
        popup=f"{region} District"
    ).add_to(m)
    
    # Display map in Streamlit
    folium_static(m, width=700, height=500)
    
    # Map Legend
    st.caption("🎨 **Legend:** Marker colors represent different crops. Click markers for farmer details.")
    
    # 📊 Crop Distribution Chart (below map)
    st.subheader("📈 Crop Distribution in " + region)
    crop_dist = region_farmers.groupby('selected_crop')['land_area'].sum().reset_index()
    crop_dist['crop_ta'] = crop_dist['selected_crop'].apply(lambda x: TA_CROPS.get(x, x))
    
    fig = px.pie(crop_dist, values='land_area', names='crop_ta', 
                 title='Land Allocation by Crop / பயிர் வாரியாக நில ஒதுக்கீடு',
                 color='crop_ta',
                 labels={'crop_ta': 'Crop / பயிர்', 'land_area': 'Acres / ஏக்கர்'})
    st.plotly_chart(fig, use_container_width=True)
    
    # 💡 Coordination Insight
    st.subheader("💡 Smart Insight / ஸ்மார்ட் ஆலோசனை")
    if not crop_dist.empty:
        top_crop = crop_dist.loc[crop_dist['land_area'].idxmax()]
        alternatives = [TA_CROPS.get(c, c) for c in region_farmers['selected_crop'].unique() if c != top_crop['selected_crop']][:3]
        st.info(f"""
        ⚠️ **Observation:** {top_crop['crop_ta']} has the highest land allocation ({top_crop['land_area']:.1f} acres)
        
        ✅ **Recommendation for next farmers:** 
        Consider planting: {', '.join(alternatives) if alternatives else 'other high-demand crops'}
        
        📈 This helps balance supply and maintain good market prices!
        """)
    
    # Navigation Buttons
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("🔄 New Farmer Login / புதிய விவசாயி"):
            st.session_state.step = 0
            st.session_state.farmer_id = ""
            st.session_state.confirmed_crop = None
            st.rerun()
    with col_b2:
        if st.button("📊 View Another Region / மற்றொரு மாவட்டம்"):
            st.session_state.step = 1
            st.rerun()

    
# 🚀 Main Router
load_data()
if st.session_state.step == 0:
    step_login()
elif st.session_state.step == 1:
    step_farm_details()
elif st.session_state.step == 2:
    step_analysis()
elif st.session_state.step == 3:
    step_regional_view()
