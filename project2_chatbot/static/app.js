let sessionId = crypto.randomUUID ? crypto.randomUUID() : Date.now().toString();
const API = '';

async function sendMessage() {
    const input = document.getElementById('userInput');
    const msg = input.value.trim();
    if (!msg) return;
    input.value = '';
    
    // Add user message to UI
    addMessage('user', msg);
    
    // Prepare bot message container for streaming
    const botMsgId = 'msg-' + Date.now();
    addStreamingMessageContainer(botMsgId);
    
    // Connect to SSE stream endpoint
    const url = `${API}/api/chat/stream?message=${encodeURIComponent(msg)}&session_id=${sessionId}`;
    const source = new EventSource(url);
    
    let fullText = "";
    
    source.onmessage = function(event) {
        if (event.data === "[DONE]") {
            source.close();
            // Once stream is done, we can optionally add the final meta tags if we had them.
            // For now, the category is hardcoded in the final render.
            return;
        }
        
        try {
            const data = JSON.parse(event.data);
            fullText += data.chunk;
            updateStreamingMessage(botMsgId, fullText);
        } catch (e) {
            console.error("Stream parse error:", e);
        }
    };
    
    source.onerror = function(event) {
        source.close();
        if (fullText === "") {
             updateStreamingMessage(botMsgId, "Error connecting to AI service.");
        }
    };
}

function addStreamingMessageContainer(id) {
    const container = document.getElementById('chatMessages');
    const div = document.createElement('div');
    div.className = `message bot`;
    div.id = id;
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    // Initial empty state with blinking cursor
    div.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content">
            <div class="message-header">
                <span class="time">${time}</span>
            </div>
            <div class="markdown-body" id="${id}-content"><span class="cursor">▋</span></div>
            <div class="meta">📂 Generative AI &bull; <span class="method-tag">GEMINI</span></div>
        </div>`;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function updateStreamingMessage(id, text) {
    const contentDiv = document.getElementById(`${id}-content`);
    if (contentDiv) {
        const safeText = text.replace(/`/g, '\\`').replace(/'/g, "\\'");
        
        // Add copy button to header now that we have text (if it's not there yet)
        const msgDiv = document.getElementById(id);
        const headerDiv = msgDiv.querySelector('.message-header');
        if (!headerDiv.querySelector('.btn-copy')) {
            headerDiv.innerHTML += `<button class="btn-copy" onclick="copyText(this, \`${safeText}\`)">📋 Copy</button>`;
        } else {
             // Update the copy button's text argument as it streams
             headerDiv.querySelector('.btn-copy').setAttribute('onclick', `copyText(this, \`${safeText}\`)`);
        }
        
        contentDiv.innerHTML = marked.parse(text) + '<span class="cursor">▋</span>';
        
        // Auto scroll
        const container = document.getElementById('chatMessages');
        container.scrollTop = container.scrollHeight;
    }
}

function addMessage(role, text, meta) {
    const container = document.getElementById('chatMessages');
    const div = document.createElement('div');
    div.className = `message ${role}`;
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    let metaHTML = '';
    
    // Only show meta if it's bot and not fallback/error
    if (meta && meta.category && role === 'bot' && meta.category !== 'Error' && meta.category !== 'System') {
        metaHTML = `<div class="meta">📂 ${meta.category} &bull; <span class="method-tag">${meta.method.toUpperCase()}</span></div>`;
    }
    
    if (role === 'bot') {
        const safeText = text.replace(/`/g, '\\`').replace(/'/g, "\\'"); // escape for onclick
        const htmlText = marked.parse(text); // render markdown
        
        div.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="message-content">
                <div class="message-header">
                    <span class="time">${time}</span>
                    <button class="btn-copy" onclick="copyText(this, \`${safeText}\`)">📋 Copy</button>
                </div>
                <div class="markdown-body">${htmlText}</div>
                ${metaHTML}
            </div>`;
    } else {
        div.innerHTML = `<div class="message-content"><p>${text}</p><span class="time">${time}</span></div>`;
    }
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function copyText(btn, text) {
    navigator.clipboard.writeText(text).then(() => {
        const originalText = btn.innerHTML;
        btn.innerHTML = "✅ Copied";
        setTimeout(() => { btn.innerHTML = originalText; }, 2000);
    }).catch(err => {
        console.error('Failed to copy: ', err);
    });
}

function showTyping() {
    const container = document.getElementById('chatMessages');
    const div = document.createElement('div');
    div.className = 'message bot typing-indicator';
    div.id = 'typingIndicator';
    div.innerHTML = '<div class="message-avatar">🤖</div><div class="message-content"><div class="dots"><span></span><span></span><span></span></div></div>';
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function removeTyping() {
    const el = document.getElementById('typingIndicator');
    if (el) el.remove();
}

async function loadSuggestions() {
    try {
        const res = await fetch(`${API}/api/suggestions`);
        const data = await res.json();
        const el = document.getElementById('suggestions');
        el.innerHTML = data.suggestions.map(s =>
            `<button class="suggestion-btn" onclick="askSuggestion('${s}')">${s}</button>`
        ).join('');
    } catch (e) { console.error(e); }
}

function askSuggestion(text) {
    document.getElementById('userInput').value = text;
    sendMessage();
    document.getElementById('suggestions').innerHTML = '';
}

async function saveSession() {
    try {
        const res = await fetch(`${API}/api/save-session`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
        });
        const data = await res.json();
        alert("Success: Chat session has been permanently saved to AWS S3 Cloud Storage!");
    } catch (e) { alert('Save failed.'); }
}

async function loadCloudStatus() {
    try {
        const res = await fetch(`${API}/api/cloud/status`);
        const data = await res.json();
        document.getElementById('cloudMode').textContent = data.mode;
    } catch (e) { }
}

loadSuggestions();
loadCloudStatus();
document.getElementById('userInput').focus();

// === Voice Input (Web Speech API) ===
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition;
let isRecording = false;

if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.lang = 'en-US';
    
    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        document.getElementById('userInput').value = transcript;
        sendMessage();
    };
    
    recognition.onend = function() {
        isRecording = false;
        document.getElementById('btnMic').classList.remove('recording');
    };
    
    recognition.onerror = function(event) {
        isRecording = false;
        document.getElementById('btnMic').classList.remove('recording');
        if(event.error !== 'no-speech') {
            console.error("Speech recognition error", event.error);
            alert("Microphone error: " + event.error);
        }
    };
}

function toggleVoice() {
    if (!SpeechRecognition) {
        alert("Sorry, your browser doesn't support Voice Input. Please use Google Chrome or Microsoft Edge.");
        return;
    }
    
    if (isRecording) {
        recognition.stop();
        isRecording = false;
        document.getElementById('btnMic').classList.remove('recording');
    } else {
        recognition.start();
        isRecording = true;
        document.getElementById('btnMic').classList.add('recording');
    }
}
