import { useState, useEffect, useCallback } from 'react';
import { useLocation } from 'wouter';
import { useAuth } from '@/lib/auth';
import { useGlobalChat } from '@/features/chat/context';
import { Button } from '@/ui/Buttons/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/ui/Cards/Card';
import { Badge } from '@/ui/Display/Badge';
import { Separator } from '@/ui/Layout/Separator';
import { Input } from '@/ui/Input/Input';
import { Label } from '@/ui/Input/Label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/ui/Selects/Select';
import { MultiSelect, MultiSelectOption } from '@/ui/Selects/MultiSelect';
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
  ArrowLeft,
  ShoppingBag,
  Package,
  Plus,
  Trash2
} from 'lucide-react';
import { usersApi } from '@/lib/api/users';
import { chatApi } from '@/lib/api/chat';
import { ordersApi, OrderSummary } from '@/lib/api/orders';
import { AddPetModal } from '@/components/AddPetModal';
import { BreedSelect } from '@/components/BreedSelect';
import { LifeStageDisplay } from '@/components/LifeStageDisplay';

export default function Profile() {
  const [, setLocation] = useLocation();
  const { user, logout, isAuthenticated, isLoading } = useAuth();
  const { setGreetingNeedsRefresh } = useGlobalChat();
  const [pets, setPets] = useState<any[]>([]);
  const [loadingPets, setLoadingPets] = useState(true);
  const [editingPet, setEditingPet] = useState<number | null>(null);
  const [editFormData, setEditFormData] = useState<any>(null);
  const [savingPet, setSavingPet] = useState<number | null>(null);
  const [orders, setOrders] = useState<OrderSummary[]>([]);
  const [loadingOrders, setLoadingOrders] = useState(true);
  const [isAddPetModalOpen, setIsAddPetModalOpen] = useState(false);
  const [deletingPet, setDeletingPet] = useState<number | null>(null);

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

  // Helper function to parse allergies string to array
  const parseAllergies = (allergies: string): string[] => {
    if (!allergies || allergies.trim() === '') return [];
    return allergies.split(',').map(allergy => allergy.trim()).filter(allergy => allergy !== '');
  };

  // Helper function to format allergies array to string
  const formatAllergies = (allergies: string[]): string => {
    return allergies.join(', ');
  };

  // Redirect if not authenticated
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      setLocation('/login');
    }
  }, [isAuthenticated, isLoading, setLocation]);

  // Fetch user's pets and orders
  useEffect(() => {
    if (user) {
      fetchUserPets();
      fetchUserOrders();
    }
  }, [user]);

  const fetchUserPets = useCallback(async () => {
    if (!user?.customer_key) return;
    
    setLoadingPets(true);
    try {
      const pets = await usersApi.getUserPets(user.customer_key);
      setPets(pets);
    } catch (error) {
      console.error('Error fetching user pets:', error);
    } finally {
      setLoadingPets(false);
    }
  }, [user?.customer_key]);

  const fetchUserOrders = async () => {
    try {
      if (user?.customer_id) {
        const ordersData = await ordersApi.getCustomerOrders(user.customer_id);
        setOrders(ordersData);
      }
    } catch (error) {
      console.error('Error fetching orders:', error);
    } finally {
      setLoadingOrders(false);
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
  const [manualDateInput, setManualDateInput] = useState('');
  const [errors, setErrors] = useState<{
    weight?: string;
    birthday?: string;
  }>({});

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
    setManualDateInput(formatDateForDisplay(selectedDate.toISOString()));
    setIsCalendarOpen(false);
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
          setEditFormData((prev: any) => ({
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
      type: pet.pet_type?.toUpperCase() || '',
      breed: pet.pet_breed || '',
      gender: pet.gender || '',
      weight: pet.weight || 0,
      life_stage: pet.life_stage || '',
      birthday: pet.birthday || '',
      allergies: parseAllergies(pet.allergies || '')
    });
    setManualDateInput(pet.birthday ? formatDateForDisplay(pet.birthday) : '');
  };

  const cancelEditing = () => {
    setEditingPet(null);
    setEditFormData(null);
    setIsCalendarOpen(false);
    setManualDateInput('');
  };

  const handleEditFormChange = (field: string, value: any) => {
    setEditFormData((prev: any) => ({
      ...prev,
      [field]: field === 'allergies' ? value : value
    }));
    
    // Clear errors when user starts typing
    if (errors[field as keyof typeof errors]) {
      setErrors(prev => ({
        ...prev,
        [field]: undefined
      }));
    }
  };

  const savePetChanges = async (petId: number) => {
    if (!editFormData) return;
    
    // Validate form data
    const weightError = validateWeight(editFormData.weight);
    const birthdayError = validateBirthday(editFormData.birthday);
    
    if (weightError || birthdayError) {
      setErrors({
        weight: weightError,
        birthday: birthdayError
      });
      return;
    }
    
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
        allergies: Array.isArray(editFormData.allergies) ? formatAllergies(editFormData.allergies) : editFormData.allergies
      };

      // Update via chat API (which handles the pet profile updates)
      await chatApi.updatePetProfile(petId, petData);
      
      // Refresh pets list
      await fetchUserPets();
      
      // Refresh greeting in chat
      setGreetingNeedsRefresh(true);
      
      // Exit editing mode
      setEditingPet(null);
      setEditFormData(null);
      setErrors({});
    } catch (error) {
      console.error('Error updating pet:', error);
    } finally {
      setSavingPet(null);
    }
  };

  const deletePet = async (petId: number) => {
    if (!confirm('Are you sure you want to delete this pet? This action cannot be undone.')) {
      return;
    }
    
    setDeletingPet(petId);
    try {
      await usersApi.deletePet(petId);
      await fetchUserPets();
      // Refresh greeting in chat
      console.log('Profile: Setting greetingNeedsRefresh to true after pet deletion');
      setGreetingNeedsRefresh(true);
    } catch (error) {
      console.error('Error deleting pet:', error);
    } finally {
      setDeletingPet(null);
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

            {/* Order History Section */}
            <Card className="mt-6">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ShoppingBag className="h-5 w-5" />
                  Recent Orders ({orders.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                {loadingOrders ? (
                  <div className="flex items-center justify-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-chewy-blue"></div>
                  </div>
                ) : orders.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <Package className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                    <p>No orders yet. Start shopping to see your order history!</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {orders.slice(0, 5).map((order) => (
                      <Card key={order.order_id} className="border border-gray-200">
                        <CardContent className="p-4">
                          <div className="flex items-center justify-between">
                            <div>
                              <div className="flex items-center gap-2 mb-1">
                                <span className="font-semibold text-gray-900">Order #{order.order_id}</span>
                                <Badge 
                                  variant={order.status === 'delivered' ? 'default' : 'secondary'}
                                  className={
                                    order.status === 'delivered' 
                                      ? 'bg-green-100 text-green-800' 
                                      : order.status === 'shipped'
                                      ? 'bg-blue-100 text-blue-800'
                                      : 'bg-gray-100 text-gray-800'
                                  }
                                >
                                  {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                                </Badge>
                              </div>
                              <div className="text-sm text-gray-600">
                                <span>{new Date(order.order_date).toLocaleDateString()} • </span>
                                <span>{order.items_count} item{order.items_count !== 1 ? 's' : ''}</span>
                              </div>
                            </div>
                            <div className="text-right">
                              <div className="font-semibold text-gray-900">
                                ${order.total_amount.toFixed(2)}
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                    {orders.length > 5 && (
                      <div className="text-center pt-4">
                        <Button variant="outline" size="sm">
                          View All Orders ({orders.length})
                        </Button>
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Pets Section */}
          <div className="xl:col-span-2">
            <Card className="bg-white border-chewy-blue/20 shadow-lg">
              <CardHeader className="bg-chewy-blue text-white rounded-t-lg">
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <PawPrint className="h-5 w-5" />
                    My Pets ({pets.length})
                  </CardTitle>
                  <Button
                    onClick={() => setIsAddPetModalOpen(true)}
                    size="sm"
                    className="bg-white text-chewy-blue hover:bg-gray-100 border-white"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Add Pet
                  </Button>
                </div>
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

                              <div className="space-y-4">
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
                                    species={editFormData?.type || ''}
                                    value={editFormData?.breed || ''}
                                    onChange={(value) => handleEditFormChange('breed', value)}
                                    label="Breed"
                                    placeholder={editFormData?.type ? "Select breed..." : "Select pet type first"}
                                    disabled={savingPet === pet.pet_profile_id}
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
                                    step="0.1"
                                    min="0"
                                    max="1000"
                                    value={editFormData?.weight || ''}
                                    onChange={(e) => {
                                      const value = e.target.value;
                                      if (value === '') {
                                        handleEditFormChange('weight', 0);
                                      } else {
                                        const numValue = parseFloat(value);
                                        if (!isNaN(numValue)) {
                                          handleEditFormChange('weight', numValue);
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
                                        className="px-3 py-2 border border-chewy-blue/20 focus:border-chewy-blue focus:ring-chewy-blue bg-white hover:bg-gray-50 transition-colors rounded-md"
                                      >
                                        <Calendar className="h-4 w-4 text-chewy-blue" />
                                      </button>
                                    </div>
                                     
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
                                    {errors.birthday && (
                                      <p className="text-red-500 text-xs mt-1">{errors.birthday}</p>
                                    )}
                                  </div>
                                </div>
                                
                                <div>
                                  <Label className="text-sm font-medium">Life Stage</Label>
                                  <div className="mt-1">
                                    <LifeStageDisplay
                                      petType={editFormData?.type || ''}
                                      birthday={editFormData?.birthday || null}
                                      legacyStage={editFormData?.life_stage}
                                      showAge={true}
                                    />
                                  </div>
                                </div>
                                
                                <div>
                                  <Label className="text-sm font-medium">Allergies</Label>
                                  <MultiSelect
                                    options={allergiesOptions}
                                    selectedValues={Array.isArray(editFormData?.allergies) ? editFormData.allergies : parseAllergies(editFormData?.allergies || '')}
                                    onSelectionChange={(selectedValues) => handleEditFormChange('allergies', selectedValues)}
                                    placeholder="Select allergies..."
                                    searchPlaceholder="Search allergies..."
                                    className="mt-1"
                                  />
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
                                    {pet.pet_breed && pet.pet_breed.toLowerCase() !== 'unknown'
                                      ? `${pet.pet_breed} • ${pet.pet_type}`
                                      : `Unknown • ${pet.pet_type}`}
                                  </p>
                                </div>
                                <div className="flex items-center gap-2">
                                  <LifeStageDisplay
                                    petType={pet.pet_type}
                                    birthday={pet.birthday}
                                    legacyStage={pet.life_stage}
                                    showAge={false}
                                  />
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    onClick={() => startEditingPet(pet)}
                                    className="text-chewy-blue border-chewy-blue/20 hover:bg-chewy-blue/10"
                                  >
                                    <Edit3 className="h-4 w-4" />
                                  </Button>
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    onClick={() => deletePet(pet.pet_profile_id)}
                                    disabled={deletingPet === pet.pet_profile_id}
                                    className="text-red-600 border-red-200 hover:bg-red-50 hover:border-red-300"
                                  >
                                    {deletingPet === pet.pet_profile_id ? (
                                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-red-600"></div>
                                    ) : (
                                      <Trash2 className="h-4 w-4" />
                                    )}
                                  </Button>
                                </div>
                              </div>

                                                                                                <div className="grid grid-cols-1 gap-3 text-sm">

                                   <div className="flex items-center gap-2 text-gray-600 bg-blue-50 rounded-lg p-2">
                                     <Weight className="h-4 w-4 text-chewy-blue" />
                                     <span className="font-medium">Weight:</span>
                                     <span>{pet.weight && pet.weight > 0 ? `${pet.weight} lbs` : 'Unknown'}</span>
                                   </div>

                                   <div className="flex items-center gap-2 text-gray-600 bg-blue-50 rounded-lg p-2">
                                     <Gift className="h-4 w-4 text-chewy-blue" />
                                     <span className="font-medium">Born:</span>
                                     <span>{pet.birthday ? new Date(pet.birthday).toLocaleDateString('en-US', { month: '2-digit', day: '2-digit', year: 'numeric' }) : 'Unknown'}</span>
                                   </div>

                                   <div className="flex items-center gap-2 text-gray-600 bg-blue-50 rounded-lg p-2">
                                     <Heart className="h-4 w-4 text-chewy-blue" />
                                     <span className="font-medium">Allergies:</span>
                                     <span>{pet.allergies && pet.allergies.trim() ? pet.allergies : 'None'}</span>
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

      {/* Add Pet Modal */}
      <AddPetModal
        isOpen={isAddPetModalOpen}
        onClose={() => setIsAddPetModalOpen(false)}
        onPetAdded={() => {
          fetchUserPets();
          setGreetingNeedsRefresh(true);
        }}
      />
    </div>
  );
} 