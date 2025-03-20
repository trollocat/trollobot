
from flask import Flask
import threading
from main import client, token

app = Flask(__name__)
bot_thread = None

def run_bot():
    client.run(token)

@app.route('/')
def home():
    return "Bot is alive", 200

if __name__ == '__main__':
    # Start bot in thread
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True  # This ensures the thread closes when the main process ends
    bot_thread.start()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=8080)
