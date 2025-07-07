import React, { useState, useEffect } from 'react';
import BirthdayPopup from '../components/BirthdayPopup';
import { useAuth } from '@/lib/auth';
import { api } from '@/lib/api';

interface Pet {
  pet_name: string;
  image?: string;
  birthday?: string;
  breed?: string;
}

const TestBirthdayPopup: React.FC = () => {
  const [showPopup, setShowPopup] = useState(false);
  const [pets, setPets] = useState<Pet[]>([]);
  const [selectedPet, setSelectedPet] = useState<Pet | null>(null);
  const { user } = useAuth();

  // Fetch user's pets when component mounts
  useEffect(() => {
    const fetchPets = async () => {
      if (user && user.customer_key) {
        try {
          const petsData = await api.getUserPets(user.customer_key);
          setPets(petsData);
          // Set the first pet as selected by default
          if (petsData.length > 0) {
            setSelectedPet(petsData[0]);
          }
        } catch (error) {
          console.error('Failed to fetch pets:', error);
          // Fallback to default pet if API fails
          setSelectedPet({ pet_name: 'Buddy', image: '/pug.png' });
        }
      } else {
        // Fallback if no user logged in
        setSelectedPet({ pet_name: 'Buddy', image: '/pug.png' });
      }
    };

    fetchPets();
  }, [user]);

  const handleOpenPopup = () => {
    setShowPopup(true);
  };

  const handleClosePopup = () => {
    setShowPopup(false);
  };

  return (
    <div style={{ padding: '50px', textAlign: 'center' }}>
      <h1>Birthday Popup Test Page</h1>
      
      {/* Pet Selection */}
      {pets.length > 1 && (
        <div style={{ marginBottom: '20px' }}>
          <label style={{ marginRight: '10px' }}>Choose a pet:</label>
          <select 
            onChange={(e) => {
              const pet = pets.find(p => p.pet_name === e.target.value);
              setSelectedPet(pet || null);
            }}
            value={selectedPet?.pet_name || ''}
            style={{ 
              padding: '5px 10px', 
              borderRadius: '5px', 
              border: '1px solid #ccc',
              marginRight: '10px'
            }}
          >
            {pets.map((pet, index) => (
              <option key={index} value={pet.pet_name}>
                {pet.pet_name} {pet.breed ? `(${pet.breed})` : ''}
              </option>
            ))}
          </select>
        </div>
      )}

      {selectedPet && (
        <div style={{ marginBottom: '20px' }}>
          <p>🎉 Birthday popup will show for: <strong>{selectedPet.pet_name}</strong></p>
          {selectedPet.birthday && (
            <p>Birthday: {new Date(selectedPet.birthday).toLocaleDateString()}</p>
          )}
        </div>
      )}

      <button 
        onClick={handleOpenPopup}
        disabled={!selectedPet}
        style={{
          backgroundColor: selectedPet ? '#007bff' : '#ccc',
          color: 'white',
          padding: '10px 20px',
          border: 'none',
          borderRadius: '5px',
          cursor: selectedPet ? 'pointer' : 'not-allowed',
          fontSize: '16px'
        }}
      >
        Show Birthday Popup {selectedPet ? `for ${selectedPet.pet_name}` : ''}
      </button>
      
      {showPopup && selectedPet && (
        <BirthdayPopup
          petName={selectedPet.pet_name}
          petImage={selectedPet.image || '/pug.png'}
          onClose={handleClosePopup}
        />
      )}
    </div>
  );
};

export default TestBirthdayPopup;
