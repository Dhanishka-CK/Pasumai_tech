from gtts import gTTS
import os

# Pre-written Tamil responses for common crops (100% offline, no API needed!)
TAMIL_ADVICE = {
    'நெல்': "வணக்கம் விவசாயியே! நெல் பயிர் சிறந்த தேர்வு. மண்ணில் 2-5 செமீ நீர் மட்டத்தை பராமரிக்கவும். நல்ல மகசூல் கிடைக்கும்!",
    'தக்காளி': "வணக்கம்! தக்காளி சிறந்த வணிகப் பயிர். துளி பாசனம் மூலம் தினமும் நீர் கொடுக்கவும். பழத் துளைப்பானை கவனிக்கவும்!",
    'கத்தரிக்காய்': "வணக்கம்! கத்தரிக்காய் லாபகரமான பயிர். 4-5 நாட்களுக்கு ஒருமுறை நீர் பாய்ச்சவும். நிழல் வலை பயன்படுத்தவும்!",
    'Chili': "வணக்கம்! மிளகாய் சிறந்த தேர்வு. 7-10 நாட்களுக்கு ஒருமுறை நீர் போதும். அஃபிட்ஸ் கட்டுப்பாடு முக்கியம்!",
    'மக்காச்சோளம்': "வணக்கம்! மக்காச்சோளம் நல்ல லாபம் தரும். பூக்கும் சமயத்தில் போதிய நீர் அவசியம். Fall Armyworm கவனிக்கவும்!",
    'நிலக்கடலை': "வணக்கம்! நிலக்கடலை மண் வளத்தை மேம்படுத்தும். பூக்கும் சமயத்தில் ஜிப்சம் இடவும். இலை நோய்களை கவனிக்கவும்!",
    'வாழை': "வணக்கம்! வாழை உயர் லாபப் பயிர். தினமும் துளி பாசனம் அவசியம். அழுகல் நோய் வராமல் பார்க்கவும்!",
    'மஞ்சள்': "வணக்கம்! மஞ்சள் மதிப்புமிக்க பயிர். மண் ஈரப்பதமாக இருக்க வேண்டும். இலை கருகல் நோயை கவனிக்கவும்!",
}

def get_tamil_ai_advice(crop_name, profit, demand, region):
    # Get advice from pre-written database
    tamil_text = TAMIL_ADVICE.get(crop_name, f"வணக்கம்! {crop_name} நல்ல பயிர்.3-4 நாட்களுக்கு ஒருமுறை நீர் பாய்ச்சவும்.பூக்கும் சமயத்தில் போதிய நீர் அவசியம். அழுகல் நோய் வராமல் பார்க்கவும்!இலை கருகல் நோயை கவனிக்கவும்!")
    
    # Convert to speech
    try:
        tts = gTTS(text=tamil_text, lang='ta')
        os.makedirs("temp_audio", exist_ok=True)
        audio_path = f"temp_audio/advice_{crop_name}.mp3"
        tts.save(audio_path)
        return tamil_text, audio_path
    except Exception as e:
        return f"Audio பிழை: {str(e)}", None
    # ... keep your existing get_tamil_ai_advice function ...

# 🆕 NEW: Login Page Guidance Function
def get_login_guidance_tamil():
    """Provides Tamil voice guidance for first-time users on login page"""
    
    guidance_text = """
    வணக்கம் விவசாயியே! நான் TN Agri Smart உதவியாளர். 
    இந்த பயன்பாட்டை பயன்படுத்த: 
    1. உங்கள் ஆதார் எண் அல்லது போன் நம்பரை உள்ளிடவும். 
    2. தமிழ் அல்லது English மொழியை தேர்வு செய்யவும். 
    3. Login பொத்தானை கிளிக் செய்யவும். 
    அடுத்த பக்கத்தில் உங்கள் பண்ணை விவரங்களை உள்ளிடலாம். 
    ஏதேனும் கேள்வி இருந்தால் கேளுங்கள்!
    """
    
    try:
        # Convert to speech
        tts = gTTS(text=guidance_text, lang='ta')
        os.makedirs("temp_audio", exist_ok=True)
        audio_path = "temp_audio/login_guidance.mp3"
        tts.save(audio_path)
        return guidance_text, audio_path
    except Exception as e:
        return f"பிழை: {str(e)}", None