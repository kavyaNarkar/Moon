const chatWindow = document.getElementById('chat-window');
const commandForm = document.getElementById('command-form');
const userInput = document.getElementById('user-input');
const micBtn = document.getElementById('mic-btn');
const modeOverlay = document.getElementById('mode-overlay');
const container = document.querySelector('.container');
const btnVoiceMode = document.getElementById('btn-voice-mode');
const btnManualMode = document.getElementById('btn-manual-mode');
const raaginiBtn = document.getElementById('raagini-btn');
const muteBtn = document.getElementById('mute-btn');
const speakerIcon = document.getElementById('speaker-icon');

// Mute State Management
let isMuted = localStorage.getItem('moon-muted') === 'true';
updateMuteUI();

function updateMuteUI() {
    if (isMuted) {
        muteBtn.classList.add('muted');
        speakerIcon.innerHTML = '<line x1="1" y1="1" x2="23" y2="23"></line><path d="M9 9l-3 3-3-3"></path><path d="M11 5L6 9H2v6h4l5 4V5z"></path>'; // Simple mute icon
        // Better Mute Icon
        speakerIcon.innerHTML = '<polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><line x1="23" y1="9" x2="17" y2="15"></line><line x1="17" y1="9" x2="23" y2="15"></line>';
    } else {
        muteBtn.classList.remove('muted');
        speakerIcon.innerHTML = '<polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>';
    }
}

muteBtn.addEventListener('click', () => {
    isMuted = !isMuted;
    localStorage.setItem('moon-muted', isMuted);
    updateMuteUI();
});

