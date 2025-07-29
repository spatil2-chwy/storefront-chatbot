import React, { useState } from 'react';
import { Button } from '../../../../ui/Buttons/Button';
import { Input } from '../../../../ui/Input/Input';
import { Label } from '../../../../ui/Input/Label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../../../ui/Selects/Select';
import { MultiSelect, MultiSelectOption } from '../../../../ui/Selects/MultiSelect';
import { Calendar, ChevronLeft, ChevronRight, Plus, X } from 'lucide-react';
import { usersApi } from '@/lib/api/users';
import { useAuth } from '@/lib/auth';
import { BreedSelect } from '../../../../components/BreedSelect';
import { LifeStageDisplay } from '../../../../components/LifeStageDisplay';

interface AddPetFromChatProps {
  onPetAdded: (petId: number) => void;
  onCancel: () => void;
}

export const AddPetFromChat: React.FC<AddPetFromChatProps> = ({
  onPetAdded,
  onCancel
}) => {
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [isCalendarOpen, setIsCalendarOpen] = useState(false);
  const [currentDate, setCurrentDate] = useState(new Date());
  const [manualDateInput, setManualDateInput] = useState('');
  const [formData, setFormData] = useState({
    pet_name: '',
    pet_type: '',
    pet_breed: '',
    gender: '',
    weight: 0,
    life_stage: '',
    birthday: '',
    allergies: [] as string[]
  });
  const [errors, setErrors] = useState<{
    weight?: string;
    birthday?: string;
  }>({});

  // Allergy options for MultiSelect
  const allergiesOptions: MultiSelectOption[] = [
    { value: 'Beef', label: 'Beef' },
    { value: 'Chicken', label: 'Chicken' },
    { value: 'Corn', label: 'Corn' },
    { value: 'Dairy', label: 'Dairy' },
    { value: 'Egg', label: 'Egg' },
    { value: 'Fish', label: 'Fish' },
    { value: 'Lamb', label: 'Lamb' },
    { value: 'Other', label: 'Other' },
    { value: 'Pork', label: 'Pork' },
    { value: 'Rabbit', label: 'Rabbit' },
    { value: 'Soy', label: 'Soy' },
    { value: 'Wheat', label: 'Wheat' },
    { value: 'None', label: 'None' }
  ];

  // Helper function to format allergies array to string
  const formatAllergies = (allergies: string[]): string => {
    return allergies.join(', ');
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
    setFormData(prev => ({
      ...prev,
      birthday: selectedDate.toISOString()
    }));
    setManualDateInput(formatDateForDisplay(selectedDate.toISOString()));
    setIsCalendarOpen(false);
  };

  const handleManualDateInput = (value: string) => {
    // Remove all non-numeric characters
    const numericValue = value.replace(/\D/g, '');
    
    // Format with slashes - add slash immediately when section is complete
    let formattedValue = '';
    for (let i = 0; i < numericValue.length && i < 8; i++) {
      formattedValue += numericValue[i];
      // Add slash after month (2 digits) or day (2 digits)
      if ((i === 1 || i === 3) && i < numericValue.length - 1) {
        formattedValue += '/';
      }
    }
    
    setManualDateInput(formattedValue);
    
    // Parse MM/DD/YYYY format when complete
    if (formattedValue.length === 10) {
      try {
        const [month, day, year] = formattedValue.split('/');
        const date = new Date(parseInt(year), parseInt(month) - 1, parseInt(day));
        
        if (!isNaN(date.getTime())) {
          setFormData(prev => ({
            ...prev,
            birthday: date.toISOString()
          }));
        }
      } catch (error) {
        // Invalid date format, ignore
      }
    }
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

  const validateWeight = (weight: number): string | undefined => {
    if (weight < 0) return 'Weight cannot be negative';
    if (weight > 1000) return 'Weight seems too high. Please check the value.';
    if (!Number.isFinite(weight)) return 'Please enter a valid number';
    return undefined;
  };

  const validateBirthday = (birthday: string): string | undefined => {
    if (!birthday) return undefined;
    
    try {
      const date = new Date(birthday);
      const today = new Date();
      today.setHours(23, 59, 59, 999); // End of today
      
      if (isNaN(date.getTime())) {
        return 'Please enter a valid date';
      }
      
      if (date > today) {
        return 'Birthday cannot be in the future';
      }
      
      // Check if date is reasonable (not too far in the past)
      const minDate = new Date();
      minDate.setFullYear(minDate.getFullYear() - 50); // 50 years ago
      
      if (date < minDate) {
        return 'Birthday seems too far in the past';
      }
      
      return undefined;
    } catch (error) {
      return 'Please enter a valid date';
    }
  };

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear errors when user starts typing
    if (errors[field as keyof typeof errors]) {
      setErrors(prev => ({
        ...prev,
        [field]: undefined
      }));
    }
  };

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) {
      e.preventDefault();
    }
    
    // Validate form data
    const weightError = validateWeight(formData.weight);
    const birthdayError = validateBirthday(formData.birthday);
    
    if (weightError || birthdayError) {
      setErrors({
        weight: weightError,
        birthday: birthdayError
      });
      return;
    }
    
    if (!user?.customer_key || !formData.pet_name || !formData.pet_type) {
      return;
    }

    setIsLoading(true);
    try {
      const petData = {
        pet_name: formData.pet_name,
        pet_type: formData.pet_type,
        pet_breed: formData.pet_breed,
        gender: formData.gender,
        weight: formData.weight,
        life_stage: formData.life_stage,
        birthday: formData.birthday ? new Date(formData.birthday).toISOString().split('T')[0] : undefined,
        allergies: formatAllergies(formData.allergies)
      };

      const newPet = await usersApi.createPet(user.customer_key, petData);
      console.log('AddPetFromChat: newPet:', newPet);
      onPetAdded(newPet.pet_profile_id);
    } catch (error) {
      console.error('Error creating pet:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg px-6 py-4 border border-green-200">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-blue-500 rounded-full flex items-center justify-center">
            <Plus className="h-4 w-4 text-white" />
          </div>
          <div>
            <h4 className="font-bold text-gray-900 text-lg">Add New Pet</h4>
            <p className="text-gray-600 text-sm">Let's create a profile for your new furry friend!</p>
          </div>
        </div>

        <div onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="pet_name" className="text-sm font-medium">
              Pet Name *
            </Label>
            <Input
              id="pet_name"
              value={formData.pet_name}
              onChange={(e) => handleInputChange('pet_name', e.target.value)}
              placeholder="Enter pet name"
              required
              className="mt-1"
            />
          </div>

          <div>
            <Label htmlFor="pet_type" className="text-sm font-medium">
              Type *
            </Label>
            <Select
              value={formData.pet_type}
              onValueChange={(value) => handleInputChange('pet_type', value)}
            >
              <SelectTrigger className="mt-1">
                <SelectValue placeholder="Select type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="DOG">Dog</SelectItem>
                <SelectItem value="CAT">Cat</SelectItem>
                <SelectItem value="HORSE">Horse</SelectItem>
                <SelectItem value="BIRD">Bird</SelectItem>
                <SelectItem value="FISH">Fish</SelectItem>
                <SelectItem value="FARM_ANIMAL">Farm Animal</SelectItem>
                <SelectItem value="SMALL_PET">Small Pet</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
                          <BreedSelect
                species={formData.pet_type}
                value={formData.pet_breed}
                onChange={(value) => handleInputChange('pet_breed', value)}
                label="Breed"
                placeholder={formData.pet_type ? "Select breed (optional)" : "Select pet type first"}
                className="mt-1"
              />
          </div>

          <div>
            <Label htmlFor="gender" className="text-sm font-medium">
              Gender
            </Label>
            <Select
              value={formData.gender}
              onValueChange={(value) => handleInputChange('gender', value)}
            >
              <SelectTrigger className="mt-1">
                <SelectValue placeholder="Select gender" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="MALE">Male</SelectItem>
                <SelectItem value="FEMALE">Female</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="weight" className="text-sm font-medium">
              Weight (lbs)
            </Label>
            <Input
              id="weight"
              type="number"
              step="0.1"
              min="0"
              max="1000"
              value={formData.weight || ''}
              onChange={(e) => {
                const value = e.target.value;
                if (value === '') {
                  handleInputChange('weight', 0);
                } else {
                  const numValue = parseFloat(value);
                  if (!isNaN(numValue)) {
                    handleInputChange('weight', numValue);
                  }
                }
              }}
              placeholder="0.0"
              className={`mt-1 ${errors.weight ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : ''}`}
            />
            {errors.weight && (
              <p className="text-red-500 text-xs mt-1">{errors.weight}</p>
            )}
          </div>

          <div>
            <Label className="text-sm font-medium">Birthday</Label>
            <div className="relative mt-1">
              <div className="flex gap-2">
                <Input
                  type="text"
                  placeholder="MM/DD/YYYY"
                  value={manualDateInput}
                  onChange={(e) => handleManualDateInput(e.target.value)}
                  className={`flex-1 ${errors.birthday ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : ''}`}
                  maxLength={10}
                  inputMode="numeric"
                />
                <button
                  type="button"
                  onClick={() => setIsCalendarOpen(!isCalendarOpen)}
                  className="px-3 py-2 border border-gray-300 focus:border-purple-500 focus:ring-purple-500 bg-white hover:bg-gray-50 transition-colors rounded-md"
                >
                  <Calendar className="h-4 w-4 text-gray-400" />
                </button>
              </div>
              {errors.birthday && (
                <p className="text-red-500 text-xs mt-1">{errors.birthday}</p>
              )}
              
              {isCalendarOpen && (
                <div className="absolute top-full left-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-50 p-4 min-w-64">
                  <div className="flex items-center justify-between mb-4">
                    <button
                      type="button"
                      onClick={() => navigateMonth('prev')}
                      className="p-1 hover:bg-gray-100 rounded-full transition-colors"
                    >
                      <ChevronLeft className="h-4 w-4 text-gray-600" />
                    </button>
                    <h3 className="text-sm font-semibold text-gray-900">
                      {currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                    </h3>
                    <button
                      type="button"
                      onClick={() => navigateMonth('next')}
                      className="p-1 hover:bg-gray-100 rounded-full transition-colors"
                    >
                      <ChevronRight className="h-4 w-4 text-gray-600" />
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

          <div>
            <Label htmlFor="life_stage" className="text-sm font-medium">
              Life Stage
            </Label>
            <div className="mt-1 p-2 border border-gray-200 rounded-md bg-gray-50">
              <LifeStageDisplay
                petType={formData.pet_type}
                birthday={formData.birthday}
                legacyStage={formData.life_stage}
                showAge={true}
              />
            </div>
          </div>

          <div>
            <Label className="text-sm font-medium">Allergies</Label>
            <MultiSelect
              options={allergiesOptions}
              selectedValues={formData.allergies}
              onSelectionChange={(selectedValues) => handleInputChange('allergies', selectedValues)}
              placeholder="Select allergies..."
              searchPlaceholder="Search allergies..."
              className="mt-1"
            />
          </div>

          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              disabled={isLoading || !formData.pet_name || !formData.pet_type}
              className="flex-1 bg-gradient-to-r from-green-500 to-blue-500 hover:from-green-600 hover:to-blue-600 text-white"
              onClick={handleSubmit}
            >
              {isLoading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              ) : (
                <>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Pet
                </>
              )}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={onCancel}
              disabled={isLoading}
              className="flex-1"
            >
              Cancel
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}; 