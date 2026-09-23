from flask import Flask, request, jsonify, render_template, render_template_string, send_from_directory
import os
import random
import base64
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

# লোকাল ফোল্ডার পাথ
BASE_MEDIA_DIR = os.path.abspath("Ai_Rubel_Media")
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
        target_img = bg_files[0] if bg_files else next((f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png'))), None)
        
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
</head>
<body>
    <h1>AI Rubel Server is Running</h1>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(CHAT_TEMPLATE, bg_url=get_bg_url())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
