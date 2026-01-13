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
            .delete-btn:hover { background: #ff0000; color: #fff; }
            .download-btn { color: #00ff41; cursor: pointer; text-decoration: none; border: 1px solid #00ff41; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; margin-left: 10px; }
            .restore-btn { color: #00ff41; cursor: pointer; border: 1px solid #00ff41; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; margin-left: 10px; background: none; }

            #status { background: #111; padding: 10px; border-left: 5px solid #00ff41; margin-top: 10px; font-size: 0.85rem; color: #fff; }
            .pass-area { border: 2px solid #ff0000; padding: 15px; margin-top: 20px; }
            #burnedList { margin-top: 10px; padding: 10px; border: 1px dashed #444; display: none; }
            .burned-item { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; border-bottom: 1px solid #222; }
            .upload-box { margin-top: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>> SECURITY_STATION_V12</h2>

            <div class="box">
                <strong>[ ACTIVE PADS ]</strong>
                <div id="otpList"></div>
                <button onclick="api('/generate', {length:500})">GENERATE MANUAL PAD</button>
                <div class="upload-box">
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
            function setPad(name) {
                document.getElementById('fn').value = name;
            }

            async function refresh() {
                try {
                    const r = await fetch('/list_otps');
                    const d = await r.json();
                    const listDiv = document.getElementById('otpList');
                    listDiv.innerHTML = "";
                    if (d.otps) {
                        d.otps.forEach(otpName => {
                            const item = document.createElement('div');
                            item.className = 'otp-item';
                            item.innerHTML = `
                                <span class="otp-name" onclick="setPad('${otpName}')">${otpName}</span>
                                <a href="/download/${otpName}" class="download-btn" download>DL</a>
                                <span class="delete-btn" onclick="manualDelete('${otpName}')">X</span>
                            `;
                            listDiv.appendChild(item);
                        });
                        if(d.otps.length === 0) listDiv.innerText = "NO ACTIVE PADS";
                    }
                } catch(e) {
                    console.error("Refresh failed", e);
                }
            }

            async function api(path, body) {
                try {
                    const r = await fetch(path, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(body)
                    });
                    const res = await r.json();
                    document.getElementById('status').innerText = `[${new Date().toLocaleTimeString()}] ${res.message || res.error}`;
                    if(res.result) document.getElementById('msg').value = res.result;
                    refresh();
                    return res;
                } catch(e) {
                    document.getElementById('status').innerText = `[${new Date().toLocaleTimeString()}] Connection error`;
                    return {error: "Connection error"};
                }
            }

            function run(type) {
                api('/'+type, {
                    filename: document.getElementById('fn').value, 
                    text: document.getElementById('msg').value
                });
            }

            function vaultAction(path) {
                const p = document.getElementById('masterPass').value;
                api(path, {password: p});
            }

            async function unlockVault() {
                const p = document.getElementById('masterPass').value;
                const res = await api('/list_burned', {password: p});
                if(res.otps) {
                    const b = document.getElementById('burnedList');
                    b.innerHTML = "<strong>BURNED PADS (Click to autofill):</strong><br>";
                    res.otps.forEach(otpName => {
                        const div = document.createElement('div');
                        div.className = 'burned-item';
                        div.innerHTML = `
                            <span class="otp-name" onclick="setPad('${otpName}')">${otpName}</span>
                            <div>
                                <button onclick="viewFile('${otpName}')" style="display:inline; width:auto; padding:2px 5px; font-size:0.7em; background:#444; color:#fff;">VIEW</button>
                                <button onclick="restorePad('${otpName}')" class="restore-btn">RESTORE</button>
                                <a href="/download_burned/${otpName}?password=${p}" class="download-btn" style="font-size:0.7em;" download>DL</a>
                            </div>
                        `;
                        b.appendChild(div);
                    });
                    if(res.otps.length === 0) b.innerHTML += "NONE";
                    b.style.display = "block";
                }
            }

            async function restorePad(name) {
                const p = document.getElementById('masterPass').value;
                const res = await api('/restore_burned', {password: p, filename: name});
                if(!res.error) {
                    unlockVault();
                }
            }

            async function viewFile(name) {
                const p = document.getElementById('masterPass').value;
                const r = await fetch('/view_burned', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({password: p, filename: name})
                });
                const res = await r.json();
                if(res.content) {
                    alert("Content of " + name + ":\\n" + res.content.substring(0, 500) + (res.content.length > 500 ? "..." : ""));
                } else {
                    alert(res.error || "Error viewing file");
                }
            }

            async function uploadPad() {
                const fileInput = document.getElementById('padUpload');
                if(!fileInput.files[0]) return alert("Select file");
                const formData = new FormData();
                formData.append('file', fileInput.files[0]);
                try {
                    const r = await fetch('/upload_pad', {
                        method: 'POST',
                        body: formData
                    });
                    const res = await r.json();
                    alert(res.message || res.error);
                    refresh();
                } catch(e) { alert("Upload failed"); }
            }

            function manualDelete(filename) {
                const p = document.getElementById('masterPass').value;
                if(!p) return alert("Enter password first!");
                api('/delete_single', {filename: filename, password: p});
            }

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
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({"error": "No filename"}), 400
    filename = secure_filename(file.filename)
    file.save(os.path.join(STORAGE_DIR, filename))
    return jsonify({"message": f"Uploaded {filename}"})

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json(force=True)
        length = int(data.get('length', 500))
        generate_pad_logic(length)
        return jsonify({"message": "Manual pad added."})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/encrypt', methods=['POST'])
def encrypt_route():
    try:
        data = request.get_json(force=True)
        path = get_path(data.get('filename', ''))
        if not os.path.exists(path): return jsonify({"error": "NOT_FOUND"}), 404
        with open(path, "r") as f:
            sheet = f.read().splitlines()
        res = ''
        for i, char in enumerate(data.get('text', '').lower()):
            if char in ALPHABET:
                if i < len(sheet):
                    res += ALPHABET[(ALPHABET.index(char) + int(sheet[i])) % 26]
                else: res += char
            else: res += char
        return jsonify({"message": "ENCRYPTED", "result": res})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/decrypt', methods=['POST'])
def decrypt_route():
    try:
        data = request.get_json(force=True)
        filename = data.get('filename', '')
        src = get_path(filename)
        if not os.path.exists(src): return jsonify({"error": "NOT_FOUND"}), 404
        with open(src, "r") as f:
            sheet = f.read().splitlines()
        res = ''
        for i, char in enumerate(data.get('text', '').lower()):
            if char in ALPHABET:
                if i < len(sheet):
                    res += ALPHABET[(ALPHABET.index(char) - int(sheet[i])) % 26]
                else: res += char
            else: res += char
        
        # Move to burned folder
        dst = get_path(filename, BURNED_DIR)
        shutil.move(src, dst)
        return jsonify({"message": f"DECRYPTED & BURNED {filename}", "result": res})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/delete_single', methods=['POST'])
def delete_single():
    data = request.get_json(force=True)
    if data.get('password') != ADMIN_PASSWORD:
        return jsonify({"error": "DENIED"}), 403
    path = get_path(data.get('filename', ''))
    if os.path.exists(path):
        os.remove(path)
        return jsonify({"message": "Deleted pad."})
    return jsonify({"error": "Not found"}), 404

@app.route('/list_burned', methods=['POST'])
def list_burned():
    data = request.get_json(force=True)
    if data.get('password') != ADMIN_PASSWORD:
        return jsonify({"error": "DENIED"}), 403
    files = [os.path.basename(x) for x in glob.glob(os.path.join(BURNED_DIR, "otp*.txt"))]
    return jsonify({"otps": sorted(files)})

@app.route('/restore_burned', methods=['POST'])
def restore_burned():
    data = request.get_json(force=True)
    if data.get('password') != ADMIN_PASSWORD:
        return jsonify({"error": "DENIED"}), 403
    filename = data.get('filename')
    src = get_path(filename, BURNED_DIR)
    dst = get_path(filename, STORAGE_DIR)
    if os.path.exists(src):
        shutil.move(src, dst)
        return jsonify({"message": "Restored pad."})
    return jsonify({"error": "Not found"}), 404

@app.route('/view_burned', methods=['POST'])
def view_burned():
    data = request.get_json(force=True)
    if data.get('password') != ADMIN_PASSWORD:
        return jsonify({"error": "DENIED"}), 403
    path = get_path(data.get('filename', ''), BURNED_DIR)
    if os.path.exists(path):
        with open(path, "r") as f:
            return jsonify({"content": f.read()})
    return jsonify({"error": "Not found"}), 404

@app.route('/download/<filename>')
def download(filename):
    path = get_path(filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "File not found", 404

@app.route('/download_burned/<filename>')
def download_burned(filename):
    password = request.args.get('password')
    if password != ADMIN_PASSWORD:
        return "Unauthorized", 401
    path = get_path(filename, BURNED_DIR)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "File not found", 404

@app.route('/purge', methods=['POST'])
def purge():
    data = request.get_json(force=True)
    if data.get('password') != ADMIN_PASSWORD:
        return jsonify({"error": "DENIED"}), 403
    for d in [STORAGE_DIR, BURNED_DIR]:
        for f in glob.glob(os.path.join(d, "*")):
            try: os.remove(f)
            except: pass
    return jsonify({"message": "SYSTEM WIPE COMPLETE."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
