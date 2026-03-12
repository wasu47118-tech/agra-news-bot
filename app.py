import requests
import time
from datetime import datetime
import os
import random

# Get token from environment variable
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8248979966:AAE_zqrfICVz_KsQDhC6u-nnK5BFcy5CTdQ')
CHANNEL_USERNAME = "@AgraNewsUpdate"  # Your channel name

# Telegram API
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# News in Hindi (50+ headlines)
NEWS = [
    # Crime News (🔴)
    ("🔴 Crime", "सदर बाजार में मोबाइल चोरी का आरोपी गिरफ्तार"),
    ("🔴 Crime", "ताजगंज में बाइक चोरी के तीन आरोपी गिरफ्तार"),
    ("🔴 Crime", "कमला नगर में चेन स्नेचिंग का प्रयास विफल"),
    ("🔴 Crime", "शास्त्रीपुरम में देर रात चोरी की वारदात"),
    ("🔴 Crime", "आगरा में साइबर ठगी के मामले में दो गिरफ्तार"),
    ("🔴 Crime", "रामबाग इलाके में लूट का प्रयास, पुलिस ने दबोचा"),
    ("🔴 Crime", "आगरा कैंट में वाहन चोरी गिरोह का पर्दाफाश"),
    ("🔴 Crime", "संजय प्लेस में दुकानदार से लूट की कोशिश"),
    
    # Politics News (🗳️)
    ("🗳️ Politics", "आगरा में भाजपा नेता का जनसभा को संबोधित"),
    ("🗳️ Politics", "विधायक ने क्षेत्र में विकास कार्यों का किया निरीक्षण"),
    ("🗳️ Politics", "नगर निगम चुनाव की तैयारियां तेज"),
    ("🗳️ Politics", "कांग्रेस नेता का प्रदर्शन, मांगों को लेकर धरना"),
    ("🗳️ Politics", "सपा प्रत्याशी ने किया नामांकन दाखिल"),
    ("🗳️ Politics", "मंत्री का आगरा दौरा आज, सुरक्षा व्यवस्था चाक-चौबंद"),
    ("🗳️ Politics", "मेयर ने सफाई व्यवस्था का लिया जायजा"),
    ("🗳️ Politics", "विपक्षी दलों का प्रदर्शन, ज्ञापन सौंपा"),
    
    # Traffic News (🚦)
    ("🚦 Traffic", "आगरा-दिल्ली हाईवे पर जाम के कारण राहगीर परेशान"),
    ("🚦 Traffic", "ताजमहल के पास यातायात व्यवस्था चाक-चौबंद"),
    ("🚦 Traffic", "आगरा शहर में नए ट्रैफिक सिग्नल लगे"),
    ("🚦 Traffic", "रामबाग चौराहे पर यातायात व्यवस्था बदली"),
    ("🚦 Traffic", "पार्किंग व्यवस्था में सुधार के निर्देश"),
    ("🚦 Traffic", "सिकंदरा में नए फ्लाईओवर का काम शुरू"),
    ("🚦 Traffic", "आगरा कैंट इलाके में पार्किंग की समस्या दूर"),
    
    # Local News (🏘️)
    ("🏘️ Local", "आगरा के बाजारों में त्योहारी रौनक"),
    ("🏘️ Local", "ताजगंज इलाके में सफाई व्यवस्था पर निगरानी"),
    ("🏘️ Local", "शहर के 20 वार्डों में पेयजल संकट दूर"),
    ("🏘️ Local", "आगरा कैंट बोर्ड चुनाव की तारीख घोषित"),
    ("🏘️ Local", "वार्ड सभा में जनसमस्याएं रखी गईं"),
    ("🏘️ Local", "मोहल्ला सभा का आयोजन कल"),
    ("🏘️ Local", "आगरा में नए पार्क का उद्घाटन"),
    
    # Education News (📚)
    ("📚 Education", "आगरा कॉलेज में दाखिले की अंतिम तिथि बढ़ी"),
    ("📚 Education", "डॉ. भीमराव आंबेडकर विश्वविद्यालय में परीक्षाएं शुरू"),
    ("📚 Education", "सीबीएसई बोर्ड परीक्षा का टाइम टेबल जारी"),
    ("📚 Education", "स्कूलों में बालिका शिक्षा को बढ़ावा"),
    ("📚 Education", "कोचिंग संस्थानों की नई लिस्ट जारी"),
    ("📚 Education", "आगरा यूनिवर्सिटी का रिजल्ट जारी"),
    ("📚 Education", "प्राइवेट स्कूलों की फीस वृद्धि पर रोक"),
    
    # Health News (🏥)
    ("🏥 Health", "एसएन मेडिकल कॉलेज में नई स्वास्थ्य सुविधाएं"),
    ("🏥 Health", "जिला अस्पताल में मुफ्त स्वास्थ्य शिविर कल"),
    ("🏥 Health", "आगरा में डेंगू के मामलों पर नियंत्रण"),
    ("🏥 Health", "आयुष्मान कार्ड बनवाने के लिए शिविर आयोजित"),
    ("🏥 Health", "प्राइवेट अस्पतालों में इलाज दरें तय"),
    ("🏥 Health", "आगरा में हेल्थ चेकअप कैंप आज"),
    
    # Business News (💼)
    ("💼 Business", "आगरा के जूते-चप्पल उद्योग में तेजी"),
    ("💼 Business", "संजय प्लेस बाजार में दुकानों की नीलामी कल"),
    ("💼 Business", "व्यापार मंडल ने सीएम से की मांग"),
    ("💼 Business", "आगरा में नए शॉपिंग मॉल का प्रस्ताव"),
    ("💼 Business", "जीएसटी से राहत के लिए व्यापारियों की मांग"),
    ("💼 Business", "आगरा के बाजारों में उमड़ी भीड़"),
    
    # Sports News (⚽)
    ("⚽ Sports", "आगरा क्रिकेट लीग का आयोजन कल से"),
    ("⚽ Sports", "ताज महोत्सव में खेल प्रतियोगिताएं आयोजित"),
    ("⚽ Sports", "आगरा के खिलाड़ियों का राष्ट्रीय स्तर पर चयन"),
    ("⚽ Sports", "स्टेडियम में मुफ्त कोचिंग शुरू"),
    ("⚽ Sports", "खेल दिवस पर विशेष कार्यक्रम आयोजित"),
    
    # Weather News (🌡️)
    ("🌡️ Weather", "आगरा में मौसम साफ, दिन में धूप खिली रहेगी"),
    ("🌡️ Weather", "तापमान में गिरावट, सर्दी बढ़ी"),
    ("🌡️ Weather", "बारिश के आसार, मौसम विभाग ने जारी किया अलर्ट"),
    ("🌡️ Weather", "आगरा में अधिकतम तापमान 32 डिग्री दर्ज"),
    ("🌡️ Weather", "ठंड से राहत, मौसम में आएगा बदलाव"),
    
    # Transport News (🚆)
    ("🚆 Transport", "आगरा कैंट रेलवे स्टेशन पर नई सुविधाएं"),
    ("🚆 Transport", "बस स्टैंड पर यात्रियों की सुविधा के लिए नए इंतजाम"),
    ("🚆 Transport", "आगरा एयरपोर्ट से नई फ्लाइट शुरू"),
    ("🚆 Transport", "ई-रिक्शा चालकों के लिए नियम सख्त"),
    
    # Events News (🎉)
    ("🎉 Events", "ताज महोत्सव की तैयारियां जोरों पर"),
    ("🎉 Events", "आगरा में सांस्कृतिक कार्यक्रम आज"),
    ("🎉 Events", "फूड फेस्टिवल का आयोजन कल से"),
    ("🎉 Events", "पुस्तक मेला में पाठकों की भीड़"),
]

