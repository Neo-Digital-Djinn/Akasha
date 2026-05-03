import React, { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { io } from "socket.io-client";

const API = "http://localhost:5000";

// ─── socket ────────────────────────────────────────────────────────────────
const socket = io(API, { transports: ["websocket"] });

// ─── helpers ───────────────────────────────────────────────────────────────
function Badge({ label, value, color = "blue" }) {
  const colors = {
    blue: "bg-blue-900 text-blue-200",
    green: "bg-green-900 text-green-200",
    yellow: "bg-yellow-900 text-yellow-200",
    red: "bg-red-900 text-red-200",
  };
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-xs font-mono ${colors[color]}`}>
      {label}: {value}
    </span>
  );
}

// ─── GovernorPanel ─────────────────────────────────────────────────────────
function GovernorPanel() {
  const [state, setState] = useState({ github_limit: 60, github_used: 0, llm_limit: 20, llm_used: 0 });
  const [ghLimit, setGhLimit] = useState(60);
  const [llmLimit, setLlmLimit] = useState(20);
  const [saved, setSaved] = useState(false);

  const fetch = useCallback(async () => {
    const r = await axios.get(`${API}/api/governor`);
    setState(r.data);
    setGhLimit(r.data.github_limit);
    setLlmLimit(r.data.llm_limit);
  }, []);

  useEffect(() => { fetch(); }, [fetch]);

  const save = async () => {
    await axios.post(`${API}/api/governor`, { github_limit: Number(ghLimit), llm_limit: Number(llmLimit) });
    setSaved(true);
    setTimeout(() => setSaved(false), 1500);
    fetch();
  };

  return (
    <div className="p-4 border border-indigo-700 rounded-lg bg-gray-900">
      <h2 className="text-indigo-300 text-lg font-semibold mb-3">⚖️ Governor Panel</h2>
      <div className="grid grid-cols-2 gap-3 mb-3">
        <div>
          <label className="text-gray-400 text-sm block mb-1">GitHub calls/min</label>
          <input
            type="number"
            value={ghLimit}
            onChange={e => setGhLimit(e.target.value)}
            className="w-full bg-gray-800 text-white border border-gray-600 rounded px-2 py-1 text-sm"
          />
          <div className="mt-1">
            <Badge label="used" value={`${state.github_used}/${state.github_limit}`} color="blue" />
          </div>
        </div>
        <div>
          <label className="text-gray-400 text-sm block mb-1">LLM calls/min</label>
          <input
            type="number"
            value={llmLimit}
            onChange={e => setLlmLimit(e.target.value)}
            className="w-full bg-gray-800 text-white border border-gray-600 rounded px-2 py-1 text-sm"
          />
          <div className="mt-1">
            <Badge label="used" value={`${state.llm_used}/${state.llm_limit}`} color="yellow" />
          </div>
        </div>
      </div>
      <button
        onClick={save}
        className="bg-indigo-700 hover:bg-indigo-600 text-white px-4 py-1 rounded text-sm transition"
      >
        {saved ? "✓ Saved" : "Update Limits"}
      </button>
    </div>
  );
}

// ─── IssueCard ─────────────────────────────────────────────────────────────
function IssueCard({ issue, onFeedback }) {
  const [adj, setAdj] = useState(0);
  const [code, setCode] = useState(issue.code || "");
  const [showCode, setShowCode] = useState(false);

  const submit = async () => {
    await axios.post(`${API}/api/feedback`, {
      repo: issue.repo,
      issue_number: issue.number,
      adjustment: adj,
    });
  };

  const push = async () => {
    await axios.post(`${API}/api/update_file`, {
      repo: issue.repo,
      path: `aetherius/issue-${issue.number}.py`,
      content: code,
      message: `aetherius: patch for #${issue.number}`,
    });
  };

  return (
    <div className="p-4 border border-gray-700 rounded-lg bg-gray-900 mb-3">
      <div className="flex items-start justify-between">
        <div>
          <a
            href={`https://github.com/${issue.repo}/issues/${issue.number}`}
            target="_blank"
            rel="noreferrer"
            className="text-indigo-400 font-semibold hover:underline"
          >
            {issue.repo}#{issue.number}
          </a>
          <span className="text-white ml-2">{issue.title}</span>
        </div>
        <Badge label="priority" value={issue.priority} color="green" />
      </div>
      {issue.labels?.length > 0 && (
        <div className="mt-1 flex gap-1 flex-wrap">
          {issue.labels.map(l => (
            <span key={l} className="text-xs bg-gray-700 text-gray-300 rounded px-1">{l}</span>
          ))}
        </div>
      )}
      <p className="text-gray-400 text-sm mt-2 line-clamp-2">{issue.body}</p>

      <div className="mt-3 flex items-center gap-2 flex-wrap">
        <input
          type="number"
          value={adj}
          onChange={e => setAdj(Number(e.target.value))}
          className="w-20 bg-gray-800 text-white border border-gray-600 rounded px-2 py-0.5 text-sm"
          placeholder="±adj"
        />
        <button
          onClick={submit}
          className="bg-blue-700 hover:bg-blue-600 text-white px-3 py-0.5 rounded text-sm"
        >
          Adjust Priority
        </button>
        <button
          onClick={() => setShowCode(!showCode)}
          className="bg-gray-700 hover:bg-gray-600 text-gray-200 px-3 py-0.5 rounded text-sm"
        >
          {showCode ? "Hide Code" : "Edit Code"}
        </button>
        {showCode && (
          <button
            onClick={push}
            className="bg-green-700 hover:bg-green-600 text-white px-3 py-0.5 rounded text-sm"
          >
            Push to GitHub
          </button>
        )}
      </div>

      {showCode && (
        <textarea
          value={code}
          onChange={e => setCode(e.target.value)}
          className="mt-2 w-full h-32 bg-gray-800 text-green-300 font-mono text-xs border border-gray-600 rounded p-2 resize-y"
          spellCheck={false}
        />
      )}
    </div>
  );
}

