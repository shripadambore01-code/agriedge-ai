// AgriVoice Frontend Logic

const netStatusBadge = document.getElementById("netStatusBadge");
const netStatusText = document.getElementById("netStatusText");
const smartModeSelect = document.getElementById("smartModeSelect");
const messagesContainer = document.getElementById("messagesContainer");
const processingBar = document.getElementById("processingBar");
const processingText = document.getElementById("processingText");
const chatForm = document.getElementById("chatForm");
const textQueryInput = document.getElementById("textQueryInput");
const micButton = document.getElementById("micButton");
const micStatus = document.getElementById("micStatus");
const audioPlayer = document.getElementById("audioPlayer");

let isRecording = false;
let mediaRecorder = null;
let audioChunks = [];

// 1. Live System Status Polling
async function checkSystemStatus() {
    try {
        const res = await fetch("/api/status");
        if (!res.ok) throw new Error("Status failed");
        const data = await res.json();

        const dot = netStatusBadge.querySelector(".dot");
        dot.className = "dot " + (data.internet_connected ? "online" : "offline");
        netStatusText.textContent = data.internet_connected ? "🌐 Online" : "🔴 Offline";
    } catch (e) {
        const dot = netStatusBadge.querySelector(".dot");
        dot.className = "dot offline";
        netStatusText.textContent = "🔴 Server / Offline";
    }
}

setInterval(checkSystemStatus, 5000);
checkSystemStatus();

// 2. Mode Change Handler
smartModeSelect.addEventListener("change", async (e) => {
    const newMode = e.target.value;
    const formData = new FormData();
    formData.append("mode", newMode);
    try {
        await fetch("/api/set-mode", { method: "POST", body: formData });
    } catch (err) {
        console.error("Failed to set mode:", err);
    }
});

// 3. Render Message Helper
function appendUserMessage(text) {
    const msgDiv = document.createElement("div");
    msgDiv.className = "message user";
    msgDiv.innerHTML = `<strong>Farmer:</strong> ${text}`;
    messagesContainer.appendChild(msgDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function appendAssistantMessage(data) {
    const msgDiv = document.createElement("div");
    msgDiv.className = "message assistant";

    const isOfflineBrain = data.offline;
    const badgeClass = isOfflineBrain ? "local" : "cloud";
    const badgeIcon = isOfflineBrain ? "fa-microchip" : "fa-cloud";

    msgDiv.innerHTML = `
        <div class="brain-badge ${badgeClass}">
            <i class="fa-solid ${badgeIcon}"></i>
            <span>Answered by: ${data.brain}</span>
        </div>
        <div class="answer-text">${data.answer}</div>
        ${data.rag_context ? `
            <details class="rag-details">
                <summary><i class="fa-solid fa-database"></i> Local RAG Context (Confidence: ${(data.rag_confidence * 100).toFixed(0)}%)</summary>
                <pre>${data.rag_context}</pre>
            </details>
        ` : ""}
    `;

    messagesContainer.appendChild(msgDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    // Play synthesized voice output
    if (data.audio_url) {
        audioPlayer.src = data.audio_url;
        audioPlayer.play().catch(e => console.log("Audio autoplay prevented:", e));
    }
}

// 4. Text Query Submission
chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const query = textQueryInput.value.trim();
    if (!query) return;

    appendUserMessage(query);
    textQueryInput.value = "";

    processingBar.classList.remove("hidden");
    processingText.textContent = "Analyzing query with RAG & Brain router...";

    try {
        const res = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: query, mode: smartModeSelect.value })
        });

        if (!res.ok) throw new Error("API request failed");
        const data = await res.json();
        appendAssistantMessage(data);
    } catch (err) {
        appendAssistantMessage({
            brain: "System Error Handler",
            offline: true,
            answer: `Sorry, there was an issue processing your request: ${err.message}`,
            rag_context: ""
        });
    } finally {
        processingBar.classList.add("hidden");
    }
});

// 5. Voice Recording & Offline STT Handling
micButton.addEventListener("click", async () => {
    if (!isRecording) {
        // Start recording
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) audioChunks.push(event.data);
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
                await sendVoiceQuery(audioBlob);
                stream.getTracks().forEach(track => track.stop());
            };

            mediaRecorder.start();
            isRecording = true;
            micButton.classList.add("recording");
            micStatus.textContent = "Listening... Tap to stop";
        } catch (err) {
            console.error("Microphone error:", err);
            alert("Could not access microphone. Please check permissions or type your question.");
        }
    } else {
        // Stop recording
        if (mediaRecorder && mediaRecorder.state !== "inactive") {
            mediaRecorder.stop();
        }
        isRecording = false;
        micButton.classList.remove("recording");
        micStatus.textContent = "Tap microphone to speak";
    }
});

async function sendVoiceQuery(audioBlob) {
    processingBar.classList.remove("hidden");
    processingText.textContent = "Transcribing voice offline with Whisper...";

    const formData = new FormData();
    formData.append("audio_file", audioBlob, "voice_input.wav");
    formData.append("mode", smartModeSelect.value);

    try {
        const res = await fetch("/api/voice", {
            method: "POST",
            body: formData
        });

        if (!res.ok) throw new Error("Voice API request failed");
        const data = await res.json();
        appendUserMessage(data.transcription);
        appendAssistantMessage(data);
    } catch (err) {
        appendAssistantMessage({
            brain: "Offline Voice Handler",
            offline: true,
            answer: `Voice processing error: ${err.message}`,
            rag_context: ""
        });
    } finally {
        processingBar.classList.add("hidden");
    }
}
