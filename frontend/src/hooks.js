// Making our own custom hooks

import { useContext } from "react";
import { AuthContext } from "./contexts";
import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router";

const useAuth = () => useContext(AuthContext);

const useAccount = () => {
    const navigate = useNavigate();
    const {loggedIn, headers, logout} = useAuth();
    const query = useQuery({
        enabled: loggedIn,
        queryKey: ["account"],
        queryFn: async () => {
            const response = await fetch("http://localhost:8000/accounts/me", {headers});
            if(response.ok){
                return await response.json();
            }
            else {
                throw new Error("invalid token");
            }
        }
    });
    if(query.isSuccess){
        return query.data;
    }
    else if(query.isError){
        logout();
        navigate("/login");
    }
    else{
        return {id: -1, username: "loading"};
    }
}

export {useAuth, useAccount}
