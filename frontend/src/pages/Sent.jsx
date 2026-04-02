import { useEffect, useState } from "react";
import { getSentLeads } from "../api";

export default function Sent() {
  const [leads, setLeads] = useState([]);

  useEffect(() => {
    getSentLeads().then(r => setLeads(r.data));
  }, []);

  return (
    <div style={{ padding: "32px" }}>
      <div style={{ marginBottom: "24px" }}>
        <h1 style={{ fontSize: "24px", fontWeight: "700", margin: 0 }}>Sent Emails</h1>
        <p style={{ color: "#64748b", margin: "4px 0 0", fontSize: "14px" }}>{leads.length} emails sent total</p>
      </div>

      <div style={{ background: "#1e293b", borderRadius: "12px", border: "1px solid #334155", overflow: "hidden" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
          <thead>
            <tr style={{ background: "#0f172a" }}>
              {["Business", "Email", "Website", "AI Score", "Sent At"].map(h => (
                <th key={h} style={{ padding: "12px 16px", textAlign: "left", color: "#64748b", fontWeight: "600" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {leads.map((lead, i) => (
              <tr key={lead.id} style={{ borderTop: "1px solid #0f172a", background: i % 2 === 0 ? "#1e293b" : "#162032" }}>
                <td style={{ padding: "10px 16px", color: "#f1f5f9", fontWeight: "500" }}>{lead.name}</td>
                <td style={{ padding: "10px 16px", color: "#34d399" }}>{lead.email}</td>
                <td style={{ padding: "10px 16px" }}>
                  <a href={lead.website} target="_blank" rel="noreferrer"
                    style={{ color: "#38bdf8", textDecoration: "none" }}>
                    {lead.website?.replace(/https?:\/\//, "").slice(0, 30)}
                  </a>
                </td>
                <td style={{ padding: "10px 16px", color: "#a78bfa" }}>{lead.ai_score ?? "—"}/10</td>
                <td style={{ padding: "10px 16px", color: "#64748b" }}>{lead.emailed_at}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {leads.length === 0 && (
          <div style={{ padding: "40px", textAlign: "center", color: "#64748b" }}>No emails sent yet</div>
        )}
      </div>
    </div>
  );
}