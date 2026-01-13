import secrets
import os
import glob
import shutil
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)
ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
ADMIN_PASSWORD = "admin"

# Setup directories
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
        <title>OTP STATION</title>
        <style>
            body { font-family: monospace; background: #050505; color: #00ff41; padding: 20px; }
            .container { max-width: 600px; margin: auto; border: 1px solid #00ff41; padding: 20px; }
            .box { border: 1px solid #004400; padding: 15px; margin: 15px 0; }
            textarea, input { width: 100%; background: #000; color: #00ff41; border: 1px solid #00ff41; padding: 10px; box-sizing: border-box; margin: 5px 0; }
            button { background: #00ff41; color: #000; border: none; padding: 10px; cursor: pointer; font-weight: bold; width: 100%; margin-top: 5px; }
            .burn-btn { background: #ff0000; color: #fff; }
            .otp-item { display: flex; justify-content: space-between; border-bottom: 1px solid #004400; padding: 5px 0; }
            #status { background: #111; padding: 10px; margin-top: 10px; border-left: 3px solid #00ff41; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>> OTP_SYSTEM_RESTORED</h2>
            <div class="box">
                <strong>ACTIVE PADS</strong>
                <div id="otpList"></div>
                <button onclick="api('/generate', {length:500})">GENERATE NEW PAD</button>
            </div>
            <div class="box">
                <input type="text" id="fn" placeholder="Pad Filename (otp0.txt)">
                <textarea id="msg" rows="5" placeholder="Message..."></textarea>
                <button onclick="run('encrypt')">ENCRYPT</button>
                <button class="burn-btn" onclick="run('decrypt')">DECRYPT & BURN</button>
            </div>
            <div id="status">STATUS: ONLINE</div>
        </div>
        <script>
            async function refresh() {
                const r = await fetch('/list_otps');
                const d = await r.json();
                const listDiv = document.getElementById('otpList');
                listDiv.innerHTML = d.otps.map(o => `
                    <div class="otp-item">
                        <span onclick="document.getElementById('fn').value='${o}'" style="cursor:pointer">${o}</span>
                    </div>
                `).join('') || 'EMPTY';
            }
            async function api(path, body) {
                const r = await fetch(path, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(body)
                });
                const res = await r.json();
                document.getElementById('status').innerText = `> ${res.message || res.error}`;
                if(res.result) document.getElementById('msg').value = res.result;
                refresh();
            }
            function run(type) {
                api('/'+type, {filename: document.getElementById('fn').value, text: document.getElementById('msg').value});
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

@app.route('/generate', methods=['POST'])
def generate():
    generate_pad_logic()
    return jsonify({"message": "New pad generated."})

@app.route('/encrypt', methods=['POST'])
def encrypt_route():
    data = request.get_json(force=True)
    path = get_path(data.get('filename', ''))
    if not os.path.exists(path): return jsonify({"error": "Pad not found"}), 404
    with open(path, "r") as f:
        sheet = f.read().splitlines()
    res = ''
    for i, char in enumerate(data.get('text', '').lower()):
        if char in ALPHABET and i < len(sheet):
            res += ALPHABET[(ALPHABET.index(char) + int(sheet[i])) % 26]
        else: res += char
    return jsonify({"message": "Encrypted.", "result": res})

@app.route('/decrypt', methods=['POST'])
def decrypt_route():
    data = request.get_json(force=True)
    filename = data.get('filename', '')
    src = get_path(filename)
    if not os.path.exists(src): return jsonify({"error": "Pad not found"}), 404
    with open(src, "r") as f:
        sheet = f.read().splitlines()
    res = ''
    for i, char in enumerate(data.get('text', '').lower()):
        if char in ALPHABET and i < len(sheet):
            res += ALPHABET[(ALPHABET.index(char) - int(sheet[i])) % 26]
        else: res += char
    
    dst = get_path(filename, BURNED_DIR)
    shutil.move(src, dst)
    return jsonify({"message": f"Decrypted. {filename} burned.", "result": res})

if __name__ == '__main__':
    # This block allows Render to assign the correct port
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
