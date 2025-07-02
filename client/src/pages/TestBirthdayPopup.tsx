import React, { useState } from 'react';
import BirthdayPopup from '../components/BirthdayPopup';

const TestBirthdayPopup: React.FC = () => {
  const [showPopup, setShowPopup] = useState(false);

  const handleOpenPopup = () => {
    setShowPopup(true);
  };

  const handleClosePopup = () => {
    setShowPopup(false);
  };

  return (
    <div style={{ padding: '50px', textAlign: 'center' }}>
      <h1>Birthday Popup Test Page</h1>
      <button 
        onClick={handleOpenPopup}
        style={{
          backgroundColor: '#007bff',
          color: 'white',
          padding: '10px 20px',
          border: 'none',
          borderRadius: '5px',
          cursor: 'pointer',
          fontSize: '16px'
        }}
      >
        Show Birthday Popup
      </button>
      {showPopup && (
        <BirthdayPopup
          petName="Buddy"
          petImage="/pug.png"
          onClose={handleClosePopup}
        />
      )}
    </div>
  );
};

export default TestBirthdayPopup;
