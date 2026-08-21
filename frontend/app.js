// AgriVoice Field Voice Assistant Logic
// Supports both Local FastAPI Backend and Standalone GitHub Pages Deployment

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
let speechRecognition = null;
let hasBackend = false;

// Embedded Knowledge Base (Ensures 100% Offline / GitHub Pages operation)
const EMBEDDED_AGRI_DB = [
    {
        id: "wheat_yellow_rust",
        topic: "Wheat Disease",
        crop: "Wheat",
        content: "Yellow Rust (Puccinia striiformis) in wheat appears as yellowish-orange powdery stripes or pustules on the upper leaves. In severe cases, it spreads to the leaf sheath and ears. Management: Spray Propiconazole 25% EC @ 1 ml/liter of water or Tebuconazole 25.9% EC @ 1 ml/liter at the first appearance of symptoms. Avoid excessive nitrogen fertilizer and ensure balanced NPK with irrigation.",
        keywords: ["wheat", "yellow rust", "fungus", "propiconazole", "leaves", "disease"]
    },
    {
        id: "rice_blast",
        topic: "Rice Disease",
        crop: "Rice / Paddy",
        content: "Rice Blast (Magnaporthe oryzae) produces spindle-shaped / diamond-shaped lesions with brown borders and grey/white centers on leaves, leaf collars, nodes, and panicles. Management: Seed treatment with Tricyclazole 75% WP @ 2g/kg seed. Foliar spray of Tricyclazole 75% WP @ 0.6g/liter or Isoprothiolane 40% EC @ 1.5 ml/liter when lesions appear on 2-5% of leaves.",
        keywords: ["rice", "paddy", "blast", "tricyclazole", "leaf blast", "neck blast"]
    },
    {
        id: "cotton_pink_bollworm",
        topic: "Cotton Pest",
        crop: "Cotton",
        content: "Pink Bollworm (Pectinophora gossypiella) damages squares, flowers, and bolls, causing rosette flowers and premature boll opening. Control: Install Pheromone traps @ 5-8 traps/acre for monitoring. If trap catches exceed 8 moths/day for 3 consecutive days, spray Profenofos 50% EC @ 2 ml/liter or Emamectin Benzoate 5% SG @ 0.4 g/liter. Release Trichogramma parasitoids early in the season.",
        keywords: ["cotton", "pink bollworm", "pest", "pheromone traps", "profenofos", "emamectin"]
    },
    {
        id: "tomato_early_blight",
        topic: "Tomato Disease",
        crop: "Tomato",
        content: "Early Blight (Alternaria solani) causes dark brown circular spots with concentric rings (target board pattern) on older lower leaves. Management: Spray Mancozeb 75% WP @ 2.5 g/liter or Chlorothalonil 75% WP @ 2 g/liter at 10-14 day intervals. Avoid overhead sprinkler irrigation and remove affected lower leaves.",
        keywords: ["tomato", "early blight", "alternaria", "mancozeb", "concentric rings", "leaf spot"]
    },
    {
        id: "soil_nitrogen_deficiency",
        topic: "Soil & Nutrients",
        crop: "General Crops",
        content: "Nitrogen deficiency causes general yellowing (chlorosis) of older lower leaves starting from the leaf tip towards the base (V-shaped pattern in corn/maize), stunted plant growth, and thin stalks. Treatment: Apply Urea (46% N) as top-dressing or spray 1-2% Urea foliar solution for quick recovery. Incorporate green manure crops like dhaincha or sunn hemp.",
        keywords: ["nitrogen", "deficiency", "chlorosis", "yellow leaves", "urea", "fertilizer", "soil"]
    },
    {
        id: "drip_irrigation_guidance",
        topic: "Irrigation",
        crop: "General / Vegetables / Fruits",
        content: "Drip irrigation saves 40-70% water and increases fertilizer efficiency via fertigation. Maintenance: Flush lateral lines every 15 days by opening end caps. Acid wash lines using 0.5-1% Hydrochloric acid or Phosphoric acid if emitters get clogged due to hard water/calcium deposits. Backwash screen and disc filters weekly.",
        keywords: ["irrigation", "drip", "water saving", "fertigation", "clogging", "maintenance"]
    },
    {
        id: "pm_kisan_scheme",
        topic: "Government Scheme",
        crop: "All Farmers",
        content: "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN) provides financial assistance of Rs. 6,000 per year in three equal 4-monthly installments of Rs. 2,000 directly into bank accounts of landholding farmer families via DBT. Registration requires Aadhaar, land ownership records (7/12 extract / RoR), and active bank account linked to Aadhaar with e-KYC completed.",
        keywords: ["pm kisan", "scheme", "subsidy", "6000", "government", "financial aid", "ekyc"]
    },
    {
        id: "pm_fby_crop_insurance",
        topic: "Government Scheme",
        crop: "All Crops",
        content: "Pradhan Mantri Fasal Bima Yojana (PMFBY) covers crop losses caused by non-preventable natural risks (drought, flood, pests, storms). Farmer premium share: 2% for Kharif crops, 1.5% for Rabi food/oilseed crops, and 5% for annual commercial/horticultural crops. Claim notification for localized calamities must be submitted within 72 hours via the Crop Insurance App or toll-free helpline 14447.",
        keywords: ["pmfby", "crop insurance", "drought", "flood", "claim", "premium", "loss compensation"]
    }
];