// ─── Ledger ────────────────────────────────────────────────────────────────
function LedgerPanel({ entries }) {
  return (
    <div className="p-4 border border-gray-700 rounded-lg bg-gray-900">
      <h2 className="text-gray-300 text-lg font-semibold mb-2">📜 Aetherius Ledger</h2>
      <div className="h-48 overflow-y-auto font-mono text-xs text-green-400 space-y-0.5">
        {entries.length === 0 && <div className="text-gray-600">— no entries yet —</div>}
        {[...entries].reverse().map((e, i) => (
          <div key={i} className="border-b border-gray-800 py-0.5">{e}</div>
        ))}
      </div>
    </div>
  );
}

// ─── App ───────────────────────────────────────────────────────────────────
export default function AetheriusDashboard() {
  const [issues, setIssues] = useState([]);
  const [ledger, setLedger] = useState([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    // Initial fetch
    axios.get(`${API}/api/issues`).then(r => setIssues(r.data));
    axios.get(`${API}/api/ledger`).then(r => setLedger(r.data));

    // Live updates
    socket.on("connect", () => setConnected(true));
    socket.on("disconnect", () => setConnected(false));
    socket.on("update", data => {
      if (data.issues) setIssues(data.issues);
      if (data.ledger) setLedger(data.ledger);
    });
    return () => socket.off("update");
  }, []);

  return (
    <div className="min-h-screen bg-gray-950 text-white p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-indigo-300 tracking-wide">⚡ Aetherius</h1>
          <p className="text-gray-500 text-sm mt-0.5">Celestial GitHub Issue Manager · Akasha Constellation</p>
        </div>
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${connected ? "bg-green-400" : "bg-red-500"}`} />
          <span className="text-gray-400 text-sm">{connected ? "live" : "disconnected"}</span>
          <Badge label="issues" value={issues.length} color="blue" />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left column — issues */}
        <div className="lg:col-span-2">
          <h2 className="text-gray-300 text-lg font-semibold mb-3">🔍 Ranked Issues</h2>
          {issues.length === 0 && (
            <div className="text-gray-600 text-sm italic">No issues loaded yet — waiting for scan cycle…</div>
          )}
          {issues.map(issue => (
            <IssueCard key={`${issue.repo}-${issue.number}`} issue={issue} />
          ))}
        </div>

        {/* Right column — governor + ledger */}
        <div className="space-y-4">
          <GovernorPanel />
          <LedgerPanel entries={ledger} />
        </div>
      </div>
    </div>
  );
}
