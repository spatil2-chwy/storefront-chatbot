import { useState, useEffect } from 'react';
import { useLocation } from 'wouter';
import { useAuth } from '@/lib/auth';
import { Button } from '@/ui/Buttons/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/ui/Cards/Card';
import { Badge } from '@/ui/Display/Badge';
import { Separator } from '@/ui/Layout/Separator';
import { Input } from '@/ui/Input/Input';
import { Label } from '@/ui/Input/Label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/ui/Selects/Select';
import { Switch } from '@/ui/Toggles/Switch';
import {
  User,
  Mail,
  MapPin,
  Calendar,
  PawPrint,
  LogOut,
  Heart,
  Weight,
  Gift,
  Edit3,
  Save,
  X,
  ChevronLeft,
  ChevronRight,
  ArrowLeft
} from 'lucide-react';
import { usersApi } from '@/lib/api/users';
import { chatApi } from '@/lib/api/chat';

export default function Profile() {
  const [, setLocation] = useLocation();
  const { user, logout, isAuthenticated, isLoading } = useAuth();
  const [pets, setPets] = useState<any[]>([]);
  const [loadingPets, setLoadingPets] = useState(true);
  const [editingPet, setEditingPet] = useState<number | null>(null);
  const [editFormData, setEditFormData] = useState<any>(null);
  const [savingPet, setSavingPet] = useState<number | null>(null);

  // Redirect if not authenticated
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      setLocation('/login');
    }
  }, [isAuthenticated, isLoading, setLocation]);

  // Fetch user's pets
  useEffect(() => {
    if (user) {
      fetchUserPets();
    }
  }, [user]);

  const fetchUserPets = async () => {
    try {
      if (user?.customer_key) {
        const petsData = await usersApi.getUserPets(user.customer_key);
        setPets(petsData);
      }
    } catch (error) {
      console.error('Error fetching pets:', error);
    } finally {
      setLoadingPets(false);
    }
  };

  const handleLogout = () => {
    logout();
    setLocation('/login');
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Unknown';
    return new Date(dateString).toLocaleDateString();
  };

  const getGenderIcon = (gender: string) => {
    return gender === 'MALE' ? '♂' : gender === 'FMLE' ? '♀' : '?';
  };

  const getLifeStageColor = (lifeStage: string) => {
    switch (lifeStage) {
      case 'P': return 'bg-blue-100 text-blue-800';
      case 'A': return 'bg-green-100 text-green-800';
      case 'S': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getLifeStageText = (lifeStage: string) => {
    switch (lifeStage) {
      case 'P': return 'Puppy/Kitten';
      case 'A': return 'Adult';
      case 'S': return 'Senior';
      default: return 'Unknown';
    }
  };

  // Calendar helper functions for birthday editing
  const [isCalendarOpen, setIsCalendarOpen] = useState(false);
  const [currentDate, setCurrentDate] = useState(new Date());

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
    setEditFormData((prev: any) => ({
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
      const isSelected = editFormData?.birthday && 
        new Date(editFormData.birthday).getDate() === day &&
        new Date(editFormData.birthday).getMonth() === currentDate.getMonth() &&
        new Date(editFormData.birthday).getFullYear() === currentDate.getFullYear();

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

  // Pet editing functions
  const startEditingPet = (pet: any) => {
    setEditingPet(pet.pet_profile_id);
    setEditFormData({
      name: pet.pet_name || '',
      type: pet.pet_type || '',
      breed: pet.pet_breed || '',
      gender: pet.gender || '',
      weight: pet.weight || 0,
      life_stage: pet.life_stage || '',
      birthday: pet.birthday || '',
      allergies: pet.allergy_count > 0
    });
  };

  const cancelEditing = () => {
    setEditingPet(null);
    setEditFormData(null);
    setIsCalendarOpen(false);
  };

  const handleEditFormChange = (field: string, value: any) => {
    setEditFormData((prev: any) => ({
      ...prev,
      [field]: value
    }));
  };

  const savePetChanges = async (petId: number) => {
    if (!editFormData) return;
    
    setSavingPet(petId);
    try {
      // Convert to the format expected by the backend
      const petData = {
        pet_name: editFormData.name,
        pet_type: editFormData.type,
        pet_breed: editFormData.breed,
        gender: editFormData.gender,
        weight: editFormData.weight,
        life_stage: editFormData.life_stage,
        birthday: editFormData.birthday,
        allergy_count: editFormData.allergies ? 1 : 0
      };

      // Update via chat API (which handles the pet profile updates)
      await chatApi.updatePetProfile(petId, petData);
      
      // Refresh pets list
      await fetchUserPets();
      
      // Exit editing mode
      setEditingPet(null);
      setEditFormData(null);
    } catch (error) {
      console.error('Error updating pet:', error);
    } finally {
      setSavingPet(null);
    }
  };

  // Persona parsing helpers
  const parseArray = (val: any) => {
    if (!val) return [];
    if (Array.isArray(val)) return val;
    try {
      return JSON.parse(val);
    } catch {
      return [];
    }
  };

  // Show loading while checking auth state
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-green-50">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-chewy-blue"></div>
      </div>
    );
  }

  // Don't show profile if not authenticated
  if (!isAuthenticated || !user) {
    return null;
  }

  // Persona fields
  const personaSummary = user.persona_summary;
  const preferredBrands = parseArray(user.preferred_brands);
  const specialDiet = parseArray(user.special_diet);
  const possibleNextBuys = user.possible_next_buys;

  return (
    <div className="min-h-screen bg-white py-8" data-main-content>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Back Button */}
        <div className="mb-6">
          <Button
            variant="outline"
            onClick={() => setLocation('/')}
            className="flex items-center gap-2 text-chewy-blue border-chewy-blue hover:bg-chewy-blue hover:text-white transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Main Page
          </Button>
        </div>

        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">My Profile</h1>
          <p className="text-gray-600 text-lg">Manage your account and view your pets</p>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
          {/* User Information Card */}
          <div className="xl:col-span-1">
            <Card className="bg-white border-chewy-blue/20 shadow-lg">
              <CardHeader className="bg-chewy-blue text-white rounded-t-lg">
                <CardTitle className="flex items-center gap-2">
                  <User className="h-5 w-5" />
                  Account Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6 p-6">
                <div className="text-center">
                  <div className="w-20 h-20 bg-chewy-blue rounded-full flex items-center justify-center text-white text-2xl font-bold mx-auto mb-4">
                    {user.name.charAt(0).toUpperCase()}
                  </div>
                  <h3 className="font-semibold text-xl text-gray-900">{user.name}</h3>
                  <p className="text-gray-600 flex items-center justify-center gap-2 mt-2">
                    <Mail className="h-4 w-4" />
                    {user.email}
                  </p>
                </div>

                {/* Persona Summary Section */}
                {personaSummary && (
                  <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-chewy-blue/30 rounded-xl p-6 shadow-sm">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-10 h-10 bg-chewy-blue rounded-full flex items-center justify-center">
                        <Heart className="h-5 w-5 text-white" />
                      </div>
                      <div>
                        <h4 className="font-bold text-chewy-blue text-lg">Persona Insight</h4>
                        <p className="text-gray-500 text-xs">Your shopping behavior analysis</p>
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      <p className="text-gray-700 text-sm leading-relaxed bg-white/60 rounded-lg p-3 border border-chewy-blue/10">
                        {personaSummary}
                      </p>
                      
                      <div className="grid grid-cols-1 gap-3">
                        {preferredBrands.length > 0 && (
                          <div className="bg-white/80 rounded-lg p-3 border border-chewy-blue/10">
                            <div className="flex items-center gap-2 mb-2">
                              <div className="w-2 h-2 bg-chewy-blue rounded-full"></div>
                              <span className="font-semibold text-gray-800 text-sm">Preferred Brands</span>
                            </div>
                                                         <div className="flex flex-wrap gap-1">
                               {preferredBrands.map((brand: string, index: number) => (
                                 <span key={index} className="px-2 py-1 bg-chewy-blue/10 text-chewy-blue text-xs rounded-full font-medium">
                                   {brand}
                                 </span>
                               ))}
                             </div>
                          </div>
                        )}
                        
                        {specialDiet.length > 0 && (
                          <div className="bg-white/80 rounded-lg p-3 border border-chewy-blue/10">
                            <div className="flex items-center gap-2 mb-2">
                              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                              <span className="font-semibold text-gray-800 text-sm">Special Diet</span>
                            </div>
                                                         <div className="flex flex-wrap gap-1">
                               {specialDiet.map((diet: string, index: number) => (
                                 <span key={index} className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full font-medium">
                                   {diet}
                                 </span>
                               ))}
                             </div>
                          </div>
                        )}
                        
                        {possibleNextBuys && (
                          <div className="bg-white/80 rounded-lg p-3 border border-chewy-blue/10">
                            <div className="flex items-center gap-2 mb-2">
                              <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                              <span className="font-semibold text-gray-800 text-sm">Possible Next Buys</span>
                            </div>
                            <p className="text-gray-600 text-xs leading-relaxed">
                              {possibleNextBuys}
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                <Separator className="bg-chewy-blue/20" />

                <div className="space-y-4">
                  <div className="flex items-center gap-3 text-sm bg-gray-50 rounded-lg p-3">
                    <MapPin className="h-4 w-4 text-chewy-blue" />
                    <span className="text-gray-700">
                      {user.customer_address_city}, {user.customer_address_state}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 text-sm bg-gray-50 rounded-lg p-3">
                    <Calendar className="h-4 w-4 text-chewy-blue" />
                    <span className="text-gray-700">
                      Customer since {user.customer_order_first_placed_dttm ?
                        formatDate(user.customer_order_first_placed_dttm) : 'Unknown'}
                    </span>
                  </div>
                </div>

                <Separator className="bg-chewy-blue/20" />

                <Button
                  onClick={handleLogout}
                  variant="outline"
                  className="w-full text-red-600 border-red-200 hover:bg-red-50 hover:border-red-300 transition-colors"
                >
                  <LogOut className="h-4 w-4 mr-2" />
                  Sign Out
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Pets Section */}
          <div className="xl:col-span-2">
            <Card className="bg-white border-chewy-blue/20 shadow-lg">
              <CardHeader className="bg-chewy-blue text-white rounded-t-lg">
                <CardTitle className="flex items-center gap-2">
                  <PawPrint className="h-5 w-5" />
                  My Pets ({pets.length})
                </CardTitle>
              </CardHeader>
              <CardContent className="p-6">
                {loadingPets ? (
                  <div className="flex items-center justify-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-chewy-blue"></div>
                  </div>
                ) : pets.length === 0 ? (
                  <div className="text-center py-12 text-gray-500">
                    <PawPrint className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                    <p className="text-lg">No pets found. Add your first pet to get started!</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {pets.map((pet) => (
                      <Card 
                        key={pet.pet_profile_id} 
                        className={`transition-all duration-300 hover:shadow-lg hover:scale-105 ${
                          editingPet === pet.pet_profile_id ? 'ring-2 ring-chewy-blue shadow-lg' : ''
                        }`}
                      >
                        <CardContent className="p-6">
                          {editingPet === pet.pet_profile_id ? (
                            // Edit Mode
                            <div className="space-y-4">
                                                             <div className="flex items-center justify-between">
                                 <h3 className="font-semibold text-lg text-chewy-blue">Editing {pet.pet_name}</h3>
                                 <div className="flex gap-2">
                                   <Button
                                     size="sm"
                                     onClick={() => savePetChanges(pet.pet_profile_id)}
                                     disabled={savingPet === pet.pet_profile_id}
                                     className="bg-chewy-blue hover:bg-blue-700 text-white"
                                   >
                                    {savingPet === pet.pet_profile_id ? (
                                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                                    ) : (
                                      <Save className="h-4 w-4" />
                                    )}
                                  </Button>
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    onClick={cancelEditing}
                                    disabled={savingPet === pet.pet_profile_id}
                                  >
                                    <X className="h-4 w-4" />
                                  </Button>
                                </div>
                              </div>

                              <div className="grid grid-cols-2 gap-4">
                                <div>
                                  <Label className="text-sm font-medium">Name</Label>
                                  <Input
                                    value={editFormData?.name || ''}
                                    onChange={(e) => handleEditFormChange('name', e.target.value)}
                                    className="mt-1"
                                  />
                                </div>
                                <div>
                                  <Label className="text-sm font-medium">Type</Label>
                                  <Select
                                    value={editFormData?.type || ''}
                                    onValueChange={(value) => handleEditFormChange('type', value)}
                                  >
                                    <SelectTrigger className="mt-1">
                                      <SelectValue />
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
                                <div>
                                  <Label className="text-sm font-medium">Breed</Label>
                                  <Input
                                    value={editFormData?.breed || ''}
                                    onChange={(e) => handleEditFormChange('breed', e.target.value)}
                                    className="mt-1"
                                  />
                                </div>
                                <div>
                                  <Label className="text-sm font-medium">Gender</Label>
                                  <Select
                                    value={editFormData?.gender || ''}
                                    onValueChange={(value) => handleEditFormChange('gender', value)}
                                  >
                                    <SelectTrigger className="mt-1">
                                      <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                      <SelectItem value="MALE">Male</SelectItem>
                                      <SelectItem value="FMLE">Female</SelectItem>
                                    </SelectContent>
                                  </Select>
                                </div>
                                <div>
                                  <Label className="text-sm font-medium">Weight (lbs)</Label>
                                  <Input
                                    type="number"
                                    value={editFormData?.weight || ''}
                                    onChange={(e) => handleEditFormChange('weight', parseFloat(e.target.value) || 0)}
                                    className="mt-1"
                                  />
                                </div>
                                <div>
                                  <Label className="text-sm font-medium">Life Stage</Label>
                                  <Select
                                    value={editFormData?.life_stage || ''}
                                    onValueChange={(value) => handleEditFormChange('life_stage', value)}
                                  >
                                    <SelectTrigger className="mt-1">
                                      <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                      <SelectItem value="P">Puppy/Kitten</SelectItem>
                                      <SelectItem value="A">Adult</SelectItem>
                                      <SelectItem value="S">Senior</SelectItem>
                                    </SelectContent>
                                  </Select>
                                </div>
                              </div>

                              <div>
                                <Label className="text-sm font-medium">Birthday</Label>
                                <div className="relative mt-1">
                                                                     <button
                                     type="button"
                                     onClick={() => setIsCalendarOpen(!isCalendarOpen)}
                                     className="w-full text-sm border border-chewy-blue/20 focus:border-chewy-blue focus:ring-chewy-blue bg-white hover:bg-gray-50 transition-colors pr-8 py-2 px-3 rounded-md text-left flex items-center justify-between"
                                   >
                                     <span className={editFormData?.birthday ? 'text-gray-900' : 'text-gray-500'}>
                                       {editFormData?.birthday ? formatDateForDisplay(editFormData.birthday) : 'Select birthday'}
                                     </span>
                                     <Calendar className="h-4 w-4 text-chewy-blue" />
                                   </button>
                                   
                                   {isCalendarOpen && (
                                     <div className="absolute top-full left-0 mt-1 bg-white border border-chewy-blue/20 rounded-lg shadow-lg z-50 p-4 min-w-64">
                                       <div className="flex items-center justify-between mb-4">
                                         <button
                                           onClick={() => navigateMonth('prev')}
                                           className="p-1 hover:bg-gray-100 rounded-full transition-colors"
                                         >
                                           <ChevronLeft className="h-4 w-4 text-chewy-blue" />
                                         </button>
                                         <h3 className="text-sm font-semibold text-gray-900">
                                           {currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                                         </h3>
                                         <button
                                           onClick={() => navigateMonth('next')}
                                           className="p-1 hover:bg-gray-100 rounded-full transition-colors"
                                         >
                                           <ChevronRight className="h-4 w-4 text-chewy-blue" />
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
                                <div className="flex items-center space-x-2 mt-1">
                                  <Switch
                                    checked={editFormData?.allergies || false}
                                    onCheckedChange={(checked) => handleEditFormChange('allergies', checked)}
                                  />
                                  <span className="text-sm text-gray-600">
                                    {editFormData?.allergies ? 'Has allergies' : 'No allergies'}
                                  </span>
                                </div>
                              </div>
                            </div>
                          ) : (
                            // View Mode
                            <div className="space-y-4">
                              <div className="flex items-start justify-between">
                                <div>
                                  <h3 className="font-semibold text-xl flex items-center gap-2 text-gray-900">
                                    {pet.pet_name}
                                    <span className="text-lg">{getGenderIcon(pet.gender)}</span>
                                  </h3>
                                  <p className="text-gray-600 text-sm mt-1">
                                    {pet.pet_breed} • {pet.pet_type}
                                  </p>
                                </div>
                                <div className="flex items-center gap-2">
                                  <Badge className={getLifeStageColor(pet.life_stage)}>
                                    {getLifeStageText(pet.life_stage)}
                                  </Badge>
                                                                     <Button
                                     size="sm"
                                     variant="outline"
                                     onClick={() => startEditingPet(pet)}
                                     className="text-chewy-blue border-chewy-blue/20 hover:bg-chewy-blue/10"
                                   >
                                    <Edit3 className="h-4 w-4" />
                                  </Button>
                                </div>
                              </div>

                                                                                                <div className="grid grid-cols-1 gap-3 text-sm">
                                   <div className="flex items-center gap-2 text-gray-600 bg-blue-50 rounded-lg p-2">
                                     <Weight className="h-4 w-4 text-chewy-blue" />
                                     <span className="font-medium">Weight:</span>
                                     <span>{pet.weight ? `${pet.weight} lbs` : 'Unknown'}</span>
                                   </div>

                                   {pet.birthday && (
                                     <div className="flex items-center gap-2 text-gray-600 bg-blue-50 rounded-lg p-2">
                                       <Gift className="h-4 w-4 text-chewy-blue" />
                                       <span className="font-medium">Born:</span>
                                       <span>{formatDate(pet.birthday)}</span>
                                     </div>
                                   )}

                                   <div className="flex items-center gap-2 text-gray-600 bg-blue-50 rounded-lg p-2">
                                     <Heart className="h-4 w-4 text-chewy-blue" />
                                     <span className="font-medium">Allergies:</span>
                                     <span>{pet.allergy_count > 0 ? `${pet.allergy_count} allergies` : 'None'}</span>
                                   </div>

                                   {pet.adopted && (
                                     <div className="flex items-center gap-2 bg-green-50 rounded-lg p-2">
                                       <Badge variant="secondary" className="bg-green-100 text-green-800">
                                         Adopted
                                       </Badge>
                                       {pet.adoption_date && (
                                         <span className="text-xs text-gray-600">
                                           {formatDate(pet.adoption_date)}
                                         </span>
                                       )}
                                     </div>
                                   )}

                                 </div>
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
} 