function appendMessage(type, text, id = null) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${type}`;
    if (id) msgDiv.id = id;
    msgDiv.innerHTML = `<p>${text}</p>`;
    chatWindow.appendChild(msgDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

// Mode Selection
function enterMode(mode) {
    modeOverlay.classList.add('hidden');
    container.classList.remove('blurred');
    appendMessage('system', `Switched to <strong>${mode}</strong>.`);
    
    if (mode === 'Voice Mode') {
        startVoiceLifecycle();
    }
}

btnVoiceMode.addEventListener('click', () => enterMode('Voice Mode'));
btnManualMode.addEventListener('click', () => enterMode('Manual Mode'));

if (raaginiBtn) {
    raaginiBtn.addEventListener('click', () => {
        sendInputCommand('open raagini');
    });
}

async function startVoiceLifecycle() {
    while (true) {
        try {
            // Wait for Wake Word
            const response = await fetch('/api/wake_word', { method: 'POST' });
            const data = await response.json();
            
            if (data.status === 'detected') {
                await triggerVoiceCommand();
            }
        } catch (e) {
            console.error("Voice lifecycle error", e);
            break;
        }
    }
}

async function triggerVoiceCommand() {
    micBtn.classList.add('listening');
    const thinkingId = 'thinking-' + Date.now();
    appendMessage('system', '<i>Listening...</i>', thinkingId);
    
    try {
        const response = await fetch('/api/voice', { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mute: isMuted })
        });
        const data = await response.json();
        
        if (document.getElementById(thinkingId)) document.getElementById(thinkingId).remove();
        
        if (data.user_text) appendMessage('user', data.user_text);
        if (data.response) appendMessage('system', data.response);
    } catch (error) {
        console.error('Error:', error);
        if (document.getElementById(thinkingId)) document.getElementById(thinkingId).innerHTML = "Error processing voice.";
    } finally {
        micBtn.classList.remove('listening');
    }
}

// Voice interaction (Manual)
micBtn.addEventListener('click', async () => {
    await triggerVoiceCommand();
});

// Security State Management
const lockScreen = document.getElementById('lock-screen');
const securityStatus = document.getElementById('security-status');
const hiddenBypass = document.getElementById('hidden-bypass');
const fingerprintIcon = document.querySelector('.fingerprint-container');

// Hidden Bypass Logic
hiddenBypass.addEventListener('click', async () => {
    const password = prompt("Secret Bypass Entered. Provide Password:");
    if (!password) return;

    try {
        const response = await fetch('/api/security/verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode: 'password', password: password })
        });
        const data = await response.json();
        
        if (data.status === 'unlocked') {
            onSecuritySuccess(data.user);
        } else {
            alert("Bypass Denied: " + data.message);
        }
    } catch (err) {
        console.error("Bypass error:", err);
    }
});

// Fingerprint Simulation Logic
fingerprintIcon.addEventListener('click', async () => {
    securityStatus.innerText = "Scanning Fingerprint...";
    fingerprintIcon.classList.add('scanning');
    
    // Simulate a short delay for scanning effect
    setTimeout(async () => {
        try {
            const response = await fetch('/api/security/verify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mode: 'fingerprint' })
            });
            const data = await response.json();
            
            if (data.status === 'unlocked') {
                onSecuritySuccess(data.user);
            } else {
                securityStatus.innerText = "Fingerprint not recognized.";
                fingerprintIcon.classList.remove('scanning');
            }
        } catch (err) {
            console.error("Verification error:", err);
            securityStatus.innerText = "Sensor Error.";
        }
    }, 1500);
});

function onSecuritySuccess(user) {
    lockScreen.classList.add('hidden');
    modeOverlay.classList.remove('hidden');
    container.classList.add('blurred');
    
    // Welcome the user with a special notification
    appendMessage('system', `<strong>Access Granted.</strong> Welcome back, ${user}!`);
}

// Security Settings Button (Shortcut in Header)
const securityBtn = document.getElementById('security-btn');
if (securityBtn) {
    securityBtn.addEventListener('click', () => {
        const password = prompt("Enter Security Password to manage security settings:");
        if (password === "RAM@3511") {
            appendMessage('system', "<strong>Security Settings:</strong> Logic for biometric management pending sensor driver integration.");
        } else if (password !== null) {
            alert("Incorrect password.");
        }
    });
}

// Contact Management
const contactBtn = document.getElementById('contacts-btn');
const contactModal = document.getElementById('contact-modal');
const closeContactModal = document.getElementById('close-contact-modal');
const contactForm = document.getElementById('contact-form');
const contactsList = document.getElementById('contacts-list');

if (contactBtn) {
    contactBtn.addEventListener('click', () => {
        contactModal.classList.remove('hidden');
        loadContacts();
    });
}

if (closeContactModal) {
    closeContactModal.addEventListener('click', () => {
        contactModal.classList.add('hidden');
    });
}

async function loadContacts() {
    try {
        const response = await fetch('/api/contacts/list');
        const data = await response.json();
        if (data.status === 'success') {
            renderContacts(data.contacts);
        }
    } catch (err) {
        console.error("Failed to load contacts", err);
    }
}

function renderContacts(contacts) {
    contactsList.innerHTML = contacts.length ? '' : '<p style="text-align:center; opacity:0.5;">No contacts saved yet.</p>';
    contacts.forEach(([name, phone]) => {
        const item = document.createElement('div');
        item.className = 'contact-item';
        item.innerHTML = `
            <div class="contact-info">
                <strong>${name.charAt(0).toUpperCase() + name.slice(1)}</strong>
                <span>${phone}</span>
            </div>
        `;
        contactsList.appendChild(item);
    });
}

if (contactForm) {
    contactForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('contact-name').value;
        const phone = document.getElementById('contact-phone').value;
        
        try {
            const response = await fetch('/api/contacts/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, phone })
            });
            const data = await response.json();
            if (data.status === 'success') {
                document.getElementById('contact-name').value = '';
                document.getElementById('contact-phone').value = '';
                loadContacts();
                appendMessage('system', `Contact <strong>${name}</strong> saved.`);
            } else {
                alert("Error: " + data.message);
            }
        } catch (err) {
            console.error("Save contact error:", err);
        }
    });
}

// Text interaction
commandForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const command = userInput.value.trim();
    if (!command) return;
    
    userInput.value = '';
    await sendInputCommand(command);
});

async function sendInputCommand(command) {
    // Display user message
    appendMessage('user', command);

    // Show thinking indicator
    const thinkingId = 'thinking-' + Date.now();
    appendMessage('system', '<span class="status-msg">Waking up brain...</span>', thinkingId);

    // Send to backend
    try {
        const response = await fetch('/api/command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: command, mute: isMuted })
        });

        const data = await response.json();
        
        // Remove thinking indicator
        if (document.getElementById(thinkingId)) {
            document.getElementById(thinkingId).remove();
        }
        
        // Display response
        if (data.response) {
            appendMessage('system', data.response);
        } else {
            appendMessage('system', "I encountered an error processing your command.");
        }
    } catch (error) {
        console.error('Error:', error);
        if (document.getElementById(thinkingId)) {
            document.getElementById(thinkingId).innerHTML = "<b>Connection error.</b> Is the Moon server running?";
        } else {
            appendMessage('system', "Connection error. Is the server running?");
        }
    }
}
