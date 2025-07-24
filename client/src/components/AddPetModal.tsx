import React, { useState } from 'react';
import { Button } from '@/ui/Buttons/Button';
import { Input } from '@/ui/Input/Input';
import { Label } from '@/ui/Input/Label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/ui/Selects/Select';
import { MultiSelect, MultiSelectOption } from '@/ui/Selects/MultiSelect';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/ui/Overlay/Modal';
import { Calendar, ChevronLeft, ChevronRight, Plus, X } from 'lucide-react';
import { usersApi } from '@/lib/api/users';
import { useAuth } from '@/lib/auth';
import { BreedSelect } from './BreedSelect';
import { LifeStageDisplay } from './LifeStageDisplay';

interface AddPetModalProps {
  isOpen: boolean;
  onClose: () => void;
  onPetAdded: () => void;
}

export const AddPetModal: React.FC<AddPetModalProps> = ({
  isOpen,
  onClose,
  onPetAdded
}) => {
  const { user } = useAuth();
  console.log('AddPetModal: user data:', user);
  console.log('AddPetModal: user?.customer_key:', user?.customer_key);
  
  const [isLoading, setIsLoading] = useState(false);
  const [isCalendarOpen, setIsCalendarOpen] = useState(false);
  const [currentDate, setCurrentDate] = useState(new Date());
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
              ? 'bg-chewy-blue text-white'
              : 'hover:bg-gray-100 text-gray-700'
          }`}
        >
          {day}
        </button>
      );
    }

    return days;
  };

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) {
      e.preventDefault();
    }
    
    console.log('AddPetModal: handleSubmit called');
    console.log('AddPetModal: user?.customer_key:', user?.customer_key);
    console.log('AddPetModal: formData:', formData);
    
    if (!user?.customer_key || !formData.pet_name || !formData.pet_type) {
      console.log('AddPetModal: Validation failed - missing required fields');
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
        birthday: formData.birthday,
        allergies: formatAllergies(formData.allergies)
      };

      console.log('AddPetModal: Calling usersApi.createPet with:', petData);
      await usersApi.createPet(user.customer_key, petData);
      
      console.log('AddPetModal: Pet created successfully');
      
      // Reset form
      setFormData({
        pet_name: '',
        pet_type: '',
        pet_breed: '',
        gender: '',
        weight: 0,
        life_stage: '',
        birthday: '',
        allergies: []
      });
      
      console.log('AddPetModal: Calling onPetAdded');
      onPetAdded();
      console.log('AddPetModal: Calling onClose');
      onClose();
    } catch (error) {
      console.error('AddPetModal: Error creating pet:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    // Reset form when closing
    setFormData({
      pet_name: '',
      pet_type: '',
      pet_breed: '',
      gender: '',
      weight: 0,
      life_stage: '',
      birthday: '',
      allergies: []
    });
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-md max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Add New Pet</DialogTitle>
        </DialogHeader>

        <div className="p-6 space-y-4">
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
                  <SelectItem value="BIRD">Bird</SelectItem>
                  <SelectItem value="FISH">Fish</SelectItem>
                  <SelectItem value="RABBIT">Rabbit</SelectItem>
                  <SelectItem value="HAMSTER">Hamster</SelectItem>
                  <SelectItem value="OTHER">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <BreedSelect
                  species={formData.pet_type}
                  value={formData.pet_breed}
                  onChange={(value) => handleInputChange('pet_breed', value)}
                  label="Breed"
                  placeholder="Select breed (optional)"
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
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="weight" className="text-sm font-medium">
                  Weight (lbs)
                </Label>
                <Input
                  id="weight"
                  type="number"
                  value={formData.weight}
                  onChange={(e) => handleInputChange('weight', parseFloat(e.target.value) || 0)}
                  placeholder="0"
                  className="mt-1"
                />
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
            </div>

            <div>
              <Label className="text-sm font-medium">Birthday</Label>
              <div className="relative mt-1">
                <button
                  type="button"
                  onClick={() => setIsCalendarOpen(!isCalendarOpen)}
                  className="w-full text-sm border border-gray-300 focus:border-chewy-blue focus:ring-chewy-blue bg-white hover:bg-gray-50 transition-colors pr-8 py-2 px-3 rounded-md text-left flex items-center justify-between"
                >
                  <span className={formData.birthday ? 'text-gray-900' : 'text-gray-500'}>
                    {formData.birthday ? formatDateForDisplay(formData.birthday) : 'Select birthday'}
                  </span>
                  <Calendar className="h-4 w-4 text-gray-400" />
                </button>
                
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
                className="flex-1 bg-chewy-blue hover:bg-blue-700 text-white"
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
                onClick={handleClose}
                disabled={isLoading}
                className="flex-1"
              >
                Cancel
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    );
  }; 