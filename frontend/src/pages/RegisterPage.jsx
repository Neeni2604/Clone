import { Navigate } from "react-router-dom";
import { useAuth } from "../hooks";
import RegisterForm from "../components/RegisterForm";

export default function RegisterPage() {
  const { loggedIn } = useAuth();
  
  // If we already logged in, navigate to chats
  if (loggedIn) {
    return <Navigate to="/chats" />;
  }
  
  return (
    <div className="min-h-full flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gray-50">
      <RegisterForm />
    </div>
  );
}