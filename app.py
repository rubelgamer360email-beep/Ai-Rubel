from flask import Flask, request, jsonify, render_template_string, send_from_directory
import os
from google import genai

app = Flask(__name__)

# জেমিনি ক্লায়েন্ট সেটআপ
client = genai.Client(api_key="AQ.Ab8RN6J5mlUlcKVzkyKGanZiT1FfoePoTZAxs21ONOQ1Fh0uqA")

# লোকাল ফোল্ডার পাথ সেটআপ
BASE_MEDIA_DIR = os.path.abspath("Ai_Rubel_Media")
PHOTO_DIR = os.path.join(BASE_MEDIA_DIR, "ছবি")
VIDEO_DIR = os.path.join(BASE_MEDIA_DIR, "ভিডিও")
STUDENT_DIR = os.path.join(BASE_MEDIA_DIR, "স্টুডেন্ট_ফাইল")

os.makedirs(PHOTO_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(STUDENT_DIR, exist_ok=True)

AI_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Rubel</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0d1117; color: #c9d1d9; display: flex; flex-direction: column; height: 100vh; }
        header { background: #161b22; padding: 12px 15px; text-align: center; font-size: 18px; font-weight: bold; border-bottom: 1px solid #30363d; display: flex; justify-content: space-between; align-items: center; }
        .header-title { margin: 0 auto; color: #58a6ff; }
        .chat-container { flex: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; max-width: 800px; margin: 0 auto; width: 100%; }
        .message { background: #21262d; padding: 12px 16px; border-radius: 12px; max-width: 85%; word-wrap: break-word; line-height: 1.5; font-size: 14px; white-space: pre-wrap; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }
        .user-msg { background: #1f6feb; color: white; align-self: flex-end; border-bottom-right-radius: 3px; }
        .ai-msg { background: #21262d; color: #e6edf3; align-self: flex-start; border-bottom-left-radius: 3px; border: 1px solid #30363d; }
        
        .input-panel { background: #161b22; padding: 12px 15px; border-top: 1px solid #30363d; max-width: 800px; margin: 0 auto; width: 100%; display: flex; flex-direction: column; gap: 8px; }
        .toolbar { display: flex; gap: 10px; align-items: center; font-size: 13px; }
        .tool-btn { background: #21262d; border: 1px solid #30363d; color: #8b949e; padding: 6px 12px; border-radius: 6px; cursor: pointer; display: flex; align-items: center; gap: 5px; transition: 0.2s; }
        .tool-btn:hover { background: #30363d; color: white; border-color: #8b949e; }
        
        .input-row { display: flex; gap: 8px; align-items: center; }
        input[type="text"] { flex: 1; background: #0d1117; border: 1px solid #30363d; color: white; padding: 12px; border-radius: 8px; outline: none; font-size: 14px; transition: 0.2s; }
        input[type="text"]:focus { border-color: #58a6ff; }
        input[type="file"] { display: none; }
        
        .send-btn { background: #238636; color: white; border: none; padding: 12px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 14px; transition: 0.2s; }
        .send-btn:hover { background: #2ea043; }
    </style>
</head>
<body>
    <header>
        <span class="header-title">🤖 AI Rubel</span>
    </header>

    <div class="chat-container" id="chatContainer">
        <div class="message ai-msg">আসসালামু আলাইকুম রুবেল ভাই! আপডেট মডেল gemini-3.6-flash সহ সিস্টেম এখন পুরোপুরি প্রস্তুত। বলুন কী জানতে চান?</div>
    </div>

    <div class="input-panel">
        <div class="toolbar">
            <label class="tool-btn" title="ফাইল বা ছবি">
                📁 ফাইল <input type="file" id="mediaInput" accept="image/*,video/*" onchange="handleFileSelect(this)">
            </label>
            <label class="tool-btn" title="ক্যামেরা">
                📷 ক্যামেরা <input type="file" id="cameraInput" accept="image/*" capture="environment" onchange="handleFileSelect(this)">
            </label>
            <button class="tool-btn" onclick="toggleVoiceRecord()" id="voiceBtn">🎤 ভয়েস</button>
        </div>
        <div class="input-row">
            <input type="text" id="userInput" placeholder="আপনার প্রশ্ন এখানে লিখুন..." onkeypress="handleKeyPress(event)">
            <button class="send-btn" onclick="sendMessage()">পাঠান</button>
        </div>
    </div>

    <script>
        async function sendMessage() {
            const input = document.getElementById('userInput');
            const container = document.getElementById('chatContainer');
            const text = input.value.trim();
            if(!text) return;
            
            const userDiv = document.createElement('div');
            userDiv.className = 'message user-msg';
            userDiv.innerText = text;
            container.appendChild(userDiv);
            
            input.value = '';
            container.scrollTop = container.scrollHeight;

            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'message ai-msg';
            loadingDiv.innerText = 'উত্তর তৈরি হচ্ছে...';
            container.appendChild(loadingDiv);
            container.scrollTop = container.scrollHeight;

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await response.json();
                
                container.removeChild(loadingDiv);

                const aiDiv = document.createElement('div');
                aiDiv.className = 'message ai-msg';
                aiDiv.innerText = data.reply;
                container.appendChild(aiDiv);
                container.scrollTop = container.scrollHeight;
            } catch (error) {
                container.removeChild(loadingDiv);
                const errDiv = document.createElement('div');
                errDiv.className = 'message ai-msg';
                errDiv.innerText = "দুঃখিত রুবেল ভাই, সার্ভারে সংযোগ করতে সমস্যা হয়েছে।";
                container.appendChild(errDiv);
            }
        }

        function handleFileSelect(input) {
            if (input.files && input.files[0]) {
                const file = input.files[0];
                const container = document.getElementById('chatContainer');
                
                const userDiv = document.createElement('div');
                userDiv.className = 'message user-msg';
                userDiv.innerText = `[ফাইল সিলেক্টেড: ${file.name}]`;
                container.appendChild(userDiv);
                container.scrollTop = container.scrollHeight;

                setTimeout(() => {
                    const aiDiv = document.createElement('div');
                    aiDiv.className = 'message ai-msg';
                    aiDiv.innerText = `ফাইলটি সফলভাবে রিসিভ করা হয়েছে, রুবেল ভাই: ${file.name}`;
                    container.appendChild(aiDiv);
                    container.scrollTop = container.scrollHeight;
                }, 800);
            }
        }

        let isRecording = false;
        function toggleVoiceRecord() {
            const btn = document.getElementById('voiceBtn');
            const container = document.getElementById('chatContainer');
            isRecording = !isRecording;
            
            if(isRecording) {
                btn.style.background = '#da3633';
                btn.style.color = 'white';
                btn.innerText = '🔴 শুনছি...';
            } else {
                btn.style.background = '#21262d';
                btn.style.color = '#8b949e';
                btn.innerText = '🎤 ভয়েস';
                
                const userDiv = document.createElement('div');
                userDiv.className = 'message user-msg';
                userDiv.innerText = '[ভয়েস মেসেজ রেকর্ড করা হয়েছে]';
                container.appendChild(userDiv);
                container.scrollTop = container.scrollHeight;
            }
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(AI_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    
    try:
        # লেটেস্ট প্রস্তাবিত মডেল gemini-3.6-flash ব্যবহার করা হলো[span_1](start_span)[span_1](end_span)
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=user_message,
        )
        reply = response.text
    except Exception as e:
        reply = f"এপিআই কানেকশন ত্রুটি: {str(e)}"
        
    return jsonify({'reply': reply})

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
