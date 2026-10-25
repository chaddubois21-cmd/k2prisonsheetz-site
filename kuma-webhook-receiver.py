#!/usr/bin/env python3
"""
K2 Prison Sheetz Uptime Kuma Webhook Receiver
Receives notifications from Uptime Kuma and sends Telegram alerts via OpenClaw.
"""

from flask import Flask, request, jsonify
import requests
import json
import logging
import os
from datetime import datetime, timedelta

# Configuration
HOST = '127.0.0.1'  # Bind only to localhost for security
PORT = 5003  # Different port to avoid conflict with K2 app

# OpenClaw Telegram API endpoint
OPENCLAW_API_URL = "https://api.openclaw.ai/v1"
TELEGRAM_TARGET = "8627616344"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/k2-webhook-receiver.log'),
        logging.StreamHandler()
    ]
)
app = Flask(__name__)


def send_telegram_alert(alert_type, message):
    """Send alert through OpenClaw Telegram API"""
    try:
        payload = {
            "channel": "telegram",
            "target": TELEGRAM_TARGET,
            "message": message
        }
        
        # Send to OpenClaw API
        response = requests.post(
            f"{OPENCLAW_API_URL}/message/send",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            logging.info(f"✅ Telegram alert sent successfully: {alert_type}")
            return True
        else:
            logging.error(f"❌ Failed to send Telegram alert (HTTP {response.status_code}): {alert_type}")
            return False
            
    except Exception as e:
        logging.error(f"❌ Error sending Telegram alert ({alert_type}): {e}")
        return False


def format_monitor_status(monitor_data):
    """Format monitor status for user-friendly message"""
    status = monitor_data.get('status', 'unknown')
    monitor_name = monitor_data.get('name', 'K2 Prison Sheetz')
    monitor_url = monitor_data.get('url', 'https://k2prisonsheetz.com')
    
    if status == 'down':
        return f"🔴 **{monitor_name} is DOWN**\n📅 **Detected:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n🔗 **URL:** {monitor_url}\n⏱️ **Status:** Service unavailable"
    elif status == 'up':
        return f"🟢 **{monitor_name} is back ONLINE**\n📅 **Recovered:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n🔗 **URL:** {monitor_url}"
    else:
        return f"⚪ **{monitor_name} status: {status.upper()}**\n📅 **Checked:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n🔗 **URL:** {monitor_url}"


@app.route('/webhook/kuma', methods=['POST'])
def kuma_webhook():
    """Receive webhook notifications from Uptime Kuma"""
    try:
        data = request.get_json()
        
        if not data:
            logging.warning("Received empty webhook payload")
            return jsonify({"error": "Empty payload"}), 400
        
        logging.info(f"Received webhook: {json.dumps(data, indent=2)}")
        
        # Parse the notification
        alert_type = data.get('alert_type', 'unknown')
        monitor_data = data.get('monitor', {})
        
        # Format message based on alert type
        if alert_type == 'down':
            message = format_monitor_status({
                **monitor_data,
                'status': 'down'
            })
            message += "\n🚨 **IMMEDIATE ACTION REQUIRED** - Service is down!"
            send_telegram_alert('down', message)
            
        elif alert_type == 'up':
            message = format_monitor_status({
                **monitor_data,
                'status': 'up'
            })
            message += "\n✅ Service has been restored!"
            send_telegram_alert('up', message)
            
        else:
            # Generic notification
            message = format_monitor_status(monitor_data)
            message += f"\n📋 **Alert Type:** {alert_type}"
            send_telegram_alert('generic', message)
        
        return jsonify({
            "status": "success",
            "processed": alert_type,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logging.error(f"Error processing webhook: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "K2 Prison Sheetz Uptime Kuma Webhook Receiver"
    }), 200


if __name__ == '__main__':
    # Ensure log directory exists
    os.makedirs('/var/log', exist_ok=True)
    
    logging.info("🚀 Starting K2 Prison Sheetz Uptime Kuma Webhook Receiver...")
    logging.info(f"Listening on {HOST}:{PORT}")
    logging.info("Webhook endpoint: /webhook/kuma")
    
    app.run(host=HOST, port=PORT, debug=False)