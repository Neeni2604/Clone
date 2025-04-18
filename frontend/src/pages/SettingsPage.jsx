import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { useAuth, useAccount } from "../hooks";
import ChatNavigation from "../components/ChatNavigation";
import LabelInput from "../components/LabelInput";

export default function SettingsPage() {
  const navigate = useNavigate();
  const { headers, logout } = useAuth();
  const account = useAccount();

  const queryClient = useQueryClient();
  
  // This is teh state for the account update form
  const [username, setUsername] = useState(account.username || "");
  const [email, setEmail] = useState(account.email || "");
  const [accountUpdateError, setAccountUpdateError] = useState(null);
  
  // State for the password update form
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmNewPassword, setConfirmNewPassword] = useState("");
  const [passwordUpdateError, setPasswordUpdateError] = useState(null);
  
  // Checking if passwords match
  const passwordsMatch = newPassword === confirmNewPassword;
  const passwordsError = !passwordsMatch && confirmNewPassword.length > 0 
    ? "Passwords do not match" 
    : null;
  
  // Mutations
  const accountUpdateMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch("http://localhost:8000/accounts/me", {
        method: "PUT",
        headers: {
          ...headers,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          username,
          email
        })
      });
      
      if (response.ok) {
        return await response.json();
      } else {
        const error = await response.json();
        throw new Error(error.message);
      }
    },
    onSuccess: (updatedAccount) => {
      queryClient.setQueryData(["account"], updatedAccount);
    },
    onError: (error) => {
      setAccountUpdateError(error.message);
    },
    onMutate: () => {
      setAccountUpdateError(null);
    }
  });
  
  const passwordUpdateMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch("http://localhost:8000/accounts/me/password", {
        method: "PUT",
        headers: {
          ...headers,
          "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new URLSearchParams({
          old_password: currentPassword,
          new_password: newPassword
        })
      });
      
      if (response.ok) {
        return true;
      } else {
        const error = await response.json();
        throw new Error(error.message);
      }
    },
    onSuccess: () => {
      setCurrentPassword("");
      setNewPassword("");
      setConfirmNewPassword("");
    },
    onError: (error) => {
      setPasswordUpdateError(error.message);
    },
    onMutate: () => {
      setPasswordUpdateError(null);
    }
  });
  
  const accountDeleteMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch("http://localhost:8000/accounts/me", {
        method: "DELETE",
        headers: headers
      });
      
      if (response.ok) {
        return true;
      } else {
        const error = await response.json();
        throw new Error(error.message);
      }
    },
    onSuccess: () => {
      logout();
      navigate("/");
    },
    onError: (error) => {
      alert(`Could not delete account: ${error.message}`);
    }
  });
  
  // Form handlers
  const handleAccountUpdate = (e) => {
    e.preventDefault();
    accountUpdateMutation.mutate();
  };
  
  const handlePasswordUpdate = (e) => {
    e.preventDefault();
    if (newPassword === confirmNewPassword) {
      passwordUpdateMutation.mutate();
    }
  };
  
  const handleLogout = () => {
    logout();
    navigate("/");
  };
  
  const handleAccountDelete = () => {
    if (window.confirm("Are you sure you want to delete your account? This action cannot be undone.")) {
      accountDeleteMutation.mutate();
    }
  };
  
  return (
    <div className="flex h-full">
      <div className="w-64">
        <ChatNavigation />
      </div>
      <div className="flex-1 overflow-y-auto p-6 bg-gray-50">
        <h1 className="text-2xl font-bold mb-6">Settings</h1>
        
        {/* Update Account Section */}
        <div className="bg-white p-6 rounded-lg shadow-sm mb-6">
          <h2 className="text-xl font-semibold mb-4">Update Account</h2>
          <form onSubmit={handleAccountUpdate} className="space-y-4">
            <LabelInput 
              name="username" 
              type="text" 
              value={username} 
              setValue={setUsername} 
            />
            <LabelInput 
              name="email" 
              type="email" 
              value={email} 
              setValue={setEmail} 
            />
            {accountUpdateError && (
              <p className="text-red-600 text-sm">{accountUpdateError}</p>
            )}
            <button
              type="submit"
              className="py-2 px-4 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
            >
              update
            </button>
          </form>
        </div>
        
        {/* Update Password Section */}
        <div className="bg-white p-6 rounded-lg shadow-sm mb-6">
          <h2 className="text-xl font-semibold mb-4">Update Password</h2>
          <form onSubmit={handlePasswordUpdate} className="space-y-4">
            <LabelInput 
              name="current password" 
              type="password" 
              value={currentPassword} 
              setValue={setCurrentPassword} 
            />
            <LabelInput 
              name="new password" 
              type="password" 
              value={newPassword} 
              setValue={setNewPassword} 
            />
            <LabelInput 
              name="confirm new password" 
              type="password" 
              value={confirmNewPassword} 
              setValue={setConfirmNewPassword} 
            />
            {passwordsError && (
              <p className="text-red-600 text-sm">{passwordsError}</p>
            )}
            {passwordUpdateError && (
              <p className="text-red-600 text-sm">{passwordUpdateError}</p>
            )}
            <button
              type="submit"
              disabled={!currentPassword || !newPassword || !confirmNewPassword || !passwordsMatch}
              className="py-2 px-4 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              update password
            </button>
          </form>
        </div>
        
        {/* Manage Account Section */}
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <h2 className="text-xl font-semibold mb-4">Account</h2>
          <div className="space-y-4">
            <button
              onClick={handleLogout}
              className="w-full py-2 px-4 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
            >
              logout
            </button>
            <button
              onClick={handleAccountDelete}
              className="w-full py-2 px-4 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
            >
              delete account
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}