
/*Try to recover a session_id previously saved, if not, then it will be generated randomly*/
let sessionId = localStorage.getItem("session_id");

if (!sessionId) {
  sessionId = crypto.randomUUID();
  localStorage.setItem("session_id", sessionId);
}

/*Search for DOM elements by their IDs in HTML*/
const sendBtn = document.getElementById("sendBtn");
const userInput = document.getElementById("userInput");

const azureChat = document.getElementById("azureChat");
const awsChat = document.getElementById("awsChat");

/* Button functionality, when the send button is clicked/enter, sendMessage function is called */
sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});

/* Every new message, appendMessage will create a new container, CSS classes are assigned.
Do scroll to bottom of chat box */
function appendMessage(container, text, type) {
  const div = document.createElement("div");
  div.className = `message ${type}`;
  div.innerText = text;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

/* The most important part of the script, this function sends the message to the backend */
async function sendMessage() {
  const message = userInput.value.trim();
  if (!message) return;

  userInput.value = "";

  appendMessage(azureChat, `Usuario: ${message}`, "user");
  appendMessage(awsChat, `Usuario: ${message}`, "user");

  try { // In case of error connecting to backend

    // POST request to the backend with session_id and user message -> responses returns list of answers from both agents
    const response = await fetch("http://localhost:3000/chatbot", {
      method: "POST", // Adjusted endpoint to match router prefix
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        session_id: sessionId, // User session ID
        message: message // Message user wants to send
      })
    });

    // Check if ChatBot response is ok
    if (!response.ok) {
      // Attempt to surface structured error details from backend
      let errText = `HTTP ${response.status}`;
      try {
        const errData = await response.json();
        if (errData && errData.detail) errText = errData.detail;
        else errText = JSON.stringify(errData);
      } catch (_) {}
      appendMessage(azureChat, `Error: ${errText}`, "bot");
      appendMessage(awsChat, `Error: ${errText}`, "bot");
      return;
    }

    const data = await response.json();

    // Shows the responses from both agents on the respective chat boxes
    appendMessage(azureChat, `Azure: ${data.azure ?? "No response from Azure"}`, "bot");
    appendMessage(awsChat, `AWS: ${data.aws ?? "No response from AWS"}`, "bot");

  } catch (error) { // Error handling
    console.error(error);
    appendMessage(azureChat, "Error connecting to the backend", "bot");
    appendMessage(awsChat, "Error connecting to the backend", "bot");
  }
}
