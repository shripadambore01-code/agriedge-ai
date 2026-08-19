// AgriVoice Field Voice Assistant Logic

const netStatusPill = document.getElementById("netStatusPill");
const netStatusLabel = document.getElementById("netStatusLabel");
const smartModeSelect = document.getElementById("smartModeSelect");
const messagesContainer = document.getElementById("messagesContainer");
const processingBar = document.getElementById("processingBar");
const processingText = document.getElementById("processingText");
const chatForm = document.getElementById("chatForm");
const textQueryInput = document.getElementById("textQueryInput");
const micButton = document.getElementById("micButton");
const micStatusTitle = document.getElementById("micStatusTitle");
const micStatusSubtitle = document.getElementById("micStatusSubtitle");
const audioPlayer = document.getElementById("audioPlayer");

let isRecording = false;
let mediaRecorder = null;
let audioChunks = [];

// 1. Live System Status Polling
async function checkSystemStatus() {
    try {
        const res = await fetch("/api/status");
        if (!res.ok) throw new Error("Status error");
        const data = await res.json();

        const dot = netStatusPill.querySelector(".pulse-dot");
        if (data.internet_connected) {
            dot.className = "pulse-dot online";
            netStatusLabel.innerHTML = "Signal: <strong>Connected</strong>";
        } else {
            dot.className = "pulse-dot offline";
            netStatusLabel.innerHTML = "Signal: <strong>Offline (Field Mode)</strong>";
        }
    } catch (e) {
        const dot = netStatusPill.querySelector(".pulse-dot");
        dot.className = "pulse-dot offline";
        netStatusLabel.innerHTML = "Signal: <strong>Offline</strong>";
    }
}

setInterval(checkSystemStatus, 6000);
checkSystemStatus();

// 2. Mode Change Handler
smartModeSelect.addEventListener("change", async (e) => {
    const newMode = e.target.value;
    const formData = new FormData();
    formData.append("mode", newMode);
    try {
        await fetch("/api/set-mode", { method: "POST", body: formData });
    } catch (err) {
        console.error("Failed to sync mode:", err);
    }
});

// 3. Quick Action Chips
document.querySelectorAll(".chip-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        const query = btn.getAttribute("data-query");
        if (query) {
            executeTextQuery(query);
        }
    });
});

// 4. Message Rendering Helpers
function appendUserDialogue(text) {
    const card = document.createElement("div");
    card.className = "dialogue-card user-entry";
    card.innerHTML = `
        <strong><i class="fa-solid fa-user"></i> Farmer Inquiry</strong>
        <div>${text}</div>
    `;
    messagesContainer.appendChild(card);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function appendAssistantDialogue(data) {
    const card = document.createElement("div");
    card.className = "dialogue-card assistant-entry";

    const isOfflineBrain = data.offline;
    const badgeClass = isOfflineBrain ? "local" : "cloud";
    const badgeIcon = isOfflineBrain ? "fa-microchip" : "fa-cloud";
    const confidencePct = Math.round((data.rag_confidence || 0) * 100);

    card.innerHTML = `
        <div class="brain-header-bar">
            <div class="brain-badge ${badgeClass}">
                <i class="fa-solid ${badgeIcon}"></i>
                <span>${data.brain}</span>
            </div>
            ${data.audio_url ? `
                <button class="play-voice-btn" onclick="playAudio('${data.audio_url}')">
                    <i class="fa-solid fa-volume-high"></i> Replay Voice
                </button>
            ` : ""}
        </div>

        <div class="answer-body">${data.answer}</div>

        ${data.rag_context ? `
            <details class="rag-accordion">
                <summary>
                    <i class="fa-solid fa-book-bookmark"></i>
                    <span>Local Knowledge Context (Confidence: ${confidencePct}%)</span>
                </summary>
                <div class="rag-content-block">${data.rag_context}</div>
            </details>
        ` : ""}
    `;

    messagesContainer.appendChild(card);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    // Automatically play synthesized speech audio
    if (data.audio_url) {
        playAudio(data.audio_url);
    }
}

function playAudio(url) {
    audioPlayer.src = url;
    audioPlayer.play().catch(e => console.log("Autoplay note:", e));
}

// 5. Text Query Submission
async function executeTextQuery(query) {
    appendUserDialogue(query);
    processingBar.classList.remove("hidden");
    processingText.textContent = "Retrieving local agricultural knowledge...";

    try {
        const res = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: query, mode: smartModeSelect.value })
        });

        if (!res.ok) throw new Error("Server error");
        const data = await res.json();
        appendAssistantDialogue(data);
    } catch (err) {
        appendAssistantDialogue({
            brain: "Offline Safety Fallback",
            offline: true,
            answer: `System notice: Could not complete query (${err.message}). Please ensure server is running.`,
            rag_context: ""
        });
    } finally {
        processingBar.classList.add("hidden");
    }
}

chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const query = textQueryInput.value.trim();
    if (!query) return;
    textQueryInput.value = "";
    executeTextQuery(query);
});

// 6. Voice Recording & Offline STT
micButton.addEventListener("click", async () => {
    if (!isRecording) {
        // Start Audio Recording
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) audioChunks.push(e.data);
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
                await submitVoiceQuery(audioBlob);
                stream.getTracks().forEach(track => track.stop());
            };

            mediaRecorder.start();
            isRecording = true;
            micButton.classList.add("recording");
            micStatusTitle.textContent = "Recording Farmer Question...";
            micStatusSubtitle = "Tap again to finish & process";
        } catch (err) {
            console.error("Microphone permission failed:", err);
            alert("Microphone access is unavailable. You can also type or use Quick Action topics.");
        }
    } else {
        // Stop Audio Recording
        if (mediaRecorder && mediaRecorder.state !== "inactive") {
            mediaRecorder.stop();
        }
        isRecording = false;
        micButton.classList.remove("recording");
        micStatusTitle.textContent = "Press Microphone to Speak";
        micStatusSubtitle.textContent = "Works without internet connection";
    }
});

async function submitVoiceQuery(audioBlob) {
    processingBar.classList.remove("hidden");
    processingText.textContent = "Transcribing voice offline with faster-whisper...";

    const formData = new FormData();
    formData.append("audio_file", audioBlob, "farmer_speech.wav");
    formData.append("mode", smartModeSelect.value);

    try {
        const res = await fetch("/api/voice", {
            method: "POST",
            body: formData
        });

        if (!res.ok) throw new Error("Voice processing error");
        const data = await res.json();
        appendUserDialogue(data.transcription);
        appendAssistantDialogue(data);
    } catch (err) {
        appendAssistantDialogue({
            brain: "Offline Voice Handler",
            offline: true,
            answer: `Voice error: ${err.message}`,
            rag_context: ""
        });
    } finally {
        processingBar.classList.add("hidden");
    }
}
