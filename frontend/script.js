// We use localhost for development testing, later this can be switched back to render
const API_URL = "https://ai-scam-detector-1-qtm7.onrender.com/scan"; // Changed back to Render backend URL

async function scanText() {
    const text = document.getElementById("inputText").value;
    const btn = document.getElementById("scanBtn");
    const resultContainer = document.getElementById("resultContainer");

    if (!text.trim()) {
        alert("Please enter some text, a link, or an email to analyze.");
        return;
    }

    // UI Loading state
    btn.disabled = true;
    btn.classList.add("loading");
    resultContainer.style.display = "none";

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ text: text })
        });

        if (!response.ok) {
            throw new Error(`Server responded with ${response.status}`);
        }

        const data = await response.json();

        // Update UI with results
        updateResultUI(data);

    } catch (error) {
        console.error("Scan Error:", error);

        // Show error state gracefully
        const riskBadge = document.getElementById("riskBadge");
        riskBadge.innerText = "Connection Error";
        riskBadge.className = "risk-badge high";

        document.getElementById("overallScore").innerText = "N/A";
        document.getElementById("mlConfidence").innerText = "N/A";
        document.getElementById("progressBar").style.width = "0%";

        const reasonsList = document.getElementById("reasonsList");
        reasonsList.innerHTML = `
            <li>Make sure the local backend server is running.</li>
            <li>Run <code>python app.py</code> in the backend folder.</li>
        `;
        resultContainer.style.display = "block";

    } finally {
        // Reset button
        btn.disabled = false;
        btn.classList.remove("loading");
    }
}

function updateResultUI(data) {
    const resultContainer = document.getElementById("resultContainer");
    const riskBadge = document.getElementById("riskBadge");
    const progressBar = document.getElementById("progressBar");

    // Dynamic risk Badge Colors
    riskBadge.innerText = `${data.risk} Risk`;
    riskBadge.className = "risk-badge"; // reset classes

    let progressColor = "var(--accent-green)";

    if (data.risk === "High") {
        riskBadge.classList.add("high");
        progressColor = "var(--accent-red)";
    } else if (data.risk === "Medium") {
        riskBadge.classList.add("medium");
        progressColor = "var(--accent-orange)";
    } else {
        riskBadge.classList.add("low");
    }

    // Set text scores
    document.getElementById("overallScore").innerText = `${data.score}/100`;
    document.getElementById("mlConfidence").innerText = `${data.ml_confidence}%`;

    // Populate reasons
    const reasonsList = document.getElementById("reasonsList");
    if (data.reasons && data.reasons.length > 0) {
        reasonsList.innerHTML = data.reasons.map(r => `<li>${r}</li>`).join("");
    } else {
        reasonsList.innerHTML = `<li>No suspicious indicators found. Looks safe!</li>`;
    }

    // Show container
    resultContainer.style.display = "block";

    // Trigger animation for the bar slightly delayed for visual effect
    setTimeout(() => {
        // Using ml confidence or the risk score
        const fillAmount = Math.max(data.ml_confidence, data.score, 5); // baseline of 5%
        progressBar.style.width = `${fillAmount}%`;
        progressBar.style.background = progressColor;
    }, 100);
}

function copyResult() {
    const risk = document.getElementById("riskBadge").innerText;
    const score = document.getElementById("overallScore").innerText;
    const ml = document.getElementById("mlConfidence").innerText;

    let reasons = [];
    document.querySelectorAll(".reasons-list li").forEach(li => {
        reasons.push("- " + li.innerText);
    });

    const textToCopy = `ScamGuard Report:
Risk: ${risk}
Score: ${score}
AI Confidence: ${ml}

Analysis:
${reasons.join("\n")}`;

    navigator.clipboard.writeText(textToCopy).then(() => {
        const btn = document.querySelector(".copy-btn");
        const originalText = btn.innerText;
        btn.innerText = "Copied to Clipboard!";
        setTimeout(() => {
            btn.innerText = originalText;
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy text: ', err);
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("inputText");
    if (input) {
        input.addEventListener("keydown", function (event) {
            // Trigger scan on Ctrl+Enter or Cmd+Enter
            if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
                event.preventDefault();
                scanText();
            }
        });
    }
});