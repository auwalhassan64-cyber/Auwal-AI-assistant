
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI
import os

app = Flask(__name__)

PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>AUWAL AI</title>
</head>
<body>
    <h1>🤖 AUWAL AI</h1>
    <p>Your personal AI assistant</p>
    <div id="chat"></div>
    <input id="question" placeholder="Ask me anything">
    <button onclick="askAI()">Send</button>
    <button onclick="speakLast()">🔊 Speak</button>

    <script>
    let lastAnswer = "";

    async function askAI() {
        const box = document.getElementById("question");
        const chat = document.getElementById("chat");
        const question = box.value.trim();
        if (!question) return;

        chat.innerHTML += "<p><b>You:</b> " +
            escapeHTML(question) + "</p>";
        box.value = "";

        try {
            const response = await fetch("/ask", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({question})
            });
            const data = await response.json();
            lastAnswer = data.answer || data.error || "No answer";
            chat.innerHTML += "<p><b>AUWAL AI:</b> " +
                escapeHTML(lastAnswer) + "</p>";
        } catch (e) {
            chat.innerHTML += "<p>Connection error. Try again.</p>";
        }
    }

    function escapeHTML(text) {
        const el = document.createElement("div");
        el.textContent = text;
        return el.innerHTML;
    }

    function speakLast() {
        if (!lastAnswer) return;
        const speech = new SpeechSynthesisUtterance(lastAnswer);
        speech.lang = "en-US";
        speechSynthesis.speak(speech);
    }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(PAGE)

@app.route("/ask", methods=["POST"])
def ask():
    question = request.json.get("question", "").strip()

    if not question:
        return jsonify({"error": "Please enter a question."}), 400

    try:
        client = OpenAI()
        result = client.responses.create(
            model="gpt-4.1-mini",
            input=question
        )
        return jsonify({"answer": result.output_text})
    except Exception:
        app.logger.exception("AI request failed")
        return jsonify({
            "error": "I could not answer. Check the API setup."
        }), 500

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
