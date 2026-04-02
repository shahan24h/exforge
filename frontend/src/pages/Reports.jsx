import { useEffect, useState } from "react";
import { getReports } from "../api";
import { FileText, Download } from "lucide-react";

export default function Reports() {
  const [reports, setReports] = useState([]);

  useEffect(() => {
    getReports().then(r => setReports(r.data));
  }, []);

  return (
    <div style={{ padding: "32px" }}>
      <div style={{ marginBottom: "24px" }}>
        <h1 style={{ fontSize: "24px", fontWeight: "700", margin: 0 }}>Reports</h1>
        <p style={{ color: "#64748b", margin: "4px 0 0", fontSize: "14px" }}>{reports.length} PDF reports generated</p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "16px" }}>
        {reports.map(report => (
          <div key={report.filename} style={{
            background: "#1e293b", borderRadius: "12px", padding: "20px",
            border: "1px solid #334155", display: "flex", flexDirection: "column", gap: "12px"
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <FileText size={20} color="#38bdf8" />
              <span style={{ fontSize: "13px", fontWeight: "500", color: "#f1f5f9" }}>
                {report.filename.replace("_report.pdf", "").replace(/_/g, " ")}
              </span>
            </div>
            <a href={`http://localhost:8000${report.url}`} target="_blank" rel="noreferrer"
              style={{
                display: "flex", alignItems: "center", gap: "6px",
                background: "#0f172a", border: "1px solid #334155",
                color: "#38bdf8", borderRadius: "8px", padding: "8px 12px",
                textDecoration: "none", fontSize: "12px", fontWeight: "500"
              }}>
              <Download size={12} /> Download PDF
            </a>
          </div>
        ))}
        {reports.length === 0 && (
          <div style={{ padding: "40px", textAlign: "center", color: "#64748b" }}>No reports generated yet</div>
        )}
      </div>
    </div>
  );
}