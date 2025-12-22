let isRagMode = false; // Default to normal memory chat

const BASE_URL = "https://day1-backend-test.onrender.com";
const WS_BASE_URL = "wss://day1-backend-test.onrender.com";
const MAX_CHARS = 10000;

let socket = null;
let authToken = null;

// 1. LOGIN LOGIC
async function login() {
    const user = document.getElementById("username").value.trim();
    const pass = document.getElementById("password").value.trim();
    const err = document.getElementById("login-error");

    try {
        const res = await fetch(`${BASE_URL}/api/v1/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username: user, password: pass })
        });

        if (!res.ok) throw new Error("Invalid Auth");

        const data = await res.json();
        authToken = data.token;

        document.getElementById("login-box").style.display = "none";
        document.getElementById("chat-box").style.display = "block";
        connectWebSocket();
    } catch (e) {
        err.innerText = "Login failed. Check your credentials.";
    }
}

// 2. KNOWLEDGE BASE MODAL LOGIC
function toggleModal(show) {
    document.getElementById("upload-modal").style.display = show ? "flex" : "none";
}

function updateCharCount() {
    const input = document.getElementById('text-block-input');
    const countDisp = document.getElementById('char-count');
    const len = input.value.length;
    
    countDisp.innerText = `${len.toLocaleString()} / ${MAX_CHARS.toLocaleString()}`;
    if (len > MAX_CHARS * 0.9) countDisp.classList.add('warning');
    else countDisp.classList.remove('warning');
}

async function uploadTextBlock() {
    const content = document.getElementById('text-block-input').value.trim();
    const status = document.getElementById('upload-status');
    const badge = document.getElementById('kb-badge');
    const progressWrapper = document.getElementById('progress-wrapper');
    const progressBar = document.getElementById('progress-bar');
    const btn = document.getElementById('process-btn');

    if (!content) return (status.innerText = "⚠️ Text is empty");

    btn.disabled = true;
    status.innerText = "Vectorizing...";
    progressWrapper.style.display = "block";
    progressBar.style.width = "40%";

    try {
        const res = await fetch(`${BASE_URL}/api/v1/essays/upload-text`, {
            method: "POST",
            headers: { 
                "Authorization": `Bearer ${authToken}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ content: content })
        });

        if (res.ok) {
            progressBar.style.width = "100%";
            status.innerText = "✅ Knowledge Updated";
            badge.innerText = "Knowledge Active";
            badge.style.background = "#c6f6d5";
            badge.style.color = "#22543d";
            
            setTimeout(() => {
                toggleModal(false);
                progressWrapper.style.display = "none";
                progressBar.style.width = "0%";
                document.getElementById('text-block-input').value = "";
            }, 1200);
            
            addSystemMessage("AI knowledge base successfully updated.");
        } else {
            throw new Error();
        }
    } catch (e) {
        status.innerText = "❌ Error processing text";
        progressBar.style.background = "#fc8181";
    } finally {
        btn.disabled = false;
    }
}

// 3. CHAT LOGIC
function connectWebSocket() {
    socket = new WebSocket(`${WS_BASE_URL}/api/v1/ai/chat?token=${authToken}`);

    socket.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        const container = document.getElementById("messages");
        container.innerHTML += `
            <div class="log">
                <div style="font-size:10px; color:#a0aec0; margin-bottom:5px;">${msg.timestamp}</div>
                <b>You:</b> ${msg.query}<br>
                <div style="margin-top:8px;"><b>AI:</b> ${msg.data}</div>
            </div>`;
        container.scrollTop = container.scrollHeight;
    };
}

function sendMessage() {
    const input = document.getElementById("message-input");
    if (!socket || !input.value.trim()) return;

    // We send a 'mode' flag so the backend knows whether to look in Qdrant
    const payload = {
        data: input.value,
        mode: isRagMode ? "rag" : "context" 
    };

    socket.send(JSON.stringify(payload));
    input.value = "";
}

function addSystemMessage(text) {
    const container = document.getElementById("messages");
    container.innerHTML += `<div style="text-align:center; font-size:11px; margin:15px 0; color:#cbd5e0;"><i>${text}</i></div>`;
}

function clearLogs() { document.getElementById("messages").innerHTML = ""; }
function handleKeyPress(e) { if (e.key === 'Enter') sendMessage(); }