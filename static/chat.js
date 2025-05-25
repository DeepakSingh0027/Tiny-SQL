document.getElementById("chat-form").addEventListener("submit", function (e) {
  e.preventDefault();

  const message = document.getElementById("chat-input").value.trim();
  if (!message) {
    showChatResults("Please enter a question about your database", false);
    return;
  }

  const sendBtn = document.querySelector(".send-btn");
  const btnText = document.querySelector(".chat-btn-text");
  const spinner = sendBtn.querySelector(".loading-spinner");
  const resultsBox = document.getElementById("chat-results");

  // Show loading state
  sendBtn.classList.add("loading");
  btnText.textContent = "Processing...";
  spinner.style.display = "block";
  resultsBox.className = "chat-results-content";
  resultsBox.innerHTML =
    '<i class="bi bi-hourglass-split"></i> Processing your request...';

  // API call to /chat_run
  fetch("/chat_run", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ message }),
  })
    .then((res) => res.json())
    .then((data) => {
      showChatResults(
        data.output || "Query executed successfully. Here are your results.",
        data.success !== false
      );
    })
    .catch((error) => {
      showChatResults("Network error: " + error.message, false);
    })
    .finally(() => {
      // Reset button state
      sendBtn.classList.remove("loading");
      btnText.textContent = "Send Query";
      spinner.style.display = "none";
    });
});

// Update chat result area with output or error
function showChatResults(text, success) {
  const resultsBox = document.getElementById("chat-results");
  resultsBox.textContent = text;
  resultsBox.className = `chat-results-content ${
    success ? "success" : "error"
  }`;
}

// Fill chat input with example message
function setChatMessage(messageText) {
  document.getElementById("chat-input").value = messageText;
  document.getElementById("chat-input").focus();
}

// Ctrl + Enter keyboard shortcut to submit chat form
document.getElementById("chat-input").addEventListener("keydown", function (e) {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    e.preventDefault();
    document.getElementById("chat-form").dispatchEvent(new Event("submit"));
  }
});
