/**
 * SkillMate AI — Main Application JavaScript
 * Voice-First Multimodal Design
 * Handles: Voice input (Web Speech API), voice states, theme, API calls, result rendering, audio playback
 */

// ============================================================
// Configuration
// ============================================================
const API_BASE = (
    window.location.hostname === 'localhost' ||
    window.location.hostname === '127.0.0.1' ||
    window.location.hostname === '' ||
    window.location.protocol === 'file:'
    ? 'http://localhost:5000'
    : 'https://skillmate-ai-3s2f.onrender.com'; // Update with your Render URL

// ============================================================
// DOM Elements
// ============================================================
const textInput = document.getElementById('textInput');
const btnMic = document.getElementById('btnMic');
const btnSubmit = document.getElementById('btnSubmit');
const btnNew = document.getElementById('btnNew');
const btnPlay = document.getElementById('btnPlay');
const loadingContainer = document.getElementById('loadingContainer');
const resultsSection = document.getElementById('resultsSection');
const inputSection = document.getElementById('inputSection');
const heroSection = document.getElementById('hero');
const audioPlayer = document.getElementById('audioPlayer');
const audioSection = document.getElementById('audioSection');
const menuToggle = document.getElementById('menuToggle');
const navLinks = document.getElementById('navLinks');
const inputContainer = document.getElementById('inputContainer');
const inputWaveform = document.getElementById('inputWaveform');
const waveformBars = inputWaveform ? Array.from(inputWaveform.querySelectorAll('.wave-bar')) : [];
const voiceStateEl = document.getElementById('voiceState');
const voiceStateLabel = document.getElementById('voiceStateLabel');

// Result elements
const detectedLang = document.getElementById('detectedLang');
const langConfidence = document.getElementById('langConfidence');
const translatedText = document.getElementById('translatedText');
const skillName = document.getElementById('skillName');
const skillCategory = document.getElementById('skillCategory');
const skillDescription = document.getElementById('skillDescription');
const resourcesList = document.getElementById('resourcesList');
const audioTitle = document.getElementById('audioTitle');
const audioSubtitle = document.getElementById('audioSubtitle');

// Loading steps
const loadingSteps = ['step1', 'step2', 'step3', 'step4', 'step5'];

// SVG icon strings for play/pause
const SVG_PLAY = '<svg viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"/></svg>';
const SVG_PAUSE = '<svg viewBox="0 0 24 24"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>';
const SVG_MIC = '<svg viewBox="0 0 24 24"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>';
const SVG_STOP = '<svg viewBox="0 0 24 24"><rect x="6" y="6" width="12" height="12" rx="2"/></svg>';

// Resource SVG icons
const SVG_DOC = '<svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>';
const SVG_VIDEO = '<svg viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"/></svg>';
const SVG_GLOBE = '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>';

const RECOGNITION_LANG_MAP = {
    hi: 'hi-IN',
    kn: 'kn-IN',
    en: 'en-IN',
    ta: 'ta-IN',
    te: 'te-IN'
};

const VOICE_PREF_KEY = 'skillmate-voice-lang-mode';
const VOICE_MANUAL_KEY = 'skillmate-voice-lang-manual';
const VOICE_LAST_DETECTED_KEY = 'skillmate-voice-last-detected';

// ============================================================
// State
// ============================================================
let isRecording = false;
let recognition = null;
let currentAudioB64 = null;
let isPlaying = false;
let accumulatedTranscript = '';
let pendingSubmitAfterVoice = false;
let isRecognitionStarting = false;
let wasManuallyStopped = false;
let isSubmitting = false;
let recordingBaseText = '';
let selectedVoiceLang = 'auto';
let lastManualVoiceLang = 'en';
let lastDetectedVoiceLang = '';
let micAudioContext = null;
let micAnalyser = null;
let micSourceNode = null;
let micStream = null;
let waveformRafId = 0;
let waveformSessionId = 0;
let waveformNoiseFloor = 8;
let waveformPeakLevel = 70;
let waveformSmoothedLevel = 0;

// ============================================================
// Theme Toggle (shared across pages)
// ============================================================
function initTheme() {
    const themeToggle = document.getElementById('themeToggle');
    if (!themeToggle) return;

    const savedTheme = localStorage.getItem('skillmate-theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);

    themeToggle.addEventListener('click', () => {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('skillmate-theme', next);
    });
}

// ============================================================
// Voice State Management
// ============================================================
function setVoiceState(state, label) {
    if (!voiceStateEl) return;
    voiceStateEl.setAttribute('data-state', state);
    voiceStateEl.classList.toggle('visible', state !== 'idle');
    if (voiceStateLabel) voiceStateLabel.textContent = label || state;

    if (inputWaveform) {
        inputWaveform.setAttribute('data-state', state);
    }

    // Update input container visual state
    if (inputContainer) {
        inputContainer.classList.toggle('listening', state === 'listening');
    }
}

function appendTranscript(base, chunk) {
    const cleanChunk = (chunk || '').trim();
    if (!cleanChunk) return base;
    const cleanBase = (base || '').trim();
    if (!cleanBase) return cleanChunk;
    const separator = /[\s]$/.test(cleanBase) || /^[,.;:!?]/.test(cleanChunk) ? '' : ' ';
    return `${cleanBase}${separator}${cleanChunk}`;
}

function normalizeSupportedLang(code) {
    if (!code) return '';
    const normalized = String(code).toLowerCase().trim().slice(0, 2);
    return RECOGNITION_LANG_MAP[normalized] ? normalized : '';
}

function setActiveLanguageBadge(langCode) {
    document.querySelectorAll('.lang-badge').forEach(b => b.classList.remove('active'));
    const targetBadge = document.querySelector(`.lang-badge[data-lang="${langCode}"]`)
        || document.querySelector('.lang-badge[data-lang="auto"]');
    if (targetBadge) {
        targetBadge.classList.add('active');
    }
}

function setVoiceLanguagePreference(langCode, options = {}) {
    const { persist = true } = options;
    const normalizedMode = langCode === 'auto' ? 'auto' : normalizeSupportedLang(langCode);
    selectedVoiceLang = normalizedMode || 'auto';

    if (selectedVoiceLang !== 'auto') {
        lastManualVoiceLang = selectedVoiceLang;
    }

    setActiveLanguageBadge(selectedVoiceLang);

    if (persist) {
        localStorage.setItem(VOICE_PREF_KEY, selectedVoiceLang);
        localStorage.setItem(VOICE_MANUAL_KEY, lastManualVoiceLang);
        if (lastDetectedVoiceLang) {
            localStorage.setItem(VOICE_LAST_DETECTED_KEY, lastDetectedVoiceLang);
        }
    }
}

function getBrowserPreferredVoiceLang() {
    const browserLang = normalizeSupportedLang(
        navigator.language || (Array.isArray(navigator.languages) ? navigator.languages[0] : '')
    );
    return browserLang || 'en';
}

function initVoiceLanguagePreference() {
    const savedMode = localStorage.getItem(VOICE_PREF_KEY) || 'auto';
    const savedManual = normalizeSupportedLang(localStorage.getItem(VOICE_MANUAL_KEY)) || 'en';
    const savedDetected = normalizeSupportedLang(localStorage.getItem(VOICE_LAST_DETECTED_KEY));

    lastManualVoiceLang = savedManual;
    lastDetectedVoiceLang = savedDetected || '';

    if (savedMode === 'auto') {
        setVoiceLanguagePreference('auto', { persist: true });
    } else {
        setVoiceLanguagePreference(savedManual, { persist: true });
    }
}

function getSelectedRecognitionLang() {
    if (selectedVoiceLang !== 'auto') {
        return RECOGNITION_LANG_MAP[selectedVoiceLang] || 'en-IN';
    }

    const autoLangCode = lastDetectedVoiceLang || getBrowserPreferredVoiceLang();
    return RECOGNITION_LANG_MAP[autoLangCode] || 'en-IN';
}

function stopAudioPlayback() {
    audioPlayer.pause();
    audioPlayer.currentTime = 0;
    isPlaying = false;
    btnPlay.innerHTML = SVG_PLAY;
    btnPlay.classList.remove('speaking');
}

function resetWaveformBars() {
    if (!waveformBars.length) return;
    waveformBars.forEach((bar) => {
        bar.style.height = '';
        bar.style.opacity = '';
    });
}

function clamp(value, min, max) {
    return Math.min(max, Math.max(min, value));
}

function stopLiveWaveform({ resetBars = true } = {}) {
    waveformSessionId += 1;

    if (waveformRafId) {
        cancelAnimationFrame(waveformRafId);
        waveformRafId = 0;
    }

    if (micSourceNode) {
        micSourceNode.disconnect();
        micSourceNode = null;
    }

    micAnalyser = null;

    if (micStream) {
        micStream.getTracks().forEach((track) => track.stop());
        micStream = null;
    }

    if (micAudioContext) {
        const context = micAudioContext;
        micAudioContext = null;
        context.close().catch(() => {});
    }

    if (inputWaveform) {
        inputWaveform.setAttribute('data-live', 'off');
    }

    if (resetBars) {
        resetWaveformBars();
    }

    waveformNoiseFloor = 8;
    waveformPeakLevel = 70;
    waveformSmoothedLevel = 0;
}

async function startLiveWaveform() {
    if (!inputWaveform || !waveformBars.length) return;
    if (!navigator.mediaDevices?.getUserMedia) return;

    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (!AudioContextClass) return;

    stopLiveWaveform({ resetBars: false });
    const sessionId = ++waveformSessionId;

    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true
            }
        });

        if (sessionId !== waveformSessionId || !isRecording) {
            stream.getTracks().forEach((track) => track.stop());
            return;
        }

        const audioContext = new AudioContextClass();
        const analyser = audioContext.createAnalyser();
        analyser.fftSize = 256;
        analyser.smoothingTimeConstant = 0.72;

        const sourceNode = audioContext.createMediaStreamSource(stream);
        sourceNode.connect(analyser);

        micStream = stream;
        micAudioContext = audioContext;
        micAnalyser = analyser;
        micSourceNode = sourceNode;

        inputWaveform.setAttribute('data-live', 'on');

        const frequencyData = new Uint8Array(analyser.frequencyBinCount);

        const animate = () => {
            if (sessionId !== waveformSessionId || !micAnalyser) return;

            micAnalyser.getByteFrequencyData(frequencyData);
            const binsPerBar = Math.max(1, Math.floor(frequencyData.length / waveformBars.length));

            let totalEnergy = 0;
            for (let i = 0; i < frequencyData.length; i++) {
                totalEnergy += frequencyData[i];
            }
            const overallLevel = totalEnergy / frequencyData.length;

            if (overallLevel < waveformNoiseFloor + 8) {
                waveformNoiseFloor = (waveformNoiseFloor * 0.985) + (overallLevel * 0.015);
            } else {
                waveformNoiseFloor = (waveformNoiseFloor * 0.995) + (overallLevel * 0.005);
            }

            waveformPeakLevel = Math.max(
                overallLevel,
                waveformPeakLevel * 0.993,
                waveformNoiseFloor + 24
            );

            const normalizedOverall = clamp(
                (overallLevel - waveformNoiseFloor) / Math.max(20, waveformPeakLevel - waveformNoiseFloor),
                0,
                1
            );

            waveformSmoothedLevel = (waveformSmoothedLevel * 0.74) + (normalizedOverall * 0.26);

            for (let i = 0; i < waveformBars.length; i++) {
                const start = i * binsPerBar;
                const end = Math.min(frequencyData.length, start + binsPerBar);
                let sum = 0;

                for (let j = start; j < end; j++) {
                    sum += frequencyData[j];
                }

                const average = sum / Math.max(1, end - start);
                const barLevel = clamp(
                    (average - waveformNoiseFloor) / Math.max(18, waveformPeakLevel - waveformNoiseFloor),
                    0,
                    1
                );
                const mixedLevel = clamp(
                    (waveformSmoothedLevel * 0.52) + (barLevel * 0.86) + ((Math.random() - 0.5) * 0.06),
                    0,
                    1
                );
                const height = 7 + (mixedLevel * 25);

                waveformBars[i].style.height = `${height.toFixed(1)}px`;
                waveformBars[i].style.opacity = `${(0.34 + mixedLevel * 0.66).toFixed(2)}`;
            }

            waveformRafId = requestAnimationFrame(animate);
        };

        animate();
    } catch (_error) {
        stopLiveWaveform();
    }
}

