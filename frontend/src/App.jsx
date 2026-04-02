import { useState } from "react";
import Dashboard from "./pages/Dashboard";
import Leads from "./pages/Leads";
import Reports from "./pages/Reports";
import Settings from "./pages/Settings";
import Sent from "./pages/Sent";
import { LayoutDashboard, Users, FileText, Settings2, Mail } from "lucide-react";

const nav = [
  { id: "dashboard", label: "Dashboard",  icon: LayoutDashboard },
  { id: "leads",     label: "Leads",      icon: Users },
  { id: "sent",      label: "Sent Emails",icon: Mail },
  { id: "reports",   label: "Reports",    icon: FileText },
  { id: "settings",  label: "Settings",   icon: Settings2 },
];

export default function App() {
  const [page, setPage] = useState("dashboard");

  const Page = {
    dashboard: Dashboard,
    leads:     Leads,
    sent:      Sent,
    reports:   Reports,
    settings:  Settings,
  }[page];

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "#0f172a", color: "#f1f5f9" }}>
      {/* Sidebar */}
      <div style={{
        width: "220px", background: "#1e293b", padding: "24px 0",
        display: "flex", flexDirection: "column", gap: "4px",
        borderRight: "1px solid #334155", flexShrink: 0
      }}>
        {/* Logo */}
        <div style={{ padding: "0 20px 24px", borderBottom: "1px solid #334155", marginBottom: "8px" }}>
          <div style={{ fontSize: "20px", fontWeight: "700", color: "#38bdf8" }}>ExForge</div>
          <div style={{ fontSize: "11px", color: "#64748b", marginTop: "2px" }}>Lead Gen Agent</div>
        </div>

        {nav.map(({ id, label, icon: Icon }) => (
          <button key={id} onClick={() => setPage(id)} style={{
            display: "flex", alignItems: "center", gap: "10px",
            padding: "10px 20px", background: page === id ? "#0f172a" : "transparent",
            border: "none", color: page === id ? "#38bdf8" : "#94a3b8",
            cursor: "pointer", fontSize: "14px", fontWeight: page === id ? "600" : "400",
            borderLeft: page === id ? "3px solid #38bdf8" : "3px solid transparent",
            width: "100%", textAlign: "left"
          }}>
            <Icon size={16} />
            {label}
          </button>
        ))}
      </div>

      {/* Main content */}
      <div style={{ flex: 1, overflow: "auto" }}>
        <Page />
      </div>
    </div>
  );
}