import React, { useState } from 'react';

const CapabilityTable = () => {
  // Define the table columns
  const columns = [
    { key: 'dirección', label: 'Dirección' },
    { key: 'comuna', label: 'Comuna' },
    { key: 'código_comuna', label: 'Código de comuna' },
    { key: 'barrio', label: 'Barrio' },
    { key: 'código_barrio', label: 'Código de barrio' },
    { key: 'coordenadas_x', label: 'Coordenadas X (latitud)' },
    { key: 'coordenadas_y', label: 'Coordenadas Y (longitud)' },
  ];

  // State for dynamic rows
  const [rows, setRows] = useState([
    {
      id: 1,
      dirección: '',
      comuna: '',
      código_comuna: '',
      barrio: '',
      código_barrio: '',
      coordenadas_x: '',
      coordenadas_y: '',
    }
  ]);

  // Mock geocoding function - simulates API call
  const handleGeocod = async (address, rowId) => {
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Mock geocoding response data
    const mockGeocodingResponse = {
      comuna_nom: 'Comuna Ejemplo',
      comuna_cod: '13101',
      barrio_nom: 'Barrio Ejemplo',
      barrio_cod: 'B001',
      direccion: address,
      latitud: '-33.4489',
      longitud: '-70.6693'
    };

    // Update the specific row with geocoded data
    setRows(prevRows => 
      prevRows.map(row => 
        row.id === rowId 
          ? {
              ...row,
              dirección: mockGeocodingResponse.direccion,
              comuna: mockGeocodingResponse.comuna_nom,
              código_comuna: mockGeocodingResponse.comuna_cod,
              barrio: mockGeocodingResponse.barrio_nom,
              código_barrio: mockGeocodingResponse.barrio_cod,
              coordenadas_x: mockGeocodingResponse.latitud,
              coordenadas_y: mockGeocodingResponse.longitud,
            }
          : row
      )
    );
  };

  // Handle geocoding for a specific row
  const handleGeocodingForRow = async (rowId) => {
    const row = rows.find(r => r.id === rowId);
    if (row && row.dirección.trim()) {
      await handleGeocod(row.dirección, rowId);
    }
  };

  // Add a new dynamic row
  const addNewRow = () => {
    const newRow = {
      id: Date.now(), // Simple ID generation
      dirección: '',
      comuna: '',
      código_comuna: '',
      barrio: '',
      código_barrio: '',
      coordenadas_x: '',
      coordenadas_y: '',
    };
    setRows([...rows, newRow]);
  };

  // Handle input changes for specific cells
  const handleCellChange = (rowId, columnKey, value) => {
    setRows(prevRows =>
      prevRows.map(row =>
        row.id === rowId
          ? { ...row, [columnKey]: value }
          : row
      )
    );
  };

  // Render individual cells based on column type and row context
  const renderCell = (row, column) => {
    const isAddressColumn = column.key === 'dirección';
    
    if (isAddressColumn) {
      // Special rendering for "Dirección" column - includes geocoding button
      return (
        <div className="address-input-container">
          <input
            type="text"
            className="address-input"
            value={row[column.key]}
            onChange={(e) => handleCellChange(row.id, column.key, e.target.value)}
            placeholder="Ingrese dirección"
          />
          <button
            className="geocode-button"
            onClick={() => handleGeocodingForRow(row.id)}
            disabled={!row.dirección.trim()}
            title="Geocodificar dirección"
          >
            📍
          </button>
        </div>
      );
    }

    // Standard input for other columns
    return (
      <input
        type="text"
        value={row[column.key]}
        onChange={(e) => handleCellChange(row.id, column.key, e.target.value)}
        placeholder={`Ingrese ${column.label.toLowerCase()}`}
      />
    );
  };

  return (
    <div>
      <table className="capability-table">
        <thead>
          <tr>
            {columns.map(column => (
              <th key={column.key}>{column.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map(row => (
            <tr key={row.id}>
              {columns.map(column => (
                <td key={`${row.id}-${column.key}`}>
                  {renderCell(row, column)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      
      <button className="add-row-button" onClick={addNewRow}>
        Agregar Nueva Fila
      </button>
    </div>
  );
};

export default CapabilityTable;