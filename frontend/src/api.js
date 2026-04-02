import axios from "axios";

const API = axios.create({ baseURL: "http://localhost:8000" });

export const getStats       = () => API.get("/stats");
export const getLeads       = (status) => API.get("/leads", { params: { status } });
export const getSentLeads   = () => API.get("/leads/sent");
export const getReports     = () => API.get("/reports");
export const getConfig      = () => API.get("/config");
export const updateConfig   = (data) => API.post("/config", data);
export const runPipeline    = () => API.post("/pipeline/run");
export const runModule      = (module) => API.post(`/pipeline/${module}`);