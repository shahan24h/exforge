import { useEffect, useState } from "react";
import { getLeads } from "../api";

const STATUS_COLORS = {
  new:              "#64748b",
  approved:         "#38bdf8",
  shortlisted:      "#38bdf8",
  audited:          "#a78bfa",
  report_ready:     "#f59e0b",
  email_drafted:    "#fb923c",
  approved_to_send: "#34d399",
  emailed:          "#22c55e",
  rejected:         "#f87171",
  no_email:         "#94a3b8",
};

export default function Leads() {
  const [leads,  setLeads]  = useState([]);
  const [filter, setFilter] = useState("");

  useEffect(() => {
    getLeads(filter || undefined).then(r => setLeads(r.data));
  }, [filter]);

  const statuses = ["", "new", "approved", "audited", "report_ready",
                    "email_drafted", "approved_to_send", "emailed", "rejected", "no_email"];

  return (
    <div style={{ padding: "32px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
        <h1 style={{ fontSize: "24px", fontWeight: "700", margin: 0 }}>Leads</h1>
        <select value={filter} onChange={e => setFilter(e.target.value)} style={{
          background: "#1e293b", border: "1px solid #334155", color: "#f1f5f9",
          borderRadius: "8px", padding: "8px 12px", fontSize: "13px"
        }}>
          {statuses.map(s => <option key={s} value={s}>{s || "All statuses"}</option>)}
        </select>
      </div>

      <div style={{ background: "#1e293b", borderRadius: "12px", border: "1px solid #334155", overflow: "hidden" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
          <thead>
            <tr style={{ background: "#0f172a" }}>
              {["Name", "Category", "Phone", "Website", "Rating", "Score", "Email", "Status"].map(h => (
                <th key={h} style={{ padding: "12px 16px", textAlign: "left", color: "#64748b", fontWeight: "600" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {leads.map((lead, i) => (
              <tr key={lead.id} style={{ borderTop: "1px solid #1e293b", background: i % 2 === 0 ? "#1e293b" : "#162032" }}>
                <td style={{ padding: "10px 16px", color: "#f1f5f9", fontWeight: "500" }}>{lead.name}</td>
                <td style={{ padding: "10px 16px", color: "#94a3b8" }}>{lead.category}</td>
                <td style={{ padding: "10px 16px", color: "#94a3b8" }}>{lead.phone}</td>
                <td style={{ padding: "10px 16px" }}>
                  <a href={lead.website} target="_blank" rel="noreferrer"
                    style={{ color: "#38bdf8", textDecoration: "none", fontSize: "12px" }}>
                    {lead.website?.replace(/https?:\/\//, "").slice(0, 25)}
                  </a>
                </td>
                <td style={{ padding: "10px 16px", color: "#f59e0b" }}>{lead.rating} ⭐</td>
                <td style={{ padding: "10px 16px", color: "#a78bfa" }}>{lead.ai_score ?? "—"}</td>
                <td style={{ padding: "10px 16px", color: "#94a3b8", fontSize: "12px" }}>{lead.email || "—"}</td>
                <td style={{ padding: "10px 16px" }}>
                  <span style={{
                    background: STATUS_COLORS[lead.status] + "22",
                    color: STATUS_COLORS[lead.status] || "#64748b",
                    borderRadius: "6px", padding: "3px 8px", fontSize: "11px", fontWeight: "600"
                  }}>
                    {lead.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {leads.length === 0 && (
          <div style={{ padding: "40px", textAlign: "center", color: "#64748b" }}>No leads found</div>
        )}
      </div>
    </div>
  );
}