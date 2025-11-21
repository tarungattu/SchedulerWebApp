# Job Shop and AMR Scheduling Web Application

## Overview

This project presents a comprehensive solution for the complex challenge of simultaneously scheduling jobs and Autonomous Mobile Robots (AMRs) in a manufacturing environment. It features a sophisticated scheduling backend built with Python and Flask, and a user-friendly web interface developed using React.

The core of this project is a novel, modularly designed scheduling algorithm based on genetic algorithms. This algorithm is not just a practical tool but also a significant contribution to academic research in the field of industrial engineering and computational intelligence.

## Features

- **Advanced Scheduling:** Solves the integrated Job Shop Scheduling and AMR scheduling problem.
- **Genetic Algorithm:** Employs a genetic algorithm to find optimal or near-optimal schedules.
- **Web-Based UI:** An intuitive React interface for setting up scheduling problems, visualizing machine layouts, and viewing results.
- **Gantt Chart Visualization:** Automatically generates Gantt charts for both machine and AMR schedules, providing a clear overview of the scheduling outcomes.
- **Benchmark Support:** Allows users to select from various predefined benchmark problems to test and evaluate the scheduler's performance.
- **Modular Backend:** The Python-based scheduling engine is built with modularity in mind, allowing for easier extension and maintenance.

## The Scheduling Algorithm

The scheduling algorithm is a key innovation of this project. It is designed to be highly modular, with distinct components for each part of the genetic algorithm process:

- **Chromosome Representation:** A flexible representation for encoding potential solutions.
- **Genetic Operators:** A suite of operators for selection (e.g., tournament selection), crossover (e.g., single-point), and mutation.
- **Fitness Evaluation:** A robust fitness function that calculates the makespan (Cmax) and guides the optimization process.
- **AMR Integration:** The algorithm explicitly models and schedules the movement of AMRs between workstations, a crucial factor in modern, flexible manufacturing systems.

For a deep dive into the algorithm's mechanics, you can explore the source code here:
[Link to Scheduling Algorithm Source Code](./server/algorithm/JobShopScheduler.py)

## Research Publication

The algorithm and the concepts behind this project are the subject of a peer-reviewed research article. This work underscores the novelty and academic significance of the scheduling approach implemented here.

**Title:** Scheduling of jobs and autonomous mobile robots: Towards the realization of line-less assembly systems

**Link to Paper:** [https://www.growingscience.com/ijiec/Vol16/IJIEC_2025_3.pdf](https://www.growingscience.com/ijiec/Vol16/IJIEC_2025_3.pdf)

**Citation:**
```bibtex
@article{Gattu2025,
    author = {Tarun Ramesh Gattu and Sachin Karadgi and Chinmay S. Magi and Amit Kore and Lloyd Lawrence
    Noronha and P. S. Hiremath},
    year = {2025},
    month = {01},
    title = {Scheduling of jobs and autonomous mobile robots: Towards the realization of line-less assembly systems},
    journal = {International Journal of Industrial Engineering Computations},
    doi = {10.5267/j.ijiec.2025.1.003}
}
```

## Technology Stack

- **Frontend:** React, Tailwind CSS
- **Backend:** Python, Flask
- **Core Algorithm:** Python, Matplotlib, NumPy

## Getting Started

### Prerequisites

- Node.js and npm
- Python 3.x and pip

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/tarungattu/SchedulerWebApp.git
    cd SchedulerWebApp
    ```

2.  **Setup the Backend:**
    ```bash
    cd server
    ```

3.  **Setup the Frontend:**
    ```bash
    cd ../client
    npm install
    ```

### Running the Application

1.  **Start the Backend Server:**
    ```bash
    cd server
    python app.py
    ```
    The Flask server will start on `http://localhost:10000`.

2.  **Start the Frontend Development Server:**
    ```bash
    cd ../client
    npm start
    ```
    The React application will open in your browser at `http://localhost:3000`.

## Usage

Once the application is running, you can use the web interface to:
1.  Select a benchmark problem.
2.  Configure scheduling parameters.
3.  Run the scheduler.
4.  View the resulting Gantt chart and performance metrics.
