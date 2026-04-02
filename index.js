import React from 'react';
import ReactDOM from 'react-dom/client';
import PreviewCapacityInfo from './PreviewCapacityInfo.jsx';
import './PreviewCapacityInfo.css';

// Sample test data to demonstrate the component
const testCapacityData = {
  'Production Capacity': [
    { period: 'Q1 2024', plant_A: 150, plant_B: 200, plant_C: 180 },
    { period: 'Q2 2024', plant_A: 160, plant_B: 220, plant_C: 190 },
    { period: 'Q3 2024', plant_A: 155, plant_B: 210, plant_C: 185 },
    { period: 'Q4 2024', plant_A: 165, plant_B: 230, plant_C: 195 }
  ],
  'Storage Capacity': [
    { period: 'Q1 2024', warehouse_1: 500, warehouse_2: 600 },
    { period: 'Q2 2024', warehouse_1: 520, warehouse_2: 650 },
    { period: 'Q3 2024', warehouse_1: 510, warehouse_2: 620 },
    { period: 'Q4 2024', warehouse_1: 530, warehouse_2: 670 }
  ],
  'Transport Capacity': [
    { period: 'Q1 2024', trucks: 50, ships: 10, planes: 5, trains: 20, drones: 8 },
    { period: 'Q2 2024', trucks: 55, ships: 12, planes: 6, trains: 22, drones: 10 },
    { period: 'Q3 2024', trucks: 52, ships: 11, planes: 5, trains: 21, drones: 9 },
    { period: 'Q4 2024', trucks: 58, ships: 13, planes: 7, trains: 24, drones: 12 }
  ],
  'Processing Capacity': [
    { period: 'Q1 2024', line_1: 80, line_2: 90, line_3: 85, line_4: 75 },
    { period: 'Q2 2024', line_1: 85, line_2: 95, line_3: 90, line_4: 80 },
    { period: 'Q3 2024', line_1: 82, line_2: 92, line_3: 87, line_4: 77 },
    { period: 'Q4 2024', line_1: 88, line_2: 98, line_3: 93, line_4: 83 }
  ]
};

function App() {
  return (
    <div>
      <header style={{ 
        background: '#1f2937', 
        color: 'white', 
        padding: '1rem',
        textAlign: 'center',
        marginBottom: '20px'
      }}>
        <h1>Capacity Information Preview Demo</h1>
        <p>Demonstrating Excel-style layout with uniform table widths and column-based totals</p>
      </header>
      
      <main>
        <PreviewCapacityInfo capacityData={testCapacityData} />
      </main>
      
      <footer style={{ 
        textAlign: 'center', 
        padding: '20px',
        color: '#6b7280',
        marginTop: '40px',
        borderTop: '1px solid #e5e7eb'
      }}>
        <p>PreviewCapacityInfo Component - Layout Improvements Demo</p>
        <p>✓ Totals displayed as columns | ✓ Uniform table widths | ✓ Excel-style formatting</p>
      </footer>
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);