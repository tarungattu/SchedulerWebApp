import { useEffect, useState } from "react";
import MachineLayout from "./components/MachineLayout";
import DistanceMatrixDisplay from "./components/DistanceMatrixDisplay";

function App() {
  const [benchmarks, setBenchmarks] = useState([]);
  const [selectedBenchmark, setSelectedBenchmark] = useState("");
  const [loading, setLoading] = useState(true);
  const [distanceMatrix, setDistanceMatrix] = useState([]);

  useEffect(() => {
    fetch("/api/benchmarks")
      .then((res) => res.json())
      .then((data) => {
        if (data.success) {
          setBenchmarks(data.benchmarks);
          setSelectedBenchmark("");
        } else {
          console.error("Failed to load benchmarks:", data.error);
        }
      })
      .catch((err) => {
        console.error("Error fetching benchmarks:", err);
      })
      .finally(() => setLoading(false));
  }, []);

  const handleSelectChange = (e) => {
    setSelectedBenchmark(e.target.value);
    console.log("Selected Benchmark:", e.target.value);
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-4">Select a Benchmark</h1>

      {loading ? (
        <p>Loading benchmarks...</p>
      ) : benchmarks.length === 0 ? (
        <p>No benchmarks available</p>
      ) : (
        <select
          value={selectedBenchmark}
          onChange={handleSelectChange}
          className="border p-2 rounded"
        >
          <option value="" disabled>
            Select a benchmark
          </option>
          {benchmarks.map((benchmark) => (
            <option key={benchmark} value={benchmark}>
              {benchmark}
            </option>
          ))}
        </select>
      )}

      {/* Pass selectedBenchmark if you want, or ignore for now */}
      <MachineLayout onDistanceMatrixGenerated={setDistanceMatrix} />

      <DistanceMatrixDisplay matrix={distanceMatrix} />
    </div>
  );
}

export default App;