// ============================================================
// Mobile Menu Toggle
// ============================================================
menuToggle.addEventListener('click', () => {
    navLinks.classList.toggle('open');
});

// ============================================================
// Language Badge Interaction
// ============================================================
document.querySelectorAll('.lang-badge').forEach(badge => {
    badge.addEventListener('click', () => {
        const langCode = badge.dataset.lang || 'auto';
        setVoiceLanguagePreference(langCode);
    });
});

// ============================================================
// Auto-resize Textarea
// ============================================================
textInput.addEventListener('input', () => {
    textInput.style.height = 'auto';
    textInput.style.height = Math.min(textInput.scrollHeight, 200) + 'px';
});

// ============================================================
// Web Speech API — Voice Input
// ============================================================
function initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        btnMic.title = 'Voice input not supported in this browser';
        btnMic.style.opacity = '0.4';
        btnMic.style.cursor = 'not-allowed';
        btnMic.disabled = true;
        return;
    }

    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.maxAlternatives = 3;

    // Support multiple languages
    recognition.lang = 'en-IN'; // Default, but handles multilingual

    recognition.onstart = () => {
        isRecording = true;
        isRecognitionStarting = false;
        if (!pendingSubmitAfterVoice) {
            wasManuallyStopped = false;
        }
        recordingBaseText = textInput.value.trim();
        accumulatedTranscript = '';
        btnMic.classList.add('recording');
        btnMic.innerHTML = SVG_STOP;
        setVoiceState('listening', 'Listening...');
        startLiveWaveform();
        showToast('Listening... Speak now', 'success');
    };

    recognition.onresult = (event) => {
        let finalTranscript = '';
        let interimTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
            const result = event.results[i];
            let transcript = result[0]?.transcript || '';
            let bestConfidence = typeof result[0]?.confidence === 'number' ? result[0].confidence : -1;

            for (let j = 1; j < result.length; j++) {
                const alt = result[j];
                const confidence = typeof alt?.confidence === 'number' ? alt.confidence : -1;
                if (confidence > bestConfidence) {
                    bestConfidence = confidence;
                    transcript = alt?.transcript || transcript;
                }
            }

            if (result.isFinal) {
                finalTranscript = appendTranscript(finalTranscript, transcript);
            } else {
                interimTranscript = appendTranscript(interimTranscript, transcript);
            }
        }

        if (finalTranscript) {
            accumulatedTranscript = appendTranscript(accumulatedTranscript, finalTranscript);
        }

        const voiceTranscript = appendTranscript(accumulatedTranscript, interimTranscript);
        const composedTranscript = appendTranscript(recordingBaseText, voiceTranscript);
        textInput.value = composedTranscript;
        textInput.dispatchEvent(new Event('input'));
    };

    recognition.onend = () => {
        isRecording = false;
        isRecognitionStarting = false;
        stopLiveWaveform();
        btnMic.classList.remove('recording');
        btnMic.innerHTML = SVG_MIC;

        if (pendingSubmitAfterVoice) {
            pendingSubmitAfterVoice = false;
            handleSubmit();
            return;
        }

        wasManuallyStopped = false;
        setVoiceState('idle', 'Ready');
    };

    recognition.onerror = (event) => {
        isRecording = false;
        isRecognitionStarting = false;
        stopLiveWaveform();
        btnMic.classList.remove('recording');
        btnMic.innerHTML = SVG_MIC;
        setVoiceState('idle', 'Ready');

        if (event.error === 'aborted' && wasManuallyStopped) {
            wasManuallyStopped = false;
            return;
        }

        if (pendingSubmitAfterVoice) {
            pendingSubmitAfterVoice = false;
        }

        wasManuallyStopped = false;

        if (event.error === 'no-speech') {
            showToast('No speech detected. Try again.');
        } else if (event.error === 'audio-capture') {
            showToast('Microphone not detected. Check your audio input device.');
        } else if (event.error === 'not-allowed') {
            showToast('Microphone access denied. Please allow microphone.');
        } else if (event.error === 'network') {
            showToast('Network issue during speech recognition. Try again.');
        } else {
            showToast(`Speech error: ${event.error}`);
        }
    };
}

