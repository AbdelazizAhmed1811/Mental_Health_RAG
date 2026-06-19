document.addEventListener("DOMContentLoaded", () => {
    const chatForm = document.getElementById("chat-form");
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const chatBox = document.getElementById("chat-box");
    const statusDot = document.getElementById("status-dot");
    const statusText = document.getElementById("status-text");
    const langText = document.getElementById("lang-text");
    const emotionText = document.getElementById("emotion-text");
    const emotionDot = document.querySelector(".emotion-dot");
    const sessionDisplay = document.getElementById("session-id-display");
    const newSessionBtn = document.getElementById("new-session-btn");
    const charCount = document.getElementById("char-count");
    const welcomeMsg = document.getElementById("welcome-msg");

    const API_URL = window.location.origin + "/chat";
    const SESSION_ID = (window.crypto && window.crypto.randomUUID) ? window.crypto.randomUUID() : Math.random().toString(36).substring(2);

    // ─── Language names map ───────────────────────────────
    const LANG_NAMES = {
        "en": "English", "es": "Spanish", "ar": "Arabic", "fr": "French", "de": "German",
        "zh": "Chinese", "hi": "Hindi", "bn": "Bengali", "pt": "Portuguese", "ru": "Russian",
        "ja": "Japanese", "pa": "Punjabi", "mr": "Marathi", "te": "Telugu", "tr": "Turkish",
        "ko": "Korean", "vi": "Vietnamese", "ta": "Tamil", "it": "Italian", "ur": "Urdu",
        "nl": "Dutch", "pl": "Polish", "uk": "Ukrainian", "fa": "Persian", "ro": "Romanian",
        "el": "Greek", "cs": "Czech", "sv": "Swedish", "hu": "Hungarian", "th": "Thai",
        "id": "Indonesian", "fi": "Finnish", "da": "Danish", "he": "Hebrew", "no": "Norwegian",
        "sk": "Slovak", "hr": "Croatian", "ms": "Malay", "bg": "Bulgarian", "sr": "Serbian"
    };
    const EMOTION_CLASSES = ["joy", "sadness", "anxiety", "anger", "fear", "neutral"];

    const updateEmotionBadge = (emotion) => {
        if (!emotion || emotion === "N/A") return;
        const key = emotion.toLowerCase();
        EMOTION_CLASSES.forEach(c => emotionDot.classList.remove(c));
        emotionDot.classList.add(EMOTION_CLASSES.includes(key) ? key : "neutral");
        emotionText.textContent = emotion.charAt(0).toUpperCase() + emotion.slice(1).toLowerCase();
    };

    const resetEmotionBadge = () => {
        EMOTION_CLASSES.forEach(c => emotionDot.classList.remove(c));
        emotionText.textContent = "—";
    };

    // ─── Status helpers ───────────────────────────────────
    const setLoading = (loading) => {
        if (loading) {
            statusDot.classList.add("loading");
            statusText.textContent = "Thinking…";
        } else {
            statusDot.classList.remove("loading");
            statusText.textContent = "Online";
        }
    };

    // ─── Time helper ─────────────────────────────────────
    const getTime = (date = new Date()) =>
        date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

    // ─── Message rendering ────────────────────────────────
    const appendMessage = (text, sender, meta = null, isHistory = false) => {
        const msgDiv = document.createElement("div");
        msgDiv.classList.add("message", sender === "user" ? "user-message" : "bot-message");
        if (isHistory) msgDiv.classList.add("history-message");

        const avatar = document.createElement("div");
        avatar.classList.add("avatar", sender === "user" ? "user-avatar" : "bot-avatar");
        avatar.textContent = sender === "user" ? "🧑" : "🌿";

        const contentDiv = document.createElement("div");
        contentDiv.classList.add("message-content");

        const p = document.createElement("p");
        p.textContent = text;
        contentDiv.appendChild(p);

        // Meta row (timestamp + optional pills)
        const metaDiv = document.createElement("div");
        metaDiv.classList.add("message-meta");

        const timeSpan = document.createElement("span");
        timeSpan.classList.add("timestamp");
        timeSpan.textContent = getTime();
        metaDiv.appendChild(timeSpan);

        if (meta && sender === "bot") {
            if (meta.intent && meta.intent !== "N/A") {
                const pill = document.createElement("span");
                pill.classList.add("meta-pill");
                pill.textContent = meta.intent.replace(/_/g, " ");
                metaDiv.appendChild(pill);
            }
            if (meta.emotion && meta.emotion !== "N/A") {
                const emotionPill = document.createElement("span");
                emotionPill.classList.add("meta-pill");
                emotionPill.textContent = "😔 " + meta.emotion;
                metaDiv.appendChild(emotionPill);
            }
        }

        contentDiv.appendChild(metaDiv);
        msgDiv.appendChild(avatar);
        msgDiv.appendChild(contentDiv);
        chatBox.appendChild(msgDiv);
        scrollToBottom();
    };

    // ─── Typing indicator ─────────────────────────────────
    const showTypingIndicator = () => {
        const msgDiv = document.createElement("div");
        msgDiv.classList.add("message", "bot-message");
        msgDiv.id = "typing-indicator";

        const avatar = document.createElement("div");
        avatar.classList.add("avatar", "bot-avatar");
        avatar.textContent = "🌿";

        const contentDiv = document.createElement("div");
        contentDiv.classList.add("message-content");

        const typingDiv = document.createElement("div");
        typingDiv.classList.add("typing-indicator");
        typingDiv.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';

        contentDiv.appendChild(typingDiv);
        msgDiv.appendChild(avatar);
        msgDiv.appendChild(contentDiv);
        chatBox.appendChild(msgDiv);
        scrollToBottom();
    };

    const hideTypingIndicator = () => {
        document.getElementById("typing-indicator")?.remove();
    };

    const scrollToBottom = () => {
        chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: "smooth" });
    };

    // ─── Textarea auto-grow ───────────────────────────────
    userInput.addEventListener("input", () => {
        const val = userInput.value.trim();
        sendBtn.disabled = val.length === 0;
        charCount.textContent = val.length > 0 ? `${userInput.value.length}` : "";

        // Auto-resize
        userInput.style.height = "auto";
        userInput.style.height = Math.min(userInput.scrollHeight, 120) + "px";
    });

    // Send on Enter (Shift+Enter for newline)
    userInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            if (!sendBtn.disabled) chatForm.dispatchEvent(new Event("submit"));
        }
    });

    // ─── Send message ─────────────────────────────────────
    chatForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const text = userInput.value.trim();
        if (!text) return;

        userInput.value = "";
        userInput.style.height = "auto";
        charCount.textContent = "";
        sendBtn.disabled = true;

        appendMessage(text, "user");
        showTypingIndicator();
        setLoading(true);

        try {
            const res = await fetch(API_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query: text, session_id: SESSION_ID })
            });

            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail || "Server error");
            }

            const data = await res.json();
            hideTypingIndicator();
            setLoading(false);

            // Update sidebar badges
            if (data.detected_language) {
                langText.textContent = LANG_NAMES[data.detected_language] || data.detected_language.toUpperCase();
            }
            if (data.detected_emotion) {
                updateEmotionBadge(data.detected_emotion);
            }

            const meta = {
                lang: data.detected_language,
                intent: data.detected_intent,
                emotion: data.detected_emotion
            };
            appendMessage(data.response, "bot", meta);

        } catch (err) {
            console.error(err);
            hideTypingIndicator();
            setLoading(false);
            appendMessage(
                "⚠️ I am having a bit of trouble thinking right now due to high server traffic. Please try again in a few seconds.",
                "bot"
            );
        }

        userInput.focus();
    });
});
