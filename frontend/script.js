async function scanText() {
    const text = document.getElementById("inputText").value;

    if (!text.trim()) {
        alert("Please enter some text");
        return;
    }

    document.getElementById("result").innerHTML = "Scanning... (wait 10-20 sec first time)";

    try {
        const response = await fetch("https://ai-scam-detector-1-qtm7.onrender.com/scan", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ text: text })
        });

        const data = await response.json();

        let color = "white";
        if (data.risk === "High") color = "red";
        else if (data.risk === "Medium") color = "orange";
        else color = "lightgreen";

        const bar = `
        <div style="background:#1f2937;border-radius:6px;overflow:hidden;height:10px;margin-top:6px">
            <div style="width:${data.ml_confidence || 0}%;height:100%;background:#22c55e"></div>
        </div>`;

        document.getElementById("result").innerHTML = `
            <p><b>Score:</b> ${data.score}%</p>
            <p style="color:${color}"><b>Risk:</b> ${data.risk}</p>
            <p><b>ML Confidence:</b> ${data.ml_confidence}%</p>
            ${bar}
            <p><b>Reasons:</b></p>
            <ul>
                ${data.reasons.map(r => `<li>${r}</li>`).join("")}
            </ul>
        `;

    } catch (error) {
        console.log(error);
        document.getElementById("result").innerHTML = `
            ❌ Error connecting to server<br><br>
            👉 Wait 20 sec (Render sleeps)<br>
            👉 Then try again
        `;
    }
}