// 1. Live System Status Polling
async function checkSystemStatus() {
    const dot = netStatusPill.querySelector(".pulse-dot");
    try {
        const res = await fetch("/api/status", { cache: "no-store" });
        if (!res.ok) throw new Error("No backend");
        const data = await res.json();
        hasBackend = true;
        dot.className = "pulse-dot " + (data.internet_connected ? "online" : "offline");
        netStatusLabel.innerHTML = data.internet_connected ? "Signal: <strong>Connected (FastAPI)</strong>" : "Signal: <strong>Offline (Local Engine)</strong>";
    } catch (e) {
        hasBackend = false;
        const isOnline = navigator.onLine;
        dot.className = "pulse-dot " + (isOnline ? "online" : "offline");
        netStatusLabel.innerHTML = isOnline ? "Signal: <strong>Connected (Web Mode)</strong>" : "Signal: <strong>Offline (Field Mode)</strong>";
    }
}

setInterval(checkSystemStatus, 5000);
checkSystemStatus();

// 2. Mode Change Handler
smartModeSelect.addEventListener("change", async (e) => {
    const newMode = e.target.value;
    if (hasBackend) {
        const formData = new FormData();
        formData.append("mode", newMode);
        try {
            await fetch("/api/set-mode", { method: "POST", body: formData });
        } catch (err) {
            console.error("Failed to sync mode:", err);
        }
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
            <button class="play-voice-btn" id="btn_voice_${Date.now()}">
                <i class="fa-solid fa-volume-high"></i> Replay Voice
            </button>
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

    // Attach replay voice button handler
    const replayBtn = card.querySelector(".play-voice-btn");
    if (replayBtn) {
        replayBtn.addEventListener("click", () => {
            speakText(data.answer, data.audio_url);
        });
    }

    // Automatically speak answer
    speakText(data.answer, data.audio_url);
}

// Voice output handler (Piper audio or browser Web Speech fallback)
function speakText(text, audioUrl) {
    if (audioUrl && hasBackend) {
        audioPlayer.src = audioUrl;
        audioPlayer.play().catch(e => {
            console.log("Audio autoplay prevented, using SpeechSynthesis:", e);
            browserSpeak(text);
        });
    } else {
        browserSpeak(text);
    }
}

function browserSpeak(text) {
    if ("speechSynthesis" in window) {
        window.speechSynthesis.cancel();
        // Remove markdown brackets for clean reading
        const cleanText = text.replace(/\[.*?\]/g, "").replace(/\*\*/g, "");
        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.rate = 0.95;
        utterance.pitch = 1.0;
        window.speechSynthesis.speak(utterance);
    }
}

// Local In-Browser RAG Retriever
function localClientRAG(query) {
    const qLower = query.toLowerCase();
    const scored = [];

    for (const doc of EMBEDDED_AGRI_DB) {
        let score = 0;
        const cLower = doc.content.toLowerCase();
        const tLower = doc.topic.toLowerCase();
        const kws = doc.keywords;

        for (const kw of kws) {
            if (qLower.includes(kw.toLowerCase())) score += 4.0;
        }
        if (qLower.includes(doc.crop.toLowerCase())) score += 3.0;
        if (qLower.includes(tLower)) score += 2.5;

        if (score > 0) {
            scored.push({ score, doc });
        }
    }

    scored.sort((a, b) => b.score - a.score);
    const top = scored.slice(0, 2);

    if (!top.length) {
        return {
            context: "No specific local farming record found for this exact query.",
            confidence: 0.1,
            answer: `For your query '${query}', please contact the nearest Krishi Vigyan Kendra (KVK) or call Kisan Call Center at 1800-180-1551.`
        };
    }

    const contextText = top.map((t, idx) => `[Agri Reference ${idx+1} - ${t.doc.topic} (${t.doc.crop}):\n${t.doc.content}]`).join("\n\n");
    const confidence = Math.min(1.0, top[0].score / 6.0);

    const answer = `Based on agricultural recommendations for '${query}':\n\n${contextText}\n\nPlease follow recommended safety equipment and dosage guidelines during spray.`;

    return {
        context: contextText,
        confidence: confidence,
        answer: answer
    };
}

// 5. Text Query Submission
async function executeTextQuery(query) {
    appendUserDialogue(query);
    processingBar.classList.remove("hidden");
    processingText.textContent = "Retrieving agricultural knowledge...";

    if (hasBackend) {
        try {
            const res = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query: query, mode: smartModeSelect.value })
            });

            if (!res.ok) throw new Error("Server error");
            const data = await res.json();
            appendAssistantDialogue(data);
            processingBar.classList.add("hidden");
            return;
        } catch (err) {
            console.log("Backend offline, falling back to embedded browser RAG:", err);
        }
    }

    // Client-side offline fallback
    setTimeout(() => {
        const ragRes = localClientRAG(query);
        appendAssistantDialogue({
            brain: "Local Offline Engine (Embedded RAG)",
            offline: true,
            answer: ragRes.answer,
            rag_context: ragRes.context,
            rag_confidence: ragRes.confidence
        });
        processingBar.classList.add("hidden");
    }, 400);
}

chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const query = textQueryInput.value.trim();
    if (!query) return;
    textQueryInput.value = "";
    executeTextQuery(query);
});

// 6. Voice Recording (Dual: MediaRecorder Audio Upload to /api/voice + WebSpeech STT)
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let audioStream = null;
let recognizedText = "";

if (SpeechRecognition) {
    try {
        speechRecognition = new SpeechRecognition();
        speechRecognition.continuous = false;
        speechRecognition.interimResults = false;
        speechRecognition.lang = "en-IN";

        speechRecognition.onresult = (event) => {
            recognizedText = event.results[0][0].transcript;
        };

        speechRecognition.onerror = (event) => {
            console.log("Speech recognition notice:", event.error);
        };
    } catch (e) {
        console.warn("WebSpeech init warning:", e);
    }
}

async function startVoiceRecording() {
    isRecording = true;
    recognizedText = "";
    audioChunks = [];
    micButton.classList.add("recording");
    micStatusTitle.textContent = "Listening to Farmer...";
    micStatusSubtitle.textContent = "Speak clearly — press again to send";

    if (speechRecognition) {
        try { speechRecognition.start(); } catch (e) {}
    }

    try {
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(audioStream);
            mediaRecorder.ondataavailable = (e) => {
                if (e.data && e.data.size > 0) audioChunks.push(e.data);
            };
            mediaRecorder.onstop = async () => {
                if (audioStream) {
                    audioStream.getTracks().forEach(track => track.stop());
                }
                if (recognizedText.trim()) {
                    executeTextQuery(recognizedText.trim());
                } else if (audioChunks.length > 0 && hasBackend) {
                    const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
                    await executeVoiceUpload(audioBlob);
                } else if (recognizedText.trim()) {
                    executeTextQuery(recognizedText.trim());
                }
            };
            mediaRecorder.start();
        }
    } catch (err) {
        console.warn("Microphone access:", err);
    }
}

function stopVoiceRecording() {
    isRecording = false;
    micButton.classList.remove("recording");
    micStatusTitle.textContent = "Press Microphone to Speak";
    micStatusSubtitle.textContent = "Works with Cloud Voice API & Offline Engine";

    if (speechRecognition) {
        try { speechRecognition.stop(); } catch (e) {}
    }

    if (mediaRecorder && mediaRecorder.state !== "inactive") {
        try { mediaRecorder.stop(); } catch (e) {}
    }
}

async function executeVoiceUpload(audioBlob) {
    processingBar.classList.remove("hidden");
    processingText.textContent = "Processing voice query with AI Speech-to-Text...";

    const formData = new FormData();
    formData.append("audio_file", audioBlob, "farmer_audio.wav");
    formData.append("mode", smartModeSelect.value);

    try {
        const res = await fetch("/api/voice", {
            method: "POST",
            body: formData
        });

        if (!res.ok) throw new Error("Voice API response failed");
        const data = await res.json();
        if (data.transcription) {
            appendUserDialogue(data.transcription);
        }
        appendAssistantDialogue(data);
    } catch (err) {
        console.error("Voice processing error:", err);
        executeTextQuery("How do I protect my crops from common pests?");
    } finally {
        processingBar.classList.add("hidden");
    }
}

micButton.addEventListener("click", () => {
    if (!isRecording) {
        startVoiceRecording();
    } else {
        stopVoiceRecording();
    }
});

