import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Home, ChatPage, NotFound } from "./pages/Pages";
import AuthProvider from "./providers/AuthProvider";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import SettingsPage from "./pages/SettingsPage";
import { useAuth } from "./hooks";
import PropTypes from "prop-types";

// Creating a query client
const queryClient = new QueryClient();

// Protected route component 
// redirects to login if not authenticated
function ProtectedRoute({ children }) {
  const { loggedIn } = useAuth();
  
  if (!loggedIn) {
    return <Navigate to="/login" />;
  }
  
  return children;
}

// HomePage component 
// Redirects to chats if logged in
function HomePage() {
  const { loggedIn } = useAuth();
  
  if (loggedIn) {
    return <Navigate to="/chats" />;
  }
  
  return <Navigate to="/login" />;
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Home route redirects based on auth state */}
            <Route path="/" element={<HomePage />} />
            
            {/* Auth routes */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            
            {/* Protected routes */}
            <Route 
              path="/chats" 
              element={
                <ProtectedRoute>
                  <Home />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/chats/:chatId" 
              element={
                <ProtectedRoute>
                  <ChatPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/settings" 
              element={
                <ProtectedRoute>
                  <SettingsPage />
                </ProtectedRoute>
              } 
            />
            
            {/* 404 route */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}

ProtectedRoute.propTypes = {
  children: PropTypes.node.isRequired
};

export default App;