import React, { useState } from "react";
import { DndProvider, useDrag, useDrop } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";

const ItemTypes = {
  MACHINE: "machine",
  LOADING_DOCK: "loadingDock",
  UNLOADING_DOCK: "unloadingDock",
};

const GRID_SIZE = 40;
const GRID_WIDTH = 800;
const GRID_HEIGHT = 600;

function snapToGrid(x, y) {
  const snappedX = Math.max(0, Math.min(x, GRID_WIDTH - GRID_SIZE));
  const snappedY = Math.max(0, Math.min(y, GRID_HEIGHT - GRID_SIZE));
  return {
    x: Math.round(snappedX / GRID_SIZE) * GRID_SIZE,
    y: Math.round(snappedY / GRID_SIZE) * GRID_SIZE,
  };
}

function DraggableItem({ id, left, top, type, moveItem, children, color }) {
  const [, drag] = useDrag({
    type,
    item: { id, left, top, type },
  });

  const [, drop] = useDrop({
    accept: [ItemTypes.MACHINE, ItemTypes.LOADING_DOCK, ItemTypes.UNLOADING_DOCK],
    drop: (item, monitor) => {
      const delta = monitor.getDifferenceFromInitialOffset();
      if (!delta) return;
      const newLeft = item.left + delta.x;
      const newTop = item.top + delta.y;
      const snapped = snapToGrid(newLeft, newTop);
      moveItem(item.id, snapped.x, snapped.y, item.type);
    },
  });

  return (
    <div
      ref={(node) => drag(drop(node))}
      style={{
        position: "absolute",
        left,
        top,
        width: GRID_SIZE,
        height: GRID_SIZE,
        backgroundColor: color,
        borderRadius: 8,
        border: "2px solid white",
        boxShadow: "0 4px 12px rgba(0,0,0,0.2)",
        cursor: "move",
        color: "white",
        fontWeight: "bold",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        userSelect: "none",
      }}
    >
      {children}
    </div>
  );
}

function MachineLayout({ onDistanceMatrixGenerated }) {
  // Initialize with 4 machines + loading + unloading docks
  const [machines, setMachines] = useState({
    1: { left: GRID_SIZE, top: GRID_SIZE },
    2: { left: GRID_SIZE * 3, top: GRID_SIZE },
    3: { left: GRID_SIZE, top: GRID_SIZE * 3 },
    4: { left: GRID_SIZE * 3, top: GRID_SIZE * 3 },
  });

  const [loadingDock, setLoadingDock] = useState({ left: GRID_SIZE * 5, top: GRID_SIZE * 1 });
  const [unloadingDock, setUnloadingDock] = useState({ left: GRID_SIZE * 5, top: GRID_SIZE * 3 });

  const moveItem = (id, left, top, type) => {
    if (type === ItemTypes.LOADING_DOCK) {
      setLoadingDock({ left, top });
    } else if (type === ItemTypes.UNLOADING_DOCK) {
      setUnloadingDock({ left, top });
    } else {
      setMachines((prev) => ({
        ...prev,
        [id]: { left, top },
      }));
    }
  };

  const calculateDistanceMatrix = () => {
    const machineEntries = Object.entries(machines).sort((a, b) => +a[0] - +b[0]);
    const entities = machineEntries.map(([, pos]) => pos);
    entities.push(loadingDock); // second last
    entities.push(unloadingDock); // last

    const matrix = entities.map((e1) =>
      entities.map((e2) => {
        // Manhattan distance on grid coordinates
        const dx = Math.abs(e1.left - e2.left) / GRID_SIZE;
        const dy = Math.abs(e1.top - e2.top) / GRID_SIZE;
        return dx + dy;
      })
    );

    onDistanceMatrixGenerated(matrix);
  };

  return (
    <div className="border p-4 mt-6">
      <h2 className="text-lg font-bold mb-2">Machine Layout</h2>
      <div
        style={{
          position: "relative",
          width: GRID_WIDTH,
          height: GRID_HEIGHT,
          backgroundColor: "#f0f0f0",
          backgroundImage:
            `linear-gradient(to right, #ccc ${GRID_SIZE}px, transparent 1px),
             linear-gradient(to bottom, #ccc ${GRID_SIZE}px, transparent 1px)`,
          backgroundSize: `${GRID_SIZE}px ${GRID_SIZE}px`,
          border: "1px solid #ccc",
          marginBottom: "1rem",
          userSelect: "none",
        }}
      >
        <DndProvider backend={HTML5Backend}>
          {Object.entries(machines).map(([id, pos]) => (
            <DraggableItem
              key={id}
              id={id}
              left={pos.left}
              top={pos.top}
              type={ItemTypes.MACHINE}
              moveItem={moveItem}
              color="#28a745"
            >
              {id}
            </DraggableItem>
          ))}

          <DraggableItem
            id="loading"
            left={loadingDock.left}
            top={loadingDock.top}
            type={ItemTypes.LOADING_DOCK}
            moveItem={moveItem}
            color="#007bff"
          >
            LOAD
          </DraggableItem>

          <DraggableItem
            id="unloading"
            left={unloadingDock.left}
            top={unloadingDock.top}
            type={ItemTypes.UNLOADING_DOCK}
            moveItem={moveItem}
            color="#dc3545"
          >
            UNLOAD
          </DraggableItem>
        </DndProvider>
      </div>
      <button
        onClick={calculateDistanceMatrix}
        className="mt-2 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
      >
        Generate Distance Matrix
      </button>
    </div>
  );
}

export default MachineLayout;