def send_news():
    """Send news to channel"""
    # Select 8-10 random news
    num_news = random.randint(8, 10)
    selected = random.sample(NEWS, min(num_news, len(NEWS)))
    
    # Group by category
    categories = {}
    for cat, title in selected:
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(title)
    
    # Create message
    message = "🚨 **AGRA NEWS UPDATE** 🚨\n\n"
    message += f"📅 {datetime.now().strftime('%d %B %Y')}\n"
    message += f"⏰ {datetime.now().strftime('%I:%M %p')}\n"
    message += "════════════════════\n\n"
    
    for cat, titles in categories.items():
        message += f"{cat}\n"
        message += "─" * 15 + "\n"
        for title in titles:
            message += f"• {title}\n"
            message += f"  📍 Agra News Bureau | ⏱️ {datetime.now().strftime('%I:%M %p')}\n"
            message += f"  🔗 [Join Channel](https://t.me/AgraNewsUpdate)\n\n"
    
    message += "════════════════════\n"
    message += "🤖 **Agra News Bot**"
    
    # Send to Telegram
    url = f"{TELEGRAM_API_URL}/sendMessage"
    data = {
        'chat_id': CHANNEL_USERNAME,
        'text': message,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': True
    }
    
    try:
        r = requests.post(url, data=data)
        if r.status_code == 200:
            print(f"✅ News sent successfully at {datetime.now()}")
            print(f"📢 Posted {len(selected)} news items")
        else:
            print(f"❌ Error: {r.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

# Main function
if __name__ == "__main__":
    print("🤖 Agra News Bot Starting...")
    print(f"📢 Channel: {CHANNEL_USERNAME}")
    print("="*50)
    
    # Send news
    send_news()
    
    print("="*50)
    print("✅ Done! Check your channel @AgraNewsUpdate")
