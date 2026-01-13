import secrets
import os
import glob
import shutil
from flask import Flask, render_template_string, request, jsonify, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)
ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
ADMIN_PASSWORD = "admin"

STORAGE_DIR = os.path.join(os.getcwd(), 'otp_storage')
BURNED_DIR = os.path.join(os.getcwd(), 'burned_otps')

for d in [STORAGE_DIR, BURNED_DIR]:
    if not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

def get_path(filename, dir_path=STORAGE_DIR):
    clean_name = "".join([c for c in filename if c.isalnum() or c in "._-"])
    return os.path.join(dir_path, clean_name)

def generate_pad_logic(length=1000):
    i = 0
    while os.path.exists(get_path(f"otp{i}.txt")): 
        i += 1
    new_filename = f"otp{i}.txt"
    path = get_path(new_filename)
    with open(path, "w") as f:
        for _ in range(length):
            f.write(str(secrets.randbelow(26)) + "\n")
    return new_filename

@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>OTP STATION V12</title>
        <style>
            body { font-family: 'Courier New', monospace; background: #050505; color: #00ff41; padding: 20px; }
            .container { max-width: 650px; margin: auto; border: 2px solid #00ff41; padding: 20px; }
            .box { border: 1px solid #004400; padding: 15px; margin: 15px 0; background: #000; }
            textarea, input { width: 100%; background: #111; color: #00ff41; border: 1px solid #00ff41; padding: 12px; box-sizing: border-box; margin: 5px 0; font-family: inherit; }
            button { background: #00ff41; color: #000; border: none; padding: 10px; cursor: pointer; font-weight: bold; width: 100%; margin-top: 5px; }
            .burn-btn { background: #ff0000; color: #fff; }
            .otp-item { display: flex; justify-content: space-between; align-items: center; background: #111; border: 1px solid #00ff41; padding: 8px; margin: 5px 0; }
            .otp-name { cursor: pointer; flex-grow: 1; }
            .delete-btn { color: #ff0000; cursor: pointer; font-weight: bold; border: 1px solid #ff0000; padding: 2px 8px; border-radius: 4px; margin-left: 10px; }
            .download-btn { color: #00ff41; cursor: pointer; text-decoration: none; border: 1px solid #00ff41; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; margin-left: 10px; }
            .restore-btn { color: #00ff41; cursor: pointer; border: 1px solid #00ff41; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; margin-left: 10px; background: none; }
            #status { background: #111; padding: 10px; border-left: 5px solid #00ff41; margin-top: 10px; font-size: 0.85rem; color: #fff; }
            .pass-area { border: 2px solid #ff0000; padding: 15px; margin-top: 20px; }
            #burnedList { margin-top: 10px; padding: 10px; border: 1px dashed #444; display: none; }
            .burned-item { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; border-bottom: 1px solid #222; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>> SECURITY_STATION_V12</h2>
            <div class="box">
                <strong>[ ACTIVE PADS ]</strong>
                <div id="otpList"></div>
                <button onclick="api('/generate', {length:500})">GENERATE MANUAL PAD</button>
                <div style="margin-top: 10px;">
                    <input type="file" id="padUpload" style="color: #00ff41;">
                    <button onclick="uploadPad()">UPLOAD PAD</button>
                </div>
            </div>
            <div class="box">
                <input type="text" id="fn" placeholder="Pad Filename (otp0.txt)">
                <textarea id="msg" rows="5" placeholder="Message content here..."></textarea>
                <button onclick="run('encrypt')">ENCRYPT</button>
                <button class="burn-btn" onclick="run('decrypt')">DECRYPT & BURN</button>
            </div>
            <div id="status">STATUS: SYSTEM ONLINE</div>
            <div class="pass-area">
                <strong style="color: #ff0000;">MASTER AUTHENTICATION</strong>
                <input type="password" id="masterPass" placeholder="Enter Master password">
                <div style="display:flex; gap:10px;">
                    <button style="background:#444; color:#fff;" onclick="unlockVault()">VIEW BURNED</button>
                    <button class="burn-btn" onclick="vaultAction('/purge')">NUCLEAR PURGE</button>
                </div>
                <div id="burnedList"></div>
            </div>
        </div>
        <script>
            function setPad(name) { document.getElementById('fn').value = name; }
            async function refresh() {
                const r = await fetch('/list_otps');
                const d = await r.json();
                const listDiv = document.getElementById('otpList');
                listDiv.innerHTML = d.otps.map(o => `
                    <div class="otp-item">
                        <span class="otp-name" onclick="setPad('${o}')">${o}</span>
                        <a href="/download/${o}" class="download-btn" download>DL</a>
                        <span class="delete-btn" onclick="manualDelete('${o}')">X</span>
                    </div>
                `).join('') || "NO ACTIVE PADS";
            }
            async function api(path, body) {
                const r = await fetch(path, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)});
                const res = await r.json();
                document.getElementById('status').innerText = `[${new Date().toLocaleTimeString()}] ${res.message || res.error}`;
                if(res.result) document.getElementById('msg').value = res.result;
                refresh();
                return res;
            }
            function run(type) { api('/'+type, {filename: document.getElementById('fn').value, text: document.getElementById('msg').value}); }
            function vaultAction(path) { api(path, {password: document.getElementById('masterPass').value}); }
            async function unlockVault() {
                const p = document.getElementById('masterPass').value;
                const res = await api('/list_burned', {password: p});
                if(res.otps) {
                    const b = document.getElementById('burnedList');
                    b.innerHTML = "<strong>BURNED PADS:</strong><br>" + res.otps.map(o => `
                        <div class="burned-item">
                            <span>${o}</span>
                            <div>
                                <button onclick="restorePad('${o}')" class="restore-btn">RESTORE</button>
                            </div>
                        </div>
                    `).join('') || "NONE";
                    b.style.display = "block";
                }
            }
            async function restorePad(name) {
                await api('/restore_burned', {password: document.getElementById('masterPass').value, filename: name});
                unlockVault();
            }
            async function uploadPad() {
                const fileInput = document.getElementById('padUpload');
                if(!fileInput.files[0]) return alert("Select file");
                const formData = new FormData();
                formData.append('file', fileInput.files[0]);
                const r = await fetch('/upload_pad', {method: 'POST', body: formData});
                const res = await r.json();
                alert(res.message || res.error);
                refresh();
            }
            function manualDelete(filename) { api('/delete_single', {filename: filename, password: document.getElementById('masterPass').value}); }
            refresh();
        </script>
    </body>
    </html>
    ''')

@app.route('/list_otps')
def list_otps():
    files = [os.path.basename(x) for x in glob.glob(os.path.join(STORAGE_DIR, "otp*.txt"))]
    return jsonify({"otps": sorted(files)})

@app.route('/upload_pad', methods=['POST'])
def upload_pad():
    file = request.files['file']
    filename = secure_filename(file.filename)
    file.save(os.path.join(STORAGE_DIR, filename))
    return jsonify({"message": f"Uploaded {filename}"})

@app.route('/encrypt', methods=['POST'])
def encrypt_route():
    data = request.get_json(force=True)
    path = get_path(data.get('filename', ''))
    if not os.path.exists(path): return jsonify({"error": "NOT_FOUND"}), 404
    with open(path, "r") as f: sheet = f.read().splitlines()
    res = ''
    for i, char in enumerate(data.get('text', '').lower()):
        if char in ALPHABET and i < len(sheet): res += ALPHABET[(ALPHABET.index(char) + int(sheet[i])) % 26]
        else: res += char
    return jsonify({"message": "ENCRYPTED", "result": res})

@app.route('/decrypt', methods=['POST'])
def decrypt_route():
    data = request.get_json(force=True)
    filename = data.get('filename', '')
    src = get_path(filename)
    if not os.path.exists(src): return jsonify({"error": "NOT_FOUND"}), 404
    with open(src, "r") as f: sheet = f.read().splitlines()
    res = ''
    for i, char in enumerate(data.get('text', '').lower()):
        if char in ALPHABET and i < len(sheet): res += ALPHABET[(ALPHABET.index(char) - int(sheet[i])) % 26]
        else: res += char
    shutil.move(src, get_path(filename, BURNED_DIR))
    generate_pad_logic() # Auto-replenish
    return jsonify({"message": f"BURNED {filename}. NEW PAD READY.", "result": res})

@app.route('/list_burned', methods=['POST'])
def list_burned():
    if request.get_json(force=True).get('password') != ADMIN_PASSWORD: return jsonify({"error": "DENIED"}), 403
    files = [os.path.basename(x) for x in glob.glob(os.path.join(BURNED_DIR, "otp*.txt"))]
    return jsonify({"otps": sorted(files)})

@app.route('/restore_burned', methods=['POST'])
def restore_burned():
    data = request.get_json(force=True)
    if data.get('password') != ADMIN_PASSWORD: return jsonify({"error": "DENIED"}), 403
    shutil.move(get_path(data.get('filename'), BURNED_DIR), get_path(data.get('filename'), STORAGE_DIR))
    return jsonify({"message": "Restored."})

@app.route('/delete_single', methods=['POST'])
def delete_single():
    data = request.get_json(force=True)
    if data.get('password') != ADMIN_PASSWORD: return jsonify({"error": "DENIED"}), 403
    os.remove(get_path(data.get('filename')))
    return jsonify({"message": "Deleted."})

@app.route('/generate', methods=['POST'])
def generate():
    generate_pad_logic()
    return jsonify({"message": "Generated."})

@app.route('/purge', methods=['POST'])
def purge():
    if request.get_json(force=True).get('password') != ADMIN_PASSWORD: return jsonify({"error": "DENIED"}), 403
    for d in [STORAGE_DIR, BURNED_DIR]:
        for f in glob.glob(os.path.join(d, "*")): os.remove(f)
    return jsonify({"message": "WIPED."})

@app.route('/download/<filename>')
def download(filename):
    return send_file(get_path(filename), as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
