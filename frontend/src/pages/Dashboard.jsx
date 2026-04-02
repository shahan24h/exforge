import { useEffect, useState } from "react";
import { getStats, runPipeline, runModule } from "../api";
import { Play, RefreshCw, Mail, Users, TrendingUp, Activity } from "lucide-react";

const card = (title, value, icon, color) => ({ title, value, icon, color });

export default function Dashboard() {
  const [stats, setStats]   = useState(null);
  const [logs,  setLogs]    = useState([]);
  const [running, setRunning] = useState(false);

  const fetchStats = () => getStats().then(r => setStats(r.data));

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws/logs");
    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      setLogs(prev => [...prev.slice(-100), data]);
      if (data.type === "done") setRunning(false);
    };
    return () => ws.close();
  }, []);

  const handleRun = async (module = null) => {
    setRunning(true);
    setLogs([]);
    try {
      if (module) await runModule(module);
      else await runPipeline();
    } catch (e) {
      setRunning(false);
    }
  };

  const statCards = stats ? [
    { title: "Total Leads",   value: stats.total_leads,  icon: Users,       color: "#38bdf8" },
    { title: "Emails Sent",   value: stats.total_sent,   icon: Mail,        color: "#34d399" },
    { title: "Sent Today",    value: stats.sent_today,   icon: TrendingUp,  color: "#f59e0b" },
    { title: "Sent This Week",value: stats.sent_week,    icon: Activity,    color: "#a78bfa" },
  ] : [];

  const modules = ["scrape", "shortlist", "audit", "report", "compose", "send"];

  return (
    <div style={{ padding: "32px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "32px" }}>
        <div>
          <h1 style={{ fontSize: "24px", fontWeight: "700", margin: 0 }}>Dashboard</h1>
          <p style={{ color: "#64748b", margin: "4px 0 0", fontSize: "14px" }}>
            {stats?.pipeline_running ? "🟢 Pipeline running..." : "⚪ Pipeline idle"}
          </p>
        </div>
        <button onClick={() => handleRun()} disabled={running} style={{
          display: "flex", alignItems: "center", gap: "8px",
          background: running ? "#334155" : "#38bdf8", color: running ? "#64748b" : "#0f172a",
          border: "none", borderRadius: "8px", padding: "10px 20px",
          fontWeight: "600", cursor: running ? "not-allowed" : "pointer", fontSize: "14px"
        }}>
          <Play size={16} />
          {running ? "Running..." : "Run Full Pipeline"}
        </button>
      </div>

      {/* Stat cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "16px", marginBottom: "32px" }}>
        {statCards.map(({ title, value, icon: Icon, color }) => (
          <div key={title} style={{
            background: "#1e293b", borderRadius: "12px", padding: "20px",
            border: "1px solid #334155"
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <div>
                <p style={{ color: "#64748b", fontSize: "12px", margin: "0 0 8px" }}>{title}</p>
                <p style={{ fontSize: "32px", fontWeight: "700", margin: 0, color }}>{value ?? "—"}</p>
              </div>
              <Icon size={20} color={color} />
            </div>
          </div>
        ))}
      </div>

      {/* Status breakdown */}
      {stats?.by_status && (
        <div style={{ background: "#1e293b", borderRadius: "12px", padding: "20px", border: "1px solid #334155", marginBottom: "24px" }}>
          <h2 style={{ fontSize: "16px", fontWeight: "600", margin: "0 0 16px" }}>Lead Status Breakdown</h2>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "10px" }}>
            {Object.entries(stats.by_status).map(([status, count]) => (
              <div key={status} style={{
                background: "#0f172a", borderRadius: "8px", padding: "8px 14px",
                fontSize: "13px", border: "1px solid #334155"
              }}>
                <span style={{ color: "#64748b" }}>{status}: </span>
                <span style={{ color: "#f1f5f9", fontWeight: "600" }}>{count}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Module buttons */}
      <div style={{ background: "#1e293b", borderRadius: "12px", padding: "20px", border: "1px solid #334155", marginBottom: "24px" }}>
        <h2 style={{ fontSize: "16px", fontWeight: "600", margin: "0 0 16px" }}>Run Individual Modules</h2>
        <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
          {modules.map(m => (
            <button key={m} onClick={() => handleRun(m)} disabled={running} style={{
              background: "#0f172a", border: "1px solid #334155", color: "#94a3b8",
              borderRadius: "8px", padding: "8px 16px", cursor: running ? "not-allowed" : "pointer",
              fontSize: "13px", textTransform: "capitalize"
            }}>
              {m}
            </button>
          ))}
        </div>
      </div>

      {/* Live logs */}
      <div style={{ background: "#1e293b", borderRadius: "12px", padding: "20px", border: "1px solid #334155" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
          <h2 style={{ fontSize: "16px", fontWeight: "600", margin: 0 }}>Live Logs</h2>
          <button onClick={() => setLogs([])} style={{
            background: "transparent", border: "none", color: "#64748b",
            cursor: "pointer", display: "flex", alignItems: "center", gap: "4px", fontSize: "12px"
          }}>
            <RefreshCw size={12} /> Clear
          </button>
        </div>
        <div style={{
          background: "#0f172a", borderRadius: "8px", padding: "12px",
          height: "300px", overflowY: "auto", fontFamily: "monospace", fontSize: "12px"
        }}>
          {logs.length === 0 ? (
            <span style={{ color: "#334155" }}>Waiting for pipeline to run...</span>
          ) : logs.map((log, i) => (
            <div key={i} style={{
              color: log.type === "error" ? "#f87171" : log.type === "done" ? "#34d399" : "#94a3b8",
              marginBottom: "2px"
            }}>
              <span style={{ color: "#475569" }}>[{log.time}]</span> {log.message}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}