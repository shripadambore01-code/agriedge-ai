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

const languageSelect = document.getElementById("languageSelect");

// 9-Language Localization Dictionary for Field Agriculture
const TRANSLATIONS = {
    en: {
        journey_tag: '🌾 Active Crop Journey',
        modal_profile_title: 'My Farm Profile',
        modal_profile_sub: 'Personalizes all AI advice, growth stages & pest alerts',
        lbl_farm_name: 'Farm / Field Name',
        lbl_farmer_name: 'Farmer Name',
        lbl_location: 'Location (District, State)',
        lbl_farm_size: 'Farm Size (Acres)',
        lbl_soil_type: 'Soil Type',
        lbl_irrigation: 'Irrigation Method',
        lbl_crop: 'Current Crop',
        lbl_variety: 'Variety / Seed Brand',
        lbl_sowing_date: 'Sowing / Planting Date',
        lbl_harvest_date: 'Expected Harvest Date (Optional)',
        btn_cancel: 'Cancel',
        btn_save_profile: 'Save Farm Profile',
        title: "AgriVoice - Farmer Field Voice Assistant",
        version_tag: "v1.0 Offline-First",
        brand_desc: "Voice Advisory System for Field Agriculture",
        rag_index: "RAG Index: <strong>8 Records</strong>",
        lang_label: "Language:",
        engine_label: "Engine:",
        engine_off: "🔒 Offline Default (Llama 3.2 3B)",
        engine_auto: "⚡ Hybrid Auto (Local + Cloud Boost)",
        engine_on: "🌐 Cloud Priority (Gemini Flash)",
        quick_actions: "Field Quick Actions",
        chip_yellow_rust: "Wheat Yellow Rust",
        chip_pink_bollworm: "Cotton Pink Bollworm",
        chip_rice_blast: "Rice Blast Treatment",
        chip_early_blight: "Tomato Early Blight",
        chip_nitrogen: "Nitrogen Deficiency",
        chip_drip: "Drip Maintenance",
        chip_pmkisan: "PM-KISAN Rs 6000 Scheme",
        chip_pmfby: "PMFBY Crop Insurance",
        arch_specs: "Architecture Specs",
        spec_voice_in: "Voice In:",
        spec_retrieval: "Retrieval:",
        spec_local_llm: "Local LLM:",
        spec_cloud_llm: "Cloud LLM:",
        spec_voice_out: "Voice Out:",
        welcome_title: "Farmer Field Assistant Ready",
        welcome_status: "100% Offline Capable • Local RAG Active",
        welcome_desc: "Press the Microphone button below or select a quick topic from the left panel to ask about crop diseases, pest outbreaks, fertilizer dosages, or government welfare schemes.",
        tag_voice_in: "Voice Command",
        tag_reasoning: "Multi-Dialect AI",
        tag_voice_out: "Spoken Audio Out",
        mic_title: "Press Microphone to Speak",
        mic_sub: "Works with Cloud Voice API & Offline Engine",
        mic_listening: "Listening to Farmer...",
        mic_listening_sub: "Speak clearly — press again to send",
        input_placeholder: "Type crop question or pest symptom...",
        send_btn: "Ask Assistant",
        processing_text: "Analyzing query with Agricultural RAG...",
        replay_voice: "Replay Voice",
        farmer_inquiry: "Farmer Inquiry",
        local_context: "Local Knowledge Context",
        confidence: "Confidence",
        signal_fastapi_online: "Signal: <strong>Connected (FastAPI)</strong>",
        signal_fastapi_offline: "Signal: <strong>Offline (Local Engine)</strong>",
        signal_web_online: "Signal: <strong>Connected (Web Mode)</strong>",
        signal_web_offline: "Signal: <strong>Offline (Field Mode)</strong>"
    },
    hi: {
        journey_tag: '🌾 सक्रिय फसल यात्रा',
        modal_profile_title: 'मेरा खेत और फसल प्रोफ़ाइल',
        modal_profile_sub: 'सभी AI सलाह, विकास चरण और कीट चेतावनियों को व्यक्तिगत बनाता है',
        lbl_farm_name: 'खेत / प्लॉट का नाम',
        lbl_farmer_name: 'किसान का नाम',
        lbl_location: 'स्थान (जिला, राज्य)',
        lbl_farm_size: 'खेत का आकार (एकड़)',
        lbl_soil_type: 'मिट्टी का प्रकार',
        lbl_irrigation: 'सिंचाई का साधन',
        lbl_crop: 'वर्तमान फसल',
        lbl_variety: 'किस्म / बीज ब्रांड',
        lbl_sowing_date: 'बुवाई / रोपाई की तिथि',
        lbl_harvest_date: 'अनुमानित कटाई तिथि (वैकल्पिक)',
        btn_cancel: 'रद्द करें',
        btn_save_profile: 'खेत प्रोफ़ाइल सहेजें',
        title: "AgriVoice - किसान फील्ड वॉइस सहायक",
        version_tag: "v1.0 ऑफलाइन-सक्षम",
        brand_desc: "किसानों के लिए AI संचालित कृषि वाणी सलाहकार प्रणाली",
        rag_index: "RAG इंडेक्स: <strong>8 रिकॉर्ड्स</strong>",
        lang_label: "भाषा:",
        engine_label: "इंजन:",
        engine_off: "🔒 पूर्ण ऑफ़लाइन (Llama 3.2 3B)",
        engine_auto: "⚡ हाइब्रिड ऑटो (स्थानीय + क्लाउड)",
        engine_on: "🌐 क्लाउड प्राथमिकता (Gemini Flash)",
        quick_actions: "त्वरित कृषि क्रियाएँ",
        chip_yellow_rust: "गेहूं पीला रतुआ",
        chip_pink_bollworm: "कपास गुलाबी सुंडी",
        chip_rice_blast: "धान ब्लास्ट (झुलसा) उपचार",
        chip_early_blight: "टमाटर अगेती झुलसा",
        chip_nitrogen: "नाइट्रोजन की कमी",
        chip_drip: "ड्रिप सिंचाई रखरखाव",
        chip_pmkisan: "पीएम-किसान ₹6000 योजना",
        chip_pmfby: "पीएम फसल बीमा योजना",
        arch_specs: "सिस्टम विवरण",
        spec_voice_in: "ध्वनि इनपुट:",
        spec_retrieval: "ज्ञान प्राप्ति:",
        spec_local_llm: "स्थानीय AI:",
        spec_cloud_llm: "क्लाउड AI:",
        spec_voice_out: "ध्वनि आउटपुट:",
        welcome_title: "किसान फील्ड सहायक तैयार है",
        welcome_status: "100% ऑफ़लाइन सक्षम • स्थानीय RAG सक्रिय",
        welcome_desc: "फसल रोग, कीट प्रकोप, उर्वरक मात्रा या सरकारी योजनाओं के बारे में पूछने के लिए नीचे दिए गए माइक बटन को दबाएं या बाईं ओर दिए गए विषयों पर क्लिक करें।",
        tag_voice_in: "वाणी आदेश",
        tag_reasoning: "बहु-भाषी AI",
        tag_voice_out: "ध्वनि उच्चारण",
        mic_title: "बोलने के लिए माइक दबाएं",
        mic_sub: "क्लाउड वॉइस API और ऑफ़लाइन इंजन के साथ काम करता है",
        mic_listening: "किसान की आवाज सुन रहे हैं...",
        mic_listening_sub: "स्पष्ट बोलें — भेजने के लिए दोबारा दबाएं",
        input_placeholder: "फसल से संबंधित प्रश्न या कीट के लक्षण लिखें...",
        send_btn: "पूछें",
        processing_text: "कृषि ज्ञान भंडार से समाधान खोज रहे हैं...",
        replay_voice: "पुनः सुनें",
        farmer_inquiry: "किसान का प्रश्न",
        local_context: "स्थानीय कृषि संदर्भ",
        confidence: "सटीकता",
        signal_fastapi_online: "सिग्नल: <strong>कनेक्टेड (FastAPI)</strong>",
        signal_fastapi_offline: "सिग्नल: <strong>ऑफ़लाइन (लोकल इंजन)</strong>",
        signal_web_online: "सिग्नल: <strong>कनेक्टेड (वेब मोड)</strong>",
        signal_web_offline: "सिग्नल: <strong>ऑफ़लाइन (फील्ड मोड)</strong>"
    },
    mr: {
        journey_tag: '🌾 चालू पीक प्रवास',
        modal_profile_title: 'माझे शेत आणि पीक प्रोफाइल',
        modal_profile_sub: 'सर्व AI सल्ला, वाढीच्या अवस्था आणि कीड अलर्ट वैयक्तिकृत करतो',
        lbl_farm_name: 'शेत / क्षेत्राचे नाव',
        lbl_farmer_name: 'शेतकऱ्याचे नाव',
        lbl_location: 'स्थान (जिल्हा, राज्य)',
        lbl_farm_size: 'शेताचा आकार (एकर)',
        lbl_soil_type: 'मातीचा प्रकार',
        lbl_irrigation: 'सिंचन पद्धत',
        lbl_crop: 'सध्याचे पीक',
        lbl_variety: 'वाण / बियाणे जात',
        lbl_sowing_date: 'पेरणी / लागवड तारीख',
        lbl_harvest_date: 'अपेक्षित कापणी तारीख (ऐच्छिक)',
        btn_cancel: 'रद्द करा',
        btn_save_profile: 'शेत प्रोफाइल जतन करा',
        title: "AgriVoice - शेतकरी व्हॉइस सल्लागार",
        version_tag: "v1.0 ऑफलाइन-सक्षम",
        brand_desc: "शेतकऱ्यांसाठी AI व्हॉइस शेती सल्लागार प्रणाली",
        rag_index: "RAG इंडेक्स: <strong>8 नोंदी</strong>",
        lang_label: "भाषा:",
        engine_label: "इंजिन:",
        engine_off: "🔒 पूर्ण ऑफलाइन (Llama 3.2 3B)",
        engine_auto: "⚡ हायब्रिड ऑटो (स्थानिक + क्लाउड)",
        engine_on: "🌐 क्लाउड प्राधान्य (Gemini Flash)",
        quick_actions: "शेतकाम जलद कृती",
        chip_yellow_rust: "गहू पिवळा तांबेरा",
        chip_pink_bollworm: "कापूस बोंडअळी नियंत्रण",
        chip_rice_blast: "भात करपा रोग उपचार",
        chip_early_blight: "टोमॅटो लवकर येणारा करपा",
        chip_nitrogen: "नायट्रोजन कमतरता",
        chip_drip: "ठिबक सिंचन देखभाल",
        chip_pmkisan: "पीएम-किसान ₹6000 योजना",
        chip_pmfby: "पंतप्रधान पीक विमा योजना",
        arch_specs: "यंत्रणा तपशील",
        spec_voice_in: "आवाज इनपुट:",
        spec_retrieval: "माहिती शोध:",
        spec_local_llm: "स्थानिक AI:",
        spec_cloud_llm: "क्लाउड AI:",
        spec_voice_out: "आवाज आउटपुट:",
        welcome_title: "शेतकरी शेती सल्लागार तयार आहे",
        welcome_status: "100% ऑफलाइन सक्षम • स्थानिक RAG सक्रिय",
        welcome_desc: "पिकांवरील रोग, कीड व्यवस्थापन, खत मात्रा किंवा शासकीय योजनांबद्दल विचारण्यासाठी खालील माइक बटण दाबा किंवा डावीकडील विषयांमधून निवडा.",
        tag_voice_in: "व्हॉइस आज्ञा",
        tag_reasoning: "बहुभाषिक AI",
        tag_voice_out: "मराठी व्हॉइस उत्तर",
        mic_title: "बोलण्यासाठी माइक दाबा",
        mic_sub: "क्लाउड व्हॉइस आणि ऑफलाइन इंजिनसह कार्यक्षम",
        mic_listening: "शेतकऱ्यांचा प्रश्न ऐकत आहे...",
        mic_listening_sub: "स्पष्ट बोला — पाठवण्यासाठी पुन्हा दाबा",
        input_placeholder: "पिकाचा प्रश्न किंवा रोगाची लक्षणे येथे लिहा...",
        send_btn: "विचारा",
        processing_text: "कृषी माहिती भांडारातून उत्तर शोधत आहे...",
        replay_voice: "पुन्हा ऐका",
        farmer_inquiry: "शेतकऱ्यांचा प्रश्न",
        local_context: "स्थानिक कृषी संदर्भ",
        confidence: "अचूकता",
        signal_fastapi_online: "सिग्नल: <strong>कनेक्टेड (FastAPI)</strong>",
        signal_fastapi_offline: "सिग्नल: <strong>ऑफलाइन (लोकल इंजिन)</strong>",
        signal_web_online: "सिग्नल: <strong>कनेक्टेड (वेब मोड)</strong>",
        signal_web_offline: "सिग्नल: <strong>ऑफलाइन (शेत मोड)</strong>"
    },
    te: {
        journey_tag: '🌾 క్రియాశీల పంట ప్రయాణం',
        modal_profile_title: 'నా వ్యవసాయ ప్రొఫైల్',
        modal_profile_sub: 'అన్ని AI సలహాలు, ఎదుగుదల దశలు మరియు తెగుళ్ల హెచ్చరికలను వ్యక్తిగతీకరిస్తుంది',
        lbl_farm_name: 'పొలం / క్షేత్రం పేరు',
        lbl_farmer_name: 'రైతు పేరు',
        lbl_location: 'ప్రాంతం (జిల్లా, రాష్ట్రం)',
        lbl_farm_size: 'పొలం పరిమాణం (ఎకరాలు)',
        lbl_soil_type: 'నేల రకం',
        lbl_irrigation: 'నీటిపారుదల పద్ధతి',
        lbl_crop: 'ప్రస్తుత పంట',
        lbl_variety: 'రకం / విత్తన బ్రాండ్',
        lbl_sowing_date: 'విత్తిన / నాటిన తేదీ',
        lbl_harvest_date: 'అంచనా కోత తేదీ (ఐచ్ఛికం)',
        btn_cancel: 'రద్దు చేయి',
        btn_save_profile: 'ప్రొఫైల్ సేవ్ చేయండి',
        title: "AgriVoice - రైతు ఫీల్డ్ వాయిస్ అసిస్టెంట్",
        version_tag: "v1.0 ఆఫ్‌లైన్-సిద్ధం",
        brand_desc: "రైతుల కోసం కృత్రిమ మేధస్సు ఆధారిత వ్యవసాయ వాయిస్ సలహా వ్యవస్థ",
        rag_index: "RAG ఇండెక్స్: <strong>8 రికార్డులు</strong>",
        lang_label: "భాష:",
        engine_label: "ఇంజిన్:",
        engine_off: "🔒 ఆఫ్‌లైన్ డీఫాల్ట్ (Llama 3.2 3B)",
        engine_auto: "⚡ హైబ్రిడ్ ఆటో (స్థానిక + క్లౌడ్)",
        engine_on: "🌐 క్లౌడ్ ప్రాధాన్యత (Gemini Flash)",
        quick_actions: "త్వరిత వ్యవసాయ చర్యలు",
        chip_yellow_rust: "గోధుమ పసుపు తుప్పు",
        chip_pink_bollworm: "ప్రత్తి గులాబీ రంగు పురుగు",
        chip_rice_blast: "వరి అగ్గి తెగులు నివారణ",
        chip_early_blight: "టమోటా ముందస్తు మచ్చల తెగులు",
        chip_nitrogen: "నత్రజని లోపం",
        chip_drip: "బిందు సేద్యం నిర్వహణ",
        chip_pmkisan: "పీఎం-కిసాన్ ₹6000 పథకం",
        chip_pmfby: "పీఎం ఫసల్ బీమా యోజన",
        arch_specs: "ఆర్కిటెక్చర్ వివరాలు",
        spec_voice_in: "వాయిస్ ఇన్పుట్:",
        spec_retrieval: "సమాచార సేకరణ:",
        spec_local_llm: "స్థానిక AI:",
        spec_cloud_llm: "క్లౌడ్ AI:",
        spec_voice_out: "వాయిస్ అవుట్‌పుట్:",
        welcome_title: "రైతు వ్యవసాయ సహాయకుడు సిద్ధంగా ఉన్నాడు",
        welcome_status: "100% ఆఫ్‌లైన్ సామర్థ్యం • స్థానిక RAG క్రియాశీలం",
        welcome_desc: "పంట తెగుళ్ళు, ఎరువుల మోతాదు లేదా ప్రభుత్వ పథకాల గురించి అడగడానికి మైక్రోఫోన్ బటన్‌ను నొక్కండి లేదా ఎడమవైపు అంశాన్ని ఎంచుకోండి.",
        tag_voice_in: "వాయిస్ కమాండ్",
        tag_reasoning: "బహుభాషా AI",
        tag_voice_out: "తెలుగు వాయిస్ సమాధానం",
        mic_title: "మాట్లాడటానికి మైక్ నొక్కండి",
        mic_sub: "క్లౌడ్ వాయిస్ మరియు ఆఫ్‌లైన్ ఇంజిన్‌తో పనిచేస్తుంది",
        mic_listening: "రైతు ప్రశ్న వింటోంది...",
        mic_listening_sub: "స్పష్టంగా మాట్లాడండి — పంపడానికి మళ్ళీ నొక్కండి",
        input_placeholder: "పంట సమస్య లేదా తెగులు లక్షణాన్ని టైప్ చేయండి...",
        send_btn: "సహాయం అడగండి",
        processing_text: "వ్యవసాయ సమాచార నిధి నుండి పరిష్కారం శోధిస్తోంది...",
        replay_voice: "వాయిస్ మళ్ళీ వినండి",
        farmer_inquiry: "రైతు ప్రశ్న",
        local_context: "స్థానిక వ్యవసాయ సందర్భం",
        confidence: "ఖచ్చితత్వం",
        signal_fastapi_online: "సిగ్నల్: <strong>కనెక్ట్ చేయబడింది (FastAPI)</strong>",
        signal_fastapi_offline: "సిగ్నల్: <strong>ఆఫ్‌లైన్ (లోకల్ ఇంజిన్)</strong>",
        signal_web_online: "సిగ్నల్: <strong>కనెక్ట్ చేయబడింది (వెబ్ మోడ్)</strong>",
        signal_web_offline: "సిగ్నల్: <strong>ఆఫ్‌లైన్ (ఫీల్డ్ మోడ్)</strong>"
    },
    ta: {
        journey_tag: '🌾 செயலில் உள்ள பயிர் பயணம்',
        modal_profile_title: 'எனது பண்ணை சுயவிவரம்',
        modal_profile_sub: 'அனைத்து AI ஆலோசனைகள் மற்றும் பூச்சி எச்சரிக்கைகளை தனிப்பயனாக்குகிறது',
        lbl_farm_name: 'பண்ணை / நிலத்தின் பெயர்',
        lbl_farmer_name: 'விவசாயி பெயர்',
        lbl_location: 'இடம் (மாவட்டம், மாநிலம்)',
        lbl_farm_size: 'பண்ணை அளவு (ஏக்கர்)',
        lbl_soil_type: 'மண் வகை',
        lbl_irrigation: 'பாசன முறை',
        lbl_crop: 'தற்போதைய பயிர்',
        lbl_variety: 'பயிர் ரகம் / விதை பிராண்ட்',
        lbl_sowing_date: 'விதைத்த / நட்ட தேதி',
        lbl_harvest_date: 'எதிர்பார்க்கப்படும் அறுவடை தேதி',
        btn_cancel: 'ரத்து செய்',
        btn_save_profile: 'சுயவிவரத்தை சேமி',
        title: "AgriVoice - விவசாய கள குரல் உதவியாளர்",
        version_tag: "v1.0 ஆஃப்லைன்-தயார்",
        brand_desc: "விவசாயிகளுக்கான AI குரல் வேளாண் ஆலோசனை அமைப்பு",
        rag_index: "RAG குறியீடு: <strong>8 பதிவுகள்</strong>",
        lang_label: "மொழி:",
        engine_label: "இயந்திரம்:",
        engine_off: "🔒 ஆஃப்லைன் இயல்புநிலை (Llama 3.2 3B)",
        engine_auto: "⚡ ஹைப்ரிட் ஆட்டோ (உள்ளூர் + கிளவுட்)",
        engine_on: "🌐 கிளவுட் முன்னுரிமை (Gemini Flash)",
        quick_actions: "கள விரைவு நடவடிக்கைகள்",
        chip_yellow_rust: "கோதுமை மஞ்சள் துரு நோய்",
        chip_pink_bollworm: "பருத்தி இளஞ்சிவப்பு காய் புழு",
        chip_rice_blast: "நெல் குலை நோய் சிகிச்சை",
        chip_early_blight: "தக்காளி ஆரம்பகால கருகல்",
        chip_nitrogen: "தழைச்சத்து குறைபாடு",
        chip_drip: "சொட்டு நீர் பாசன பராமரிப்பு",
        chip_pmkisan: "பிஎம் கிசான் ₹6000 திட்டம்",
        chip_pmfby: "பயிர் காப்பீட்டுத் திட்டம்",
        arch_specs: "கட்டமைப்பு விவரங்கள்",
        spec_voice_in: "குரல் உள்ளீடு:",
        spec_retrieval: "தரவு மீட்டெடுப்பு:",
        spec_local_llm: "உள்ளூர் AI:",
        spec_cloud_llm: "கிளவுட் AI:",
        spec_voice_out: "குரல் வெளியீடு:",
        welcome_title: "விவசாய கள உதவியாளர் தயார்",
        welcome_status: "100% ஆஃப்லைன் திறன் • உள்ளூர் RAG செயலில்",
        welcome_desc: "பயிர் நோய்கள், உர அளவு அல்லது அரசு நலத்திட்டங்கள் பற்றி கேட்க கீழே உள்ள மைக்ரோஃபோன் பொத்தானை அழுத்தவும்.",
        tag_voice_in: "குரல் கட்டளை",
        tag_reasoning: "பன்மொழி AI",
        tag_voice_out: "தமிழ் குரல் வெளியீடு",
        mic_title: "பேச மைக்ரோஃபோனை அழுத்தவும்",
        mic_sub: "கிளவுட் வாய்ஸ் மற்றும் ஆஃப்லைன் இன்ஜின் மூலம் செயல்படுகிறது",
        mic_listening: "விவசாயியின் கேள்வியைக் கேட்கிறது...",
        mic_listening_sub: "தெளிவாகப் பேசுங்கள் — அனுப்ப மீண்டும் அழுத்தவும்",
        input_placeholder: "பயிர் பிரச்சனை அல்லது கேள்வியை உள்ளிடவும்...",
        send_btn: "கேளுங்கள்",
        processing_text: "வேளாண் தரவுத்தளத்தில் இருந்து தீர்வு தேடுகிறது...",
        replay_voice: "மீண்டும் கேட்க",
        farmer_inquiry: "விவசாயி கேள்வி",
        local_context: "உள்ளூர் வேளாண் சூழல்",
        confidence: "துல்லியம்",
        signal_fastapi_online: "சிக்னல்: <strong>இணைக்கப்பட்டது (FastAPI)</strong>",
        signal_fastapi_offline: "சிக்னல்: <strong>ஆஃப்லைன் (லோக்கல் இன்ஜின்)</strong>",
        signal_web_online: "சிக்னல்: <strong>இணைக்கப்பட்டது (Web Mode)</strong>",
        signal_web_offline: "சிக்னல்: <strong>ஆஃப்லைன் (Field Mode)</strong>"
    },
    kn: {
        journey_tag: '🌾 ಸಕ್ರಿಯ ಬೆಳೆ ಪ್ರಯಾಣ',
        modal_profile_title: 'ನನ್ನ ಕೃಷಿ ಪ್ರೊಫೈಲ್',
        modal_profile_sub: 'ಎಲ್ಲಾ AI ಸಲಹೆಗಳು ಮತ್ತು ಕೀಟ ಎಚ್ಚರಿಕೆಗಳನ್ನು ವೈಯಕ್ತೀಕರಿಸುತ್ತದೆ',
        lbl_farm_name: 'ಜಮೀನು / ತೋಟದ ಹೆಸರು',
        lbl_farmer_name: 'ರೈತರ ಹೆಸರು',
        lbl_location: 'ಸ್ಥಳ (ಜಿಲ್ಲೆ, ರಾಜ್ಯ)',
        lbl_farm_size: 'ಜಮೀನಿನ ವಿಸ್ತೀರ್ಣ (ಎಕರೆ)',
        lbl_soil_type: 'ಮಣ್ಣಿನ ವಿಧ',
        lbl_irrigation: 'ನೀರಾವರಿ ವಿಧಾನ',
        lbl_crop: 'ಪ್ರಸ್ತುತ ಬೆಳೆ',
        lbl_variety: 'ತಳಿ / ಬೀಜದ ಬ್ರಾಂಡ್',
        lbl_sowing_date: 'ಬಿತ್ತನೆ / ನಾಟಿ ದಿನಾಂಕ',
        lbl_harvest_date: 'ನಿರೀಕ್ಷಿತ ಕೊಯ್ಲು ದಿನಾಂಕ',
        btn_cancel: 'ರದ್ದುಮಾಡಿ',
        btn_save_profile: 'ಪ್ರೊಫೈಲ್ ಉಳಿಸಿ',
        title: "AgriVoice - ರೈತ ಫೀಲ್ಡ್ ಧ್ವನಿ ಸಹಾಯಕ",
        version_tag: "v1.0 ಆಫ್‌ಲೈನ್-ಸಿದ್ಧ",
        brand_desc: "ರೈತರಿಗಾಗಿ ಕೃತಕ ಬುದ್ಧಿಮತ್ತೆ ಆಧಾರಿತ ಕೃಷಿ ಧ್ವನಿ ಸಲಹಾ ವ್ಯವಸ್ಥೆ",
        rag_index: "RAG ಸೂಚ್ಯಂಕ: <strong>8 ದಾಖಲೆಗಳು</strong>",
        lang_label: "ಭಾಷೆ:",
        engine_label: "ಎಂಜಿನ್:",
        engine_off: "🔒 ಆಫ್‌ಲೈನ್ ಡೀಫಾಲ್ಟ್ (Llama 3.2 3B)",
        engine_auto: "⚡ ಹೈಬ್ರಿಡ್ ಆಟೋ (ಸ್ಥಳೀಯ + ಕ್ಲೌಡ್)",
        engine_on: "🌐 ಕ್ಲೌಡ್ ಆದ್ಯತೆ (Gemini Flash)",
        quick_actions: "ಕ್ಷೇತ್ರ ತ್ವರಿತ ಕ್ರಮಗಳು",
        chip_yellow_rust: "ಗೋಧಿ ಹಳದಿ ತುಕ್ಕು ರೋಗ",
        chip_pink_bollworm: "ಹತ್ತಿ ಗುಲಾಬಿ ಕಾಯಿ ಕೊರೆಯುವ ಹುಳು",
        chip_rice_blast: "ಭತ್ತದ ಬೆಂಕಿರೋಗ ಚಿಕಿತ್ಸೆ",
        chip_early_blight: "ಟೊಮ್ಯಾಟೊ ಅರ್ಲಿ ಬ್ಲೈಟ್",
        chip_nitrogen: "ಸಾರಜನಕ ಕೊರತೆ",
        chip_drip: "ಹನಿ ನೀರಾವರಿ ನಿರ್ವಹಣೆ",
        chip_pmkisan: "ಪಿಎಂ ಕಿಸಾನ್ ₹6000 ಯೋಜನೆ",
        chip_pmfby: "ಪ್ರಧಾನ ಮಂತ್ರಿ ಬೆಳೆ ವಿಮೆ",
        arch_specs: "ತಂತ್ರಜ್ಞಾನ ವಿವರಣೆ",
        spec_voice_in: "ಧ್ವನಿ ಇನ್ಪುಟ್:",
        spec_retrieval: "ಮಾಹಿತಿ ಶೋಧ:",
        spec_local_llm: "ಸ್ಥಳೀಯ AI:",
        spec_cloud_llm: "ಕ್ಲೌಡ್ AI:",
        spec_voice_out: "ಧ್ವನಿ ಔಟ್‌ಪುಟ್:",
        welcome_title: "ರೈತ ಕೃಷಿ ಸಹಾಯಕ ಸಿದ್ಧವಾಗಿದೆ",
        welcome_status: "100% ಆಫ್‌ಲೈನ್ ಸಾಮರ್ಥ್ಯ • ಸ್ಥಳೀಯ RAG ಸಕ್ರಿಯ",
        welcome_desc: "ಬೆಳೆ ರೋಗಗಳು, ಕೀಟ ನಿರ್ವಹಣೆ, ಗೊಬ್ಬರದ ಪ್ರಮಾಣ ಅಥವಾ ಸರಕಾರಿ ಯೋಜನೆಗಳ ಬಗ್ಗೆ ಕೇಳಲು ಕೆಳಗಿನ ಮೈಕ್ರೋಫೋನ್ ಬಟನ್ ಒತ್ತಿರಿ.",
        tag_voice_in: "ಧ್ವನಿ ಆದೇಶ",
        tag_reasoning: "ಬಹುಭಾಷಾ AI",
        tag_voice_out: "ಕನ್ನಡ ಧ್ವನಿ ಉತ್ತರ",
        mic_title: "ಮಾತನಾಡಲು ಮೈಕ್ ಒತ್ತಿರಿ",
        mic_sub: "ಕ್ಲೌಡ್ ಧ್ವನಿ ಮತ್ತು ಆಫ್‌ಲೈನ್ ಎಂಜಿನ್‌ನೊಂದಿಗೆ ಕಾರ್ಯನಿರ್ವಹಿಸುತ್ತದೆ",
        mic_listening: "ರೈತರ ಧ್ವನಿ ಆಲಿಸುತ್ತಿದೆ...",
        mic_listening_sub: "ಸ್ಪಷ್ಟವಾಗಿ ಮಾತನಾಡಿ — ಕಳುಹಿಸಲು ಮತ್ತೊಮ್ಮೆ ಒತ್ತಿರಿ",
        input_placeholder: "ಬೆಳೆ ಸಮಸ್ಯೆ ಅಥವಾ ಕೀಟ ಲಕ್ಷಣವನ್ನು ಟೈಪ್ ಮಾಡಿ...",
        send_btn: "ಕೇಳಿ",
        processing_text: "ಕೃಷಿ ಮಾಹಿತಿ ಭಂಡಾರದಿಂದ ಉತ್ತರ ಹುಡುಕಲಾಗುತ್ತಿದೆ...",
        replay_voice: "ಮತ್ತೆ ಕೇಳಿ",
        farmer_inquiry: "ರೈತರ ಪ್ರಶ್ನೆ",
        local_context: "ಸ್ಥಳೀಯ ಕೃಷಿ ಮಾಹಿತಿ",
        confidence: "ನಿಖರತೆ",
        signal_fastapi_online: "ಸಿಗ್ನಲ್: <strong>ಸಂಪರ್ಕಗೊಂಡಿದೆ (FastAPI)</strong>",
        signal_fastapi_offline: "ಸಿಗ್ನಲ್: <strong>ಆಫ್‌ಲೈನ್ (ಸ್ಥಳೀಯ ಎಂಜಿನ್)</strong>",
        signal_web_online: "ಸಿಗ್ನಲ್: <strong>ಸಂಪರ್ಕಗೊಂಡಿದೆ (ವೆಬ್ ಮೋಡ್)</strong>",
        signal_web_offline: "ಸಿಗ್ನಲ್: <strong>ಆಫ್‌ಲೈನ್ (ಕ್ಷೇತ್ರ ಮೋಡ್)</strong>"
    },
    pa: {
        journey_tag: '🌾 ਸਰਗਰਮ ਫਸਲ ਯਾਤਰਾ',
        modal_profile_title: 'ਮੇਰਾ ਖੇਤ ਪ੍ਰੋਫਾਈਲ',
        modal_profile_sub: 'ਸਾਰੀਆਂ AI ਸਲਾਹਾਂ ਅਤੇ ਕੀੜਿਆਂ ਦੇ ਅਲਰਟ ਨੂੰ ਨਿੱਜੀ ਬਣਾਉਂਦਾ ਹੈ',
        lbl_farm_name: 'ਖੇਤ / ਜ਼ਮੀਨ ਦਾ ਨਾਮ',
        lbl_farmer_name: 'ਕਿਸਾਨ ਦਾ ਨਾਮ',
        lbl_location: 'ਸਥਾਨ (ਜ਼ਿਲ੍ਹਾ, ਰਾਜ)',
        lbl_farm_size: 'ਖੇਤ ਦਾ ਆਕਾਰ (ਏਕੜ)',
        lbl_soil_type: 'ਮਿੱਟੀ ਦੀ ਕਿਸਮ',
        lbl_irrigation: 'ਸਿੰਚਾਈ ਦਾ ਤਰੀਕਾ',
        lbl_crop: 'ਮੌਜੂਦਾ ਫਸਲ',
        lbl_variety: 'ਕਿਸਮ / ਬੀਜ ਬ੍ਰਾਂਡ',
        lbl_sowing_date: 'ਬਿਜਾਈ ਦੀ ਮਿਤੀ',
        lbl_harvest_date: 'ਕਟਾਈ ਦੀ ਸੰਭਾਵਿਤ ਮਿਤੀ',
        btn_cancel: 'ਰੱਦ ਕਰੋ',
        btn_save_profile: 'ਪ੍ਰੋਫਾਈਲ ਸੰਭਾਲੋ',
        title: "AgriVoice - ਕਿਸਾਨ ਖੇਤਰੀ ਵਾਇਸ ਸਹਾਇਕ",
        version_tag: "v1.0 ਆਫਲਾਈਨ-ਸਮਰੱਥ",
        brand_desc: "ਕਿਸਾਨਾਂ ਲਈ AI ਸੰਚਾਲਿਤ ਖੇਤੀਬਾੜੀ ਵਾਇਸ ਸਲਾਹਕਾਰ ਪ੍ਰਣਾਲੀ",
        rag_index: "RAG ਸੂਚਕਾਂਕ: <strong>8 ਰਿਕਾਰਡ</strong>",
        lang_label: "ਭਾਸ਼ਾ:",
        engine_label: "ਇੰਜਣ:",
        engine_off: "🔒 ਪੂਰਾ ਆਫਲਾਈਨ (Llama 3.2 3B)",
        engine_auto: "⚡ ਹਾਈਬ੍ਰਿਡ ਆਟੋ (ਸਥਾਨਕ + ਕਲਾਉਡ)",
        engine_on: "🌐 ਕਲਾਉਡ ਤਰਜੀਹ (Gemini Flash)",
        quick_actions: "ਖੇਤਰੀ ਤੁਰੰਤ ਕਾਰਵਾਈਆਂ",
        chip_yellow_rust: "ਕਣਕ ਦੀ ਪੀਲੀ ਕੁੰਗੀ",
        chip_pink_bollworm: "ਨਰਮੇ ਦੀ ਗੁਲਾਬੀ ਸੁੰਡੀ",
        chip_rice_blast: "ਝੋਨੇ ਦਾ ਝੁਲਸ ਰੋਗ ਇਲਾਜ",
        chip_early_blight: "ਟਮਾਟਰ ਦਾ ਅਗੇਤਾ ਝੁਲਸ",
        chip_nitrogen: "ਨਾਈਟ੍ਰੋਜਨ ਦੀ ਘਾਟ",
        chip_drip: "ਤੁਪਕਾ ਸਿੰਚਾਈ ਸਾਂਭ-ਸੰਭਾਲ",
        chip_pmkisan: "ਪ੍ਰਧਾਨ ਮੰਤਰੀ ਕਿਸਾਨ ₹6000",
        chip_pmfby: "ਫਸਲ ਬੀਮਾ ਯੋਜਨਾ",
        arch_specs: "ਸਿਸਟਮ ਵੇਰਵਾ",
        spec_voice_in: "ਅਵਾਜ਼ ਇਨਪੁਟ:",
        spec_retrieval: "ਜਾਣਕਾਰੀ ਖੋਜ:",
        spec_local_llm: "ਸਥਾਨਕ AI:",
        spec_cloud_llm: "ਕਲਾਉਡ AI:",
        spec_voice_out: "ਅਵਾਜ਼ ਆਉਟਪੁੱਟ:",
        welcome_title: "ਕਿਸਾਨ ਖੇਤੀ ਸਹਾਇਕ ਤਿਆਰ ਹੈ",
        welcome_status: "100% ਆਫਲਾਈਨ ਸਮਰੱਥ • ਸਥਾਨਕ RAG ਸਰਗਰਮ",
        welcome_desc: "ਫਸਲਾਂ ਦੇ ਰੋਗਾਂ, ਕੀਟ ਪ੍ਰਬੰਧਨ, ਖਾਦ ਦੀ ਮਾਤਰਾ ਜਾਂ ਸਰਕਾਰੀ ਸਕੀਮਾਂ ਬਾਰੇ ਪੁੱਛਣ ਲਈ ਹੇਠਾਂ ਦਿੱਤਾ ਮਾਈਕ ਬਟਨ ਦਬਾਓ।",
        tag_voice_in: "ਅਵਾਜ਼ ਹੁਕਮ",
        tag_reasoning: "ਬਹੁ-ਭਾਸ਼ਾਈ AI",
        tag_voice_out: "ਪੰਜਾਬੀ ਅਵਾਜ਼ ਉੱਤਰ",
        mic_title: "ਬੋਲਣ ਲਈ ਮਾਈਕ ਦਬਾਓ",
        mic_sub: "ਕਲਾਉਡ ਵਾਇਸ ਅਤੇ ਆਫਲਾਈਨ ਇੰਜਣ ਨਾਲ ਕੰਮ ਕਰਦਾ ਹੈ",
        mic_listening: "ਕਿਸਾਨ ਦਾ ਸਵਾਲ ਸੁਣ ਰਿਹਾ ਹੈ...",
        mic_listening_sub: "ਸਾਫ਼ ਬੋਲੋ — ਭੇਜਣ ਲਈ ਦੁਬਾਰਾ ਦਬਾਓ",
        input_placeholder: "ਫਸਲ ਦਾ ਸਵਾਲ ਜਾਂ ਬਿਮਾਰੀ ਦੇ ਲੱਛਣ ਲਿਖੋ...",
        send_btn: "ਪੁੱਛੋ",
        processing_text: "ਖੇਤੀ ਗਿਆਨ ਭੰਡਾਰ ਤੋਂ ਉੱਤਰ ਲੱਭ ਰਿਹਾ ਹੈ...",
        replay_voice: "ਦੁਬਾਰਾ ਸੁਣੋ",
        farmer_inquiry: "ਕਿਸਾਨ ਦਾ ਸਵਾਲ",
        local_context: "ਸਥਾਨਕ ਖੇਤੀ ਸੰਦਰਭ",
        confidence: "ਸ਼ੁੱਧਤਾ",
        signal_fastapi_online: "ਸਿਗਨਲ: <strong>ਕਨੈਕਟਡ (FastAPI)</strong>",
        signal_fastapi_offline: "ਸਿਗਨਲ: <strong>ਆਫਲਾਈਨ (ਲੋਕਲ ਇੰਜਣ)</strong>",
        signal_web_online: "ਸਿਗਨਲ: <strong>ਕਨੈਕਟਡ (ਵੈੱਬ ਮੋਡ)</strong>",
        signal_web_offline: "ਸਿਗਨਲ: <strong>ਆਫਲਾਈਨ (ਖੇਤਰੀ ਮੋਡ)</strong>"
    },
    gu: {
        journey_tag: '🌾 સક્રિય પાક યાત્રા',
        modal_profile_title: 'મારી ફાર્મ પ્રોફાઇલ',
        modal_profile_sub: 'તમામ AI સલાહ અને જીવાત ચેતવણીઓને વ્યક્તિગત બનાવે છે',
        lbl_farm_name: 'ખેતર / પ્લોટનું નામ',
        lbl_farmer_name: 'ખેડૂતનું નામ',
        lbl_location: 'સ્થળ (જિલ્લો, રાજ્ય)',
        lbl_farm_size: 'ખેતરનું કદ (એકર)',
        lbl_soil_type: 'જમીનનો પ્રકાર',
        lbl_irrigation: 'પિયત પદ્ધતિ',
        lbl_crop: 'હાલનો પાક',
        lbl_variety: 'જાત / બિયારણ બ્રાન્ડ',
        lbl_sowing_date: 'વાવણી / રોપણી તારીખ',
        lbl_harvest_date: 'અંદાજિત લણણી તારીખ',
        btn_cancel: 'રદ કરો',
        btn_save_profile: 'પ્રોફાઇલ સાચવો',
        title: "AgriVoice - ખેડૂત ફીલ્ડ વૉઇસ સહાયક",
        version_tag: "v1.0 ઑફલાઇન-સક્ષમ",
        brand_desc: "ખેડૂતો માટે AI સંચાલિત કૃષિ વૉઇસ સલાહકાર પ્રણાલી",
        rag_index: "RAG ઇન્ડેક્સ: <strong>8 રેકોર્ડ્સ</strong>",
        lang_label: "ભાષા:",
        engine_label: "એન્જિન:",
        engine_off: "🔒 સંપૂર્ણ ઑફલાઇન (Llama 3.2 3B)",
        engine_auto: "⚡ હાઇબ્રિડ ઑટો (સ્થાનિક + ક્લાઉડ)",
        engine_on: "🌐 ક્લાઉડ પ્રાથમિકતા (Gemini Flash)",
        quick_actions: "ત્વરિત ખેતી ક્રિયાઓ",
        chip_yellow_rust: "ઘઉં પીળો ગેરુ રોગ",
        chip_pink_bollworm: "કપાસ ગુલાબી ઈયળ",
        chip_rice_blast: "ડાંગર કરપા રોગ ઉપચાર",
        chip_early_blight: "ટામેટા આગોતરો સુકારો",
        chip_nitrogen: "નાઇટ્રોજનની ઉણપ",
        chip_drip: "ટપક સિંચાઈ જાળવણી",
        chip_pmkisan: "પીએમ કિસાન ₹6000 યોજના",
        chip_pmfby: "પીએમ ફસલ બીમા યોજના",
        arch_specs: "સિસ્ટમ વિગતો",
        spec_voice_in: "વૉઇસ ઇનપુટ:",
        spec_retrieval: "માહિતી શોધ:",
        spec_local_llm: "સ્થાનિક AI:",
        spec_cloud_llm: "ક્લાઉડ AI:",
        spec_voice_out: "વૉઇસ આઉટપુટ:",
        welcome_title: "ખેડૂત મિત્ર સહાયક તૈયાર છે",
        welcome_status: "100% ઑફલાઇન સક્ષમ • સ્થાનિક RAG સક્રિય",
        welcome_desc: "પાકના રોગો, જીવાત નિયંત્રણ, ખાતરના ડોઝ અથવા સરકારી યોજનાઓ વિશે પૂછવા માટે નીચેનું માઇક બટન દબાવો.",
        tag_voice_in: "વૉઇસ કમાન્ડ",
        tag_reasoning: "બહુભાષીય AI",
        tag_voice_out: "ગુજરાતી વૉઇસ ઉત્તર",
        mic_title: "બોલવા માટે માઇક દબાવો",
        mic_sub: "ક્લાઉડ વૉઇસ અને ઑફલાઇન એન્જિન સાથે કાર્ય કરે છે",
        mic_listening: "ખેડૂતનો પ્રશ્ન સાંભળી રહ્યું છે...",
        mic_listening_sub: "સ્પષ્ટ બોલો — મોકલવા માટે ફરી દબાવો",
        input_placeholder: "પાકનો પ્રશ્ન અથવા જીવાતના લક્ષણ લખો...",
        send_btn: "પૂછો",
        processing_text: "કૃષિ માહિતી ભંડારમાંથી ઉકેલ શોધી રહ્યું છે...",
        replay_voice: "ફરી સાંભળો",
        farmer_inquiry: "ખેડૂતનો પ્રશ્ન",
        local_context: "સ્થાનિક કૃષિ સંદર્ભ",
        confidence: "ચોકસાઈ",
        signal_fastapi_online: "સિગ્નલ: <strong>કનેક્ટેડ (FastAPI)</strong>",
        signal_fastapi_offline: "સિગ્નલ: <strong>ઑફલાઇન (લોકલ એન્જિન)</strong>",
        signal_web_online: "સિગ્નલ: <strong>કનેક્ટેડ (વેબ મોડ)</strong>",
        signal_web_offline: "સિગ્નલ: <strong>ઑફલાઇન (ફીલ્ડ મોડ)</strong>"
    },
    bn: {
        journey_tag: '🌾 সক্রিয় ফসলের যাত্রা',
        modal_profile_title: 'আমার খামারের প্রোফাইল',
        modal_profile_sub: 'সমস্ত AI পরামর্শ এবং কীটপতঙ্গের সতর্কতা ব্যক্তিগতকৃত করে',
        lbl_farm_name: 'খামার / জমির নাম',
        lbl_farmer_name: 'কৃষকের নাম',
        lbl_location: 'স্থান (জেলা, রাজ্য)',
        lbl_farm_size: 'জমির পরিমাণ (একর)',
        lbl_soil_type: 'মাটির ধরন',
        lbl_irrigation: 'সেচ পদ্ধতি',
        lbl_crop: 'বর্তমান ফসল',
        lbl_variety: 'জাত / বীজ ব্র্যান্ড',
        lbl_sowing_date: 'বপন / রোপণের তারিখ',
        lbl_harvest_date: 'আনুমানিক ফসল তোলার তারিখ',
        btn_cancel: 'বাতিল করুন',
        btn_save_profile: 'প্রোফাইল সংরক্ষণ করুন
        title: "AgriVoice - কৃষক ফিল্ড ভয়েস সহকারী",
        version_tag: "v1.0 অফলাইন-সক্ষম",
        brand_desc: "কৃষকদের জন্য AI ভিত্তিক কৃষি ভয়েস পরামর্শদাতা ব্যবস্থা",
        rag_index: "RAG সূচক: <strong>8 রেকর্ড</strong>",
        lang_label: "ভাষা:",
        engine_label: "ইঞ্জিন:",
        engine_off: "🔒 সম্পূর্ণ অফলাইন (Llama 3.2 3B)",
        engine_auto: "⚡ হাইব্রিড অটো (স্থানীয় + ক্লাউড)",
        engine_on: "🌐 ক্লাউড অগ্রাধিকার (Gemini Flash)",
        quick_actions: "জরুরী কৃষি পদক্ষেপ",
        chip_yellow_rust: "গম হলুদ মরিচা রোগ",
        chip_pink_bollworm: "তুলা গোলাপি বলওয়ার্ম",
        chip_rice_blast: "ধানের ব্লাস্ট রোগ প্রতিকার",
        chip_early_blight: "টমেটো আর্লি ব্লাইট",
        chip_nitrogen: "নাইট্রোজেনের ঘাটতি",
        chip_drip: "ড্রিপ সেচ রক্ষণাবেক্ষণ",
        chip_pmkisan: "পিএম-কিসান ₹৬০০০ প্রকল্প",
        chip_pmfby: "ফসল বীমা যোজনা",
        arch_specs: "সিস্টেম বিবরণ",
        spec_voice_in: "ভয়েস ইনপুট:",
        spec_retrieval: "তথ্য অনুসন্ধান:",
        spec_local_llm: "স্থানীয় AI:",
        spec_cloud_llm: "ক্লাউড AI:",
        spec_voice_out: "ভয়েস আউটপুট:",
        welcome_title: "কৃষক বন্ধু সহকারী প্রস্তুত",
        welcome_status: "100% অফলাইন সক্ষম • স্থানীয় RAG সক্রিয়",
        welcome_desc: "ফসলের রোগ, কীটপতঙ্গ দমন, সারের মাত্রা বা সরকারী প্রকল্প সম্পর্কে জানতে নিচের মাইক্রোফোন বোতামটি চাপুন।",
        tag_voice_in: "ভয়েস কমান্ড",
        tag_reasoning: "বহুভাষিক AI",
        tag_voice_out: "বাংলা ভয়েস উত্তর",
        mic_title: "বলার জন্য মাইক টিপুন",
        mic_sub: "ক্লাউড ভয়েস ও অফলাইন ইঞ্জিন উভয় সমর্থিত",
        mic_listening: "কৃষকের কথা শুনছি...",
        mic_listening_sub: "স্পষ্ট করে বলুন — পাঠাতে আবার টিপুন",
        input_placeholder: "ফসলের সমস্যা বা লক্ষণ এখানে লিখুন...",
        send_btn: "জিজ্ঞাসা করুন",
        processing_text: "কৃষি তথ্যভাণ্ডার থেকে সমাধান খুঁজছি...",
        replay_voice: "পুনরায় শুনুন",
        farmer_inquiry: "কৃষকের প্রশ্ন",
        local_context: "স্থানীয় কৃষি প্রসঙ্গ",
        confidence: "নির্ভুলতা",
        signal_fastapi_online: "সিগন্যাল: <strong>সংযুক্ত (FastAPI)</strong>",
        signal_fastapi_offline: "সিগন্যাল: <strong>অফলাইন (লোকাল ইঞ্জিন)</strong>",
        signal_web_online: "সিग्নাল: <strong>সংযুক্ত (ওয়েব মোড)</strong>",
        signal_web_offline: "সিগন্যাল: <strong>অফলাইন (ফিল্ড মোড)</strong>"
    }
};

