/**
 * IntelliBrief - Frontend Application Logic
 * Clean, basic vanilla JavaScript interacting with the FastAPI backend.
 */

// Detect backend URL (use localhost:8000 when opened as file://, or origin if served by FastAPI)
const API_BASE = window.location.origin.includes("localhost:8000") || window.location.origin.includes("127.0.0.1:8000")
  ? window.location.origin
  : "http://localhost:8000";

// Global App State
const state = {
  userId: localStorage.getItem("intellibrief_user_id") || null,
  userEmail: localStorage.getItem("intellibrief_user_email") || null,
  activeView: "landing",
  quizQuestions: [],
  currentQuestionIndex: 0,
  quizAnswers: {}, // key: question_id, value: array of topic_ids
};

// -----------------------------------------------------------------------------
// View Switching Logic
// -----------------------------------------------------------------------------
function switchView(viewName) {
  state.activeView = viewName;

  // Hide all sections
  document.querySelectorAll(".view-section").forEach((sec) => {
    sec.classList.remove("active");
  });

  // Show target section
  const target = document.getElementById(`view-${viewName}`);
  if (target) {
    target.classList.add("active");
  }

  // Update navbar active state
  document.querySelectorAll(".nav-link").forEach((link) => {
    link.classList.remove("text-sky-600", "font-semibold");
    link.classList.add("text-slate-600");
  });
  const activeLink = document.getElementById(`nav-${viewName}`);
  if (activeLink) {
    activeLink.classList.remove("text-slate-600");
    activeLink.classList.add("text-sky-600", "font-semibold");
  }

  // Automatically trigger view loaders
  if (viewName === "dashboard") {
    loadTodayReport();
  } else if (viewName === "explorer") {
    loadNewsExplorer();
  } else if (viewName === "profile") {
    loadProfile();
  } else if (viewName === "quiz") {
    if (state.quizQuestions.length === 0) {
      loadQuiz();
    } else {
      renderCurrentQuestion();
    }
  }
}

// -----------------------------------------------------------------------------
// Toast Notifications
// -----------------------------------------------------------------------------
function showToast(message, isError = false) {
  const toast = document.getElementById("toast");
  toast.innerText = message;
  toast.style.backgroundColor = isError ? "#ef4444" : "#0f172a";
  toast.style.display = "block";
  setTimeout(() => {
    toast.style.display = "none";
  }, 3500);
}

