// Main application component
// Sets up routing, authentication, and global providers

import { Switch, Route, Redirect } from "wouter";
import { Toaster } from "@/ui/Feedback/Toaster";
import { TooltipProvider } from "@/ui/Tooltips/Tooltip";
import { AuthProvider, useAuth } from "@/lib/auth";
import { GlobalChatProvider } from "@/features/chat/context";
import { CartProvider } from "@/features/cart/context";
import { ToastProvider } from "@/components/ui/toast";
import Login from "@/pages/Login";
import ProductListing from "@/pages/ProductListing";
import ProductDetail from "@/pages/ProductDetail";
import ProductComparison from "@/pages/ProductComparison";
import Checkout from "@/pages/Checkout";
import Profile from "@/pages/Profile";
import NotFound from "@/pages/not-found";
import TestBirthdayPopup from "@/pages/TestBirthdayPopup";
import { BreedSelectTest } from "@/components/BreedSelectTest";

// Route wrapper that checks authentication
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  
  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-chewy-blue"></div>
      </div>
    );
  }
  
  if (!isAuthenticated) {
    return <Redirect to="/login" />;
  }
  
  return <>{children}</>;
}

// Main routing component
function Router() {
  return (
    <Switch>
      <Route path="/login" component={Login} />
      <Route path="/">
        <ProtectedRoute>
          <ProductListing />
        </ProtectedRoute>
      </Route>
      <Route path="/product/:id">
        <ProtectedRoute>
          <ProductDetail />
        </ProtectedRoute>
      </Route>
      <Route path="/compare">
        <ProtectedRoute>
          <ProductComparison />
        </ProtectedRoute>
      </Route>
      <Route path="/checkout">
        <ProtectedRoute>
          <Checkout />
        </ProtectedRoute>
      </Route>
      <Route path="/profile">
        <ProtectedRoute>
          <Profile />
        </ProtectedRoute>
      </Route>
      <Route path="/birthday-test">
        <ProtectedRoute>
          <TestBirthdayPopup />
        </ProtectedRoute>
      </Route>
      <Route path="/breed-test">
        <ProtectedRoute>
          <BreedSelectTest />
        </ProtectedRoute>
      </Route>
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <TooltipProvider>
      <AuthProvider>
        <CartProvider>
          <GlobalChatProvider>
            <ToastProvider>
              <Toaster />
              <Router />
            </ToastProvider>
          </GlobalChatProvider>
        </CartProvider>
      </AuthProvider>
    </TooltipProvider>
  );
}

export default App;
