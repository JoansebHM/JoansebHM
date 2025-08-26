import React, { useState, useRef } from 'react';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

const PreviewCapacityInfo = ({ capacityData }) => {
  const tableRef = useRef(null);

  // Sample data structure for testing if no data is provided
  const defaultCapacityData = {
    'Production Capacity': [
      { period: 'Q1', location1: 100, location2: 150, location3: 200 },
      { period: 'Q2', location1: 120, location2: 180, location3: 220 },
      { period: 'Q3', location1: 110, location2: 160, location3: 210 }
    ],
    'Storage Capacity': [
      { period: 'Q1', warehouse1: 500, warehouse2: 600 },
      { period: 'Q2', warehouse1: 520, warehouse2: 650 },
      { period: 'Q3', warehouse1: 510, warehouse2: 620 }
    ],
    'Transport Capacity': [
      { period: 'Q1', trucks: 50, ships: 10, planes: 5, trains: 20 },
      { period: 'Q2', trucks: 55, ships: 12, planes: 6, trains: 22 },
      { period: 'Q3', trucks: 52, ships: 11, planes: 5, trains: 21 }
    ]
  };

  const data = capacityData || defaultCapacityData;

  // Calculate the maximum number of columns across all capacity types
  const getMaxColumns = () => {
    let maxCols = 0;
    Object.values(data).forEach(typeData => {
      if (typeData.length > 0) {
        const cols = Object.keys(typeData[0]).length;
        maxCols = Math.max(maxCols, cols);
      }
    });
    // Add 1 for the total column
    return maxCols + 1;
  };

  const maxColumns = getMaxColumns();

  // Calculate totals for each capacity type
  const calculateTotals = (typeData) => {
    const totals = {};
    
    if (typeData.length === 0) return totals;
    
    const keys = Object.keys(typeData[0]);
    keys.forEach(key => {
      if (key !== 'period') {
        totals[key] = typeData.reduce((sum, row) => sum + (row[key] || 0), 0);
      }
    });
    
    return totals;
  };

  // Generate empty cells to pad tables to uniform width
  const generatePaddingCells = (currentColumns) => {
    const paddingCount = maxColumns - currentColumns;
    return Array(paddingCount).fill(null).map((_, index) => (
      <td key={`padding-${index}`} className="excel-cell empty-cell"></td>
    ));
  };

  // Render a single capacity type table with totals as columns
  const renderCapacityTable = (typeName, typeData) => {
    if (typeData.length === 0) return null;

    const totals = calculateTotals(typeData);
    const dataKeys = Object.keys(typeData[0]).filter(key => key !== 'period');
    const currentColumns = dataKeys.length + 1; // +1 for period column

    return (
      <div key={typeName} className="capacity-table-section">
        <h3 className="table-title">{typeName}</h3>
        <table className="excel-table">
          <thead>
            <tr>
              <th className="excel-header">Period</th>
              {dataKeys.map(key => (
                <th key={key} className="excel-header">{key}</th>
              ))}
              <th className="excel-header total-header">Total</th>
              {generatePaddingCells(currentColumns + 1)}
            </tr>
          </thead>
          <tbody>
            {typeData.map((row, index) => (
              <tr key={index}>
                <td className="excel-cell period-cell">{row.period}</td>
                {dataKeys.map(key => (
                  <td key={key} className="excel-cell data-cell">{row[key] || 0}</td>
                ))}
                <td className="excel-cell total-cell">
                  {dataKeys.reduce((sum, key) => sum + (row[key] || 0), 0)}
                </td>
                {generatePaddingCells(currentColumns + 1)}
              </tr>
            ))}
            {/* Totals row */}
            <tr className="totals-row">
              <td className="excel-cell total-label">Total</td>
              {dataKeys.map(key => (
                <td key={key} className="excel-cell column-total">{totals[key] || 0}</td>
              ))}
              <td className="excel-cell grand-total">
                {Object.values(totals).reduce((sum, val) => sum + val, 0)}
              </td>
              {generatePaddingCells(currentColumns + 1)}
            </tr>
          </tbody>
        </table>
      </div>
    );
  };

  // Render the complete Excel-style sheet
  const renderExcelSheet = () => {
    return (
      <div className="excel-sheet" ref={tableRef}>
        <div className="sheet-header">
          <h2>Capacity Information Report</h2>
        </div>
        {Object.entries(data).map(([typeName, typeData]) =>
          renderCapacityTable(typeName, typeData)
        )}
      </div>
    );
  };

  // Export to PDF functionality
  const exportToPDF = async () => {
    if (!tableRef.current) return;

    try {
      const canvas = await html2canvas(tableRef.current, {
        scale: 2,
        useCORS: true,
        backgroundColor: '#ffffff'
      });

      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('l', 'mm', 'a4'); // Landscape orientation
      
      const imgWidth = 280;
      const pageHeight = pdf.internal.pageSize.height;
      const imgHeight = (canvas.height * imgWidth) / canvas.width;
      let heightLeft = imgHeight;

      let position = 20;

      pdf.addImage(imgData, 'PNG', 10, position, imgWidth, imgHeight);
      heightLeft -= pageHeight;

      while (heightLeft >= 0) {
        position = heightLeft - imgHeight + 20;
        pdf.addPage();
        pdf.addImage(imgData, 'PNG', 10, position, imgWidth, imgHeight);
        heightLeft -= pageHeight;
      }

      pdf.save('capacity-report.pdf');
    } catch (error) {
      console.error('Error generating PDF:', error);
    }
  };

  return (
    <div className="preview-capacity-container">
      <div className="controls">
        <button onClick={exportToPDF} className="export-btn">
          Export to PDF
        </button>
      </div>
      {renderExcelSheet()}
    </div>
  );
};

export default PreviewCapacityInfo;