from flask import Flask, request, jsonify
import requests
import json
import hmac
import hashlib
from config import Config
from inventory import InventoryManager

app = Flask(__name__)
app.config.from_object(Config)

# Initialize inventory manager
inventory_manager = InventoryManager()

def verify_webhook(payload, signature):
    """Verify webhook signature for security"""
    expected_signature = hmac.new(
        app.config['SECRET_KEY'].encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected_signature)

def send_whatsapp_message(phone_number, message):
    """Send message via WhatsApp Business API"""
    url = f"https://graph.facebook.com/v18.0/{app.config['WHATSAPP_PHONE_NUMBER_ID']}/messages"
    
    headers = {
        'Authorization': f'Bearer {app.config["WHATSAPP_TOKEN"]}',
        'Content-Type': 'application/json'
    }
    
    data = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {"body": message}
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending message: {e}")
        return False

@app.route('/webhook', methods=['GET'])
def webhook_verify():
    """Verify webhook for WhatsApp"""
    verify_token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if verify_token == app.config['WEBHOOK_VERIFY_TOKEN']:
        return challenge
    else:
        return 'Invalid verify token', 403

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming WhatsApp messages"""
    try:
        data = request.get_json()
        
        # Process webhook data
        if data and 'entry' in data:
            for entry in data['entry']:
                if 'changes' in entry:
                    for change in entry['changes']:
                        if change['field'] == 'messages':
                            if 'messages' in change['value']:
                                for message in change['value']['messages']:
                                    # Extract message details
                                    from_number = message['from']
                                    message_text = message.get('text', {}).get('body', '')
                                    
                                    # Process inventory command
                                    response = inventory_manager.process_command(
                                        message_text, from_number
                                    )
                                    
                                    # Send response back
                                    send_whatsapp_message(from_number, response)
        
        return jsonify({'status': 'success'}), 200
    
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return jsonify({'status': 'error'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

@app.route('/')
def index():
    """Basic info endpoint"""
    return jsonify({
        'name': 'WhatsApp Inventory Management System',
        'status': 'running',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)