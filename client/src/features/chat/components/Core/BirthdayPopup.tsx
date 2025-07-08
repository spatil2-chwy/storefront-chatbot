import React, { useEffect, useState } from 'react';
import './BirthdayPopup.css';

interface BirthdayPopupProps {
  petName: string;
  petImage: string;
  onClose: () => void;
}

interface ConfettiPiece {
  id: number;
  emoji: string;
  left: number;
  delay: number;
  duration: number;
  size: number;
}

const BirthdayPopup: React.FC<BirthdayPopupProps> = ({ petName, petImage, onClose }) => {
  const [confetti, setConfetti] = useState<ConfettiPiece[]>([]);
  const [showBirthdayImage, setShowBirthdayImage] = useState(false);
  const [isVibrating, setIsVibrating] = useState(false);

  useEffect(() => {
    const emojis = ['🎉', '🎊', '🎈', '🎁', '✨', '🌟', '🎂'];
    const pieces: ConfettiPiece[] = [];
    
    for (let i = 0; i < 12; i++) {
      pieces.push({
        id: i,
        emoji: emojis[Math.floor(Math.random() * emojis.length)],
        left: Math.random() * 100,
        delay: Math.random() * 3,
        duration: 3 + Math.random() * 2,
        size: 32 + Math.random() * 16
      });
    }
    
    setConfetti(pieces);

    // Start vibrating after 1 second
    const vibrateTimer = setTimeout(() => {
      setIsVibrating(true);
    }, 1000);

    // Transition to birthday image after vibration (1.5 seconds total)
    const transitionTimer = setTimeout(() => {
      setIsVibrating(false);
      setShowBirthdayImage(true);
    }, 1500);

    return () => {
      clearTimeout(vibrateTimer);
      clearTimeout(transitionTimer);
    };
  }, []);

  return (
    <div className="birthday-popup">
      {confetti.map((piece) => (
        <div
          key={piece.id}
          className="confetti-piece"
          style={{
            left: `${piece.left}%`,
            animationDelay: `${piece.delay}s`,
            animationDuration: `${piece.duration}s`,
            fontSize: `${piece.size}px`
          }}
        >
          {piece.emoji}
        </div>
      ))}
      <div className="popup-content">
        <button className="close-button" onClick={onClose}>×</button>
        <div className="confetti-background">
          <img 
            src={showBirthdayImage ? "/pugbirthday.png" : petImage} 
            alt={`${petName}'s birthday`} 
            className={`pet-image ${isVibrating ? 'vibrating' : ''}`}
          />
          <h1>Happy Birthday {petName}!</h1>
          <p>We hope your pup has a fur-tastic day. Here is a coupon for a free treat with your next order!</p>
          {/* share button  */}
            <button 
            className="bg-gray-500 hover:bg-gray-600 text-white font-medium py-2 px-4 rounded transition-colors duration-200 cursor-pointer"
            onClick={() => alert('Share functionality coming soon!')}
            >
            Share to social media
            </button>
        </div>
      </div>
    </div>
  );
};

export default BirthdayPopup;