btnMic.addEventListener('click', () => {
    if (!recognition) {
        showToast('Voice input is not supported in this browser. Please use Chrome.');
        return;
    }

    if (isSubmitting || isRecognitionStarting) {
        return;
    }

    if (isRecording) {
        wasManuallyStopped = true;
        try {
            recognition.stop();
        } catch (_error) {
            isRecognitionStarting = false;
            wasManuallyStopped = false;
        }
    } else {
        if (isPlaying) {
            stopAudioPlayback();
            setVoiceState('idle', 'Ready');
        }

        pendingSubmitAfterVoice = false;
        wasManuallyStopped = false;
        recognition.lang = getSelectedRecognitionLang();

        try {
            isRecognitionStarting = true;
            recognition.start();
        } catch (error) {
            isRecognitionStarting = false;
            wasManuallyStopped = false;
            stopLiveWaveform();
            showToast('Could not start microphone. Please try again.');
        }
    }
});

// ============================================================
// Submit Handler
// ============================================================
btnSubmit.addEventListener('click', handleSubmit);
textInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSubmit();
    }
});

async function handleSubmit() {
    if (isSubmitting) {
        return;
    }

    if ((isRecording || isRecognitionStarting) && recognition) {
        pendingSubmitAfterVoice = true;
        wasManuallyStopped = true;
        setVoiceState('processing', 'Finalizing voice input...');
        try {
            recognition.stop();
        } catch (_error) {
            pendingSubmitAfterVoice = false;
            isRecording = false;
            isRecognitionStarting = false;
            wasManuallyStopped = false;
            handleSubmit();
        }
        return;
    }

    const text = textInput.value.trim();
    if (!text) {
        showToast('Please enter some text or use voice input.');
        return;
    }

    isSubmitting = true;
    btnSubmit.disabled = true;

    // Show loading, hide input/results
    showLoading();
    setVoiceState('processing', 'Processing...');

    try {
        // Animate loading steps
        animateLoadingSteps();

        // Call API
        const response = await fetch(`${API_BASE}/api/process`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, voice: true })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || `Server error: ${response.status}`);
        }

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.message || 'Processing failed');
        }

        // Render results
        setVoiceState('idle', 'Ready');
        renderResults(data);

    } catch (error) {
        console.error('Process error:', error);
        showToast(error.message || 'Failed to connect to server. Make sure the backend is running.');
        hideLoading();
        setVoiceState('idle', 'Ready');
    } finally {
        isSubmitting = false;
        btnSubmit.disabled = false;
    }
}

