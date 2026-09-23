from flask import Flask, render_template_string, send_from_directory
import os

app = Flask(__name__)

# লোকাল ফোল্ডার পাথ
BASE_MEDIA_DIR = os.path.abspath("Ai_Rubel_Media")
PHOTO_DIR = os.path.join(BASE_MEDIA_DIR, "ছবি")
VIDEO_DIR = os.path.join(BASE_MEDIA_DIR, "ভিডিও")
STUDENT_DIR = os.path.join(BASE_MEDIA_DIR, "স্টুডেন্ট_ফাইল")

os.makedirs(PHOTO_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(STUDENT_DIR, exist_ok=True)

# মূল চ্যাট এবং আপলোড ইন্টারফেসের ডিজাইন
CHAT_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Rubel - Storage & Chat</title>
    <style>
        * { box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0d1117; color: #c9d1d9; margin: 0; padding: 0; display: flex; flex-direction: column; height: 100vh; }
        header { background: #161b22; padding: 15px; text-align: center; font-size: 20px; font-weight: bold; border-bottom: 1px solid #30363d; }
        .chat-container { flex: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; max-width: 800px; margin: 0 auto; width: 100%; }
        .message { background: #21262d; padding: 10px 15px; border-radius: 8px; max-width: 75%; word-wrap: break-word; }
        .user-msg { background: #1f6feb; color: white; align-self: flex-end; }
        .ai-msg { background: #30363d; align-self: flex-start; }
        .input-container { padding: 15px; background: #161b22; display: flex; gap: 10px; border-top: 1px solid #30363d; max-width: 800px; margin: 0 auto; width: 100%; }
        input[type="text"] { flex: 1; background: #0d1117; border: 1px solid #30363d; color: white; padding: 10px; border-radius: 6px; outline: none; }
        button { background: #238636; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: bold; }
        button:hover { background: #2ea043; }
    </style>
</head>
<body>
    <header>🤖 AI Rubel Workspace</header>
    <div class="chat-container" id="chatContainer">
        <div class="message ai-msg">আসসালামু আলাইকুম রুবেল ভাই! আপনার প্রজেক্টের ফুল ইন্টারফেস প্রস্তুত। বলুন কীভাবে সাহায্য করব?</div>
    </div>
    <div class="input-container">
        <input type="text" id="userInput" placeholder="এখানে কিছু লিখুন...">
        <button onclick="sendMessage()">পাঠান</button>
    </div>
    <script>
        function sendMessage() {
            const input = document.getElementById('userInput');
            const container = document.getElementById('chatContainer');
            if(!input.value.trim()) return;
            
            const userDiv = document.createElement('div');
            userDiv.className = 'message user-msg';
            userDiv.innerText = input.value;
            container.appendChild(userDiv);
            
            input.value = '';
            container.scrollTop = container.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(CHAT_TEMPLATE)

@app.route('/media_file/<file_type>/<filename>')
def media_file(file_type, filename):
    if file_type == 'photo':
        return send_from_directory(PHOTO_DIR, filename)
    elif file_type == 'video':
        return send_from_directory(VIDEO_DIR, filename)
    elif file_type == 'student':
        return send_from_directory(STUDENT_DIR, filename)
    return "Not Found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