const CHIP_QUERIES = {
    wheat_yellow_rust: {
        en: "How do I identify and treat Yellow Rust in wheat crops?",
        hi: "गेहूं की फसल में पीला रतुआ (येलो रस्ट) की पहचान और उपचार कैसे करें?",
        mr: "गहू पिकातील पिवळा तांबेरा कसा ओळखावा आणि त्यावर काय उपाय करावा?",
        te: "గోధుమ పంటలో పసుపు తుప్పు తెగులును ఎలా గుర్తించాలి మరియు నివారించాలి?",
        ta: "கோதுமை பயிரில் மஞ்சள் துரு நோயை எவ்வாறு கட்டுப்படுத்துவது?",
        kn: "ಗೋಧಿ ಬೆಳೆಯಲ್ಲಿ ಹಳದಿ ತುಕ್ಕು ರೋಗವನ್ನು ಹೇಗೆ ನಿರ್ವಹಿಸುವುದು?",
        pa: "ਕਣਕ ਦੀ ਫਸਲ ਵਿੱਚ ਪੀਲੀ ਕੁੰਗੀ ਦੀ ਰੋਕਥਾਮ ਕਿਵੇਂ ਕਰੀਏ?",
        gu: "ઘઉંના પાકમાં પીળો ગેરુ રોગ કેવી રીતે નિયંત્રિત કરવો?",
        bn: "গম ফসলে হলুদ মরিচা রোগ কীভাবে প্রতিকার করবেন?"
    },
    cotton_pink_bollworm: {
        en: "How to control Pink Bollworm in cotton crops?",
        hi: "कपास की फसल में गुलाबी सुंडी (पिंक बॉलवर्म) का नियंत्रण कैसे करें?",
        mr: "कापूस पिकातील गुलाबी बोंडअळीचे नियंत्रण कसे करावे?",
        te: "ప్రత్తి పంటలో గులాబీ రంగు కాయ తొలిచే పురుగు నివారణ ఎలా?",
        ta: "பருத்தியில் இளஞ்சிவப்பு காய் புழுவை எவ்வாறு கட்டுப்படுத்துவது?",
        kn: "ಹತ್ತಿ ಬೆಳೆಯಲ್ಲಿ ಗುಲಾಬಿ ಕಾಯಿ ಕೊರೆಯುವ ಹುಳುವಿನ ನಿರ್ವಹಣೆ ಹೇಗೆ?",
        pa: "ਨਰਮੇ ਵਿੱਚ ਗੁਲਾਬੀ ਸੁੰਡੀ ਦੀ ਰੋਕਥਾਮ ਕਿਵੇਂ ਕਰੀਏ?",
        gu: "કપાસમાં ગુલાબી ઈયળનું નિયંત્રણ કેવી રીતે કરવું?",
        bn: "তুলা ফসলে গোলাপি বলওয়ার্ম কীভাবে নিয়ন্ত্রণ করবেন?"
    },
    rice_blast: {
        en: "What are symptoms of Rice Blast disease and what is the spray dosage?",
        hi: "धान के ब्लास्ट (झुलसा) रोग के लक्षण क्या हैं और कौन सी दवा छिड़कें?",
        mr: "भात पिकावरील करपा रोगाची लक्षणे काय आहेत आणि फवारणीचे प्रमाण किती?",
        te: "వరి పంటలో అగ్గి తెగులు లక్షణాలు మరియు మందుల మోతాదు ఏమిటి?",
        ta: "நெல் குலை நோயின் அறிகுறிகள் மற்றும் மருந்து அளவு என்ன?",
        kn: "ಭತ್ತದ ಬೆಂಕಿರೋಗದ ಲಕ್ಷಣಗಳು ಮತ್ತು ಔಷಧಿಯ ಪ್ರಮಾಣವೇನು?",
        pa: "ਝੋਨੇ ਦੇ ਝੁਲਸ ਰੋਗ ਦੇ ਲੱਛਣ ਅਤੇ ਸਪਰੇਅ ਦੀ ਮਾਤਰਾ ਕੀ ਹੈ?",
        gu: "ડાંગરના પાકમાં કરપા રોગના લક્ષણો અને દવાનો છંટકાવ?",
        bn: "ধানের ব্লাস্ট রোগের লক্ষণ ও স্প্রে করার মাত্রা কী?"
    },
    tomato_early_blight: {
        en: "How do I treat Early Blight concentric spots on tomato plants?",
        hi: "टमाटर में अगेती झुलसा (अल्टरनेरिया) के धब्बों का इलाज कैसे करें?",
        mr: "टोमॅटो पिकावरील लवकर येणारा करपा (Early Blight) यावर उपाय काय?",
        te: "టమోటా పంటలో ముందస్తు మచ్చల తెగులు నివారణ ఎలా?",
        ta: "தக்காளி பயிரில் ஆரம்பகால கருகல் நோயை எவ்வாறு குணப்படுத்துவது?",
        kn: "ಟೊಮ್ಯಾಟೊ ಬೆಳೆಯಲ್ಲಿ ಮುಂಚಿನ ಬ್ಲೈಟ್ ರೋಗದ ಚಿಕಿತ್ಸೆ ಹೇಗೆ?",
        pa: "ਟਮਾਟਰ ਦੇ ਅਗੇਤੇ ਝੁਲਸ ਰੋਗ ਦਾ ਇਲਾਜ ਕਿਵੇਂ ਕਰੀਏ?",
        gu: "ટામેટામાં આગોતરો સુકારો રોગનો ઉપચાર કેવી રીતે કરવો?",
        bn: "টমেটো গাছে আর্লি ব্লাইট রোগের চিকিৎসা কীভাবে করবেন?"
    },
    soil_nitrogen_deficiency: {
        en: "What are signs of Nitrogen deficiency in crops and how to fix with Urea?",
        hi: "फसलों में नाइट्रोजन की कमी के लक्षण क्या हैं और यूरिया का उपयोग कैसे करें?",
        mr: "पिकांमध्ये नायट्रोजनच्या कमतरतेची लक्षणे काय आहेत आणि युरियाचा वापर कसा करावा?",
        te: "పంటలలో నత్రజని లోపం లక్షణాలు మరియు యూరియాతో ఎలా సరిచేయాలి?",
        ta: "பயிர்களில் தழைச்சத்து குறைபாட்டின் அறிகுறிகள் மற்றும் யூரியா பயன்பாடு?",
        kn: "ಬೆಳೆಗಳಲ್ಲಿ ಸಾರಜನಕದ ಕೊರತೆಯ ಲಕ್ಷಣಗಳು ಮತ್ತು ಯೂರಿಯಾ ಬಳಕೆ ಹೇಗೆ?",
        pa: "ਫਸਲਾਂ ਵਿੱਚ ਨਾਈਟ੍ਰੋਜਨ ਦੀ ਘਾਟ ਦੇ ਲੱਛਣ ਅਤੇ ਯੂਰੀਆ ਦੀ ਵਰਤੋਂ ਕਿਵੇਂ ਕਰੀਏ?",
        gu: "પાકમાં નાઇટ્રોજનની ઉણપના ચિહ્નો અને યુરિયાનો ઉપયોગ કેવી રીતે કરવો?",
        bn: "ফসলে নাইট্রোজেনের ঘাটতির লক্ষণ এবং ইউরিয়ার সঠিক প্রয়োগ?"
    },
    drip_irrigation_guidance: {
        en: "What are the benefits and maintenance steps for drip irrigation systems?",
        hi: "ड्रिप (टपक) सिंचाई के लाभ और पाइप लाइन की सफाई के उपाय क्या हैं?",
        mr: "ठिबक सिंचनाचे फायदे आणि ड्रीप लाईन स्वच्छ ठेवण्याच्या पद्धती काय आहेत?",
        te: "బిందు సేద్యం (డ్రిప్) ప్రయోజనాలు మరియు నిర్వహణ పద్ధతులు ఏమిటి?",
        ta: "சொட்டு நீர் பாசனத்தின் நன்மைகள் மற்றும் பராமரிப்பு முறைகள் என்ன?",
        kn: "ಹನಿ ನೀರಾವರಿಯ ಪ್ರಯೋಜನಗಳು ಮತ್ತು ನಿರ್ವಹಣಾ ಕ್ರಮಗಳು ಯಾವುವು?",
        pa: "ਤੁਪਕਾ ਸਿੰਚਾਈ ਦੇ ਲਾਭ ਅਤੇ ਸਾਂਭ-ਸੰਭਾਲ ਦੇ ਤਰੀਕੇ ਕੀ ਹਨ?",
        gu: "ટપક સિંચાઈ પદ્ધતિના ફાયદા અને જાળવણીના પગલાં?",
        bn: "ড্রিপ সেচ ব্যবস্থার সুবিধা এবং পাইপ পরিষ্কারের নিয়ম?"
    },
    pm_kisan_scheme: {
        en: "What is the PM-KISAN subsidy scheme and what documents are required?",
        hi: "पीएम-किसान ₹6000 योजना क्या है और आवेदन के लिए कौन से दस्तावेज चाहिए?",
        mr: "पीएम-किसान ₹6000 योजना काय आहे आणि त्यासाठी कोणती कागदपत्रे लागतात?",
        te: "పీఎం-కిసాన్ ₹6000 పథకం ఏమిటి మరియు ఏ పత్రాలు అవసరం?",
        ta: "பிஎம் கிசான் ₹6000 திட்டம் என்ன மற்றும் தேவையான ஆவணங்கள் யாவை?",
        kn: "ಪಿಎಂ ಕಿಸಾನ್ ₹6000 ಯೋಜನೆ ಎಂದರೇನು ಮತ್ತು ಅಗತ್ಯ ದಾಖಲೆಗಳು ಯಾವುವು?",
        pa: "ਪ੍ਰਧਾਨ ਮੰਤਰੀ ਕਿਸਾਨ ₹6000 ਯੋਜਨਾ ਕੀ ਹੈ ਅਤੇ ਕਿਹੜੇ ਕਾਗਜ਼ਾਤ ਚਾਹੀਦੇ ਹਨ?",
        gu: "પીએમ કિસાન ₹6000 યોજના શું છે અને કયા દસ્તાવેજો જોઈએ?",
        bn: "পিএম-কিসান ₹৬০০০ প্রকল্প কী এবং কী কী নথি প্রয়োজন?"
    },
    pm_fby_crop_insurance: {
        en: "How does PMFBY Crop Insurance work and what is the claim deadline?",
        hi: "पीएम फसल बीमा योजना (PMFBY) का लाभ कैसे लें और क्लेम की समयसीमा क्या है?",
        mr: "पंतप्रधान पीक विमा योजना (PMFBY) चे नियम आणि नुकसान भरपाईची मुदत काय आहे?",
        te: "పీఎం ఫసల్ బీమా యోజన ఎలా పనిచేస్తుంది మరియు క్లెయిమ్ గడువు ఎంత?",
        ta: "பிரதான் மந்திரி பயிர் காப்பீட்டுத் திட்டம் எவ்வாறு செயல்படுகிறது?",
        kn: "ಪ್ರಧಾನ ಮಂತ್ರಿ ಬೆಳೆ ವಿಮೆ ಯೋಜನೆ ಹೇಗೆ ಕಾರ್ಯನಿರ್ವಹಿಸುತ್ತದೆ?",
        pa: "ਪ੍ਰਧਾਨ ਮੰਤਰੀ ਫਸਲ ਬੀਮਾ ਯੋਜਨਾ ਦੇ ਨਿਯਮ ਅਤੇ ਕਲੇਮ ਦੀ ਆਖਰੀ ਮਿਤੀ?",
        gu: "પીએમ ફસલ બીમા યોજના કેવી રીતે કામ કરે છે અને ક્લેમ કરવાની મુદત?",
        bn: "প্রধানমন্ত্রী ফসল বীমা যোজনা কীভাবে কাজ করে এবং ক্ষতিপূরণের সময়সীমা?"
    }
};

