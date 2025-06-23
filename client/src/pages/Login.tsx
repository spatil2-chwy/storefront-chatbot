import { useState } from 'react';
import { useLocation } from 'wouter';
import { useAuth } from '@/lib/auth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';

export default function Login() {
  const [, setLocation] = useLocation();
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    const success = await login(email, password);
    if (success) {
      setLocation('/');
    }
    
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <div className="w-16 h-16 bg-chewy-blue rounded-full flex items-center justify-center">
            <div className="text-2xl font-bold text-white font-work-sans">C</div>
          </div>
        </div>
        <h2 className="mt-6 text-center text-2xl font-bold text-gray-900">
          Sign in or create account
        </h2>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <Card className="shadow-xl">
          <CardContent className="py-8 px-10">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <Label htmlFor="email" className="block text-sm font-medium text-gray-700">
                  Email Address
                </Label>
                <div className="mt-1">
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Enter your email"
                    className="w-full"
                  />
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

              <Button
                type="submit"
                disabled={isLoading}
                className="w-full bg-chewy-blue hover:bg-blue-700 text-white py-3 rounded-xl text-sm font-medium"
              >
                {isLoading ? 'Signing in...' : 'Continue'}
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
