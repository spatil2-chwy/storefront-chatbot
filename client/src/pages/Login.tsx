import { useState, useEffect } from 'react';
import { useLocation } from 'wouter';
import { useAuth } from '@/lib/auth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { ChevronDown } from 'lucide-react';

// Demo: 5 users who have pets - these will always be suggested for quick login
const USERS_WITH_PETS = [
  'diane.anderson@gmail.com',
  'jessica.ewing@gmail.com',
  'rebecca.ellis@gmail.com',
  'kathleen.simpson@gmail.com',
  'aaron.simon@gmail.com',
];

export default function Login() {
  const [, setLocation] = useLocation();
  const { login, isAuthenticated, isLoading: authLoading } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [filteredEmails, setFilteredEmails] = useState<string[]>([]);

  // If already authenticated, redirect to the home page
  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      setLocation('/');
    }
  }, [isAuthenticated, authLoading, setLocation]);

  // Filter the demo email suggestions based on input - always show all 5 if there's any input
  useEffect(() => {
    if (email.length > 0) {
      const filtered = USERS_WITH_PETS.filter(emailOption => 
        emailOption.toLowerCase().includes(email.toLowerCase())
      );
      setFilteredEmails(filtered);
      setShowSuggestions(true); // Always show suggestions if there's input
    } else {
      setShowSuggestions(false);
      setFilteredEmails([]);
    }
  }, [email]);

  // Show a loading spinner while checking authentication state
  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-chewy-blue"></div>
      </div>
    );
  }

  // If already authenticated, don't show the login form (redirect will happen via useEffect)
  if (isAuthenticated) {
    return null;
  }

  // When a suggestion is clicked, fill the email input and hide suggestions
  const handleEmailSelect = (selectedEmail: string) => {
    setEmail(selectedEmail);
    setShowSuggestions(false);
  };

  // Handle login form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    const ok = await login(email, password);
    setIsSubmitting(false);

    if (ok) {
      // first click → they existed in the DB, so we just redirect
      setLocation("/");
    } else {
      setError("No account found for that email.");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <img 
            src="/chewy-c-white.png" 
            alt="Chewy" 
            className="h-16 w-16"
          />
        </div>
        <h2 className="mt-6 text-center text-2xl font-bold text-gray-900">
          Sign in or create account
        </h2>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <Card className="shadow-xl">
          <CardContent className="py-8 px-10">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="relative">
                <Label htmlFor="email" className="block text-sm font-medium text-gray-700">
                  Email Address
                </Label>
                <div className="mt-1 relative">
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    onFocus={() => email.length > 0 && setShowSuggestions(true)}
                    onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                    placeholder="Enter your email"
                    className="w-full"
                  />
                  {showSuggestions && (
                    <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-48 overflow-y-auto">
                      {filteredEmails.map((emailOption, index) => (
                        <button
                          key={index}
                          type="button"
                          className="w-full px-4 py-2 text-left hover:bg-gray-100 focus:bg-gray-100 focus:outline-none text-sm"
                          onClick={() => handleEmailSelect(emailOption)}
                        >
                          {emailOption}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              <div>
                <Label htmlFor="password" className="block text-sm font-medium text-gray-700">
                  Password
                </Label>
                <div className="mt-1">
                  <Input
                    id="password"
                    name="password"
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    className="w-full"
                  />
                </div>
              </div>

              {error && (
                <div className="text-red-600 text-sm text-center">
                  {error}
                </div>
              )}

              <Button
                type="submit"
                disabled={isSubmitting}
                className="w-full bg-chewy-blue hover:bg-blue-700 text-white py-3 rounded-xl text-sm font-medium"
              >
                {isSubmitting ? 'Signing in...' : 'Continue'}
              </Button>

              <div className="mt-6">
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <Separator className="w-full" />
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-2 bg-white text-gray-500">or</span>
                  </div>
                </div>

                <div className="mt-6 space-y-3">
                  <Button
                    type="button"
                    variant="outline"
                    className="w-full flex items-center justify-center space-x-2 py-3 rounded-xl"
                  >
                    <span>🔍</span>
                    <span>Continue With Google</span>
                  </Button>
                  
                  <Button
                    type="button"
                    variant="outline"
                    className="w-full flex items-center justify-center space-x-2 py-3 rounded-xl"
                  >
                    <span>🍎</span>
                    <span>Continue With Apple</span>
                  </Button>
                </div>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>

      <div className="mt-8 text-center text-sm text-gray-500">
        Questions? We're here 24 hours a day: 1-800-672-4399
      </div>
    </div>
  );
}