const LANG_SPEECH_CODES = {
    en: "en-IN",
    hi: "hi-IN",
    mr: "mr-IN",
    te: "te-IN",
    ta: "ta-IN",
    kn: "kn-IN",
    pa: "pa-IN",
    gu: "gu-IN",
    bn: "bn-IN"
};

let currentLanguage = localStorage.getItem("agri_lang") || "en";

function applyLanguage(lang) {
    if (!TRANSLATIONS[lang]) lang = "en";
    currentLanguage = lang;
    localStorage.setItem("agri_lang", lang);
    if (languageSelect) languageSelect.value = lang;

    const t = TRANSLATIONS[lang];
    document.title = t.title;
    document.documentElement.lang = lang;

    // 1. Translate all data-i18n elements
    document.querySelectorAll("[data-i18n]").forEach(el => {
        const key = el.getAttribute("data-i18n");
        if (t[key]) {
            el.innerHTML = t[key];
        }
    });

    // 2. Translate all placeholders
    document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
        const key = el.getAttribute("data-i18n-placeholder");
        if (t[key]) {
            el.placeholder = t[key];
        }
    });

    // 3. Update quick action chip queries
    document.querySelectorAll(".chip-btn").forEach(btn => {
        const chipKey = btn.getAttribute("data-chip");
        if (chipKey && CHIP_QUERIES[chipKey] && CHIP_QUERIES[chipKey][lang]) {
            btn.setAttribute("data-query", CHIP_QUERIES[chipKey][lang]);
        }
    });

    // 4. Update Speech Recognition language
    if (speechRecognition) {
        speechRecognition.lang = LANG_SPEECH_CODES[lang] || "en-IN";
    }

    // 5. Update processing text if visible
    if (processingText) {
        processingText.textContent = t.processing_text;
    }
}