// ============================================================
// Loading Animation
// ============================================================
function showLoading() {
    heroSection.style.display = 'none';
    inputSection.style.display = 'none';
    resultsSection.classList.remove('active');
    if (voiceStateEl) voiceStateEl.style.display = 'none';
    loadingContainer.classList.add('active');

    // Reset steps
    loadingSteps.forEach(id => {
        document.getElementById(id).className = 'loading-step';
    });
}

function hideLoading() {
    loadingContainer.classList.remove('active');
    heroSection.style.display = '';
    inputSection.style.display = '';
    if (voiceStateEl) voiceStateEl.style.display = '';
}

function animateLoadingSteps() {
    const delays = [300, 800, 1500, 2200, 3000];
    loadingSteps.forEach((id, i) => {
        setTimeout(() => {
            const el = document.getElementById(id);
            el.classList.add('active');
            if (i > 0) {
                document.getElementById(loadingSteps[i - 1]).classList.remove('active');
                document.getElementById(loadingSteps[i - 1]).classList.add('done');
            }
        }, delays[i]);
    });
}

// ============================================================
// Render Results
// ============================================================
function renderResults(data) {
    loadingContainer.classList.remove('active');
    resultsSection.classList.add('active');

    // Language
    const langName = data.input.language.name || 'unknown';
    detectedLang.textContent = langName.charAt(0).toUpperCase() + langName.slice(1);
    langConfidence.textContent = data.input.language.confidence
        ? `(${Math.round(data.input.language.confidence * 100)}% confidence)`
        : '';

    // Highlight active language badge
    const detectedCode = normalizeSupportedLang(data.input.language.code);
    if (detectedCode) {
        lastDetectedVoiceLang = detectedCode;
        localStorage.setItem(VOICE_LAST_DETECTED_KEY, detectedCode);
    }
    if (selectedVoiceLang === 'auto') {
        setActiveLanguageBadge('auto');
    }

    // Translation
    translatedText.textContent = data.translation.english_text || data.input.text;

    // Skill
    skillName.textContent = data.skill.name || '—';
    skillCategory.textContent = data.skill.category || '—';
    skillDescription.textContent = data.skill.description || '—';

    // Audio
    if (data.audio && data.audio.base64) {
        currentAudioB64 = data.audio.base64;
        audioSection.style.display = 'flex';
        audioTitle.textContent = `Listen about "${data.skill.name}"`;
        audioSubtitle.textContent = `Audio in ${langName.charAt(0).toUpperCase() + langName.slice(1)}`;

        // Auto-play
        playAudio();
    } else {
        audioSection.style.display = 'none';
        currentAudioB64 = null;
    }

    // Resources
    renderResources(data.resources);

    // Smooth scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ============================================================
// Render Resources
// ============================================================
function renderResources(resources) {
    // M-001 fix: Use safe DOM methods instead of innerHTML
    resourcesList.innerHTML = '';

    let hasContent = false;

    // Documentation
    if (resources.docs && resources.docs.length > 0) {
        hasContent = true;
        const typeDiv = document.createElement('div');
        typeDiv.className = 'resource-type';

        const labelDiv = document.createElement('div');
        labelDiv.className = 'resource-type-label';
        labelDiv.innerHTML = `${SVG_DOC} Documentation`; // SVG_DOC is safe static string
        typeDiv.appendChild(labelDiv);

        const linksDiv = document.createElement('div');
        linksDiv.className = 'resource-links';

        resources.docs.forEach(doc => {
            const link = document.createElement('a');
            link.href = doc.url || '#';
            link.target = '_blank';
            link.rel = 'noopener';
            link.className = 'resource-link';

            const iconDiv = document.createElement('div');
            iconDiv.className = 'r-icon docs';
            iconDiv.innerHTML = SVG_DOC;

            const titleSpan = document.createElement('span');
            titleSpan.className = 'r-title';
            titleSpan.textContent = doc.title || 'Untitled'; // Safe: textContent doesn't execute scripts

            const typeSpan = document.createElement('span');
            typeSpan.className = 'r-type';
            typeSpan.textContent = doc.type || 'docs';

            link.appendChild(iconDiv);
            link.appendChild(titleSpan);
            link.appendChild(typeSpan);
            linksDiv.appendChild(link);
        });

        typeDiv.appendChild(linksDiv);
        resourcesList.appendChild(typeDiv);
    }

    // YouTube
    if (resources.youtube && resources.youtube.length > 0) {
        hasContent = true;
        const typeDiv = document.createElement('div');
        typeDiv.className = 'resource-type';

        const labelDiv = document.createElement('div');
        labelDiv.className = 'resource-type-label';
        labelDiv.innerHTML = `${SVG_VIDEO} YouTube Tutorials`;
        typeDiv.appendChild(labelDiv);

        const linksDiv = document.createElement('div');
        linksDiv.className = 'resource-links';

        resources.youtube.forEach(vid => {
            const link = document.createElement('a');
            link.href = vid.url || '#';
            link.target = '_blank';
            link.rel = 'noopener';
            link.className = 'resource-link';

            const iconDiv = document.createElement('div');
            iconDiv.className = 'r-icon youtube';
            iconDiv.innerHTML = SVG_VIDEO;

            const titleSpan = document.createElement('span');
            titleSpan.className = 'r-title';
            titleSpan.textContent = vid.title || 'Untitled';

            const typeSpan = document.createElement('span');
            typeSpan.className = 'r-type';
            typeSpan.textContent = vid.type || 'video';

            link.appendChild(iconDiv);
            link.appendChild(titleSpan);
            link.appendChild(typeSpan);
            linksDiv.appendChild(link);
        });

        typeDiv.appendChild(linksDiv);
        resourcesList.appendChild(typeDiv);
    }

    // Wikipedia
    if (resources.wikipedia) {
        hasContent = true;
        const typeDiv = document.createElement('div');
        typeDiv.className = 'resource-type';

        const labelDiv = document.createElement('div');
        labelDiv.className = 'resource-type-label';
        labelDiv.innerHTML = `${SVG_GLOBE} Wikipedia`;
        typeDiv.appendChild(labelDiv);

        const linksDiv = document.createElement('div');
        linksDiv.className = 'resource-links';

        const link = document.createElement('a');
        link.href = resources.wikipedia;
        link.target = '_blank';
        link.rel = 'noopener';
        link.className = 'resource-link';

        const iconDiv = document.createElement('div');
        iconDiv.className = 'r-icon wiki';
        iconDiv.innerHTML = SVG_GLOBE;

        const titleSpan = document.createElement('span');
        titleSpan.className = 'r-title';
        titleSpan.textContent = 'Wikipedia Article';

        const typeSpan = document.createElement('span');
        typeSpan.className = 'r-type';
        typeSpan.textContent = 'reference';

        link.appendChild(iconDiv);
        link.appendChild(titleSpan);
        link.appendChild(typeSpan);
        linksDiv.appendChild(link);

        typeDiv.appendChild(linksDiv);
        resourcesList.appendChild(typeDiv);
    }

    if (!hasContent) {
        const emptyMsg = document.createElement('p');
        emptyMsg.className = 'resources-empty-state';
        emptyMsg.textContent = 'No resources found for this skill.';
        resourcesList.appendChild(emptyMsg);
    }
}

// ============================================================
// Audio Playback
// ============================================================
function playAudio() {
    if (!currentAudioB64) return;

    try {
        audioPlayer.src = `data:audio/mp3;base64,${currentAudioB64}`;
        audioPlayer.play()
            .then(() => {
                isPlaying = true;
                btnPlay.innerHTML = SVG_PAUSE;
                btnPlay.classList.add('speaking');
                setVoiceState('speaking', 'Speaking...');
            })
            .catch(err => {
                console.warn('Auto-play blocked:', err);
                isPlaying = false;
                btnPlay.innerHTML = SVG_PLAY;
                btnPlay.classList.remove('speaking');
            });
    } catch (err) {
        console.error('Audio error:', err);
    }
}

btnPlay.addEventListener('click', () => {
    if (!currentAudioB64) return;

    if (isPlaying) {
        stopAudioPlayback();
        setVoiceState('idle', 'Ready');
    } else {
        playAudio();
    }
});

audioPlayer.addEventListener('ended', () => {
    isPlaying = false;
    btnPlay.innerHTML = SVG_PLAY;
    btnPlay.classList.remove('speaking');
    setVoiceState('idle', 'Ready');
});

// ============================================================
// New Query
// ============================================================
btnNew.addEventListener('click', () => {
    resultsSection.classList.remove('active');
    heroSection.style.display = '';
    inputSection.style.display = '';
    if (voiceStateEl) voiceStateEl.style.display = '';
    textInput.value = '';
    textInput.style.height = 'auto';
    stopLiveWaveform();
    stopAudioPlayback();
    currentAudioB64 = null;
    accumulatedTranscript = '';
    recordingBaseText = '';
    pendingSubmitAfterVoice = false;
    isRecognitionStarting = false;
    wasManuallyStopped = false;
    setVoiceState('idle', 'Ready');

    window.scrollTo({ top: 0, behavior: 'smooth' });
    textInput.focus();
});

// ============================================================
// Toast Notifications
// ============================================================
function showToast(message, type = 'error') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 4000);
}

// ============================================================
// Initialize
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initVoiceLanguagePreference();
    initSpeechRecognition();
    stopLiveWaveform();
    textInput.focus();
});

window.addEventListener('beforeunload', () => {
    stopLiveWaveform();
});
