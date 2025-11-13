import React, { useState, useEffect, useRef, useCallback } from 'react';

const WarehouseApp = () => {
  // State management
  const [machines, setMachines] = useState([]);
  const [loadingDock, setLoadingDock] = useState({ x: 120, y: 120, type: 'loading' });
  const [unloadingDock, setUnloadingDock] = useState({ x: 320, y: 120, type: 'unloading' });
  const [selectedBenchmark, setSelectedBenchmark] = useState(null);
  const [availableBenchmarks, setAvailableBenchmarks] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const [dragItem, setDragItem] = useState(null);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const [distanceMatrix, setDistanceMatrix] = useState(null);
  const [statusText, setStatusText] = useState('Ready - Select a benchmark and start placing machines');
  const [isLoading, setIsLoading] = useState(false);
  const [schedulingResult, setSchedulingResult] = useState(null);

  // GA Parameters
  const [gaParams, setGaParams] = useState({
    numAMRs: 2,
    crossoverProb: 0.7,
    mutationProb: 0.5,
    populationSize: 250,
    terminationLimit: 300,
    stagnationLimit: 50
  });

  const canvasRef = useRef(null);
  const gridSize = 40;
  // const API_BASE_URL = 'https://flask-backend-l0s9.onrender.com';
  const API_BASE_URL = 'http://10.1.10.13:10000/';

  // Fetch available benchmarks from backend
  useEffect(() => {
    const fetchBenchmarks = async () => {
      try {
        // const response = await fetch(`https://flask-backend-l0s9.onrender.com/api/benchmarks`);
        const response = await fetch(`/api/benchmarks`);
        const data = await response.json();
        if (data.success) {
          setAvailableBenchmarks(data.benchmarks);
        }
      } catch (error) {
        setStatusText('Error: Could not connect to backend');
        console.error('Error fetching benchmarks:', error);
      }
    };
    fetchBenchmarks();
  }, []);

  // Canvas drawing functions
  const drawGrid = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw grid lines
    ctx.strokeStyle = '#d7d1d1ff';
    ctx.lineWidth = 1;
    
    for (let x = 0; x <= canvas.width; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, canvas.height);
      ctx.stroke();
    }
    
    for (let y = 0; y <= canvas.height; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(canvas.width, y);
      ctx.stroke();
    }
    
    // Draw machines
    machines.forEach((machine) => {
      ctx.fillStyle = machine.selected ? '#00d4aa' : '#00b794';
      ctx.fillRect(machine.x, machine.y, gridSize, gridSize);
      ctx.strokeStyle = '#2a2a2a';
      ctx.lineWidth = 2;
      ctx.strokeRect(machine.x, machine.y, gridSize, gridSize);
      
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 13px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(machine.id.toString(), machine.x + gridSize/2, machine.y + gridSize/2 + 5);
    });
    
    // Draw loading dock
    if (loadingDock) {
      ctx.fillStyle = '#4285f4';
      ctx.fillRect(loadingDock.x, loadingDock.y, gridSize, gridSize);
      ctx.strokeStyle = '#2a2a2a';
      ctx.lineWidth = 2;
      ctx.strokeRect(loadingDock.x, loadingDock.y, gridSize, gridSize);
      
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 9px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('LOAD', loadingDock.x + gridSize/2, loadingDock.y + gridSize/2 + 3);
    }
    
    // Draw unloading dock
    if (unloadingDock) {
      ctx.fillStyle = '#ea4335';
      ctx.fillRect(unloadingDock.x, unloadingDock.y, gridSize, gridSize);
      ctx.strokeStyle = '#2a2a2a';
      ctx.lineWidth = 2;
      ctx.strokeRect(unloadingDock.x, unloadingDock.y, gridSize, gridSize);
      
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 8px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('UNLOAD', unloadingDock.x + gridSize/2, unloadingDock.y + gridSize/2 + 3);
    }
  }, [machines, loadingDock, unloadingDock, gridSize]);

  useEffect(() => {
    drawGrid();
  }, [drawGrid]);

  // Utility functions
  const snapToGrid = (x, y) => ({
    x: Math.floor(x / gridSize) * gridSize,
    y: Math.floor(y / gridSize) * gridSize
  });

  const getItemAt = (x, y) => {
    for (let machine of machines) {
      if (x >= machine.x && x <= machine.x + gridSize &&
          y >= machine.y && y <= machine.y + gridSize) {
        return { type: 'machine', item: machine };
      }
    }
    
    if (loadingDock && x >= loadingDock.x && x <= loadingDock.x + gridSize &&
        y >= loadingDock.y && y <= loadingDock.y + gridSize) {
      return { type: 'loading', item: loadingDock };
    }
    
    if (unloadingDock && x >= unloadingDock.x && x <= unloadingDock.x + gridSize &&
        y >= unloadingDock.y && y <= unloadingDock.y + gridSize) {
      return { type: 'unloading', item: unloadingDock };
    }
    
    return null;
  };

  // Event handlers
  const handleMouseDown = (e) => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const item = getItemAt(x, y);
    if (item) {
      setIsDragging(true);
      setDragItem(item);
      setDragOffset({ x: x - item.item.x, y: y - item.item.y });
    }
  };

  const handleMouseMove = (e) => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    if (isDragging && dragItem) {
      const newPos = snapToGrid(x - dragOffset.x, y - dragOffset.y);
      const constrainedPos = {
        x: Math.max(0, Math.min(newPos.x, canvas.width - gridSize)),
        y: Math.max(0, Math.min(newPos.y, canvas.height - gridSize))
      };
      
      if (dragItem.type === 'machine') {
        setMachines(prev => prev.map(m => 
          m.id === dragItem.item.id ? { ...m, ...constrainedPos } : m
        ));
      } else if (dragItem.type === 'loading') {
        setLoadingDock(prev => ({ ...prev, ...constrainedPos }));
      } else if (dragItem.type === 'unloading') {
        setUnloadingDock(prev => ({ ...prev, ...constrainedPos }));
      }
    }
  };

  const handleMouseUp = () => {
    if (isDragging) {
      setIsDragging(false);
      setDragItem(null);
      setStatusText('Item moved');
    }
  };

  // Helper function to find the next available machine ID
  const getNextAvailableMachineId = (currentMachines) => {
    if (currentMachines.length === 0) {
      return 0;
    }
    
    // Extract and sort all existing IDs
    const existingIds = currentMachines.map(m => m.id).sort((a, b) => a - b);
    
    // Find the first gap in the sequence
    for (let i = 0; i < existingIds.length; i++) {
      if (existingIds[i] !== i) {
        return i;
      }
    }
    
    // If no gaps, return the next sequential number
    return existingIds.length;
  };

  // Machine management
  const addMachine = () => {
    const pos = snapToGrid(100 + (machines.length * 60), 200);
    const newId = getNextAvailableMachineId(machines);
    const newMachine = {
      id: newId,
      x: pos.x,
      y: pos.y,
      selected: false
    };
    setMachines(prev => [...prev, newMachine]);
    setStatusText(`Machine ${newId} added`);
  };

  const removeMachine = () => {
    if (machines.length > 0) {
      const removed = machines[machines.length - 1];
      setMachines(prev => prev.slice(0, -1));
      setStatusText(`Machine ${removed.id} removed`);
    }
  };

  const clearLayout = () => {
    setMachines([]);
    setLoadingDock({ x: 120, y: 120, type: 'loading' });
    setUnloadingDock({ x: 320, y: 120, type: 'unloading' });
    setDistanceMatrix(null);
    setSchedulingResult(null);
    setStatusText('Layout cleared');
  };

  // Distance matrix generation
  const generateDistanceMatrix = async () => {
    if (machines.length === 0 || !loadingDock || !unloadingDock) {
      setStatusText('Error: Need at least 1 machine, loading dock, and unloading dock');
      return null;
    }
    
    setIsLoading(true);
    setStatusText('Generating distance matrix...');
    
    try {
      const payload = {
        machines: machines,
        loadingDock: loadingDock,
        unloadingDock: unloadingDock,
        gridSize: gridSize
      };
      
      const response = await fetch(`/api/generate-distance-matrix`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });
      
      const result = await response.json();
      
      if (!response.ok || !result.success) {
        throw new Error(result.error || 'Failed to generate distance matrix');
      }
      
      setDistanceMatrix(result.matrix);
      setStatusText(`Distance matrix generated (${result.size}x${result.size})`);
      return result.matrix;
    } catch (error) {
      setStatusText(`Error: ${error.message || 'Failed to generate distance matrix'}`);
      console.error('Distance matrix generation error:', error);
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  // Run GA optimization
  const runOptimization = async () => {
    if (!selectedBenchmark) {
      setStatusText('Error: Please select a benchmark first');
      return;
    }
    
    // Use saved distance matrix from state
    if (!distanceMatrix) {
      setStatusText('Error: Please generate distance matrix first');
      return;
    }
    
    setIsLoading(true);
    setStatusText('Running genetic algorithm optimization...');
    
    try {
      const payload = {
        benchmark_name: selectedBenchmark,
        distance_matrix: distanceMatrix,
        m: machines.length,
        a: gaParams.numAMRs,
        N: gaParams.populationSize,
        Pc: gaParams.crossoverProb,
        Pm: gaParams.mutationProb,
        T: gaParams.terminationLimit,
        stagnation_limit: gaParams.stagnationLimit
      };
      
      // const response = await fetch(`https://flask-backend-l0s9.onrender.com/api/run`, {
      const response = await fetch(`/api/run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });
      
      if (!response.ok) {
        throw new Error('Failed to run optimization');
      }
      
      const result = await response.json();
      setSchedulingResult(result);
      setStatusText(`Optimization completed! Cmax: ${result.chromosome.Cmax}`);
    } catch (error) {
      setStatusText(`Error: ${error.message || 'Failed to run optimization'}`);
      console.error('Optimization error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Render coordinates display
  const renderCoordinates = () => {
    const machineCoords = machines.map(m => `M${m.id}:(${m.x/gridSize},${m.y/gridSize})`).join(', ');
    const loadingCoords = loadingDock ? `(${loadingDock.x/gridSize},${loadingDock.y/gridSize})` : 'None';
    const unloadingCoords = unloadingDock ? `(${unloadingDock.x/gridSize},${unloadingDock.y/gridSize})` : 'None';
    
    return (
      <div className="coordinates-display">
        <div><strong>Machines:</strong> {machineCoords || 'None'}</div>
        <div><strong>Loading Dock:</strong> {loadingCoords}</div>
        <div><strong>Unloading Dock:</strong> {unloadingCoords}</div>
      </div>
    );
  };

  // Render distance matrix
  const renderDistanceMatrix = () => {
    if (!distanceMatrix) {
      return 'Distance matrix will appear here after generation...';
    }
    
    let matrixText = 'Distance Matrix:\n';
    matrixText += '# Last column: Unloading Dock\n';
    matrixText += '# Second last column: Loading Dock\n\n';
    
    distanceMatrix.forEach((row, i) => {
      matrixText += `[${row.map(val => val.toString().padStart(2)).join(', ')}]`;
      if (i < distanceMatrix.length - 1) matrixText += ',\n';
    });
    
    return matrixText;
  };

  return (
    <div className="min-h-screen bg-black text-white" style={{ fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif' }}>
      {/* Header */}
      <div className="bg-gradient-to-r from-black to-gray-800 border-b border-gray-700 px-6 py-6 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-gradient-to-br from-white to-gray-300 rounded-lg flex items-center justify-center text-black font-black text-lg shadow-lg">
            JSSP
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Job Shop Scheduler UI</h1>
            <p className="text-sm text-gray-400">Dynamic Job Shop layout designer for Genetic Algorithm Solver</p>
            <a href="https://www.growingscience.com/ijiec/Vol16/IJIEC_2025_3.pdf" target="_blank">Read About the Scheduler Here!</a>
          </div>
        </div>
        <div className="bg-gradient-to-r from-green-400 to-green-500 px-5 py-3 rounded-lg flex items-center gap-3 font-semibold text-sm shadow-lg">
          <div className="w-6 h-6 bg-white bg-opacity-20 rounded flex items-center justify-center text-xs">🤖</div>
          <div>
            <div className="text-xs opacity-80">Active AMRs</div>
            <div className="text-lg font-bold">{gaParams.numAMRs}</div>
          </div>
        </div>
      </div>

      <div className="flex h-screen">
        {/* Sidebar */}
        <div className="w-80 bg-gray-900 border-r border-gray-700 p-5 overflow-y-auto">
          {/* Benchmark Selection */}
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-5 mb-5">
            <h3 className="text-white mb-4 text-sm font-semibold uppercase tracking-wide opacity-90">📊 Benchmark Selection</h3>
            <div className="space-y-2">
              {availableBenchmarks.map((benchmark) => (
                <div
                  key={benchmark}
                  className={`p-3 border rounded-lg cursor-pointer transition-all ${
                    selectedBenchmark === benchmark
                      ? 'bg-gradient-to-r from-green-400 to-green-500 text-white border-green-400'
                      : 'bg-black border-gray-700 hover:bg-gray-800 hover:border-green-400'
                  }`}
                  onClick={() => {
                    setSelectedBenchmark(benchmark);
                    setStatusText(`Selected ${benchmark} benchmark`);
                  }}
                >
                    <strong className={selectedBenchmark === benchmark ? "text-black" : "text-green-400"}>
                    {benchmark} Benchmark
                  </strong><br />
                  {/* <small className="opacity-70">Available benchmark data</small> */}
                </div>
              ))}
            </div>
          </div>

          {/* AMR Configuration */}
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-5 mb-5">
            <h3 className="text-white mb-4 text-sm font-semibold uppercase tracking-wide opacity-90">🤖 AMR Configuration</h3>
            <div className="mb-4">
              <label className="block mb-2 text-sm font-medium text-white opacity-90">Number of AMRs:</label>
              <input
                type="number"
                value={gaParams.numAMRs}
                onChange={(e) => setGaParams(prev => ({ ...prev, numAMRs: parseInt(e.target.value) }))}
                className="w-full px-3 py-2 bg-black border border-gray-700 rounded-lg text-white text-sm focus:outline-none focus:border-green-400 focus:ring-2 focus:ring-green-400 focus:ring-opacity-20"
                min="1"
                max="10"
              />
            </div>
          </div>

          {/* GA Parameters */}
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-5 mb-5">
            <h3 className="text-white mb-4 text-sm font-semibold uppercase tracking-wide opacity-90">🧬 Genetic Algorithm Parameters</h3>
            {[
              { key: 'crossoverProb', label: 'Crossover Probability (Pc)', step: 0.1, min: 0, max: 1 },
              { key: 'mutationProb', label: 'Mutation Probability (Pm)', step: 0.1, min: 0, max: 1 },
              { key: 'populationSize', label: 'Population Size (N)', step: 1, min: 10, max: 1000 },
              { key: 'terminationLimit', label: 'Termination Limit', step: 1, min: 50, max: 1000 },
              { key: 'stagnationLimit', label: 'Stagnation Limit', step: 1, min: 10, max: 200 }
            ].map(({ key, label, step, min, max }) => (
              <div key={key} className="mb-4">
                <label className="block mb-2 text-sm font-medium text-white opacity-90">{label}:</label>
                <input
                  type="number"
                  value={gaParams[key]}
                  onChange={(e) => setGaParams(prev => ({ ...prev, [key]: parseFloat(e.target.value) }))}
                  className="w-full px-3 py-2 bg-black border border-gray-700 rounded-lg text-white text-sm focus:outline-none focus:border-green-400 focus:ring-2 focus:ring-green-400 focus:ring-opacity-20"
                  step={step}
                  min={min}
                  max={max}
                />
              </div>
            ))}
          </div>

          {/* Coordinates Display */}
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-5 mb-5">
            <h3 className="text-white mb-4 text-sm font-semibold uppercase tracking-wide opacity-90">📍 Current Coordinates</h3>
            {renderCoordinates()}
          </div>

          {/* Actions */}
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-5 mb-5">
            <h3 className="text-white mb-4 text-sm font-semibold uppercase tracking-wide opacity-90">⚡ Actions</h3>
            <div className="space-y-3">
              <button
                onClick={generateDistanceMatrix}
                className="w-full bg-gradient-to-r from-green-400 to-green-500 text-white px-4 py-2 rounded-lg font-semibold text-sm hover:-translate-y-0.5 transition-all shadow-lg"
              >
                Generate Distance Matrix
              </button>
              <button
                onClick={runOptimization}
                disabled={isLoading}
                className="w-full bg-gradient-to-r from-blue-500 to-blue-600 text-white px-4 py-2 rounded-lg font-semibold text-sm hover:-translate-y-0.5 transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Running Optimization...' : 'Run GA Optimization'}
              </button>
              <button
                onClick={clearLayout}
                className="w-full bg-gradient-to-r from-red-500 to-red-600 text-white px-4 py-2 rounded-lg font-semibold text-sm hover:-translate-y-0.5 transition-all shadow-lg"
              >
                Clear Layout
              </button>
            </div>
          </div>

          {/* Distance Matrix Display */}
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-5 mb-5">
            <h3 className="text-white mb-4 text-sm font-semibold uppercase tracking-wide opacity-90">📈 Distance Matrix</h3>
            <div className="bg-black border border-gray-700 rounded-lg p-4 font-mono text-xs max-h-48 overflow-auto text-green-400">
              <pre>{renderDistanceMatrix()}</pre>
            </div>
          </div>

          {/* Optimization Results */}
          {schedulingResult && (
            <div className="bg-gray-800 border border-gray-700 rounded-lg p-5">
              <h3 className="text-white mb-4 text-sm font-semibold uppercase tracking-wide opacity-90">🎯 Optimization Results</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Cmax:</span>
                  <span className="text-green-400 font-semibold">{schedulingResult.chromosome.Cmax}</span>
                </div>
                <div className="flex justify-between">
                  <span>Fitness:</span>
                  <span className="text-green-400 font-semibold">{schedulingResult.chromosome.fitness}</span>
                </div>
                <div className="flex justify-between">
                  <span>Penalty:</span>
                  <span className="text-red-400 font-semibold">{schedulingResult.chromosome.penalty}</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Main Workspace */}
        <div className="flex-1 flex flex-col bg-black">
          {/* Toolbar */}
          <div className="bg-gray-800 border-b border-gray-700 px-5 py-4 flex gap-3 items-center">
            <button
              onClick={addMachine}
              className="bg-gradient-to-r from-blue-500 to-blue-600 text-white px-4 py-2 rounded-lg font-semibold text-sm hover:-translate-y-0.5 transition-all"
            >
              + Add Machine
            </button>
            <button
              onClick={removeMachine}
              className="bg-gradient-to-r from-red-500 to-red-600 text-white px-4 py-2 rounded-lg font-semibold text-sm hover:-translate-y-0.5 transition-all"
            >
              - Remove Machine
            </button>
            <div className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-xs text-white opacity-80">
              Grid Size: 40x40 units | Click to place items | Drag to move
            </div>
          </div>

          {/* Canvas Area */}
          <div className="flex-1 p-6 bg-black overflow-y-auto">
            <div className="mb-6">
              <canvas
                ref={canvasRef}
                width={800}
                height={600}
                className="border border-gray-700 rounded-lg bg-gray-800 cursor-crosshair"
                onMouseDown={handleMouseDown}
                onMouseMove={handleMouseMove}
                onMouseUp={handleMouseUp}
              />
            </div>

            {/* Optimization Result Visualization */}
            {schedulingResult && (
              <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
                <h3 className="text-white mb-4 text-lg font-semibold flex items-center gap-2">
                  📊 Optimization Result Visualization
                  <span className="text-sm text-gray-400 font-normal">
                    (Cmax: {schedulingResult.chromosome.Cmax})
                  </span>
                </h3>
                
                <div className="bg-black border border-gray-700 rounded-lg p-4">
                  <img
                    src={`${schedulingResult.image_url}?t=${Date.now()}`}
                    alt="Scheduling Optimization Result"
                    width={600}
                    height={600}
                    className=" rounded-lg shadow-lg"
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.nextSibling.style.display = 'block';
                    }}
                  />
                  <div 
                    className="text-center text-gray-400 py-8 hidden"
                    style={{ display: 'none' }}
                  >
                    <div className="text-4xl mb-2">🖼️</div>
                    <div>Result image not available</div>
                    <div className="text-sm">Check if result.png exists in Flask static folder</div>
                  </div>
                </div>

                {/* Additional Result Details */}
                <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-black border border-gray-700 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-green-400">{schedulingResult.chromosome.Cmax}</div>
                    <div className="text-sm text-gray-400">Makespan (Cmax)</div>
                  </div>
                  <div className="bg-black border border-gray-700 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-blue-400">{schedulingResult.chromosome.fitness?.toFixed(4) || 'N/A'}</div>
                    <div className="text-sm text-gray-400">Fitness Score</div>
                  </div>
                  <div className="bg-black border border-gray-700 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-red-400">{schedulingResult.chromosome.penalty || 0}</div>
                    <div className="text-sm text-gray-400">Penalty</div>
                  </div>
                </div>

                {/* Machine Sequence Display */}
                {schedulingResult.chromosome.machine_sequence && (
                  <div className="mt-4 bg-black border border-gray-700 rounded-lg p-4">
                    <h4 className="text-white font-semibold mb-2">Machine Sequence:</h4>
                    <div className="text-sm text-gray-300 font-mono">
                      {schedulingResult.chromosome.machine_sequence.map((seq, idx) => (
                        <span key={idx} className="mr-2">
                          M{seq}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* AMR Sequences Display */}
                {schedulingResult.chromosome.amr_machine_sequences && (
                  <div className="mt-4 bg-black border border-gray-700 rounded-lg p-4">
                    <h4 className="text-white font-semibold mb-2">AMR Machine Sequences:</h4>
                    <div className="space-y-2">
                      {schedulingResult.chromosome.amr_machine_sequences.map((amrSeq, idx) => (
                        <div key={idx} className="text-sm">
                          <span className="text-green-400 font-semibold">AMR {idx}:</span>
                          <span className="text-gray-300 font-mono ml-2">
                            {amrSeq.map((machine, seqIdx) => (
                              <span key={seqIdx} className="mr-2">M{machine}</span>
                            ))}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <div className="bg-gray-900 border-t border-gray-700 px-5 py-3 flex justify-between items-center text-xs">
        <span>{statusText}</span>
        <span>
          Machines: {machines.length} | Loading Dock: {loadingDock ? '✅' : '❌'} | Unloading Dock: {unloadingDock ? '✅' : '❌'}
        </span>
      </div>
    {/* Footer */}
    <footer className="bg-black border-t border-gray-800 px-5 py-4 text-center text-xs text-gray-400">
      <div>
        <a href="https://www.linkedin.com/in/tarun-gattu123" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">LinkedIn</a>
        {' | '}
        <a href="mailto:tarunrgattu@gmail.com" className="text-green-400 hover:underline">tarunrgattu@gmail.com</a>
      </div>
    </footer>
    </div>
  );
};

export default WarehouseApp;