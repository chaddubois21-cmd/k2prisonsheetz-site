# ====================================================================
# 🐍 1. APP.PY - THE BRAIN: Manages Content, Routes, and Telegram Alerts
# ====================================================================
from flask import Flask, render_template, request, jsonify
from telegram import Bot
import logging
import time
import random
from datetime import datetime

# --- ⚙️ CONFIGURATION (HARDCODED VALUES) ---
TELEGRAM_BOT_TOKEN = "8986370233:AAFMpKs_TsEAim7PhUDbUJBKbK6XMgNTNSg"
TELEGRAM_CHAT_ID = "8986370233"
WALLET_ADDRESS = "bc1qtema35w6qeeqmwnuxr3u9f3nx3gvqc79cl7dxv"
# --- END CONFIGURATION ---

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Telegram Bot
try:
    telegram_bot = Bot(token=TELEGRAM_BOT_TOKEN)
    logging.info("✅ Telegram Bot initialized successfully.")
except Exception as e:
    logging.error(f"❌ Failed to initialize Telegram Bot: {e}")
    telegram_bot = None

app = Flask(__name__)

# --- SIMULATED DATA STORE (Future: Database) ---
ORDER_HISTORY = {}
# ====================================================================

def send_telegram_alert(order_id, amount, notes, products_info):
    """Sends the comprehensive alert message to your Telegram chat."""
    if not telegram_bot:
        logging.warning("Telegram bot is not available. Skipping alert.")
        return False

    message_parts = [
        f"🔔 NEW K2PRISONSHEETZ ORDER! 🔔",
        f"----------------------------------",
        f"Order ID: {order_id}",
        f"Amount Paid: {amount} BTC",
        f"Notes: {notes if notes else 'N/A'}",
        f"Products: {products_info}",
        f"Source: BTC Wallet {WALLET_ADDRESS}",
        f"----------------------------------"
    ]
    full_message = "\n".join(message_parts)
    try:
        telegram_bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=full_message)
        logging.info(f"🚀 Alert sent for Order ID: {order_id}")
        return True
    except Exception as e:
        logging.error(f"❌ Error sending Telegram message for {order_id}: {e}")
        return False


# 1. THE SHOP (Index) - Entry Point
@app.route('/')
def index():
    """Serves the primary shop page content with featured products."""
    # Data structured for immediate marketing impact (Listing 1 & 2 Hooks)
    products_data = {
        'JAIL_TERROR': {'name': 'Jail Terror', 'hook': "The pinnacle of potency. Our 300gsm Jail Terror cards are meticulously dipped in a massive 9g of 5F-ADB. For an undetectable, professional finish.", 'price_btc': 0.001786, 'price_usd': 150.00, 'slug': 'jail-terror'},
        'ZOMBIE_SHEETS': {'name': 'Zombie Sheets', 'hook': "Unleash the power. Our 200gsm Zombie Sheets are hyper-saturated, soaking in a massive 5g dose of 5F-ADB. An experience engineered for maximum impact.", 'price_btc': 0.001610, 'price_usd': 135.00, 'slug': 'zombie-sheets'}
    }
    return render_template('index.html', products=products_data)

# 2. THE DETAIL PAGE (product_detail.html)
@app.route('/product/<product_slug>')
def product_detail(product_slug):
    """Serves the detailed spec sheet page based on the URL slug."""
    # --- Data Lookups based on the slugs ---
    if product_slug.lower() == 'jail-terror':
        product_data = {
            'name': 'Jail Terror (300gsm Cardstock)', 
            'hook': "The pinnacle of potency. Our 300gsm Jail Terror cards are meticulously dipped in a massive 9g of 5F-ADB. We pour two decades of soaking expertise into every card, ensuring a professional, undetectable finish.",
            'promise': "Obsession Driven: We pride ourselves on soaking every piece to its maximum capacity. This isn't just dipped; it's mastered.",
            'metrics': "0.001786 BTC | $150.00 USD",
            'details': "Our two decades of soaking expertise ensures maximum capacity and professional finish. Note: A piece too large could send you to the ground in tears."
        }
    elif product_slug.lower() == 'zombie-sheets':
        product_data = {
            'name': 'Zombie Sheets (200gsm Drip)', 
            'hook': "Unleash the power. Hyper-saturated 200gsm sheets, soaking in a massive 5g dose of 5F-ADB. An experience engineered for maximum impact.",
            'promise': "Built to the Limit: These sheets are soaked to maximum capacity—be warned: a piece too large can bring you to tears (in the best way possible!).",
            'metrics': "0.001610 BTC | $135.00 USD",
            'details': "Built to handle high impact and maximize saturation. Built to the limit."
        }
    else:
        return render_template('404.html') 

    return render_template('product_detail.html', product=product_data)


# 3. THE CHECKOUT PAGE (payment.html) - Handles the actual transaction logic
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """Serves the payment portal and handles the BTC transaction logic."""
    if request.method == 'POST':
        order_id = request.form.get('order_id', 'UNKNOWN_ORDER')
        try:
            amount = float(request.form.get('crypto_amount', 0.0))
            notes = request.form.get('notes', 'No notes provided.')

            # --- 🛒 TRANSACTION PROCESSING ---
            ORDER_HISTORY[order_id] = {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                'amount': amount, 
                'notes': notes, 
                'status': 'PENDING_TRACKING'
            }

            # 1. Send Alert
            # (We pass simplified context for the immediate alert)
            products_info_msg = f"Order {order_id} processed. (Check cart/index for item details)"
            send_telegram_alert(order_id, amount, notes, products_info_msg)

            # 2. Generate Tracking (Simulation)
            tracking_number = f"TMF-{random.randint(10000, 99999)}-{datetime.now().strftime('%y%m%d')}"
            ORDER_HISTORY[order_id]['tracking'] = tracking_number
            logging.info(f"Generated Tracking: {tracking_number} for {order_id}")

            # 3. Final User Confirmation
            return render_template('payment.html', order_id=order_id, tracking_number=tracking_number, status="Success")

        except ValueError:
             return render_template('payment.html', status="Error", error_message="Please enter a valid BTC amount.")


    # GET request: Show the payment page
    return render_template('payment.html', products_data=None, order_id=None, tracking_number=None, status=None)

# 4. The Error Page
@app.route('/404')
def not_found():
    return render_template('404.html')

if __name__ == '__main__':
    # NOTE: When deploying to Droplet, you REPLACE this line with Gunicorn/Supervisor configuration
    app.run(host='0.0.0.0', port=5000, debug=True)