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

@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>EDDIE13S // TERMINAL</title>
        <style>
            :root { --neon-green: #00ff41; --neon-blue: #00f2ff; --matrix-color: #00ff41; --glitch-red: #ff003c; }
            
            /* --- VISUAL CORE --- */
            body { 
                margin: 0; padding: 0; overflow-x: hidden;
                background: #050505; color: var(--neon-green); 
                font-family: 'Courier New', monospace;
                cursor: crosshair; /* Custom Cursor */
            }
            
            canvas#matrix { position: fixed; top: 0; left: 0; z-index: -1; opacity: 0.15; }

            .container { max-width: 800px; margin: 40px auto; position: relative; z-index: 1; }
            
            /* --- GLITCH EFFECT --- */
            .glitch {
                font-size: 2.5rem; font-weight: bold; position: relative; display: inline-block; cursor: pointer;
            }
            .glitch:hover::before {
                content: attr(data-text); position: absolute; left: -2px; text-shadow: 2px 0 var(--glitch-red);
                background: #050505; overflow: hidden; clip: rect(0, 900px, 0, 0);
                animation: noise-1 2s infinite linear alternate-reverse;
            }

            /* --- SYSTEM DASHBOARD --- */
            .dashboard {
                display: flex; justify-content: space-between; background: rgba(0, 255, 65, 0.1);
                border: 1px solid var(--neon-green); padding: 10px; font-size: 0.8rem; margin-bottom: 20px;
            }

            .box { border: 1px solid var(--neon-green); padding: 20px; background: rgba(0,0,0,0.9); margin-bottom: 20px; box-shadow: 0 0 15px rgba(0,255,65,0.2); }
            
            /* --- TERMINAL INPUTS --- */
            textarea, input { 
                width: 100%; background: #000; color: var(--neon-green); 
                border: 1px solid var(--neon-green); padding: 12px; margin: 5px 0; outline: none;
            }
            button { 
                background: var(--neon-green); color: #000; border: none; 
                padding: 10px; font-weight: bold; cursor: pointer; width: 100%; margin: 5px 0;
            }
            button:hover { filter: brightness(1.2); }
            .burn-btn { background: var(--glitch-red); color: #fff; }

            /* --- FIREWALL GRID (LOCKOUT) --- */
            #firewall {
                position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background: repeating-linear-gradient(0deg, transparent, transparent 40px, rgba(255,0,0,0.3) 41px);
                display: none; z-index: 9999; pointer-events: none;
            }

            /* --- ALERTS --- */
            #customAlert {
                position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
                background: #000; border: 2px solid var(--neon-green); padding: 20px;
                display: none; z-index: 10000; text-align: center; box-shadow: 0 0 50px #000;
            }

            @keyframes noise-1 {
                0% { clip: rect(10px, 9999px, 50px, 0); }
                100% { clip: rect(80px, 9999px, 100px, 0); }
            }
            
            .shake { animation: shake 0.5s infinite; }
            @keyframes shake {
                0% { transform: translate(1px, 1px); }
                20% { transform: translate(-3px, 0px); }
                100% { transform: translate(1px, -2px); }
            }
        </style>
    </head>
    <body>
        <canvas id="matrix"></canvas>
        <div id="firewall"></div>
        
        <div id="customAlert">
            <div id="alertMsg">SYSTEM_ALERT</div>
            <button onclick="closeAlert()" style="width: 80px; margin-top: 15px;">OK</button>
        </div>

        <div class="container">
            <div class="dashboard">
                <span>ENCRYPTION: ACTIVE</span>
                <span id="liveClock">00:00:00</span>
                <span>IP: <span id="userIp">FETCHING...</span></span>
            </div>

            <h1 class="glitch" data-text="EDDIE13S" onmouseover="this.innerText='EDDIE13S'" onmouseout="this.innerText='EDDIE13S'">EDDIE13S</h1>
            
            <div id="terminal-bio" style="margin-bottom: 20px; color: var(--neon-blue);"></div>

            <div class="box">
                <strong>[ SCANNING PORTS... ]</strong>
                <div id="portScanner" style="font-size: 0.7rem; color: #555;"></div>
            </div>

            <div class="box">
                <strong>ACTIVE PADS</strong>
                <div id="otpList"></div>
                <input type="text" id="fn" placeholder="COMMAND / FILENAME" oninput="checkFirewall(this.value)">
                <textarea id="msg" rows="4" placeholder="Input payload..."></textarea>
                <button onclick="run('encrypt')">ENCRYPT</button>
                <button class="burn-btn" onclick="run('decrypt')">DECRYPT & BURN</button>
            </div>

            <div id="adminGate" style="display:none;" class="box">
                <strong style="color: var(--glitch-red);">[ ADMIN ACCESS GRANTED ]</strong>
                <input type="password" id="masterPass" placeholder="ADMIN PASS">
                <button class="burn-btn" onclick="selfDestruct()">SELF DESTRUCT</button>
                <button onclick="exportCore()">EXPORT CORE (INDEX.HTML)</button>
            </div>
            
            <div id="status">> SYSTEM READY</div>
        </div>

        <script>
            // --- MATRIX RAIN ---
            const canvas = document.getElementById('matrix');
            const ctx = canvas.getContext('2d');
            canvas.width = window.innerWidth; canvas.height = window.innerHeight;
            const letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$+-*/=%\"'#&_(),.;:?!\\|{}<>[]^~";
            const fontSize = 16; const columns = canvas.width / fontSize;
            const drops = Array(Math.floor(columns)).fill(1);

            function drawMatrix() {
                ctx.fillStyle = "rgba(0, 0, 0, 0.05)"; ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = "#00ff41"; ctx.font = fontSize + "px monospace";
                for (let i = 0; i < drops.length; i++) {
                    const text = letters.charAt(Math.floor(Math.random() * letters.length));
                    ctx.fillText(text, i * fontSize, drops[i] * fontSize);
                    if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) drops[i] = 0;
                    drops[i]++;
                }
            }
            setInterval(drawMatrix, 33);

            // --- TERMINAL TYPER ---
            const bio = "Initializing secure node... Connection established... User: Eddie13s... Status: Elite.";
            let bioIdx = 0;
            function typeBio() {
                if(bioIdx < bio.length) {
                    document.getElementById('terminal-bio').innerHTML += bio.charAt(bioIdx);
                    bioIdx++; setTimeout(typeBio, 50);
                }
            }
            typeBio();

            // --- LIVE CLOCK & IP ---
            setInterval(() => {
                document.getElementById('liveClock').innerText = new Date().toLocaleTimeString();
            }, 1000);

            fetch('https://api.ipify.org?format=json').then(r => r.json()).then(d => {
                document.getElementById('userIp').innerText = d.ip;
            });

            // --- FIREWALL LOGIC ---
            function checkFirewall(val) {
                const forbidden = ['hack', 'root', 'exploit', 'admin'];
                if(forbidden.includes(val.toLowerCase())) {
                    document.getElementById('firewall').style.display = 'block';
                    if(val.toLowerCase() === 'admin') document.getElementById('adminGate').style.display = 'block';
                } else {
                    document.getElementById('firewall').style.display = 'none';
                }
            }

            // --- CUSTOM ALERTS ---
            function showAlert(msg) {
                document.getElementById('alertMsg').innerText = "> " + msg;
                document.getElementById('customAlert').style.display = 'block';
            }
            function closeAlert() { document.getElementById('customAlert').style.display = 'none'; }

            // --- SELF DESTRUCT ---
            function selfDestruct() {
                document.body.classList.add('shake');
                showAlert("KERNEL PANIC: WIPING DATA...");
                setTimeout(() => { location.reload(); }, 3000);
            }

            // --- PORT SCANNER SIM ---
            const ports = [22, 80, 443, 3000, 8080];
            setInterval(() => {
                const p = ports[Math.floor(Math.random()*ports.length)];
                document.getElementById('portScanner').innerText = `PROBING PORT ${p}... [SECURE]`;
            }, 2000);

            // --- EXPORT CORE ---
            function exportCore() {
                const html = document.documentElement.outerHTML;
                const blob = new Blob([html], {type: 'text/html'});
                const a = document.createElement('a');
                a.href = URL.createObjectURL(blob);
                a.download = 'eddie13s_core.html';
                a.click();
            }

            // (Keep your existing API and Refresh functions here)
            async function refresh() {
                const r = await fetch('/list_otps');
                const d = await r.json();
                document.getElementById('otpList').innerHTML = d.otps.map(o => `<div class="otp-item">${o}</div>`).join('') || "NO ACTIVE PADS";
            }
            refresh();
        </script>
    </body>
    </html>
    ''')

# (Include all your existing Flask routes from V12 here: /list_otps, /encrypt, /decrypt, etc.)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
