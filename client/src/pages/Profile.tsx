import { useState, useEffect } from 'react';
import { useLocation } from 'wouter';
import { useAuth } from '@/lib/auth';
import { Button } from '@/ui/Buttons/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/ui/Cards/Card';
import { Badge } from '@/ui/Display/Badge';
import { Separator } from '@/ui/Layout/Separator';
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
  ShoppingBag,
  Package
} from 'lucide-react';
import { usersApi } from '@/lib/api/users';
import { ordersApi, OrderSummary } from '@/lib/api/orders';

export default function Profile() {
  const [, setLocation] = useLocation();
  const { user, logout, isAuthenticated, isLoading } = useAuth();
  const [pets, setPets] = useState<any[]>([]); // Changed type to any[] as Pet is not exported
  const [orders, setOrders] = useState<OrderSummary[]>([]);
  const [loadingPets, setLoadingPets] = useState(true);
  const [loadingOrders, setLoadingOrders] = useState(true);

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
      <div className="min-h-screen flex items-center justify-center">
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
    <div className="min-h-screen bg-gray-50 py-8" data-main-content>
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">My Profile</h1>
          <p className="text-gray-600 mt-2">Manage your account and view your pets</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* User Information Card */}
          <div className="lg:col-span-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="h-5 w-7" />
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

                {/* Persona Summary Section */}
                {personaSummary && (
                  <div className="bg-chewy-blue/5 border border-chewy-blue/10 rounded-lg p-2 mt-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Heart className="h-4 w-4 text-chewy-blue" />
                      <span className="font-semibold text-chewy-blue">Persona Insight</span>
                    </div>
                    <p className="text-gray-700 text-sm leading-relaxed">{personaSummary}</p>
                    {preferredBrands.length > 0 && (
                      <div className="mt-2 text-xs text-gray-500">
                        <span className="font-semibold">Preferred Brands:</span> {preferredBrands.join(', ')}
                      </div>
                    )}
                    {specialDiet.length > 0 && (
                      <div className="mt-1 text-xs text-gray-500">
                        <span className="font-semibold">Special Diet:</span> {specialDiet.join(', ')}
                      </div>
                    )}
                    {possibleNextBuys && (
                      <div className="mt-1 text-xs text-gray-500">
                        <span className="font-semibold">Possible Next Buys:</span> {possibleNextBuys}
                      </div>
                    )}
                  </div>
                )}

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