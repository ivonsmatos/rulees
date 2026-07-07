import { spawn, spawnSync } from "node:child_process";
import { existsSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const isWindows = process.platform === "win32";
const logsDir = path.join(root, "logs");
mkdirSync(logsDir, { recursive: true });

const ports = {
  backend: "http://127.0.0.1:8001",
  frontend: "http://127.0.0.1:5173",
  website: "http://127.0.0.1:3000",
};

const started = [];
const output = new Map();

function appendOutput(name, text) {
  const current = output.get(name) ?? "";
  output.set(name, (current + text).slice(-12000));
}

function startProcess(name, command, args, cwd, env = {}) {
  const child = spawn(command, args, {
    cwd,
    env: { ...process.env, ...env },
    windowsHide: true,
    shell: isWindows && command.endsWith(".cmd"),
  });
  started.push({ name, child });
  child.stdout?.on("data", (chunk) => appendOutput(name, chunk.toString()));
  child.stderr?.on("data", (chunk) => appendOutput(name, chunk.toString()));
  return child;
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function waitForUrl(url, name, timeoutMs = 45000) {
  const startedAt = Date.now();
  let lastError = "";
  while (Date.now() - startedAt < timeoutMs) {
    try {
      const response = await fetch(url);
      if (response.ok) return response;
      lastError = `HTTP ${response.status}`;
    } catch (error) {
      lastError = error.message;
    }
    await delay(500);
  }
  throw new Error(`${name} not ready at ${url}: ${lastError}`);
}

async function request(pathname, { method = "GET", token, tenantId, body, expect = 200, raw = false } = {}) {
  const headers = {};
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (token) headers.Authorization = `Bearer ${token}`;
  if (tenantId) headers["X-Tenant-Id"] = tenantId;
  const response = await fetch(`${ports.backend}${pathname}`, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (response.status !== expect) {
    const text = await response.text().catch(() => "");
    throw new Error(`${method} ${pathname} expected ${expect}, got ${response.status}: ${text.slice(0, 500)}`);
  }
  if (raw) return response;
  const text = await response.text();
  return text ? JSON.parse(text) : null;
}

async function openWs(url) {
  const ws = new WebSocket(url);
  const queue = [];
  const waiters = [];
  ws.addEventListener("message", async (event) => {
    const data = JSON.parse(await wsText(event.data));
    const waiter = waiters.shift();
    if (waiter) waiter(data);
    else queue.push(data);
  });
  await new Promise((resolve, reject) => {
    ws.addEventListener("open", resolve, { once: true });
    ws.addEventListener("error", reject, { once: true });
  });
  return {
    send(data) {
      ws.send(JSON.stringify(data));
    },
    next(timeoutMs = 8000) {
      if (queue.length > 0) return Promise.resolve(queue.shift());
      return new Promise((resolve, reject) => {
        const timer = setTimeout(() => {
          const index = waiters.indexOf(resolve);
          if (index >= 0) waiters.splice(index, 1);
          reject(new Error("Timed out waiting for websocket event"));
        }, timeoutMs);
        waiters.push((data) => {
          clearTimeout(timer);
          resolve(data);
        });
      });
    },
    close() {
      ws.close();
    },
  };
}

async function wsText(data) {
  if (typeof data === "string") return data;
  if (data instanceof ArrayBuffer) return Buffer.from(data).toString("utf8");
  if (ArrayBuffer.isView(data)) return Buffer.from(data.buffer).toString("utf8");
  if (data && typeof data.text === "function") return data.text();
  return String(data);
}

async function sendAudioChunk(ws, payload, eventId) {
  ws.send({ event_id: eventId, event_type: "audio.chunk", payload });
  const events = [];
  while (true) {
    const event = await ws.next();
    events.push(event);
    if (event.event_type === "system.ack" && (!eventId || event.event_id === eventId)) {
      return events;
    }
  }
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function runApiFlow() {
  const stamp = `${Date.now()}-${Math.random().toString(16).slice(2, 8)}`;
  const auth = await request("/api/auth/register", {
    method: "POST",
    body: {
      name: "Smoke Tester",
      email: `smoke-${stamp}@rulees.dev`,
      password: "rulees123",
      organization_name: "Smoke Tenant",
    },
  });
  const token = auth.access_token;
  const tenantId = auth.tenant.id;
  const authed = { token, tenantId };

  const projectName = `Projeto Smoke ${stamp}`;
  const project = await request("/api/projects", {
    ...authed,
    method: "POST",
    body: { name: projectName, description: "Fluxo browser smoke" },
  });

  const other = await request("/api/auth/register", {
    method: "POST",
    body: {
      name: "Other Tenant",
      email: `other-${stamp}@rulees.dev`,
      password: "rulees123",
      organization_name: "Other Tenant",
    },
  });
  await request(`/api/projects/${project.id}/rag/search?query=cashback`, {
    token: other.access_token,
    tenantId: other.tenant.id,
    expect: 404,
  });

  const meeting = await request(`/api/projects/${project.id}/meetings`, {
    ...authed,
    method: "POST",
    body: { title: `Reuniao Smoke ${stamp}`, objective: "Validar ciclo MVP no navegador" },
  });

  await request(`/api/meetings/${meeting.id}/start`, { ...authed, method: "POST", expect: 400 });
  await request(`/api/meetings/${meeting.id}/consent`, {
    ...authed,
    method: "POST",
    body: { text_version: "v1", accepted_scope: { audio: true, transcription: true, ai_analysis: true } },
  });
  await request(`/api/meetings/${meeting.id}/start`, { ...authed, method: "POST" });

  const ws = await openWs(`ws://127.0.0.1:8001/ws/meetings/${meeting.id}?token=${token}`);
  const connected = await ws.next();
  assert(connected.event_type === "client.connected", "WebSocket did not send client.connected");

  ws.send({
    event_id: "invalid-audio",
    event_type: "audio.chunk",
    payload: { audio_base64: "@@@", mime_type: "audio/webm" },
  });
  const invalidAudio = await ws.next();
  assert(invalidAudio.event_type === "error.validation", "Invalid audio was not rejected");

  const chunks = [
    "Quando o cliente tiver investimento acima de R$ 15000, deve receber 1% de cashback.",
    "Quando o cliente tiver investimento acima de R$ 15000, deve receber 1% de cashback.",
    "Cliente premium tera beneficio especial.",
    "Fica aprovado que a primeira versao sera lancada para clientes premium.",
  ];
  const wsEvents = [];
  for (let index = 0; index < chunks.length; index += 1) {
    wsEvents.push(...(await sendAudioChunk(ws, { text: chunks[index] }, `chunk-${index + 1}`)));
  }
  ws.close();

  const eventTypes = new Set(wsEvents.map((event) => event.event_type));
  for (const eventType of ["transcript.final", "ai.rule.detected", "ai.question.suggested", "ai.decision.detected"]) {
    assert(eventTypes.has(eventType), `Missing websocket event ${eventType}`);
  }

  const rag = await request(`/api/projects/${project.id}/rag/search?query=cashback%20cliente%20investimento`, authed);
  assert(Array.isArray(rag) && rag.length > 0, "RAG search returned no results");

  const state = await request(`/api/meetings/${meeting.id}/state`, authed);
  const rule = state.rules.find((item) => item.status === "needs_review");
  assert(rule, "No rule in needs_review status");
  assert(state.questions.length > 0, "No question detected");
  assert(state.decisions.length > 0, "No decision detected");

  const approved = await request(`/api/rules/${rule.id}/approve`, { ...authed, method: "POST" });
  assert(approved.status === "approved", "Rule was not approved");

  const document = await request(`/api/meetings/${meeting.id}/documents/generate`, { ...authed, method: "POST" });
  assert(document.content.includes(approved.code), "Generated document does not reference approved rule");

  const sections = await request(`/api/documents/${document.id}/sections`, authed);
  assert(new Set(sections.map((section) => section.section_key)).has("rules"), "Document sections missing rules");

  const pdf = await request(`/api/documents/${document.id}/export/pdf`, { ...authed, raw: true });
  assert(pdf.headers.get("content-type")?.includes("application/pdf"), "PDF export did not return application/pdf");

  await request(`/api/documents/${document.id}/export/markdown`, { ...authed, raw: true });
  await request(`/api/documents/${document.id}/export/excel`, { ...authed, raw: true });
  await request(`/api/documents/${document.id}/export-jobs`, {
    ...authed,
    method: "POST",
    body: { format: "jira" },
  });

  const audit = await request("/api/audit/logs", authed);
  const auditActions = new Set(audit.map((item) => item.action));
  for (const action of ["meeting.start", "rule.approve", "document.generate"]) {
    assert(auditActions.has(action), `Audit log missing ${action}`);
  }

  const usage = await request("/api/usage/summary", authed);
  const usageTypes = new Set(usage.map((item) => item.event_type));
  for (const eventType of ["audio_chunk_received", "ai_rule_detected", "document_generated", "pdf_exported"]) {
    assert(usageTypes.has(eventType), `Usage summary missing ${eventType}`);
  }

  const billing = await request("/api/billing/status", authed);
  assert(billing.plan_name === "trial", "Billing did not return trial plan");

  const agentRuns = await request(`/api/meetings/${meeting.id}/agent-runs`, authed);
  const agentNames = new Set(agentRuns.map((run) => run.agent_name));
  for (const agentName of ["Scribe", "Observer", "RAG Guardian", "Rule Quality", "Inquisitor", "Decision"]) {
    assert(agentNames.has(agentName), `Agent run missing ${agentName}`);
  }

  const metrics = await fetch(`${ports.backend}/metrics`).then((response) => response.text());
  assert(metrics.includes("rulees_http_requests_total"), "Metrics endpoint missing request counter");

  return { auth, projectName, meetingTitle: meeting.title, documentTitle: document.title, documentId: document.id };
}

class CdpClient {
  constructor(wsUrl) {
    this.ws = new WebSocket(wsUrl);
    this.id = 0;
    this.pending = new Map();
    this.events = [];
    this.ready = new Promise((resolve, reject) => {
      this.ws.addEventListener("open", resolve, { once: true });
      this.ws.addEventListener("error", reject, { once: true });
    });
    this.ws.addEventListener("message", async (event) => {
      const message = JSON.parse(await wsText(event.data));
      if (message.id && this.pending.has(message.id)) {
        const { resolve, reject } = this.pending.get(message.id);
        this.pending.delete(message.id);
        if (message.error) reject(new Error(message.error.message));
        else resolve(message.result);
      } else {
        this.events.push(message);
      }
    });
    this.ws.addEventListener("close", () => {
      for (const { reject } of this.pending.values()) {
        reject(new Error("CDP socket closed"));
      }
      this.pending.clear();
    });
  }

  async send(method, params = {}) {
    await this.ready;
    const id = ++this.id;
    const response = new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      setTimeout(() => {
        if (this.pending.has(id)) {
          this.pending.delete(id);
          reject(new Error(`CDP timeout for ${method}`));
        }
      }, 10000);
    });
    this.ws.send(JSON.stringify({ id, method, params }));
    return response;
  }

  close() {
    this.ws.close();
  }
}

async function launchChrome() {
  const chromePath = existsSync("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")
    ? "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    : "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
  const userDataDir = path.join(tmpdir(), `rulees-chrome-${Date.now()}`);
  const port = 9223;
  const child = spawn(chromePath, [
    "--headless=new",
    "--disable-gpu",
    "--no-first-run",
    "--no-default-browser-check",
    "--remote-allow-origins=*",
    "--window-size=1440,1200",
    `--user-data-dir=${userDataDir}`,
    `--remote-debugging-port=${port}`,
    "about:blank",
  ], { windowsHide: true });
  started.push({ name: "chrome", child, cleanup: () => rmSync(userDataDir, { recursive: true, force: true }) });
  await waitForUrl(`http://127.0.0.1:${port}/json/version`, "Chrome DevTools", 15000);
  return { port };
}

async function newPage(port, url = "about:blank") {
  const response = await fetch(`http://127.0.0.1:${port}/json/new?${encodeURIComponent(url)}`, { method: "PUT" });
  const target = await response.json();
  const client = new CdpClient(target.webSocketDebuggerUrl);
  await client.send("Page.enable");
  await client.send("Runtime.enable");
  return client;
}

async function waitForText(client, text, timeoutMs = 20000) {
  const startedAt = Date.now();
  while (Date.now() - startedAt < timeoutMs) {
    const result = await client.send("Runtime.evaluate", {
      expression: `document.body && document.body.innerText.includes(${JSON.stringify(text)})`,
      returnByValue: true,
    });
    if (result.result.value === true) return;
    await delay(500);
  }
  throw new Error(`Text not found in browser: ${text}`);
}

async function browserChecks(smokeData) {
  const { port } = await launchChrome();
  const app = await newPage(port, ports.frontend);
  await waitForText(app, "Rulees");
  await app.send("Runtime.evaluate", {
    expression: `localStorage.setItem("rulees.session", ${JSON.stringify(JSON.stringify(smokeData.auth))}); location.reload();`,
    returnByValue: true,
  });
  await waitForText(app, "Fluxo MVP");
  await waitForText(app, smokeData.projectName);
  await app.send("Runtime.evaluate", {
    expression: `[...document.querySelectorAll("button")].find((button) => button.innerText.includes("Rules Ledger"))?.click()`,
    returnByValue: true,
  });
  await waitForText(app, "Rules Ledger");
  await waitForText(app, "Execuções IA");
  await app.send("Runtime.evaluate", {
    expression: `[...document.querySelectorAll("button")].find((button) => button.innerText.includes("Documentos"))?.click()`,
    returnByValue: true,
  });
  await waitForText(app, "Documentos");
  await waitForText(app, smokeData.documentTitle);
  const appShot = await app.send("Page.captureScreenshot", { format: "png", captureBeyondViewport: true });
  writeFileSync(path.join(logsDir, "smoke-frontend.png"), Buffer.from(appShot.data, "base64"));
  app.close();

  const site = await newPage(port, ports.website);
  await waitForText(site, "Rulees");
  const siteShot = await site.send("Page.captureScreenshot", { format: "png", captureBeyondViewport: true });
  writeFileSync(path.join(logsDir, "smoke-website.png"), Buffer.from(siteShot.data, "base64"));
  site.close();
}

async function main() {
  const python = isWindows
    ? path.join(root, "backend", ".venv", "Scripts", "python.exe")
    : path.join(root, "backend", ".venv", "bin", "python");
  startProcess("backend", python, ["-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8001"], path.join(root, "backend"));
  startProcess("frontend", isWindows ? "npm.cmd" : "npm", ["run", "dev", "--", "--host", "127.0.0.1", "--port", "5173"], path.join(root, "frontend"));
  startProcess("website", isWindows ? "npm.cmd" : "npm", ["run", "dev", "--", "--hostname", "127.0.0.1", "--port", "3000"], path.join(root, "website"));

  await waitForUrl(`${ports.backend}/health`, "backend");
  await waitForUrl(ports.frontend, "frontend");
  await waitForUrl(ports.website, "website");

  const health = await request("/health");
  const dependencies = await request("/health/dependencies");
  const observability = await request("/observability/status");
  const dependencyByName = new Map(dependencies.components.map((component) => [component.name, component]));
  assert(health.status === "ok", "Backend health is not ok");
  assert(dependencyByName.get("database")?.status === "ok", "Database dependency is not ok");
  assert(dependencyByName.get("redis")?.status === "ok", "Redis dependency is not ok");
  assert(observability.metrics.enabled === true, "Metrics not enabled");

  const smokeData = await runApiFlow();
  await browserChecks(smokeData);

  const summary = {
    status: "ok",
    health,
    dependencies,
    project: smokeData.projectName,
    document: smokeData.documentTitle,
    screenshots: [
      path.join(logsDir, "smoke-frontend.png"),
      path.join(logsDir, "smoke-website.png"),
    ],
  };
  writeFileSync(path.join(logsDir, "smoke-summary.json"), JSON.stringify(summary, null, 2));
  console.log(JSON.stringify(summary, null, 2));
}

let exitCode = 0;
try {
  await main();
} catch (error) {
  exitCode = 1;
  console.error(error);
} finally {
  for (const item of started.reverse()) {
    try {
      if (isWindows && item.child.pid) {
        spawnSync("taskkill", ["/PID", String(item.child.pid), "/T", "/F"], { stdio: "ignore" });
      } else {
        item.child.kill();
      }
    } catch {
      // best effort cleanup
    }
    try {
      item.cleanup?.();
    } catch {
      // best effort cleanup
    }
  }
  for (const [name, text] of output) {
    writeFileSync(path.join(logsDir, `smoke-${name}.log`), text);
  }
}
process.exit(exitCode);
