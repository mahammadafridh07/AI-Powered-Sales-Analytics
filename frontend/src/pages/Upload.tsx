import { useState, useCallback } from "react";
import { UploadCloud, FileSpreadsheet, X, CheckCircle2, AlertCircle } from "lucide-react";
import { api } from "../lib/api";
import { ChartCard } from "../components/UI";

const STAGES = ["Uploading", "Validating", "Cleaning", "Analyzing", "Complete"];

export default function Upload() {
  const [file, setFile] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [stageIndex, setStageIndex] = useState(-1);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files?.[0]) setFile(e.dataTransfer.files[0]);
  }, []);

  function reset() {
    setFile(null);
    setStageIndex(-1);
    setResult(null);
    setError("");
  }

  async function handleUpload() {
    if (!file) return;
    setError("");
    setResult(null);
    setStageIndex(0);

    const formData = new FormData();
    formData.append("file", file);

    // Simulate the visible pipeline progression while the real request is in flight
    const timers = [1, 2, 3].map((i) => setTimeout(() => setStageIndex(i), i * 500));

    try {
      const res = await api.post("/upload", formData, { headers: { "Content-Type": "multipart/form-data" } });
      timers.forEach(clearTimeout);
      if (res.data.status === "failed") {
        setStageIndex(-1);
        setError(res.data.error_message || "Upload failed.");
      } else {
        setStageIndex(4);
        setResult(res.data);
      }
    } catch (e: any) {
      timers.forEach(clearTimeout);
      setStageIndex(-1);
      setError(e?.response?.data?.detail || "Upload failed. Please check the file and try again.");
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-xl font-semibold text-slate-900 dark:text-white">Upload Sales Data</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Upload a CSV or Excel file with your order-level sales data.
        </p>
      </div>

      <ChartCard title="Upload File">
        {!file ? (
          <div
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={onDrop}
            className={`flex flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed p-12 text-center transition ${
              dragOver ? "border-brand-500 bg-brand-500/5" : "border-slate-300 dark:border-white/10"
            }`}
          >
            <div className="rounded-full bg-brand-500/10 p-3 text-brand-500">
              <UploadCloud size={24} />
            </div>
            <p className="text-sm font-medium text-slate-700 dark:text-slate-200">
              Drag & drop your CSV or Excel file here
            </p>
            <p className="text-xs text-slate-500 dark:text-slate-400">or</p>
            <label className="cursor-pointer rounded-lg bg-brand-500 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-600">
              Browse files
              <input
                type="file"
                accept=".csv,.xlsx,.xls"
                className="hidden"
                onChange={(e) => e.target.files?.[0] && setFile(e.target.files[0])}
              />
            </label>
            <p className="text-xs text-slate-400">Required columns: order_date, customer_id, customer_name, region, product_id, product_name, category, quantity, unit_price, revenue, profit</p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between rounded-xl bg-slate-50 px-4 py-3 dark:bg-ink-700/40">
              <div className="flex items-center gap-3">
                <FileSpreadsheet size={20} className="text-brand-500" />
                <div>
                  <p className="text-sm font-medium text-slate-700 dark:text-slate-200">{file.name}</p>
                  <p className="text-xs text-slate-500 dark:text-slate-400">{(file.size / 1024).toFixed(1)} KB</p>
                </div>
              </div>
              {stageIndex === -1 && (
                <button onClick={reset} className="text-slate-400 hover:text-negative-500">
                  <X size={18} />
                </button>
              )}
            </div>

            {stageIndex >= 0 && (
              <div className="space-y-2">
                {STAGES.map((s, i) => (
                  <div key={s} className="flex items-center gap-3 text-sm">
                    {i < stageIndex || stageIndex === 4 ? (
                      <CheckCircle2 size={16} className="text-positive-500" />
                    ) : i === stageIndex ? (
                      <span className="h-4 w-4 animate-spin rounded-full border-2 border-brand-500 border-t-transparent" />
                    ) : (
                      <span className="h-4 w-4 rounded-full border-2 border-slate-200 dark:border-white/10" />
                    )}
                    <span className={i <= stageIndex ? "text-slate-700 dark:text-slate-200" : "text-slate-400"}>{s}...</span>
                  </div>
                ))}
              </div>
            )}

            {error && (
              <div className="flex items-start gap-2 rounded-xl bg-negative-500/10 px-4 py-3 text-sm text-negative-500">
                <AlertCircle size={16} className="mt-0.5 shrink-0" />
                {error}
              </div>
            )}

            {result && (
              <div className="rounded-xl bg-positive-500/10 px-4 py-3 text-sm text-positive-500">
                Successfully processed {result.rows_processed.toLocaleString()} rows.
                {result.error_message && <p className="mt-1 text-xs text-warning-500">Note: {result.error_message}</p>}
              </div>
            )}

            <div className="flex gap-3">
              {stageIndex === -1 && (
                <button onClick={handleUpload} className="rounded-lg bg-brand-500 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-600">
                  Start processing
                </button>
              )}
              {(stageIndex === 4 || error) && (
                <button onClick={reset} className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 dark:border-white/10 dark:text-slate-300">
                  Upload another file
                </button>
              )}
            </div>
          </div>
        )}
      </ChartCard>
    </div>
  );
}