// Language selector change listener
if (languageSelect) {
    languageSelect.addEventListener("change", (e) => {
        applyLanguage(e.target.value);
    });
}

// 1. Live System Status Polling
async function checkSystemStatus() {
    const dot = netStatusPill.querySelector(".pulse-dot");
    const t = TRANSLATIONS[currentLanguage] || TRANSLATIONS.en;
    try {
        const res = await fetch("/api/status", { cache: "no-store" });
        if (!res.ok) throw new Error("No backend");
        const data = await res.json();
        hasBackend = true;
        dot.className = "pulse-dot " + (data.internet_connected ? "online" : "offline");
        netStatusLabel.innerHTML = data.internet_connected ? t.signal_fastapi_online : t.signal_fastapi_offline;
    } catch (e) {
        hasBackend = false;
        const isOnline = navigator.onLine;
        dot.className = "pulse-dot " + (isOnline ? "online" : "offline");
        netStatusLabel.innerHTML = isOnline ? t.signal_web_online : t.signal_web_offline;
    }
}

setInterval(checkSystemStatus, 5000);
checkSystemStatus();

// Initialize active language
applyLanguage(currentLanguage);

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
    const t = TRANSLATIONS[currentLanguage] || TRANSLATIONS.en;
    const card = document.createElement("div");
    card.className = "dialogue-card user-entry";
    card.innerHTML = `
        <strong><i class="fa-solid fa-user"></i> ${t.farmer_inquiry}</strong>
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
        utterance.lang = LANG_SPEECH_CODES[currentLanguage] || "en-IN";
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
    const t = TRANSLATIONS[currentLanguage] || TRANSLATIONS.en;
    processingBar.classList.remove("hidden");
    processingText.textContent = t.processing_text;

    if (hasBackend) {
        try {
            const res = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query: query, mode: smartModeSelect.value, language: currentLanguage })
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
        speechRecognition.lang = LANG_SPEECH_CODES[currentLanguage] || "en-IN";

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
    const t = TRANSLATIONS[currentLanguage] || TRANSLATIONS.en;
    isRecording = true;
    recognizedText = "";
    audioChunks = [];
    micButton.classList.add("recording");
    micStatusTitle.textContent = t.mic_listening;
    micStatusSubtitle.textContent = t.mic_listening_sub;

    if (speechRecognition) {
        speechRecognition.lang = LANG_SPEECH_CODES[currentLanguage] || "en-IN";
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
    const t = TRANSLATIONS[currentLanguage] || TRANSLATIONS.en;
    isRecording = false;
    micButton.classList.remove("recording");
    micStatusTitle.textContent = t.mic_title;
    micStatusSubtitle.textContent = t.mic_sub;

    if (speechRecognition) {
        try { speechRecognition.stop(); } catch (e) {}
    }

    if (mediaRecorder && mediaRecorder.state !== "inactive") {
        try { mediaRecorder.stop(); } catch (e) {}
    }
}

async function executeVoiceUpload(audioBlob) {
    const t = TRANSLATIONS[currentLanguage] || TRANSLATIONS.en;
    processingBar.classList.remove("hidden");
    processingText.textContent = t.processing_text;

    const formData = new FormData();
    formData.append("audio_file", audioBlob, "farmer_audio.wav");
    formData.append("mode", smartModeSelect.value);
    formData.append("language", currentLanguage);

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

// ==========================================================================
// Phase 1: Farm Profile & Growth Stage Manager (100% Offline Capable)
// ==========================================================================

const CROP_LIFECYCLE_CLIENT = {
    "Cotton": {
        duration_days: 160,
        stages: [
            { name: "Germination & Emergence", start: 0, end: 12, desc: "Seed sprouting & root establishment." },
            { name: "Early Vegetative", start: 13, end: 35, desc: "Main stem growth & first true leaves." },
            { name: "Squaring & Branching", start: 36, end: 65, desc: "Floral buds (squares) & canopy growth." },
            { name: "Flowering & Boll Setting", start: 66, end: 105, desc: "Peak flowering & boll formation." },
            { name: "Boll Maturation & Opening", start: 106, end: 140, desc: "Boll filling & early bursting." },
            { name: "Harvest Readiness", start: 141, end: 180, desc: "Open bolls ready for picking." }
        ]
    },
    "Wheat": {
        duration_days: 125,
        stages: [
            { name: "Crown Root Initiation (CRI)", start: 0, end: 22, desc: "First critical irrigation stage." },
            { name: "Tillering Stage", start: 23, end: 45, desc: "Secondary shoot production." },
            { name: "Jointing & Stem Elongation", start: 46, end: 70, desc: "Rapid canopy & stem expansion." },
            { name: "Booting & Heading", start: 71, end: 90, desc: "Spikes & ears emergence." },
            { name: "Grain Milking & Dough Stage", start: 91, end: 110, desc: "Kernel starch accumulation." },
            { name: "Maturity & Harvest", start: 111, end: 135, desc: "Golden straw, harvest ready." }
        ]
    },
    "Rice / Paddy": {
        duration_days: 130,
        stages: [
            { name: "Nursery & Transplanting", start: 0, end: 25, desc: "Seedling growth & transplanting." },
            { name: "Tillering & Rooting", start: 26, end: 50, desc: "Active tillers & root expansion." },
            { name: "Stem Elongation & Panicle", start: 51, end: 75, desc: "Panicle initiation & flag leaf." },
            { name: "Heading & Flowering", start: 76, end: 95, desc: "Flowering & pollination." },
            { name: "Milk & Dough Grain Filling", start: 96, end: 115, desc: "Starch filling in grain." },
            { name: "Ripening & Harvesting", start: 116, end: 140, desc: "Golden yellow panicles." }
        ]
    },
    "Tomato": {
        duration_days: 110,
        stages: [
            { name: "Nursery & Establishment", start: 0, end: 20, desc: "Transplant shock recovery." },
            { name: "Active Vegetative & Branching", start: 21, end: 40, desc: "Foliage expansion & side shoots." },
            { name: "First Flowering & Fruit Set", start: 41, end: 60, desc: "Yellow blossoms & fruit set." },
            { name: "Fruit Development & Sizing", start: 61, end: 85, desc: "Rapid fruit expansion." },
            { name: "Color Break & Harvesting", start: 86, end: 120, desc: "Breaker to red ripe harvest." }
        ]
    },
    "Sugarcane": {
        duration_days: 360,
        stages: [
            { name: "Germination Phase", start: 0, end: 45, desc: "Sett sprouting & root emergence." },
            { name: "Tillering Phase", start: 46, end: 120, desc: "Profuse tillering & canopy cover." },
            { name: "Grand Growth Phase", start: 121, end: 270, desc: "Rapid cane elongation." },
            { name: "Ripening & Maturation", start: 271, end: 365, desc: "Sucrose accumulation." }
        ]
    },
    "Soybean": {
        duration_days: 95,
        stages: [
            { name: "Emergence & Cotyledon", start: 0, end: 12, desc: "Seedling emergence." },
            { name: "Vegetative & Nodulation", start: 13, end: 35, desc: "Trifoliate leaves & nitrogen nodes." },
            { name: "Flowering (R1-R2)", start: 36, end: 55, desc: "Purple/white blooms on nodes." },
            { name: "Pod Formation & Seed Filling", start: 56, end: 80, desc: "Pod elongation & seed growth." },
            { name: "Full Maturity & Defoliation", start: 81, end: 105, desc: "Brown pods ready to thresh." }
        ]
    },
    "Maize": {
        duration_days: 105,
        stages: [
            { name: "Seedling & Emergence", start: 0, end: 18, desc: "Coleoptile emergence." },
            { name: "Knee-High Vegetative", start: 19, end: 42, desc: "Rapid vertical stalk growth." },
            { name: "Tasseling & Silking", start: 43, end: 65, desc: "Tassel pollen shed & silking." },
            { name: "Blister & Milk Kernel Filling", start: 66, end: 85, desc: "Starch fluid in kernels." },
            { name: "Black Layer & Harvest", start: 86, end: 115, desc: "Physiological maturity & drying." }
        ]
    },
    "Onion": {
        duration_days: 120,
        stages: [
            { name: "Transplanting & Rooting", start: 0, end: 20, desc: "Seedling rooting." },
            { name: "Foliage Development", start: 21, end: 50, desc: "Leaf blade expansion." },
            { name: "Bulb Initiation", start: 51, end: 80, desc: "Bulb base swelling." },
            { name: "Bulb Enlargement", start: 81, end: 105, desc: "Rapid bulb sizing." },
            { name: "Neck Fall & Curing", start: 106, end: 130, desc: "50% top fall & curing." }
        ]
    },
    "General / Other Crop": {
        duration_days: 120,
        stages: [
            { name: "Germination & Seedling", start: 0, end: 20, desc: "Sprouting & establishment." },
            { name: "Vegetative Growth", start: 21, end: 50, desc: "Canopy & foliage growth." },
            { name: "Flowering & Reproductive", start: 51, end: 80, desc: "Bloom & fruit setting." },
            { name: "Maturation & Ripening", start: 81, end: 110, desc: "Yield filling & color change." },
            { name: "Harvest Readiness", start: 111, end: 130, desc: "Crop ready for harvesting." }
        ]
    }
};

let currentFarmProfile = {
    farm_name: "Green Acres Farm",
    farmer_name: "Farmer",
    location: "Nashik, Maharashtra",
    farm_size: 3.0,
    soil_type: "Black Soil / Regur",
    irrigation_method: "Drip Irrigation",
    current_crop: "Cotton",
    variety: "BT Cotton Hybrid",
    sowing_date: new Date(Date.now() - 40 * 86400000).toISOString().split("T")[0],
    expected_harvest_date: ""
};

function calculateClientCropMetrics(profile) {
    const sowingDate = new Date(profile.sowing_date || Date.now());
    const today = new Date();
    const ageDays = Math.max(0, Math.floor((today - sowingDate) / (1000 * 60 * 60 * 24)));
    
    const cropConfig = CROP_LIFECYCLE_CLIENT[profile.current_crop] || CROP_LIFECYCLE_CLIENT["General / Other Crop"];
    const totalDuration = cropConfig.duration_days;
    const stages = cropConfig.stages;

    let currentStage = stages[stages.length - 1];
    let stageIdx = stages.length - 1;

    for (let i = 0; i < stages.length; i++) {
        if (ageDays >= stages[i].start && ageDays <= stages[i].end) {
            currentStage = stages[i];
            stageIdx = i;
            break;
        } else if (ageDays < stages[i].start) {
            currentStage = stages[Math.max(0, i - 1)];
            stageIdx = Math.max(0, i - 1);
            break;
        }
    }

    const progressPct = Math.min(100, Math.round((ageDays / totalDuration) * 100));
    const daysRemaining = Math.max(0, totalDuration - ageDays);

    const summary = `Farm: '${profile.farm_name}' in ${profile.location}. Farm Size: ${profile.farm_size} acres, Soil: ${profile.soil_type}, Irrigation: ${profile.irrigation_method}. Crop: ${profile.current_crop} (Variety: ${profile.variety}), Sown on ${profile.sowing_date} (Day ${ageDays} of ~${totalDuration} days, ${progressPct}% completed). Current Growth Stage: '${currentStage.name}' (${currentStage.desc}). Estimated ${daysRemaining} days remaining until harvest.`;

    return {
        crop_age_days: ageDays,
        total_duration_days: totalDuration,
        progress_percentage: progressPct,
        current_stage_name: currentStage.name,
        current_stage_description: currentStage.desc,
        days_to_harvest: daysRemaining,
        personalized_summary: summary
    };
}

function updateFarmProfileUI(profile, metrics) {
    // 1. Top Nav Badge
    const navFarmName = document.getElementById("navFarmName");
    const navFarmCropStage = document.getElementById("navFarmCropStage");
    if (navFarmName) navFarmName.textContent = profile.farm_name || "My Farm";
    if (navFarmCropStage) navFarmCropStage.textContent = `${profile.current_crop} (Day ${metrics.crop_age_days})`;

    // 2. Sidebar Journey Card
    const sidebarFarmName = document.getElementById("sidebarFarmName");
    const sidebarCropPill = document.getElementById("sidebarCropPill");
    const sidebarAgeBadge = document.getElementById("sidebarAgeBadge");
    const sidebarStageName = document.getElementById("sidebarStageName");
    const sidebarStagePct = document.getElementById("sidebarStagePct");
    const sidebarProgressFill = document.getElementById("sidebarProgressFill");
    const sidebarDaysRemaining = document.getElementById("sidebarDaysRemaining");
    const sidebarLocation = document.getElementById("sidebarLocation");

    if (sidebarFarmName) sidebarFarmName.textContent = profile.farm_name;
    if (sidebarCropPill) sidebarCropPill.textContent = `${profile.current_crop} (${profile.variety || 'Hybrid'})`;
    if (sidebarAgeBadge) sidebarAgeBadge.textContent = `Day ${metrics.crop_age_days}`;
    if (sidebarStageName) sidebarStageName.textContent = metrics.current_stage_name;
    if (sidebarStagePct) sidebarStagePct.textContent = `${metrics.progress_percentage}%`;
    if (sidebarProgressFill) sidebarProgressFill.style.width = `${metrics.progress_percentage}%`;
    if (sidebarDaysRemaining) sidebarDaysRemaining.innerHTML = `<i class="fa-regular fa-clock"></i> ${metrics.days_to_harvest} days left`;
    if (sidebarLocation) sidebarLocation.innerHTML = `<i class="fa-solid fa-location-dot"></i> ${profile.location.split(',')[0]}`;
}

async function loadFarmProfile() {
    const saved = localStorage.getItem("agriedge_farm_profile");
    if (saved) {
        try {
            currentFarmProfile = JSON.parse(saved);
        } catch (e) {}
    }

    if (hasBackend) {
        try {
            const res = await fetch("/api/farm/profile");
            if (res.ok) {
                const data = await res.json();
                if (data.profile) {
                    currentFarmProfile = data.profile;
                    localStorage.setItem("agriedge_farm_profile", JSON.stringify(currentFarmProfile));
                    updateFarmProfileUI(currentFarmProfile, data.metrics);
                    return;
                }
            }
        } catch (e) {
            console.log("Using local offline farm profile state:", e);
        }
    }

    const clientMetrics = calculateClientCropMetrics(currentFarmProfile);
    updateFarmProfileUI(currentFarmProfile, clientMetrics);
}

async function saveFarmProfileData(profileData) {
    currentFarmProfile = profileData;
    localStorage.setItem("agriedge_farm_profile", JSON.stringify(currentFarmProfile));
    
    let metrics = calculateClientCropMetrics(currentFarmProfile);
    
    if (hasBackend) {
        try {
            const res = await fetch("/api/farm/profile", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(currentFarmProfile)
            });
            if (res.ok) {
                const data = await res.json();
                metrics = data.metrics;
            }
        } catch (e) {
            console.warn("Saved profile locally (offline):", e);
        }
    }

    updateFarmProfileUI(currentFarmProfile, metrics);
}

// Farm Profile Modal Controller
const farmProfileModal = document.getElementById("farmProfileModal");
const openProfileBtn = document.getElementById("openProfileBtn");
const sidebarEditProfileBtn = document.getElementById("sidebarEditProfileBtn");
const closeProfileModalBtn = document.getElementById("closeProfileModalBtn");
const cancelProfileBtn = document.getElementById("cancelProfileBtn");
const farmProfileForm = document.getElementById("farmProfileForm");

function openProfileModal() {
    if (!farmProfileModal) return;
    document.getElementById("inputFarmName").value = currentFarmProfile.farm_name || "";
    document.getElementById("inputFarmerName").value = currentFarmProfile.farmer_name || "";
    document.getElementById("inputLocation").value = currentFarmProfile.location || "";
    document.getElementById("inputFarmSize").value = currentFarmProfile.farm_size || 3.0;
    document.getElementById("inputSoilType").value = currentFarmProfile.soil_type || "Black Soil / Regur";
    document.getElementById("inputIrrigation").value = currentFarmProfile.irrigation_method || "Drip Irrigation";
    document.getElementById("inputCrop").value = currentFarmProfile.current_crop || "Cotton";
    document.getElementById("inputVariety").value = currentFarmProfile.variety || "";
    document.getElementById("inputSowingDate").value = currentFarmProfile.sowing_date || "";
    document.getElementById("inputExpectedHarvest").value = currentFarmProfile.expected_harvest_date || "";

    farmProfileModal.classList.remove("hidden");
}

function closeProfileModal() {
    if (farmProfileModal) farmProfileModal.classList.add("hidden");
}

if (openProfileBtn) openProfileBtn.addEventListener("click", openProfileModal);
if (sidebarEditProfileBtn) sidebarEditProfileBtn.addEventListener("click", openProfileModal);
if (closeProfileModalBtn) closeProfileModalBtn.addEventListener("click", closeProfileModal);
if (cancelProfileBtn) cancelProfileBtn.addEventListener("click", closeProfileModal);

if (farmProfileForm) {
    farmProfileForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const updated = {
            farm_name: document.getElementById("inputFarmName").value.trim() || "My Farm",
            farmer_name: document.getElementById("inputFarmerName").value.trim() || "Farmer",
            location: document.getElementById("inputLocation").value.trim() || "India",
            farm_size: parseFloat(document.getElementById("inputFarmSize").value) || 1.0,
            soil_type: document.getElementById("inputSoilType").value,
            irrigation_method: document.getElementById("inputIrrigation").value,
            current_crop: document.getElementById("inputCrop").value,
            variety: document.getElementById("inputVariety").value.trim() || "Standard",
            sowing_date: document.getElementById("inputSowingDate").value || new Date().toISOString().split("T")[0],
            expected_harvest_date: document.getElementById("inputExpectedHarvest").value || null
        };

        await saveFarmProfileData(updated);
        closeProfileModal();
    });
}

// Load Farm Profile on application start
loadFarmProfile();


