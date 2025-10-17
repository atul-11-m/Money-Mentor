import { useState } from "react";
import { uploadCSV } from "./api";

export default function UploadCSV() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);

  async function handleUpload() {
    if (!file) return;
    setUploading(true);
    setStatus(null);
    try {
      const res = await uploadCSV(file);
      setStatus(`Uploaded ${res.inserted || 0} rows`);
    } catch (err: any) {
      setStatus(`Error: ${err.message || err}`);
    } finally {
      setUploading(false);
      setFile(null);
    }
  }

  return (
    <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 12 }}>
      <input type="file" accept=".csv,text/csv" onChange={(e) => setFile(e.target.files ? e.target.files[0] : null)} className="input" />
      <button className="btn btn-primary" onClick={handleUpload} disabled={!file || uploading}>{uploading ? "Uploading..." : "Upload CSV"}</button>
      {status && <div style={{ color: "var(--muted)", fontSize: 13 }}>{status}</div>}
    </div>
  );
}
