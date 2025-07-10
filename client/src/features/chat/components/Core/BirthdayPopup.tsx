import React, { useEffect, useState } from 'react';

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
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50 overflow-hidden animate-fadeIn">
      {confetti.map((piece) => (
        <div
          key={piece.id}
          className="absolute -top-12 pointer-events-none opacity-80 animate-confettiFall"
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
      <div className="bg-white rounded-xl p-8 text-center relative max-w-md w-11/12 shadow-2xl animate-slideIn text-gray-800 border border-gray-200">
        <button 
          className="absolute top-4 right-4 bg-gray-100 border border-gray-300 text-gray-500 w-8 h-8 rounded-full flex items-center justify-center text-xl cursor-pointer transition-all duration-200 hover:bg-gray-200 hover:text-gray-700"
          onClick={onClose}
        >
          ×
        </button>
        <div className="relative">
          <img 
            src={showBirthdayImage ? "/pugbirthday.png" : petImage} 
            alt={`${petName}'s birthday`} 
            className={`w-30 h-30 rounded-full mb-6 border-4 border-gray-200 object-cover transition-all duration-300 ease-in-out ${
              isVibrating 
                ? 'animate-vibrate' 
                : 'animate-bounce'
            }`}
          />
          <h1 className="text-3xl font-bold mb-4 text-gray-900">
            Happy Birthday {petName}!
          </h1>
          <p className="text-lg leading-relaxed mb-6 text-gray-700">
            We hope your pup has a fur-tastic day. Here is a coupon for a free treat with your next order!
          </p>
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