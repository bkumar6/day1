const LOGIN_URL = "https://day1-backend-test.onrender.com/api/v1/auth/login";
const WS_BASE_URL = "wss://day1-backend-test.onrender.com/api/v1/ai/chat";

let socket = null;
let authToken = null;

//login
async function login() {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();
  const errorBox = document.getElementById("login-error");

  errorBox.innerText = "";

  try {
    const res = await fetch(LOGIN_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });

    if (!res.ok) {
      errorBox.innerText = "Invalid credentials";
      return;
    }

    const data = await res.json();
    authToken = data.token;

    document.getElementById("login-box").style.display = "none";
    document.getElementById("chat-box").style.display = "block";

    connectWebSocket();
  } catch (err) {
    errorBox.innerText = "Server error. Try again.";
  }
}

//Websocket
function connectWebSocket() {
  socket = new WebSocket(`${WS_BASE_URL}?token=${authToken}`);

  socket.onopen = () => {
    addSystemMessage("Connected to AI");
  };

  socket.onmessage = (event) => {
    handleAIResponse(event.data);
  };

  socket.onclose = () => {
    addSystemMessage("Disconnected");
  };

  socket.onerror = () => {
    addSystemMessage("WebSocket error");
  };
}

//Send meesage
function sendMessage() {
  if (!socket || socket.readyState !== WebSocket.OPEN) return;

  const input = document.getElementById("message-input");
  const message = input.value.trim();

  if (!message) return;

  // Backend expects json
  socket.send(JSON.stringify({ data: message }));

  addUserMessage(message);
  input.value = "";
}

//AI response
function handleAIResponse(rawData) {
  let msg;

  try {
    msg = JSON.parse(rawData);
  } catch (e) {
    console.error("Invalid JSON from WebSocket:", rawData);
    return;
  }

  // Backend guarantees these keys
  if (!msg.timestamp || !msg.query || !msg.data) return;

  const messages = document.getElementById("messages");

  messages.innerHTML += `
    <div class="log">
      <div><b>🕒 Time:</b> ${msg.timestamp}</div>
      <div><b>👤 You:</b> ${msg.query}</div>
      <div><b>🤖 AI:</b> ${msg.data}</div>
      <hr />
    </div>
  `;

  messages.scrollTop = messages.scrollHeight;
}

//UI
function addUserMessage(text) {
  const messages = document.getElementById("messages");
  messages.innerHTML += `<div><b>You:</b> ${text}</div>`;
  messages.scrollTop = messages.scrollHeight;
}

function addSystemMessage(text) {
  const messages = document.getElementById("messages");
  messages.innerHTML += `<div><i>${text}</i></div>`;
  messages.scrollTop = messages.scrollHeight;
}
