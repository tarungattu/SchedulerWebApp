import React from "react";

function DistanceMatrixDisplay({ matrix }) {
  if (!matrix || matrix.length === 0) return null;

  return (
    <div className="mt-6 overflow-auto max-h-60 border p-2">
      <h3 className="text-md font-semibold mb-2">Distance Matrix:</h3>
      <table className="border-collapse border border-gray-300 w-full text-center">
        <tbody>
          {matrix.map((row, i) => (
            <tr key={i}>
              {row.map((val, j) => (
                <td
                  key={j}
                  className="border border-gray-400 px-3 py-1"
                  title={`Distance from ${i} to ${j}`}
                >
                  {val}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      <p className="mt-2 text-sm text-gray-600">
        <strong>Note:</strong> Last column = Unloading Dock, Second last column = Loading Dock
      </p>
    </div>
  );
}

export default DistanceMatrixDisplay;
