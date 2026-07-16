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
    <div className="mb-3 flex items-center gap-2">
      <input
        type="file"
        accept=".csv,text/csv"
        onChange={(e) => setFile(e.target.files ? e.target.files[0] : null)}
        className="input"
      />
      <button
        className="btn btn-primary"
        onClick={handleUpload}
        disabled={!file || uploading}
      >
        {uploading ? "Uploading..." : "Upload CSV"}
      </button>
      {status && <div className="text-sm text-muted">{status}</div>}
    </div>
  );
}
