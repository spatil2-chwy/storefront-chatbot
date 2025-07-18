import React, { useState } from 'react';
import { Button } from '../../../../ui/Buttons/Button';
import { Input } from '../../../../ui/Input/Input';
import { Label } from '../../../../ui/Input/Label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../../../ui/Selects/Select';
import { Switch } from '../../../../ui/Toggles/Switch';
import { Calendar, ChevronLeft, ChevronRight } from 'lucide-react';
import { PetProfileInfo } from '../../../../types';

interface PetEditProps {
  petInfo: PetProfileInfo;
  onSave: (updatedPet: PetProfileInfo) => void;
  onCancel: () => void;
}

export const PetEdit: React.FC<PetEditProps> = ({
  petInfo,
  onSave,
  onCancel,
}) => {
  const [formData, setFormData] = useState<PetProfileInfo>(petInfo);
  const [isLoading, setIsLoading] = useState(false);
  const [isCalendarOpen, setIsCalendarOpen] = useState(false);
  const [currentDate, setCurrentDate] = useState(new Date());

  const handleInputChange = (field: keyof PetProfileInfo, value: string | number | boolean) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSave = async () => {
    setIsLoading(true);
    try {
      await onSave(formData);
    } finally {
      setIsLoading(false);
    }
  };

  // Calendar helper functions
  const getDaysInMonth = (date: Date) => {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
  };

  const getFirstDayOfMonth = (date: Date) => {
    return new Date(date.getFullYear(), date.getMonth(), 1).getDay();
  };

  const formatDateForDisplay = (date: string | null) => {
    if (!date) return '';
    try {
      const d = new Date(date);
      return d.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      });
    } catch {
      return '';
    }
  };

  const handleDateSelect = (day: number) => {
    const selectedDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
    handleInputChange('birthday', selectedDate.toISOString());
    setIsCalendarOpen(false);
  };

  const navigateMonth = (direction: 'prev' | 'next') => {
    setCurrentDate(prev => {
      const newDate = new Date(prev);
      if (direction === 'prev') {
        newDate.setMonth(newDate.getMonth() - 1);
      } else {
        newDate.setMonth(newDate.getMonth() + 1);
      }
      return newDate;
    });
  };

  const renderCalendar = () => {
    const daysInMonth = getDaysInMonth(currentDate);
    const firstDayOfMonth = getFirstDayOfMonth(currentDate);
    const days = [];

    // Add empty cells for days before the first day of the month
    for (let i = 0; i < firstDayOfMonth; i++) {
      days.push(<div key={`empty-${i}`} className="h-8 w-8"></div>);
    }

    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      const isSelected = formData.birthday && 
        new Date(formData.birthday).getDate() === day &&
        new Date(formData.birthday).getMonth() === currentDate.getMonth() &&
        new Date(formData.birthday).getFullYear() === currentDate.getFullYear();

      days.push(
        <button
          key={day}
          onClick={() => handleDateSelect(day)}
          className={`h-8 w-8 rounded-full text-sm font-medium transition-colors ${
            isSelected
              ? 'bg-purple-500 text-white'
              : 'hover:bg-purple-100 text-gray-700'
          }`}
        >
          {day}
        </button>
      );
    }

    return days;
  };

  // Close calendar when clicking outside
  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (isCalendarOpen && !(event.target as Element).closest('.calendar-container')) {
        setIsCalendarOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isCalendarOpen]);

  return (
    <div className="space-y-4">
      <div className="text-sm text-gray-600 mb-4">
        Let's update {petInfo.name}'s information. You can skip any field you don't want to fill out.
      </div>

      <div className="space-y-4">
        {/* Pet Name */}
        <div className="space-y-2">
          <Label htmlFor="pet-name">Pet Name</Label>
          <Input
            id="pet-name"
            value={formData.name}
            onChange={(e) => handleInputChange('name', e.target.value)}
            placeholder="Enter pet name"
          />
        </div>

        {/* Pet Type */}
        <div className="space-y-2">
          <Label htmlFor="pet-type">Pet Type</Label>
          <Select
            value={formData.type}
            onValueChange={(value) => handleInputChange('type', value)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select pet type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="DOG">Dog</SelectItem>
              <SelectItem value="CAT">Cat</SelectItem>
              <SelectItem value="BIRD">Bird</SelectItem>
              <SelectItem value="FISH">Fish</SelectItem>
              <SelectItem value="RABBIT">Rabbit</SelectItem>
              <SelectItem value="HAMSTER">Hamster</SelectItem>
              <SelectItem value="OTHER">Other</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Breed */}
        <div className="space-y-2">
          <Label htmlFor="pet-breed">Breed</Label>
          <Input
            id="pet-breed"
            value={formData.breed}
            onChange={(e) => handleInputChange('breed', e.target.value)}
            placeholder="Enter breed"
          />
        </div>

        {/* Gender */}
        <div className="space-y-2">
          <Label htmlFor="pet-gender">Gender</Label>
          <Select
            value={formData.gender}
            onValueChange={(value) => handleInputChange('gender', value)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select gender" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="MALE">Male</SelectItem>
              <SelectItem value="FMLE">Female</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Life Stage */}
        <div className="space-y-2">
          <Label htmlFor="pet-life-stage">Life Stage</Label>
          <Select
            value={formData.life_stage}
            onValueChange={(value) => handleInputChange('life_stage', value)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select life stage" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="P">Puppy/Kitten</SelectItem>
              <SelectItem value="A">Adult</SelectItem>
              <SelectItem value="S">Senior</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Weight */}
        <div className="space-y-2">
          <Label htmlFor="pet-weight">Weight (lbs)</Label>
          <Input
            id="pet-weight"
            type="number"
            value={formData.weight}
            onChange={(e) => handleInputChange('weight', parseFloat(e.target.value) || 0)}
            placeholder="Enter weight"
          />
        </div>

        {/* Birthday */}
        <div className="space-y-2">
          <Label htmlFor="pet-birthday">Birthday</Label>
          <div className="relative calendar-container">
            <button
              type="button"
              onClick={() => setIsCalendarOpen(!isCalendarOpen)}
              className="w-full text-sm border border-purple-200 focus:border-purple-500 focus:ring-purple-500 bg-white hover:bg-purple-50 transition-colors pr-8 py-2 px-3 rounded-md text-left flex items-center justify-between"
            >
              <span className={formData.birthday ? 'text-gray-900' : 'text-gray-500'}>
                {formData.birthday ? formatDateForDisplay(formData.birthday) : 'Select birthday'}
              </span>
              <Calendar className="h-4 w-4 text-purple-400" />
            </button>
            
            {isCalendarOpen && (
              <div className="absolute top-full right-0 mt-1 bg-white border border-purple-200 rounded-lg shadow-lg z-50 p-4 min-w-64 calendar-container">
                <div className="flex items-center justify-between mb-4">
                  <button
                    onClick={() => navigateMonth('prev')}
                    className="p-1 hover:bg-purple-100 rounded-full transition-colors"
                  >
                    <ChevronLeft className="h-4 w-4 text-purple-600" />
                  </button>
                  <h3 className="text-sm font-semibold text-gray-900">
                    {currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                  </h3>
                  <button
                    onClick={() => navigateMonth('next')}
                    className="p-1 hover:bg-purple-100 rounded-full transition-colors"
                  >
                    <ChevronRight className="h-4 w-4 text-purple-600" />
                  </button>
                </div>
                
                <div className="grid grid-cols-7 gap-1 mb-2">
                  {['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'].map(day => (
                    <div key={day} className="h-8 w-8 flex items-center justify-center text-xs font-medium text-gray-500">
                      {day}
                    </div>
                  ))}
                </div>
                
                <div className="grid grid-cols-7 gap-1">
                  {renderCalendar()}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Allergies */}
        <div className="space-y-2">
          <Label htmlFor="pet-allergies">Allergies</Label>
          <div className="flex items-center space-x-2">
            <Switch
              id="pet-allergies"
              checked={formData.allergies}
              onCheckedChange={(checked) => handleInputChange('allergies', checked)}
            />
            <span className="text-sm text-gray-600">
              {formData.allergies ? 'Has allergies' : 'No allergies'}
            </span>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex space-x-3 pt-4">
        <Button
          onClick={handleSave}
          disabled={isLoading}
          className="flex-1 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white"
        >
          {isLoading ? 'Saving...' : 'Save Changes'}
        </Button>
        <Button
          variant="outline"
          onClick={onCancel}
          disabled={isLoading}
          className="flex-1"
        >
          Cancel
        </Button>
      </div>
    </div>
  );
}; 