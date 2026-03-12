import logging
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import json
import os
import random

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ====== CHANGE THESE TWO LINES ======
BOT_TOKEN = "8248979966:AAE_zqrfICVz_KsQDhC6u-nnK5BFcy5CTdQ"  # Put your bot token here
CHANNEL_USERNAME = "@AgraNewsUpdate"  # Put your channel username here
# ====================================

# Telegram API URLs
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Store posted news
news_cache = {}
processed_updates = set()
cache_file = "news_cache.json"
updates_file = "processed_updates.json"

def load_cache():
    global news_cache, processed_updates
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                news_cache = json.load(f)
        except:
            news_cache = {}
    
    if os.path.exists(updates_file):
        try:
            with open(updates_file, 'r', encoding='utf-8') as f:
                processed_updates = set(json.load(f))
        except:
            processed_updates = set()

def save_cache():
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(news_cache, f, ensure_ascii=False, indent=2)
        with open(updates_file, 'w', encoding='utf-8') as f:
            json.dump(list(processed_updates), f)
    except:
        pass

# Daily news generator (changes every day)
def get_daily_news():
    """Generate fresh news for each day"""
    day_of_year = datetime.now().timetuple().tm_yday
    random.seed(day_of_year)  # Same news all day, changes next day
    
    news_categories = {
        '🔴 Crime': [
            "सदर बाजार में चोरी का प्रयास विफल, एक गिरफ्तार",
            "ताजगंज में बाइक चोरी के तीन आरोपी गिरफ्तार",
            "कमला नगर में चेन स्नेचिंग की वारदात",
            "शास्त्रीपुरम में देर रात चोरी की कोशिश",
            "आगरा में साइबर ठगी के मामले में दो गिरफ्तार",
            "रामबाग इलाके में मोबाइल चोरी का आरोपी गिरफ्तार",
            "आगरा कैंट में वाहन चोरी गिरोह का पर्दाफाश"
        ],
        
        '🗳️ Politics': [
            "आगरा में भाजपा नेता का जनसभा को संबोधित",
            "विधायक ने क्षेत्र में विकास कार्यों का किया निरीक्षण",
            "नगर निगम चुनाव की तैयारियां तेज",
            "कांग्रेस नेता का प्रदर्शन, मांगों को लेकर धरना",
            "सपा प्रत्याशी ने किया नामांकन दाखिल",
            "मंत्री का आगरा दौरा आज, सुरक्षा व्यवस्था चाक-चौबंद"
        ],
        
        '🚦 Traffic': [
            "आगरा-दिल्ली हाईवे पर जाम के कारण राहगीर परेशान",
            "ताजमहल के पास यातायात व्यवस्था चाक-चौबंद",
            "आगरा शहर में नए ट्रैफिक सिग्नल लगे",
            "रामबाग चौराहे पर यातायात व्यवस्था बदली",
            "पार्किंग व्यवस्था में सुधार के निर्देश",
            "सिकंदरा में नए फ्लाईओवर का काम शुरू"
        ],
        
        '🏘️ Local': [
            "आगरा के बाजारों में दिवाली की रौनक",
            "ताजगंज इलाके में सफाई व्यवस्था पर निगरानी",
            "शहर के 20 वार्डों में पेयजल संकट दूर",
            "आगरा कैंट बोर्ड चुनाव की तारीख घोषित",
            "वार्ड सभा में जनसमस्याएं रखी गईं",
            "मोहल्ला सभा का आयोजन कल"
        ],
        
        '📚 Education': [
            "आगरा कॉलेज में दाखिले की अंतिम तिथि बढ़ी",
            "डॉ. भीमराव आंबेडकर विश्वविद्यालय में परीक्षाएं शुरू",
            "सीबीएसई बोर्ड परीक्षा का टाइम टेबल जारी",
            "स्कूलों में बालिका शिक्षा को बढ़ावा",
            "कोचिंग संस्थानों की नई लिस्ट जारी",
            "आगरा यूनिवर्सिटी का रिजल्ट जारी"
        ],
        
        '🏥 Health': [
            "एसएन मेडिकल कॉलेज में नई स्वास्थ्य सुविधाएं",
            "जिला अस्पताल में मुफ्त स्वास्थ्य शिविर कल",
            "आगरा में डेंगू के मामलों पर नियंत्रण",
            "आयुष्मान कार्ड बनवाने के लिए शिविर आयोजित",
            "प्राइवेट अस्पतालों में इलाज दरें तय",
            "आगरा में हेल्थ चेकअप कैंप आज"
        ],
        
        '💼 Business': [
            "आगरा के जूते-चप्पल उद्योग में तेजी",
            "संजय प्लेस बाजार में दुकानों की नीलामी कल",
            "व्यापार मंडल ने सीएम से की मांग",
            "आगरा में नए शॉपिंग मॉल का प्रस्ताव",
            "जीएसटी से राहत के लिए व्यापारियों की मांग",
            "आगरा के बाजारों में उमड़ी भीड़"
        ],
        
        '⚽ Sports': [
            "आगरा क्रिकेट लीग का आयोजन कल से",
            "ताज महोत्सव में खेल प्रतियोगिताएं आयोजित",
            "आगरा के खिलाड़ियों का राष्ट्रीय स्तर पर चयन",
            "स्टेडियम में मुफ्त कोचिंग शुरू",
            "खेल दिवस पर विशेष कार्यक्रम आयोजित",
            "आगरा में कबड्डी प्रतियोगिता का आयोजन"
        ],
        
        '🌡️ Weather': [
            "आगरा में मौसम साफ, दिन में धूप खिली रहेगी",
            "तापमान में गिरावट, सर्दी बढ़ी",
            "बारिश के आसार, मौसम विभाग ने जारी किया अलर्ट",
            "आगरा में अधिकतम तापमान 32 डिग्री दर्ज",
            "ठंड से राहत, मौसम में आएगा बदलाव",
            "आगरा में कोहरे के कारण विजिबिलिटी कम"
        ],
        
        '🚆 Transport': [
            "आगरा कैंट रेलवे स्टेशन पर नई सुविधाएं",
            "बस स्टैंड पर यात्रियों की सुविधा के लिए नए इंतजाम",
            "आगरा एयरपोर्ट से नई फ्लाइट शुरू",
            "मेट्रो रेल प्रोजेक्ट पर सर्वे जारी",
            "ई-रिक्शा चालकों के लिए नियम सख्त",
            "आगरा में नए बस रूट घोषित"
        ],
        
        '🎉 Events': [
            "ताज महोत्सव की तैयारियां जोरों पर",
            "आगरा में सांस्कृतिक कार्यक्रम आज",
            "फूड फेस्टिवल का आयोजन कल से",
            "पुस्तक मेला में पाठकों की भीड़",
            "आगरा में संगीत संध्या का आयोजन",
            "ताजमहल पर पूर्णिमा पर विशेष व्यूइंग"
        ]
    }
    
    # Select random news from each category
    selected_news = []
    for category, headlines in news_categories.items():
        # Select 1-2 headlines per category
        num_to_select = random.randint(1, 2)
        selected = random.sample(headlines, min(num_to_select, len(headlines)))
        for headline in selected:
            selected_news.append({
                'title': headline,
                'category': category,
                'source': 'Agra News Bureau',
                'time': datetime.now().strftime('%I:%M %p')
            })
    
    # Shuffle the list
    random.shuffle(selected_news)
    return selected_news