// -----------------------------------------------------------------------------
// 1. Subscription Handler (Landing Page)
// -----------------------------------------------------------------------------
async function handleSubscribe(event) {
  event.preventDefault();
  const emailInput = document.getElementById("subscribe-email");
  const email = emailInput.value.trim();

  if (!email || !email.includes("@")) {
    showToast("Please enter a valid email address.", true);
    return;
  }

  try {
    const response = await fetch(`${API_BASE}/api/subscriptions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: email }),
    });

    if (!response.ok) {
      throw new Error("Failed to subscribe");
    }

    const data = await response.json();
    state.userId = data.user_id;
    state.userEmail = data.email;
    localStorage.setItem("intellibrief_user_id", data.user_id);
    localStorage.setItem("intellibrief_user_email", data.email);

    showToast("Subscribed! Now let's customize your news feed.");

    // Direct user to quiz
    switchView("quiz");
  } catch (error) {
    console.error("Subscription error:", error);
    showToast("Could not connect to backend at " + API_BASE, true);
  }
}

// -----------------------------------------------------------------------------
// 2. Onboarding Quiz Handlers
// -----------------------------------------------------------------------------
async function loadQuiz() {
  try {
    const res = await fetch(`${API_BASE}/api/quiz/questions`);
    if (!res.ok) throw new Error("Could not fetch quiz questions");
    state.quizQuestions = await res.json();
    state.currentQuestionIndex = 0;
    renderCurrentQuestion();
  } catch (err) {
    console.error("Quiz load error:", err);
    showToast("Failed to load quiz. Check backend server.", true);
  }
}

function renderCurrentQuestion() {
  const container = document.getElementById("quiz-card-container");
  const progressText = document.getElementById("quiz-progress-text");
  const progressBar = document.getElementById("quiz-progress-bar");

  if (!state.quizQuestions || state.quizQuestions.length === 0) return;

  const currentQ = state.quizQuestions[state.currentQuestionIndex];
  const total = state.quizQuestions.length;

  progressText.innerText = `Question ${state.currentQuestionIndex + 1} of ${total}`;
  progressBar.style.width = `${((state.currentQuestionIndex + 1) / total) * 100}%`;

  const selectedTopics = state.quizAnswers[currentQ.id] || [];

  let optionsHtml = currentQ.options
    .map((opt) => {
      // Check if any of this option's topics are already selected
      const isSelected = opt.topics.some((t) => selectedTopics.includes(t));
      return `
        <div class="quiz-option p-4 rounded-lg bg-white ${isSelected ? "selected" : ""}" 
             onclick="toggleQuizOption('${currentQ.id}', '${opt.topics.join(",")}')">
          <div class="font-medium text-slate-800">${opt.label}</div>
          <div class="text-xs text-slate-500 mt-1">Tags: ${opt.topics.join(", ")}</div>
        </div>
      `;
    })
    .join("");

  container.innerHTML = `
    <h3 class="text-xl font-bold text-slate-900 mb-2">${currentQ.question}</h3>
    <p class="text-sm text-slate-500 mb-6">Select all topics that interest you.</p>
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-8">
      ${optionsHtml}
    </div>
  `;

  // Update Navigation buttons
  const backBtn = document.getElementById("quiz-back-btn");
  const nextBtn = document.getElementById("quiz-next-btn");

  backBtn.style.visibility = state.currentQuestionIndex > 0 ? "visible" : "hidden";
  nextBtn.innerText = state.currentQuestionIndex === total - 1 ? "Complete & Save" : "Next →";
}

function toggleQuizOption(questionId, topicsStr) {
  const topics = topicsStr.split(",");
  if (!state.quizAnswers[questionId]) {
    state.quizAnswers[questionId] = [];
  }

  const currentList = state.quizAnswers[questionId];
  const allAlreadySelected = topics.every((t) => currentList.includes(t));

  if (allAlreadySelected) {
    // Deselect
    state.quizAnswers[questionId] = currentList.filter((t) => !topics.includes(t));
  } else {
    // Add missing
    topics.forEach((t) => {
      if (!currentList.includes(t)) currentList.push(t);
    });
  }

  renderCurrentQuestion();
}

function handleQuizNext() {
  const total = state.quizQuestions.length;
  if (state.currentQuestionIndex < total - 1) {
    state.currentQuestionIndex++;
    renderCurrentQuestion();
  } else {
    submitQuizAnswers();
  }
}

function handleQuizBack() {
  if (state.currentQuestionIndex > 0) {
    state.currentQuestionIndex--;
    renderCurrentQuestion();
  }
}

async function submitQuizAnswers() {
  if (!state.userId) {
    showToast("Please subscribe on the homepage first.", true);
    switchView("landing");
    return;
  }

  // Format payload according to QuizSubmissionRequest schema
  const answersPayload = Object.keys(state.quizAnswers).map((qId) => ({
    question_id: qId,
    selected_topic_ids: state.quizAnswers[qId],
    interest_level: 8,
  }));

  try {
    const res = await fetch(`${API_BASE}/api/quiz/complete`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: state.userId,
        answers: answersPayload,
      }),
    });

    if (!res.ok) throw new Error("Failed to save quiz preferences");

    showToast("Preferences saved! Loading your personalized briefing...");
    switchView("dashboard");
  } catch (err) {
    console.error("Quiz submission error:", err);
    showToast("Failed to complete quiz.", true);
  }
}

// -----------------------------------------------------------------------------
// 3. Today's Intelligence Briefing (Dashboard)
// -----------------------------------------------------------------------------
async function loadTodayReport() {
  const container = document.getElementById("dashboard-content");
  if (!state.userId) {
    container.innerHTML = `
      <div class="p-8 text-center bg-white rounded-xl shadow-sm border border-slate-200">
        <p class="text-slate-600 mb-4">Please subscribe and take the quiz to see your personalized briefing.</p>
        <button onclick="switchView('landing')" class="px-4 py-2 bg-sky-600 text-white rounded-lg hover:bg-sky-700">Go to Home</button>
      </div>
    `;
    return;
  }

  container.innerHTML = `<div class="p-8 text-center text-slate-500">Loading today's briefing...</div>`;

  try {
    const res = await fetch(`${API_BASE}/api/reports/today/${state.userId}`);
    if (!res.ok) throw new Error("Could not load report");
    const data = await res.json();

    // Render briefing layout
    container.innerHTML = `
      <!-- Briefing Header -->
      <div class="bg-slate-900 text-white p-6 sm:p-8 rounded-2xl mb-8 shadow-sm">
        <div class="text-xs uppercase tracking-wider text-sky-400 font-semibold mb-2">Daily Intelligence Briefing &bull; ${data.report_date}</div>
        <h2 class="text-2xl sm:text-3xl font-bold tracking-tight mb-4">Today's Executive Summary</h2>
        <p class="text-slate-300 leading-relaxed whitespace-pre-line text-sm sm:text-base">${escapeHtml(data.executive_summary)}</p>
      </div>

      <!-- Finance Section -->
      <div class="mb-10">
        <div class="flex items-center justify-between border-b-2 border-slate-900 pb-3 mb-6">
          <h3 class="text-xl font-bold text-slate-900 flex items-center gap-2">
            <span>📈 Finance Developments</span>
            <span class="text-sm font-normal text-slate-500">(${data.finance_stories.length}/5 stories)</span>
          </h3>
        </div>
        ${data.finance_shortage_note ? `<div class="p-3 bg-amber-50 text-amber-800 text-sm rounded-lg mb-4 border border-amber-200">${data.finance_shortage_note}</div>` : ""}
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          ${data.finance_stories.map(renderStoryCard).join("")}
        </div>
      </div>

      <!-- Technology Section -->
      <div class="mb-10">
        <div class="flex items-center justify-between border-b-2 border-slate-900 pb-3 mb-6">
          <h3 class="text-xl font-bold text-slate-900 flex items-center gap-2">
            <span>💻 Technology Developments</span>
            <span class="text-sm font-normal text-slate-500">(${data.technology_stories.length}/5 stories)</span>
          </h3>
        </div>
        ${data.tech_shortage_note ? `<div class="p-3 bg-amber-50 text-amber-800 text-sm rounded-lg mb-4 border border-amber-200">${data.tech_shortage_note}</div>` : ""}
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          ${data.technology_stories.map(renderStoryCard).join("")}
        </div>
      </div>
    `;
  } catch (err) {
    console.error("Dashboard error:", err);
    container.innerHTML = `
      <div class="p-6 bg-red-50 text-red-700 rounded-lg border border-red-200">
        Could not load today's report. Please ensure the backend is running.
      </div>
    `;
  }
}

function renderStoryCard(story) {
  const catClass = story.category === "Finance" ? "tag-finance" : "tag-tech";
  const regClass = story.region === "India" ? "tag-india" : "tag-global";

  return `
    <div class="story-card bg-white p-5 rounded-xl border border-slate-200 flex flex-col justify-between">
      <div>
        <div class="flex items-center gap-2 mb-3">
          <span class="text-xs font-semibold px-2 py-0.5 rounded-full ${catClass}">${story.category}</span>
          <span class="text-xs font-semibold px-2 py-0.5 rounded-full ${regClass}">${story.region}</span>
          <span class="text-xs text-slate-400 ml-auto">${story.source_name}</span>
        </div>
        <h4 class="font-bold text-slate-900 text-base mb-2 leading-snug">
          <a href="${story.source_url}" target="_blank" class="hover:text-sky-600 transition-colors">
            ${escapeHtml(story.title)} &nearr;
          </a>
        </h4>
        <p class="text-xs text-slate-600 line-clamp-3 leading-relaxed mb-4">
          ${escapeHtml(story.summary || story.content_excerpt)}
        </p>
      </div>

      ${story.why_it_matters ? `
        <div class="p-2.5 bg-slate-50 rounded-lg border-l-2 border-sky-500 text-xs text-slate-700 mt-2">
          <span class="font-semibold text-slate-900">Why it matters:</span> ${escapeHtml(story.why_it_matters)}
        </div>
      ` : ""}
    </div>
  `;
}

// -----------------------------------------------------------------------------
// 4. News Explorer Handlers
// -----------------------------------------------------------------------------
async function loadNewsExplorer() {
  const container = document.getElementById("explorer-results");
  const query = document.getElementById("explorer-search").value.trim();
  const category = document.getElementById("explorer-cat-filter").value;
  const region = document.getElementById("explorer-reg-filter").value;

  let url = `${API_BASE}/api/news?limit=40`;
  if (category) url += `&category=${category}`;
  if (region) url += `&region=${region}`;
  if (query) url += `&query=${encodeURIComponent(query)}`;

  container.innerHTML = `<div class="p-8 text-center text-slate-500">Searching news pool...</div>`;

  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error("Could not fetch news");
    const articles = await res.json();

    if (articles.length === 0) {
      container.innerHTML = `<div class="p-8 text-center text-slate-500">No matching articles found in candidate pool.</div>`;
      return;
    }

    container.innerHTML = `
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        ${articles.map(renderStoryCard).join("")}
      </div>
    `;
  } catch (err) {
    console.error("Explorer error:", err);
    container.innerHTML = `<div class="p-4 bg-red-50 text-red-600 rounded">Failed to load news articles.</div>`;
  }
}

// -----------------------------------------------------------------------------
// 5. Interest Profile & Account Handlers
// -----------------------------------------------------------------------------
async function loadProfile() {
  const container = document.getElementById("profile-content");
  if (!state.userId) {
    container.innerHTML = `<p class="text-slate-600">Please subscribe first to view your profile.</p>`;
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/api/preferences/${state.userId}`);
    if (!res.ok) throw new Error("Could not fetch preferences");
    const data = await res.json();

    container.innerHTML = `
      <div class="bg-white p-6 rounded-xl border border-slate-200 mb-6">
        <h3 class="text-lg font-bold text-slate-900 mb-1">Subscriber Account</h3>
        <p class="text-sm text-slate-500 mb-4">${state.userEmail || "Subscribed User"}</p>
        <div class="text-xs text-slate-400">Timezone: Asia/Kolkata (Daily Delivery at 07:00 IST)</div>
      </div>

      <div class="bg-white p-6 rounded-xl border border-slate-200 mb-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold text-slate-900">Customized Interests (${data.preferences.length} topics)</h3>
          <button onclick="switchView('quiz')" class="text-xs text-sky-600 font-semibold hover:underline">Retake Quiz</button>
        </div>
        <div class="space-y-3">
          ${data.preferences
            .map(
              (p) => `
            <div class="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
              <div>
                <div class="font-medium text-sm text-slate-800">${p.display_name}</div>
                <div class="text-xs text-slate-500">${p.category} &bull; Keywords: ${p.keywords.slice(0, 3).join(", ")}</div>
              </div>
              <div class="text-right">
                <span class="text-xs font-bold text-sky-700 bg-sky-100 px-2 py-1 rounded-full">Score ${p.interest_score}/10</span>
              </div>
            </div>
          `
            )
            .join("")}
        </div>
      </div>

      <div class="bg-white p-6 rounded-xl border border-red-100">
        <h3 class="text-base font-bold text-red-600 mb-2">Unsubscribe</h3>
        <p class="text-xs text-slate-500 mb-4">You will immediately stop receiving your daily 07:00 IST briefings.</p>
        <button onclick="handleUnsubscribe()" class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-xs font-semibold">
          Unsubscribe from Daily Briefings
        </button>
      </div>
    `;
  } catch (err) {
    console.error("Profile error:", err);
    container.innerHTML = `<div class="text-red-500 text-sm">Failed to load profile.</div>`;
  }
}

async function handleUnsubscribe() {
  if (!confirm("Are you sure you want to unsubscribe from IntelliBrief?")) return;

  try {
    const res = await fetch(`${API_BASE}/api/subscriptions/unsubscribe`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: state.userEmail }),
    });

    if (res.ok) {
      showToast("You have been unsubscribed.");
      localStorage.clear();
      state.userId = null;
      state.userEmail = null;
      switchView("landing");
    }
  } catch (err) {
    showToast("Error processing unsubscribe request.", true);
  }
}

// Utility for HTML escaping
function escapeHtml(text) {
  if (!text) return "";
  const div = document.createElement("div");
  div.innerText = text;
  return div.innerHTML;
}

// Initialize on page load
window.addEventListener("DOMContentLoaded", () => {
  // If user already subscribed, default to dashboard, otherwise landing
  if (state.userId) {
    switchView("dashboard");
  } else {
    switchView("landing");
  }
});
