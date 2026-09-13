const API_BASE = "http://localhost:8000";

const el = (id) => document.getElementById(id);
const themeToggle = el("themeToggle");
const statusDot = el("statusDot");
const providerSelect = el("providerSelect");
const queryInput = el("queryInput");
const runBtn = el("runBtn");
const examplesEl = el("examples");
const chatbotOutput = el("chatbotOutput");
const agentOutput = el("agentOutput");

/* ===== Theme toggle ===== */
themeToggle.addEventListener("click", () => {
  const root = document.documentElement;
  const next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
  root.setAttribute("data-theme", next);
});

/* ===== Health check ===== */
async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/api/health`);
    const data = await res.json();
    statusDot.classList.add("is-ok");
    statusDot.title = `Server OK · Provider: ${data.provider}`;
    providerSelect.value = guessProviderKey(data.provider);
  } catch (e) {
    statusDot.classList.add("is-error");
    statusDot.title = "Không kết nối được server. Hãy chạy: uvicorn server:app --reload --port 8000";
  }
}

function guessProviderKey(className) {
  if (className.includes("Gemini")) return "gemini";
  if (className.includes("OpenAI")) return "openai";
  return "mock";
}

providerSelect.addEventListener("change", async () => {
  try {
    await fetch(`${API_BASE}/api/provider/${providerSelect.value}`, { method: "POST" });
  } catch (e) {
    console.error("Không đổi được provider:", e);
  }
});

/* ===== Example chips từ test_cases.json ===== */
async function loadExamples() {
  try {
    const res = await fetch(`${API_BASE}/api/test-cases`);
    const cases = await res.json();
    examplesEl.innerHTML = "";
    cases.forEach((tc) => {
      if (tc.question.trim().startsWith("TODO")) return;
      const chip = document.createElement("button");
      chip.className = "example-chip";
      chip.type = "button";
      chip.textContent = tc.question.length > 46 ? tc.question.slice(0, 46) + "…" : tc.question;
      chip.addEventListener("click", () => { queryInput.value = tc.question; });
      examplesEl.appendChild(chip);
    });
    renderTestsTable(cases);
  } catch (e) {
    console.error("Không tải được test cases:", e);
  }
}

/* ===== Chạy so sánh Chatbot vs Agent ===== */
runBtn.addEventListener("click", runComparison);
queryInput.addEventListener("keydown", (e) => { if (e.key === "Enter") runComparison(); });

async function runComparison() {
  const query = queryInput.value.trim();
  if (!query) return;

  runBtn.disabled = true;
  chatbotOutput.innerHTML = `<p class="empty-state">Đang xử lý…</p>`;
  agentOutput.innerHTML = `<p class="empty-state">Đang xử lý…</p>`;

  await Promise.all([runChatbot(query), runAgent(query)]);

  runBtn.disabled = false;
}

async function runChatbot(query) {
  try {
    const res = await fetch(`${API_BASE}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });
    const data = await res.json();
    chatbotOutput.innerHTML = `<p class="chatbot-answer"></p>`;
    chatbotOutput.querySelector("p").textContent = data.response;
  } catch (e) {
    chatbotOutput.innerHTML = `<p class="empty-state">Lỗi kết nối server: ${e.message}</p>`;
  }
}

async function runAgent(query) {
  try {
    const res = await fetch(`${API_BASE}/api/agent`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });
    const data = await res.json();
    agentOutput.innerHTML = "";
    data.trace.forEach((step) => agentOutput.appendChild(renderStepCard(step)));
  } catch (e) {
    agentOutput.innerHTML = `<p class="empty-state">Lỗi kết nối server: ${e.message}</p>`;
  }
}

const STEP_META = {
  TOOL_EXECUTION: { label: "🛠️ Action", cls: "action" },
  FINAL_ANSWER: { label: "🏁 Final Answer", cls: "final" },
};