def send_to_telegram(message, chat_id=None):
    """Send message to Telegram"""
    if chat_id is None:
        chat_id = CHANNEL_USERNAME
    
    url = f"{TELEGRAM_API_URL}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': True
    }
    
    try:
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            logger.info(f"✅ Message sent to {chat_id}")
            return True
        else:
            logger.error(f"❌ Failed to send: {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Error sending: {e}")
        return False

def post_news():
    """Post news to channel"""
    try:
        logger.info("Generating daily news...")
        news_items = get_daily_news()
        
        # Split into multiple messages if too many
        chunk_size = 8
        for i in range(0, len(news_items), chunk_size):
            chunk = news_items[i:i+chunk_size]
            
            # Group chunk by category
            by_category = {}
            for news in chunk:
                cat = news['category']
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(news)
            
            # Create message
            message = "🚨 **AGRA NEWS UPDATE** 🚨\n\n"
            message += f"📅 {datetime.now().strftime('%d %B %Y')}\n"
            message += f"⏰ {datetime.now().strftime('%I:%M %p')}\n"
            message += "════════════════════\n\n"
            
            for category, items in by_category.items():
                message += f"{category}\n"
                message += "─" * 15 + "\n"
                for news in items:
                    message += f"• {news['title']}\n"
                    message += f"  📍 {news['source']} | ⏱️ {news['time']}\n"
                    message += f"  🔗 [Join Channel](https://t.me/{CHANNEL_USERNAME[1:]})\n\n"
            
            message += "════════════════════\n"
            message += "🤖 **Agra News Bot**"
            
            # Send to channel
            send_to_telegram(message)
            time.sleep(2)  # Wait 2 seconds between messages
            
        logger.info(f"✅ Posted {len(news_items)} news items")
        
    except Exception as e:
        logger.error(f"Error in post_news: {e}")

def handle_updates():
    """Handle incoming messages"""
    try:
        url = f"{TELEGRAM_API_URL}/getUpdates"
        params = {'timeout': 30, 'offset': -1}
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            updates = response.json().get('result', [])
            
            for update in updates:
                update_id = update['update_id']
                
                if update_id in processed_updates:
                    continue
                
                if 'message' in update and 'text' in update['message']:
                    text = update['message']['text']
                    chat_id = update['message']['chat']['id']
                    
                    logger.info(f"Received message: {text} from {chat_id}")
                    
                    if text == '/start':
                        welcome = f"""
🚀 **Agra News Bot Started!**

✅ Bot is running 24/7 on Render
✅ News posted every 20 minutes
✅ No commands needed

📢 **Join channel:** {CHANNEL_USERNAME}

Just sit back and watch news come!
                        """
                        send_to_telegram(welcome, chat_id)
                        logger.info(f"✅ Replied to /start from user {chat_id}")
                
                processed_updates.add(update_id)
            
            save_cache()
            
            if len(processed_updates) > 1000:
                processed_updates.clear()
                
    except Exception as e:
        logger.error(f"Error handling updates: {e}")

def run_bot():
    """Main loop"""
    load_cache()
    
    print("\n" + "="*60)
    print("🤖 AGRA NEWS BOT - RUNNING ON RENDER 24/7")
    print("="*60)
    print(f"📢 Channel: {CHANNEL_USERNAME}")
    print(f"⏰ Posting every 20 minutes")
    print("="*60)
    print("\n✅ Bot is running 24/7!")
    print("✅ News will keep posting")
    print("✅ You can close your computer now")
    print("\n" + "="*60)
    
    last_post_time = 0
    last_update_check = time.time()
    
    while True:
        current_time = time.time()
        
        # Post news every 20 minutes (1200 seconds)
        if current_time - last_post_time > 1200:
            post_news()
            last_post_time = current_time
        
        # Check for /start commands every 5 seconds
        if current_time - last_update_check > 5:
            handle_updates()
            last_update_check = current_time
        
        time.sleep(1)

if __name__ == '__main__':
    try:
        run_bot()
    except KeyboardInterrupt:
        print("\n\n👋 Bot stopped. Goodbye!")
