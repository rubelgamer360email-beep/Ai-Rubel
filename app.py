from flask import Flask, request, jsonify, render_template_string, send_from_directory, redirect, url_for
import os
import random
import base64
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

# লোকাল ফোল্ডার পাথ
BASE_MEDIA_DIR = os.path.abspath("/storage/emulated/0/Ai Rubel")
PHOTO_DIR = os.path.join(BASE_MEDIA_DIR, "ছবি")
VIDEO_DIR = os.path.join(BASE_MEDIA_DIR, "ভিডিও")
STUDENT_DIR = os.path.join(BASE_MEDIA_DIR, "স্টুডেন্ট_ফাইল")

os.makedirs(PHOTO_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(STUDENT_DIR, exist_ok=True)

# ফোল্ডার থেকে সরাসরি ব্যাকগ্রাউন্ড ইমেজ পাথ লোড করার ফাংশন
def get_bg_url():
    if os.path.exists(PHOTO_DIR):
        files = os.listdir(PHOTO_DIR)
        bg_files = [f for f in files if f.lower() in ['bg.jpg', 'bg.png', 'bg.jpeg']]
        target_img = bg_files[0] if bg_files else next((f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))), None)
        
        if target_img:
            return f"/media_file/photo/{target_img}"
    return ""

CHAT_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Rubel - Storage & Chat</title>
    <style>
        * { box-sizing: border-box; }
        html, body { 
            height: 100%; margin: 0; padding: 0; 
            color: #f1f5f9; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
        }
        body {
            background-color: #090d16;
            background-image: linear-gradient(135deg, rgba(9, 13, 22, 0.75), rgba(20, 15, 38, 0.75)), url('{{ bg_url }}');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            display: flex; 
            flex-direction: column; 
        }

        header { 
            background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(12px); 
            padding: 12px 18px; text-align: center; font-size: 16px; font-weight: 600; 
            border-bottom: 1px solid rgba(255, 255, 255, 0.08); 
            position: fixed; top: 0; left: 0; width: 100%; z-index: 100;
            display: flex; justify-content: space-between; align-items: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        }
        header a { color: #38bdf8; text-decoration: none; font-size: 13px; font-weight: 500; background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.3); padding: 6px 12px; border-radius: 8px; transition: 0.2s; }
        header a:hover { background: rgba(56, 189, 248, 0.2); }
        
        #chat-container { 
            margin-top: 60px; margin-bottom: 75px; flex: 1; padding: 15px; 
            overflow-y: auto; display: flex; flex-direction: column; gap: 14px; 
        }
        .message { max-width: 85%; padding: 12px 16px; border-radius: 14px; font-size: 14px; line-height: 1.5; word-wrap: break-word; backdrop-filter: blur(8px); animation: fadeIn 0.3s ease; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
        
        .user-msg { background: linear-gradient(135deg, #3b82f6, #2563eb); color: white; align-self: flex-end; border-bottom-right-radius: 4px; box-shadow: 0 4px 15px rgba(59, 130, 246, 0.35); }
        .bot-msg { background: rgba(30, 41, 59, 0.8); color: #f8fafc; align-self: flex-start; border-bottom-left-radius: 4px; border: 1px solid rgba(168, 85, 247, 0.25); box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
        
        .speak-btn {
            background: rgba(51, 65, 85, 0.7); color: #cbd5e1; border: 1px solid rgba(255,255,255,0.1); padding: 5px 10px;
            font-size: 12px; border-radius: 6px; cursor: pointer; margin-top: 8px;
            display: inline-flex; align-items: center; gap: 5px; transition: 0.2s;
        }
        .speak-btn:hover { background: #3b82f6; color: white; border-color: #3b82f6; }

        .media-box { margin-top: 10px; max-width: 100%; border-radius: 10px; overflow: hidden; border: 1px solid rgba(255,255,255,0.1); }
        .media-box img, .media-box video { width: 100%; max-height: 240px; border-radius: 10px; display: block; background: black; object-fit: contain; }
        
        #input-container { 
            position: fixed; bottom: 0; left: 0; width: 100%; padding: 12px 15px; 
            background: rgba(9, 13, 22, 0.88); backdrop-filter: blur(12px); 
            display: flex; gap: 10px; border-top: 1px solid rgba(255, 255, 255, 0.08); z-index: 100;
            box-shadow: 0 -4px 20px rgba(0,0,0,0.4);
        }
        input[type="text"] { flex: 1; padding: 12px 16px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.12); background: rgba(15, 23, 42, 0.8); color: white; outline: none; font-size: 14px; transition: 0.2s; }
        input[type="text"]:focus { border-color: #38bdf8; box-shadow: 0 0 10px rgba(56, 189, 248, 0.2); }
        
        button.send-btn { background: linear-gradient(135deg, #10b981, #059669); color: white; border: none; padding: 0 20px; border-radius: 10px; font-weight: bold; cursor: pointer; font-size: 14px; transition: 0.2s; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3); }
        button.send-btn:hover { background: linear-gradient(135deg, #059669, #047857); }
    </style>
</head>
<body>
    <header>
        <span>✨ AI Rubel Hub</span>
        <a href="/storage">স্টোরেজ ফাইল দেখুন</a>
    </header>
    
    <div id="chat-container">
        <div class="message bot-msg">
            <div>আসসালামু আলাইকুম! চ্যাট বক্সে "ছবি" বা "ভিডিও" লিখে পাঠান, সরাসরি স্টোরেজ থেকে মিডিয়া দেখতে পাবেন।</div>
            <button class="speak-btn" onclick="speakText(this.previousElementSibling.innerText)">🔊 শুনুন</button>
        </div>
    </div>
    
    <div id="input-container">
        <input type="text" id="user-input" placeholder="এখানে কিছু লিখুন (যেমন: ছবি, ভিডিও)..." onkeypress="checkEnter(event)">
        <button class="send-btn" onclick="sendMessage()">পাঠাও</button>
    </div>

    <script>
        // পেজ লোড হওয়ার সাথে সাথে স্পিচ সিন্থেসিস ইনিশিয়ালাইজ করা যাতে কাজ করে
        window.addEventListener('DOMContentLoaded', () => {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.getVoices();
            }
        });

        function speakText(text) {
            if (!('speechSynthesis' in window)) {
                alert('আপনার ব্রাউজার স্পিচ সিন্থেসিস সাপোর্ট করে না!');
                return;
            }
            
            window.speechSynthesis.cancel();
            
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'bn-BD';
            utterance.rate = 0.95;
            utterance.pitch = 1.0;

            // যদি বাংলা ভয়েস সরাসরি না পায়, তবে ডিফল্ট ভয়েস দিয়ে চেষ্টা করবে
            const voices = window.speechSynthesis.getVoices();
            const bnVoice = voices.find(v => v.lang.includes('bn') || v.lang.includes('Bengali'));
            if (bnVoice) {
                utterance.voice = bnVoice;
            }

            utterance.onerror = (event) => {
                console.error('Speech synthesis error', event);
            };

            window.speechSynthesis.speak(utterance);
        }

        function checkEnter(e) { if (e.key === 'Enter') { sendMessage(); } }

        function appendMessage(text, sender, mediaUrl = null, mediaType = null) {
            const container = document.getElementById('chat-container');
            const msgDiv = document.createElement('div');
            msgDiv.className = `message ${sender === 'user' ? 'user-msg' : 'bot-msg'}`;
            
            let content = `<div>${text}</div>`;
            
            if (mediaUrl) {
                if (mediaType === 'photo') {
                    content += `<div class="media-box"><img src="${mediaUrl}" alt="Media Image"></div>`;
                } else if (mediaType === 'video') {
                    content += `<div class="media-box"><video controls><source src="${mediaUrl}" type="video/mp4">আপনার ব্রাউজার ভিডিওটি সাপোর্ট করছে না।</video></div>`;
                }
            }

            if (sender === 'bot') {
                content += `<br><button class="speak-btn" onclick="speakText(this.previousElementSibling.innerText)">🔊 শুনুন</button>`;
            }

            msgDiv.innerHTML = content;
            container.appendChild(msgDiv);
            window.scrollTo(0, document.body.scrollHeight);
        }

        async function sendMessage() {
            const inputField = document.getElementById('user-input');
            const text = inputField.value.trim();
            if (!text) return;

            appendMessage(text, 'user');
            inputField.value = '';

            try {
                const response = await fetch('/process', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                
                const data = await response.json();
                if (data.status === 'success') {
                    appendMessage(data.response_message, 'bot', data.media_url, data.media_type);
                } else {
                    appendMessage('❌ এরর: ' + data.message, 'bot');
                }
            } catch (error) {
                appendMessage('❌ সার্ভার কানেকশনে সমস্যা হয়েছে!', 'bot');
            }
        }
    </script>
</body>
</html>
"""

STORAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Rubel - File Manager</title>
    <style>
        * { box-sizing: border-box; }
        body { 
            background-color: #090d16;
            background-image: linear-gradient(135deg, rgba(9, 13, 22, 0.75), rgba(20, 15, 38, 0.75)), url('{{ bg_url }}');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            color: #f1f5f9; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; padding: 20px; min-height: 100vh;
        }

        h2 { text-align: center; color: #c084fc; text-shadow: 0 0 15px rgba(192, 132, 252, 0.4); margin-bottom: 25px; }
        .card { background: rgba(30, 41, 59, 0.75); backdrop-filter: blur(12px); padding: 20px; border-radius: 14px; margin-bottom: 20px; box-shadow: 0 8px 30px rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.08); }
        .card h3 { margin-top: 0; color: #38bdf8; font-size: 18px; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 10px; }
        .card h4 { color: #e2e8f0; font-size: 15px; margin: 15px 0 10px 0; }
        
        form { display: flex; flex-direction: column; gap: 12px; }
        select, input[type="file"] { padding: 12px; background: rgba(15, 23, 42, 0.8); color: white; border: 1px solid rgba(255,255,255,0.15); border-radius: 8px; outline: none; }
        
        button.upload-btn { background: linear-gradient(135deg, #10b981, #059669); color: white; border: none; padding: 12px; border-radius: 8px; font-weight: bold; cursor: pointer; transition: 0.2s; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3); }
        button.upload-btn:hover { background: linear-gradient(135deg, #059669, #047857); }
        
        ul { list-style: none; padding: 0; margin: 0; }
        li { background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(6px); margin-bottom: 10px; padding: 12px; border-radius: 10px; display: flex; flex-direction: column; gap: 10px; border: 1px solid rgba(255,255,255,0.05); }
        .file-info { display: flex; justify-content: space-between; align-items: center; word-break: break-all; font-size: 14px; }
        .btn-group { display: flex; gap: 8px; }
        
        a.play-btn { background: #06b6d4; color: white; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-size: 12px; font-weight: 500; transition: 0.2s; }
        a.play-btn:hover { background: #0891b2; }
        
        a.download { background: #3b82f6; color: white; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-size: 12px; font-weight: 500; transition: 0.2s; }
        a.download:hover { background: #2563eb; }
        
        .back-btn { display: inline-block; background: rgba(51, 65, 85, 0.8); color: #f8fafc; padding: 8px 16px; border-radius: 8px; text-decoration: none; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.1); font-size: 13px; font-weight: 500; transition: 0.2s; }
        .back-btn:hover { background: #475569; }
        
        video, img { width: 100%; max-height: 220px; border-radius: 8px; margin-top: 5px; background: black; object-fit: contain; border: 1px solid rgba(255,255,255,0.1); }
        .empty-text { color: #64748b; font-size: 13px; font-style: italic; }
    </style>
</head>
<body>
    <a href="/" class="back-btn">⬅️ চ্যাটে ফিরে যান</a>
    <h2>📦 অনলাইন স্টোরেজ ফাইল ম্যানেজার</h2>
    
    <div class="card">
        <h3>নতুন ফাইল আপলোড করুন</h3>
        <form action="/upload" method="POST" enctype="multipart/form-data">
            <select name="folder">
                <option value="photo">ছবি ফোল্ডার (এখানে ছবি দিলে ব্যাকগ্রাউন্ড সেট হবে)</option>
                <option value="video">ভিডিও ফোল্ডার</option>
                <option value="student">স্টুডেন্ট ফাইল ফোল্ডার</option>
            </select>
            <input type="file" name="file" required>
            <button type="submit" class="upload-btn">আপলোড করুন</button>
        </form>
    </div>

    <div class="card">
        <h3>ফাইল তালিকা ও প্লেয়ার</h3>
        
        <h4>🖼️ ছবি ফোল্ডার:</h4>
        <ul>
            {% for f in photos %}
                <li>
                    <div class="file-info">
                        <span>{{ f }}</span>
                        <div class="btn-group">
                            <a class="play-btn" href="javascript:void(0);" onclick="toggleMedia('photo-{{ loop.index }}')">👁️ দেখুন</a>
                            <a class="download" href="/download/photo/{{ f }}">ডাউনলোড</a>
                        </div>
                    </div>
                    <div id="photo-{{ loop.index }}" style="display:none;">
                        <img src="/media_file/photo/{{ f }}" alt="{{ f }}">
                    </div>
                </li>
            {% else %}
                <li class="empty-text">কোনো ছবি নেই</li>
            {% endfor %}
        </ul>

        <h4>🎬 ভিডিও ফোল্ডার:</h4>
        <ul>
            {% for f in videos %}
                <li>
                    <div class="file-info">
                        <span>{{ f }}</span>
                        <div class="btn-group">
                            <a class="play-btn" href="javascript:void(0);" onclick="toggleMedia('video-{{ loop.index }}')">▶️ প্লে করুন</a>
                            <a class="download" href="/download/video/{{ f }}">ডাউনলোড</a>
                        </div>
                    </div>
                    <div id="video-{{ loop.index }}" style="display:none;">
                        <video controls>
                            <source src="/media_file/video/{{ f }}" type="video/mp4">
                            আপনার ব্রাউজার ভিডিওটি সাপোর্ট করছে না।
                        </video>
                    </div>
                </li>
            {% else %}
                <li class="empty-text">কোনো ভিডিও নেই</li>
            {% endfor %}
        </ul>

        <h4>📚 স্টুডেন্ট ফাইল:</h4>
        <ul>
            {% for f in students %}
                <li>
                    <div class="file-info">
                        <span>{{ f }}</span>
                        <div class="btn-group">
                            <a class="download" href="/download/student/{{ f }}">ডাউনলোড</a>
                        </div>
                    </div>
                </li>
            {% else %}
                <li class="empty-text">কোনো ফাইল নেই</li>
            {% endfor %}
        </ul>
    </div>

    <script>
        function toggleMedia(id) {
            const el = document.getElementById(id);
            if (el.style.display === "none") {
                el.style.display = "block";
            } else {
                el.style.display = "none";
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    bg_url = get_bg_url()
    return render_template_string(CHAT_TEMPLATE, bg_url=bg_url)

@app.route('/storage')
def storage_page():
    bg_url = get_bg_url()
    photos = os.listdir(PHOTO_DIR) if os.path.exists(PHOTO_DIR) else []
    videos = os.listdir(VIDEO_DIR) if os.path.exists(VIDEO_DIR) else []
    students = os.listdir(STUDENT_DIR) if os.path.exists(STUDENT_DIR) else []
    return render_template_string(STORAGE_TEMPLATE, photos=photos, videos=videos, students=students, bg_url=bg_url)

@app.route('/upload', methods=['POST'])
def upload_file():
    target_folder = request.form.get('folder')
    uploaded_file = request.files.get('file')
    
    if uploaded_file and uploaded_file.filename:
        filename = secure_filename(uploaded_file.filename)
        if target_folder == 'photo':
            save_path = os.path.join(PHOTO_DIR, filename)
        elif target_folder == 'video':
            save_path = os.path.join(VIDEO_DIR, filename)
        else:
            save_path = os.path.join(STUDENT_DIR, filename)
            
        uploaded_file.save(save_path)
    return redirect(url_for('storage_page'))

@app.route('/download/<folder_type>/<filename>')
def download_file(folder_type, filename):
    if folder_type == 'photo':
        return send_from_directory(PHOTO_DIR, filename, as_attachment=True)
    elif folder_type == 'video':
        return send_from_directory(VIDEO_DIR, filename, as_attachment=True)
    elif folder_type == 'student':
        return send_from_directory(STUDENT_DIR, filename, as_attachment=True)
    return "Not Found", 404

@app.route('/media_file/<path:folder_type>/<path:filename>')
def serve_media(folder_type, filename):
    if folder_type == 'photo':
        return send_from_directory(PHOTO_DIR, filename)
    elif folder_type == 'video':
        return send_from_directory(VIDEO_DIR, filename)
    elif folder_type == 'student':
        return send_from_directory(STUDENT_DIR, filename)
    return "Not Found", 404

@app.route('/process', methods=['POST'])
def process_data():
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()
        msg_lower = user_message.lower()
        
        bot_response = ""
        media_url = None
        media_type = None
        
        days_bn = {
            'Saturday': 'শনিবার', 'Sunday': 'রবিবার', 'Monday': 'সোমবার',
            'Tuesday': 'মঙ্গলবার', 'Wednesday': 'বুধবার', 'Thursday': 'বৃহস্পতিবার', 'Friday': 'শুক্রবার'
        }
        
        if "কেমন আছ" in msg_lower or "how are you" in msg_lower:
            bot_response = "আলহামদুলিল্লাহ, আমি একদম ভালো আছি!"
        elif "খাওয়া" in msg_lower or "খাওয়া" in msg_lower:
            bot_response = "হ্যাঁ ভাই, খাওয়া দাওয়া হয়েছে।"
        elif "কে তুমি" in msg_lower or "who are you" in msg_lower:
            bot_response = "আমি আপনার পার্সোনাল স্টোরেজ ও অ্যাসিস্ট্যান্ট।"
        elif "কয়টা বাজে" in msg_lower or "কয়টা" in msg_lower or "সময়" in msg_lower:
            current_time = datetime.now().strftime('%I:%M %p')
            bot_response = f"এখন সময় প্রায় {current_time}।"
        elif "বার" in msg_lower or "তারিখ" in msg_lower:
            current_day_en = datetime.now().strftime('%A')
            current_day_bn = days_bn.get(current_day_en, current_day_en)
            current_date = datetime.now().strftime('%d-%m-%Y')
            bot_response = f"আজ হলো {current_day_bn}, তারিখ {current_date}।"
        elif "ছবি" in msg_lower or "photo" in msg_lower:
            photos = os.listdir(PHOTO_DIR) if os.path.exists(PHOTO_DIR) else []
            photos = [f for f in photos if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
            if photos:
                selected_photo = random.choice(photos)
                bot_response = "আপনার স্টোরেজ ফোল্ডার থেকে একটি ছবি নিচে চ্যাট বক্সে নিয়ে আসা হলো।"
                media_url = f"/media_file/photo/{selected_photo}"
                media_type = "photo"
            else:
                bot_response = "আপনার ছবি ফোল্ডারে কোনো ছবি পাওয়া যায়নি।"
        elif "ভিডিও" in msg_lower or "video" in msg_lower:
            videos = os.listdir(VIDEO_DIR) if os.path.exists(VIDEO_DIR) else []
            videos = [f for f in videos if f.lower().endswith(('.mp4', '.mkv', '.webm', '.avi'))]
            if videos:
                selected_video = random.choice(videos)
                bot_response = "আপনার স্টোরেজ ফোল্ডার থেকে একটি ভিডিও নিচে চ্যাট বক্সে প্লে করা হলো।"
                media_url = f"/media_file/video/{selected_video}"
                media_type = "video"
            else:
                bot_response = "আপনার ভিডিও ফোল্ডারে কোনো ভিডিও পাওয়া যায়নি।"
        else:
            bot_response = "আপনার কথাটি বুঝতে পেরেছি। আপনি চাইলে চ্যাট বক্সে 'ছবি' বা 'ভিডিও' লিখে পাঠাতে পারেন।"
        
        return jsonify({
            "status": "success",
            "received_message": user_message,
            "response_message": bot_response,
            "media_url": media_url,
            "media_type": media_type
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)