import { useState, useEffect } from 'react';
import { useLocation } from 'wouter';
import { useAuth } from '@/lib/auth';
import { Button } from '@/components/Buttons/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/Cards/Card';
import { Badge } from '@/components/Display/Badge';
import { Separator } from '@/components/Layout/separator';
import { 
  User, 
  Mail, 
  MapPin, 
  Calendar, 
  PawPrint, 
  LogOut,
  Heart,
  Weight,
  Gift
} from 'lucide-react';

interface Pet {
  pet_profile_id: number;
  pet_name: string;
  pet_type: string;
  pet_breed: string;
  gender: string;
  birthday: string;
  life_stage: string;
  adopted: boolean;
  adoption_date: string | null;
  weight: number;
  allergy_count: number;
  status: string;
}

export default function Profile() {
  const [, setLocation] = useLocation();
  const { user, logout, isAuthenticated, isLoading } = useAuth();
  const [pets, setPets] = useState<Pet[]>([]);
  const [loadingPets, setLoadingPets] = useState(true);

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
      const response = await fetch(`http://localhost:8000/customers/${user?.customer_key}/pets`);
      if (response.ok) {
        const petsData = await response.json();
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

  // Show loading while checking auth state
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-chewy-blue"></div>
      </div>
    );
  }

  // Don't show profile if not authenticated
  if (!isAuthenticated || !user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">My Profile</h1>
          <p className="text-gray-600 mt-2">Manage your account and view your pets</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* User Information Card */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="h-5 w-5" />
                  Account Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h3 className="font-semibold text-lg">{user.name}</h3>
                  <p className="text-gray-600 flex items-center gap-2 mt-1">
                    <Mail className="h-4 w-4" />
                    {user.email}
                  </p>
                </div>

                <Separator />

                <div className="space-y-3">
                  <div className="flex items-center gap-2 text-sm">
                    <MapPin className="h-4 w-4 text-gray-500" />
                    <span className="text-gray-600">
                      {user.customer_address_city}, {user.customer_address_state}
                    </span>
                  </div>
                  
                  <div className="flex items-center gap-2 text-sm">
                    <Calendar className="h-4 w-4 text-gray-500" />
                    <span className="text-gray-600">
                      Customer since {user.customer_order_first_placed_dttm ? 
                        formatDate(user.customer_order_first_placed_dttm) : 'Unknown'}
                    </span>
                  </div>
                </div>

                <Separator />

                <Button 
                  onClick={handleLogout}
                  variant="outline" 
                  className="w-full text-red-600 border-red-200 hover:bg-red-50"
                >
                  <LogOut className="h-4 w-4 mr-2" />
                  Sign Out
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Pets Section */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PawPrint className="h-5 w-5" />
                  My Pets ({pets.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                {loadingPets ? (
                  <div className="flex items-center justify-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-chewy-blue"></div>
                  </div>
                ) : pets.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <PawPrint className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                    <p>No pets found. Add your first pet to get started!</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {pets.map((pet) => (
                      <Card key={pet.pet_profile_id} className="hover:shadow-md transition-shadow">
                        <CardContent className="p-4">
                          <div className="flex items-start justify-between mb-3">
                            <div>
                              <h3 className="font-semibold text-lg flex items-center gap-2">
                                {pet.pet_name}
                                <span className="text-lg">{getGenderIcon(pet.gender)}</span>
                              </h3>
                              <p className="text-gray-600 text-sm">
                                {pet.pet_breed} • {pet.pet_type}
                              </p>
                            </div>
                            <Badge className={getLifeStageColor(pet.life_stage)}>
                              {getLifeStageText(pet.life_stage)}
                            </Badge>
                          </div>

                          <div className="space-y-2 text-sm">
                            {pet.birthday && (
                              <div className="flex items-center gap-2 text-gray-600">
                                <Gift className="h-4 w-4" />
                                <span>Born: {formatDate(pet.birthday)}</span>
                              </div>
                            )}
                            
                            {pet.weight && (
                              <div className="flex items-center gap-2 text-gray-600">
                                <Weight className="h-4 w-4" />
                                <span>{pet.weight} lbs</span>
                              </div>
                            )}

                            <div className="flex items-center gap-2 text-gray-600">
                              <Heart className="h-4 w-4" />
                              <span>{pet.allergy_count} allergies</span>
                            </div>

                            {pet.adopted && (
                              <div className="flex items-center gap-2">
                                <Badge variant="secondary" className="bg-green-100 text-green-800">
                                  Adopted
                                </Badge>
                                {pet.adoption_date && (
                                  <span className="text-xs text-gray-500">
                                    {formatDate(pet.adoption_date)}
                                  </span>
                                )}
                              </div>
                            )}
                          </div>
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