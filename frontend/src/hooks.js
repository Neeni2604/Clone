// Custom hooks for auth and account data
import { useContext } from "react";
import { AuthContext } from "./contexts";
import { useQuery } from "@tanstack/react-query";

// This is a hook to access auth context
export const useAuth = () => useContext(AuthContext);

// This is a hook to access current account data
export const useAccount = () => {
  const { loggedIn, headers, logout } = useAuth();
  
  const query = useQuery({
    queryKey: ["account"],
    queryFn: async () => {
      const response = await fetch("http://localhost:8000/accounts/me", { headers });
      if (response.ok) {
        return await response.json();
      } else {
        const data = await response.json();
        // If token is expired, log out
        if (data.error === "expired_access_token") {
          logout();
        }
        throw new Error(data.message || "Failed to fetch account");
      }
    },
    enabled: loggedIn, // Only run query if logged in and don't retry on error
    retry: false, 
  });

  // If successful, return data. Else, return default object
  return query.data || { id: -1, username: "", email: "" };
};