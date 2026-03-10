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

// Web Speech API Initialization
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition;

if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.lang = 'en-IN'; // Default to Indian English for better matching
    recognition.interimResults = false;

    recognition.onstart = () => {
        micBtn.classList.add('listening');
        userInput.placeholder = "Listening...";
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        userInput.value = transcript;
        sendInputCommand(transcript);
    };

    recognition.onerror = (event) => {
        console.error("Speech Recognition Error", event.error);
        micBtn.classList.remove('listening');
        userInput.placeholder = "Try again...";
    };

    recognition.onend = () => {
        micBtn.classList.remove('listening');
        userInput.placeholder = "Say 'Hello Moon' or type a command...";
    };
}

async function triggerVoiceCommand() {
    if (recognition) {
        try {
            recognition.start();
        } catch (e) {
            recognition.stop();
        }
    } else {
        alert("Speech Recognition is not supported in this browser.");
    }
}

// Voice interaction (Manual)
micBtn.addEventListener('click', () => {
    triggerVoiceCommand();
});

async function speakResponse(text) {
    if (isMuted) return;
    
    try {
        const response = await fetch('/api/voice/speak', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });
        const data = await response.json();
        if (data.status === 'success') {
            const audio = new Audio(data.url);
            audio.play();
        }
    } catch (err) {
        console.error("TTS Playback Error", err);
    }
}

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
    if (fingerprintIcon.classList.contains('scanning')) return;
    
    securityStatus.innerText = "AUTHENTICATING...";
    securityStatus.style.color = "var(--primary)";
    fingerprintIcon.classList.remove('error', 'success');
    fingerprintIcon.classList.add('scanning');
    
    try {
        const response = await fetch('/api/security/verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode: 'fingerprint' })
        });
        const data = await response.json();
        
        fingerprintIcon.classList.remove('scanning');
        
        if (data.status === 'unlocked') {
            fingerprintIcon.classList.add('success');
            securityStatus.innerText = "IDENTITY VERIFIED";
            securityStatus.style.color = "#00ff88";
            
            setTimeout(() => {
                onSecuritySuccess(data.user);
            }, 800);
        } else {
            fingerprintIcon.classList.add('error');
            securityStatus.innerText = data.message || "VERIFICATION FAILED";
            securityStatus.style.color = "#ff4444";
        }
    } catch (err) {
        console.error("Verification error:", err);
        fingerprintIcon.classList.remove('scanning');
        fingerprintIcon.classList.add('error');
        securityStatus.innerText = "SENSOR DISCONNECTED";
        securityStatus.style.color = "#ff4444";
    }
});

function onSecuritySuccess(user) {
    lockScreen.classList.add('hidden');
    modeOverlay.classList.remove('hidden');
    container.classList.add('blurred');
    
    // Welcome the user with a special notification
    appendMessage('system', `<strong>Access Granted.</strong> Welcome back, ${user}!`);
    
    // Start auto-lock timer
    resetInactivityTimer();
}

// Security Settings Button (Shortcut in Header)
const securityBtn = document.getElementById('security-btn');
if (securityBtn) {
    securityBtn.addEventListener('click', async () => {
        const password = prompt("Enter Security Password to manage security settings:");
        if (password === "RAM@3511") {
            appendMessage('system', "<strong>Security Settings Access Granted.</strong> You can now manage biometric profiles.");
            // Future logic for managing profiles
        } else if (password !== null) {
            alert("Incorrect password.");
        }
    });
}

// Session Management: Auto-Lock Logic
let inactivityTimer;
const INACTIVITY_LIMIT = 5 * 60 * 1000; // 5 minutes

function resetInactivityTimer() {
    if (lockScreen.classList.contains('hidden')) {
        clearTimeout(inactivityTimer);
        inactivityTimer = setTimeout(lockSystem, INACTIVITY_LIMIT);
    }
}

function lockSystem() {
    appendMessage('system', '<strong>Security:</strong> Session locked due to inactivity.');
    lockScreen.classList.remove('hidden');
    container.classList.add('blurred');
}

// Listen for user activity to reset timer
['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'].forEach(type => {
    document.addEventListener(type, resetInactivityTimer, true);
});

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
            // TTS Playback
            speakResponse(data.response);
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
// System Pulse Dashboard Logic
const pulseBtn = document.getElementById('pulse-btn');
const dashboardModal = document.getElementById('dashboard-modal');
const closeDashboard = document.getElementById('close-dashboard');
let statsInterval;

if (pulseBtn) {
    pulseBtn.addEventListener('click', () => {
        dashboardModal.classList.remove('hidden');
        pulseBtn.classList.add('pulse-active');
        startStatsPolling();
    });
}

if (closeDashboard) {
    closeDashboard.addEventListener('click', () => {
        dashboardModal.classList.add('hidden');
        pulseBtn.classList.remove('pulse-active');
        stopStatsPolling();
    });
}

function startStatsPolling() {
    updateSystemStats(); // Initial call
    statsInterval = setInterval(updateSystemStats, 3000);
}

function stopStatsPolling() {
    clearInterval(statsInterval);
}

async function updateSystemStats() {
    try {
        const response = await fetch('/api/system/stats');
        const data = await response.json();
        
        if (data.status === 'success') {
            const stats = data.stats;
            
            // CPU
            document.getElementById('cpu-val').innerText = `${stats.cpu}%`;
            document.getElementById('cpu-bar').style.width = `${stats.cpu}%`;
            
            // RAM
            document.getElementById('ram-val').innerText = `${stats.ram_used} / ${stats.ram_total} GB`;
            document.getElementById('ram-bar').style.width = `${stats.ram}%`;
            
            // Battery
            if (stats.battery !== null) {
                document.getElementById('battery-val').innerText = `${stats.battery}%`;
                document.getElementById('battery-bar').style.width = `${stats.battery}%`;
                const pluggedEl = document.getElementById('battery-plugged');
                if (stats.battery_plugged) {
                    pluggedEl.innerHTML = `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"></path></svg> CHARGING`;
                    pluggedEl.style.color = "#00ff88";
                } else {
                    pluggedEl.innerHTML = `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="16" height="10" rx="2" ry="2"></rect><line x1="22" y1="11" x2="22" y2="13"></line></svg> DISCHARGING`;
                    pluggedEl.style.color = "rgba(255,255,255,0.5)";
                }
            }
        }
    } catch (err) {
        console.error("Failed to fetch system stats", err);
    }
}
// Help Modal Logic
const helpBtn = document.getElementById('help-btn');
const helpModal = document.getElementById('help-modal');
const closeHelp = document.getElementById('close-help');

if (helpBtn) {
    helpBtn.addEventListener('click', () => {
        helpModal.classList.remove('hidden');
    });
}

if (closeHelp) {
    closeHelp.addEventListener('click', () => {
        helpModal.classList.add('hidden');
    });
}

// Function to copy example commands to input
window.copyCmd = function(cmd) {
    userInput.value = cmd;
    helpModal.classList.add('hidden');
    userInput.focus();
    // Optional: show a small toast or visual feedback
};
