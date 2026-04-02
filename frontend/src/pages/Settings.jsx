import { useEffect, useState } from "react";
import { getConfig, updateConfig } from "../api";
import { Plus, Trash2, Save } from "lucide-react";

export default function Settings() {
  const [config,  setConfig]  = useState(null);
  const [saved,   setSaved]   = useState(false);

  useEffect(() => {
    getConfig().then(r => setConfig(r.data));
  }, []);

  const save = async () => {
    await updateConfig(config);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const addNiche = () => {
    setConfig(prev => ({
      ...prev,
      search_queries: [...prev.search_queries, { niche: "", location: "", active: true }]
    }));
  };

  const removeNiche = (i) => {
    setConfig(prev => ({
      ...prev,
      search_queries: prev.search_queries.filter((_, idx) => idx !== i)
    }));
  };

  const updateNiche = (i, field, value) => {
    setConfig(prev => ({
      ...prev,
      search_queries: prev.search_queries.map((q, idx) =>
        idx === i ? { ...q, [field]: value } : q
      )
    }));
  };

  if (!config) return <div style={{ padding: "32px", color: "#64748b" }}>Loading...</div>;

  const input = {
    background: "#0f172a", border: "1px solid #334155", color: "#f1f5f9",
    borderRadius: "8px", padding: "8px 12px", fontSize: "13px", width: "100%"
  };

  return (
    <div style={{ padding: "32px", maxWidth: "700px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "32px" }}>
        <h1 style={{ fontSize: "24px", fontWeight: "700", margin: 0 }}>Settings</h1>
        <button onClick={save} style={{
          display: "flex", alignItems: "center", gap: "8px",
          background: saved ? "#34d399" : "#38bdf8", color: "#0f172a",
          border: "none", borderRadius: "8px", padding: "10px 20px",
          fontWeight: "600", cursor: "pointer", fontSize: "14px"
        }}>
          <Save size={16} />
          {saved ? "Saved!" : "Save Settings"}
        </button>
      </div>

      {/* Niches */}
      <div style={{ background: "#1e293b", borderRadius: "12px", padding: "20px", border: "1px solid #334155", marginBottom: "20px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
          <h2 style={{ fontSize: "16px", fontWeight: "600", margin: 0 }}>Target Niches</h2>
          <button onClick={addNiche} style={{
            display: "flex", alignItems: "center", gap: "6px",
            background: "#0f172a", border: "1px solid #334155", color: "#38bdf8",
            borderRadius: "8px", padding: "6px 12px", cursor: "pointer", fontSize: "12px"
          }}>
            <Plus size={12} /> Add Niche
          </button>
        </div>

        {config.search_queries.map((q, i) => (
          <div key={i} style={{ display: "flex", gap: "10px", marginBottom: "10px", alignItems: "center" }}>
            <input
              value={q.niche}
              onChange={e => updateNiche(i, "niche", e.target.value)}
              placeholder="e.g. cleaning services"
              style={{ ...input, flex: 1 }}
            />
            <input
              value={q.location}
              onChange={e => updateNiche(i, "location", e.target.value)}
              placeholder="e.g. New York, NY"
              style={{ ...input, flex: 1 }}
            />
            <label style={{ display: "flex", alignItems: "center", gap: "6px", color: "#94a3b8", fontSize: "13px", whiteSpace: "nowrap" }}>
              <input
                type="checkbox"
                checked={q.active}
                onChange={e => updateNiche(i, "active", e.target.checked)}
              />
              Active
            </label>
            <button onClick={() => removeNiche(i)} style={{
              background: "transparent", border: "none", color: "#f87171",
              cursor: "pointer", padding: "4px"
            }}>
              <Trash2 size={16} />
            </button>
          </div>
        ))}
      </div>

      {/* Other settings */}
      <div style={{ background: "#1e293b", borderRadius: "12px", padding: "20px", border: "1px solid #334155" }}>
        <h2 style={{ fontSize: "16px", fontWeight: "600", margin: "0 0 16px" }}>Pipeline Settings</h2>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
          <div>
            <label style={{ fontSize: "12px", color: "#64748b", display: "block", marginBottom: "6px" }}>Max Results Per Scrape</label>
            <input
              type="number"
              value={config.max_results}
              onChange={e => setConfig(prev => ({ ...prev, max_results: parseInt(e.target.value) }))}
              style={input}
            />
          </div>
          <div>
            <label style={{ fontSize: "12px", color: "#64748b", display: "block", marginBottom: "6px" }}>Daily Run Time</label>
            <input
              type="time"
              value={config.run_time}
              onChange={e => setConfig(prev => ({ ...prev, run_time: e.target.value }))}
              style={input}
            />
          </div>
          <div>
            <label style={{ fontSize: "12px", color: "#64748b", display: "block", marginBottom: "6px" }}>Daily Email Limit</label>
            <input
              type="number"
              value={config.daily_email_limit}
              onChange={e => setConfig(prev => ({ ...prev, daily_email_limit: parseInt(e.target.value) }))}
              style={input}
            />
          </div>
        </div>
      </div>
    </div>
  );
}