import React, { useEffect, useState } from "react";
import axios from "axios";

function BenchmarkSelector({ selectedBenchmark, setSelectedBenchmark }) {
  const [benchmarks, setBenchmarks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

useEffect(() => {
  axios.get("/api/benchmarks")
    .then((res) => {
      if (res.data.success && res.data.benchmarks.length > 0) {
        setBenchmarks(res.data.benchmarks);
        setSelectedBenchmark(res.data.benchmarks[0]);  // auto-select first
      } else {
        setError("Failed to fetch benchmarks.");
      }
    })
    .catch(() => setError("Error fetching benchmark list."))
    .finally(() => setLoading(false));
}, []);

  if (loading) return <p className="text-gray-600">Loading benchmarks...</p>;
  if (error) return <p className="text-red-500">{error}</p>;

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        Select Benchmark:
      </label>
      <select
        value={selectedBenchmark}
        onChange={(e) => setSelectedBenchmark(e.target.value)}
        className="w-full p-2 border rounded"
      >
        <option value="">-- Select Benchmark --</option>
        {benchmarks.map((bm) => (
            <option key={bm} value={bm}>
                {bm}
            </option>
            ))}
      </select>
    </div>
  );
}

export default BenchmarkSelector;