"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import { getJobs, startJob, uploadRIS, uploadText } from "@/lib/api";
import type { ProcessingJob } from "@/lib/types";

export default function UploadPage() {
  const [jobs, setJobs] = useState<ProcessingJob[]>([]);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [pasteText, setPasteText] = useState("");
  const [pasting, setPasting] = useState(false);

  const loadJobs = () => {
    getJobs().then(setJobs).catch(() => {});
  };

  useEffect(() => {
    loadJobs();
    const interval = setInterval(loadJobs, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setMessage(null);
    try {
      const job = await uploadRIS(file);
      setMessage(`Uploaded "${job.filename}" — ${job.total_records} records found.`);
      loadJobs();
    } catch {
      setMessage("Upload failed.");
    } finally {
      setUploading(false);
    }
  };

  const handlePaste = async () => {
    if (!pasteText.trim()) return;
    setPasting(true);
    setMessage(null);
    try {
      const job = await uploadText(pasteText);
      setMessage(`Text submitted — "${job.filename}" created.`);
      setPasteText("");
      loadJobs();
    } catch {
      setMessage("Text upload failed.");
    } finally {
      setPasting(false);
    }
  };

  const handleStart = async (jobId: number) => {
    try {
      await startJob(jobId);
      loadJobs();
    } catch {
      // ignore
    }
  };

  const statusColor = (status: string) => {
    switch (status) {
      case "completed": return "text-green-600";
      case "processing": return "text-blue-600";
      case "failed": return "text-red-600";
      default: return "text-gray-500";
    }
  };

  return (
    <div className="max-w-3xl">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Upload Papers</h1>
      <p className="text-gray-500 mb-6">
        Upload RIS exports from EBSCO, Scopus, Web of Science, or PubMed — or
        paste text directly from a paper. Papers will be processed through AI extraction.
      </p>

      <div className="mb-6 p-6 bg-white border-2 border-dashed border-gray-300 rounded-lg text-center">
        <input
          type="file"
          accept=".ris"
          onChange={handleUpload}
          disabled={uploading}
          className="hidden"
          id="ris-upload"
        />
        <label
          htmlFor="ris-upload"
          className="cursor-pointer text-blue-600 hover:text-blue-700 font-medium"
        >
          {uploading ? "Uploading..." : "Click to select a .ris file"}
        </label>
      </div>

      <div className="mb-8 p-6 bg-white border border-gray-200 rounded-lg">
        <h2 className="text-sm font-semibold text-gray-700 mb-2">Paste paper text</h2>
        <textarea
          value={pasteText}
          onChange={(e) => setPasteText(e.target.value)}
          placeholder="Paste the title, abstract, or full text from a paper..."
          rows={6}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-y"
        />
        <div className="flex items-center justify-between mt-3">
          <span className="text-xs text-gray-400">
            {pasteText.length > 0 ? `${pasteText.length} characters` : ""}
          </span>
          <button
            onClick={handlePaste}
            disabled={pasting || !pasteText.trim()}
            className="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {pasting ? "Submitting..." : "Submit"}
          </button>
        </div>
      </div>

      {message && <p className="mb-4 text-sm text-gray-600">{message}</p>}

      <h2 className="text-lg font-semibold text-gray-700 mb-4">Processing Jobs</h2>
      {jobs.length === 0 ? (
        <p className="text-gray-400">No jobs yet.</p>
      ) : (
        <div className="space-y-3">
          {jobs.map((job) => (
            <div key={job.id} className="p-4 bg-white border border-gray-200 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900">{job.filename}</p>
                  <p className="text-sm text-gray-500">
                    {job.total_records} records
                    {job.processed_count > 0 && ` — ${job.processed_count} processed`}
                    {job.failed_count > 0 && `, ${job.failed_count} failed`}
                    {job.flagged_count > 0 && `, ${job.flagged_count} flagged`}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`text-sm font-medium capitalize ${statusColor(job.status)}`}>
                    {job.status}
                  </span>
                  {job.status === "pending" && (
                    <button
                      onClick={() => handleStart(job.id)}
                      className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                      Start
                    </button>
                  )}
                </div>
              </div>
              {job.status === "completed" && job.result_ingredients && job.result_ingredients.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {job.result_ingredients.map((ing) => (
                    <Link
                      key={ing.slug}
                      href={`/ingredients/${ing.slug}`}
                      className="inline-flex items-center px-3 py-1 text-sm bg-green-50 text-green-700 border border-green-200 rounded-full hover:bg-green-100"
                    >
                      {ing.name} &rarr;
                    </Link>
                  ))}
                </div>
              )}
              {job.status === "processing" && job.total_records > 0 && (
                <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all"
                    style={{ width: `${((job.processed_count + job.failed_count) / job.total_records) * 100}%` }}
                  />
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
