const API = "https://resume-analyzerai-backend.onrender.com"; // 🔥 CHANGE THIS

let user_id = "user123";

// Load roles dynamically
function loadRoles() {
  fetch(API + "/roles")
    .then(res => res.json())
    .then(data => {
      let roleSelect = document.getElementById("role");
      roleSelect.innerHTML = "";

      data.forEach(role => {
        let option = document.createElement("option");
        option.value = role;
        option.textContent = role;
        roleSelect.appendChild(option);
      });
    })
    .catch(err => console.error("Error loading roles:", err));
}

// Resume Analysis
function analyzeResume() {
  let resume = document.getElementById("resume").value;
  let role = document.getElementById("role").value;

  if (!resume) {
    alert("Please paste your resume");
    return;
  }

  fetch(API + "/analyze", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      resume: resume,
      role: role
    })
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById("analysisResult").innerHTML =
      `<p><b>Score:</b> ${data.score}</p>
       <p><b>Suggestions:</b> ${data.suggestions}</p>`;
  });
}

// Start interview
function startInterview() {
  let role = document.getElementById("role").value;

  fetch(API + "/start", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      user_id: user_id,
      role: role,
      duration: 5
    })
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById("chat").innerHTML = "";
    document.getElementById("chat").innerHTML += `<p><b>Q:</b> ${data.question}</p>`;
  });
}

// Send answer
function sendAnswer() {
  let answer = document.getElementById("answer").value;

  if (!answer) return;

  fetch(API + "/next", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      user_id: user_id,
      answer: answer
    })
  })
  .then(res => res.json())
  .then(data => {
    let chat = document.getElementById("chat");

    chat.innerHTML += `<p><b>You:</b> ${answer}</p>`;
    chat.innerHTML += `<p><b>Feedback:</b> ${data.evaluation}</p>`;

    if (data.end) {
      chat.innerHTML += `<p><b>Final Score:</b> ${data.result.final_score}</p>`;
      return;
    }

    chat.innerHTML += `<p><b>Q:</b> ${data.question}</p>`;
  });

  document.getElementById("answer").value = "";
}

// Load roles on page load
window.onload = loadRoles;