function renderStepCard(step) {
  const meta = STEP_META[step.action_type] || { label: step.action_type, cls: "thought" };
  const card = document.createElement("div");
  card.className = "step-card";

  const head = document.createElement("div");
  head.className = "step-card__head";
  head.innerHTML = `
    <span class="step-card__type step-card__type--${meta.cls}">${meta.label}</span>
    <span>${step.thought ? escapeHtml(step.thought) : (step.tool_name || "")}</span>
    <span class="step-card__latency">${step.latency_ms ?? ""} ms</span>
  `;

  const body = document.createElement("div");
  body.className = "step-card__body is-collapsed";
  if (step.action_type === "TOOL_EXECUTION") {
    body.textContent =
      `Arguments:\n${JSON.stringify(step.arguments, null, 2)}\n\nObservation:\n${JSON.stringify(step.observation, null, 2)}`;
  } else {
    body.textContent = step.output || "";
  }

  head.addEventListener("click", () => body.classList.toggle("is-collapsed"));

  card.appendChild(head);
  card.appendChild(body);
  return card;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

/* ===== MCP Tools Inspector ===== */
async function loadTools() {
  try {
    const res = await fetch(`${API_BASE}/api/tools`);
    const tools = await res.json();
    const container = el("toolsList");
    container.innerHTML = "";
    tools.forEach((tool) => {
      const card = document.createElement("div");
      card.className = "tool-card";
      card.innerHTML = `
        <p class="tool-card__name">${tool.name || "(chưa đặt tên)"}</p>
        <p class="tool-card__desc">${tool.description || "Chưa có mô tả."}</p>
      `;
      container.appendChild(card);
    });
  } catch (e) {
    console.error("Không tải được tools:", e);
  }
}

/* ===== Test Suite table ===== */
function renderTestsTable(cases) {
  const body = el("testsBody");
  body.innerHTML = "";
  cases.forEach((tc) => {
    const isTodo = tc.question.trim().startsWith("TODO");
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${tc.id}</td>
      <td>${tc.type}</td>
      <td>${tc.complexity}</td>
      <td>${isTodo ? "(chưa điền câu hỏi)" : tc.question}</td>
      <td><span class="badge-status ${isTodo ? "badge-status--todo" : "badge-status--idle"}">${isTodo ? "TODO" : "Sẵn sàng"}</span></td>
      <td><button class="btn btn--ghost" data-question="${encodeURIComponent(tc.question)}" ${isTodo ? "disabled" : ""}>Run</button></td>
    `;
    row.querySelector("button").addEventListener("click", (e) => {
      queryInput.value = decodeURIComponent(e.target.dataset.question);
      runComparison();
    });
    body.appendChild(row);
  });
}

el("runAllBtn").addEventListener("click", async () => {
  const rows = document.querySelectorAll("#testsBody button:not([disabled])");
  for (const btn of rows) {
    queryInput.value = decodeURIComponent(btn.dataset.question);
    await runComparison();
  }
});

/* ===== Trace Waterfall ===== */
async function loadWaterfall() {
  try {
    const res = await fetch(`${API_BASE}/api/trace-waterfall`);
    const trace = await res.json();
    const container = el("waterfallChart");
    container.innerHTML = "";
    if (!trace.length) {
      container.innerHTML = `<p class="empty-state">Chưa có dữ liệu trace. Hãy chạy 1 câu hỏi trước.</p>`;
      return;
    }
    const maxLatency = Math.max(...trace.map((t) => t.latency_ms || 0), 1);
    trace.forEach((t) => {
      const row = document.createElement("div");
      row.className = "waterfall__row";
      const width = Math.max(4, ((t.latency_ms || 0) / maxLatency) * 300);
      row.innerHTML = `
        <span class="waterfall__label">Step ${t.step} · ${t.action_type}</span>
        <span class="waterfall__bar" style="width:${width}px"></span>
        <span class="waterfall__ms">${t.latency_ms ?? 0} ms</span>
      `;
      container.appendChild(row);
    });
  } catch (e) {
    console.error("Không tải được trace waterfall:", e);
  }
}

/* ===== Tabs ===== */
document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((t) => t.classList.remove("is-active"));
    document.querySelectorAll(".panel").forEach((p) => p.classList.remove("is-active"));
    tab.classList.add("is-active");
    el(`panel-${tab.dataset.tab}`).classList.add("is-active");
    if (tab.dataset.tab === "waterfall") loadWaterfall();
  });
});

/* ===== Init ===== */
checkHealth();
loadExamples();
loadTools();