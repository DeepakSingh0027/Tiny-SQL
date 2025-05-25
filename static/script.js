let currentTab = "sql";

// Tab Switching
function switchTab(tab) {
  // Update active tab button
  document.querySelectorAll(".tab-button").forEach((btn) => {
    btn.classList.remove("active");
  });
  document.querySelector(`[data-tab="${tab}"]`).classList.add("active");

  // Show/hide content sections
  document.querySelectorAll(".content-section").forEach((section) => {
    section.classList.remove("active");
  });
  document.getElementById(`${tab}-section`).classList.add("active");

  currentTab = tab;
}

// SQL Query Execution
document.getElementById("query-form").addEventListener("submit", function (e) {
  e.preventDefault();

  const query = document.getElementById("query").value.trim();
  if (!query) {
    showOutput("Please enter a SQL query", false);
    return;
  }

  const executeBtn = document.querySelector(".execute-btn");
  const btnText = document.querySelector(".btn-text");
  const spinner = document.querySelector(".loading-spinner");
  const outputBox = document.getElementById("output");

  // Show loading state
  executeBtn.classList.add("loading");
  btnText.textContent = "Executing...";
  spinner.style.display = "block";
  outputBox.className = "output-content";
  outputBox.innerHTML =
    '<i class="bi bi-hourglass-split"></i> Executing query...';

  fetch("/run_query", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ query }),
  })
    .then((res) => res.json())
    .then((data) => {
      showOutput(data.output, data.success);
    })
    .catch((error) => {
      showOutput("Network error: " + error.message, false);
    })
    .finally(() => {
      // Reset button state
      executeBtn.classList.remove("loading");
      btnText.textContent = "Execute Query";
      spinner.style.display = "none";
    });
});

// Chat Form Submission
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

  // Simulate API call (replace with actual endpoint)
  fetch("/chat_query", {
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

function showOutput(text, success) {
  const outputBox = document.getElementById("output");
  outputBox.textContent = text;
  outputBox.className = `output-content ${success ? "success" : "error"}`;
}

function showChatResults(text, success) {
  const resultsBox = document.getElementById("chat-results");
  resultsBox.textContent = text;
  resultsBox.className = `chat-results-content ${
    success ? "success" : "error"
  }`;
}

function setQuery(queryText) {
  document.getElementById("query").value = queryText;
  document.getElementById("query").focus();
}

function setChatMessage(messageText) {
  document.getElementById("chat-input").value = messageText;
  document.getElementById("chat-input").focus();
}

// Theme Toggler
function toggleTheme() {
  const body = document.body;
  const toggleBtn = document.querySelector(".theme-toggle i");

  body.classList.toggle("dark-mode");
  body.classList.toggle("light-mode");

  const isDark = body.classList.contains("dark-mode");
  toggleBtn.className = isDark ? "bi bi-sun-fill" : "bi bi-moon-fill";

  // Save theme preference
  localStorage.setItem("theme", isDark ? "dark" : "light");
}

// Load saved theme
document.addEventListener("DOMContentLoaded", function () {
  const savedTheme = localStorage.getItem("theme");
  if (savedTheme === "dark") {
    document.body.classList.remove("light-mode");
    document.body.classList.add("dark-mode");
    document.querySelector(".theme-toggle i").className = "bi bi-sun-fill";
  }
});

// Add keyboard shortcuts
document.getElementById("query").addEventListener("keydown", function (e) {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    e.preventDefault();
    document.getElementById("query-form").dispatchEvent(new Event("submit"));
  }
});

document.getElementById("chat-input").addEventListener("keydown", function (e) {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    e.preventDefault();
    document.getElementById("chat-form").dispatchEvent(new Event("submit"));
  }
});
