import PropTypes from "prop-types";
import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { useAuth } from "../hooks";
import LabelInput from "./LabelInput";

function LoginError({message}){
    if(message){
        return <p>{message}</p>
    }
    else{
        return <></>
    }
}

export default function LoginForm(){
    const {login} = useAuth();
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [errorMessage, setErrorMessage] = useState(null); 

    const mutation = useMutation({
        mutationFn: async() => {
            const response = await fetch("http://localhost:8000/auth/token",
                {
                    method: "POST",
                    headers: {"content-type": "application/x-www-form-urlencoded"},
                    body: new URLSearchParams({username, password})
                }
            );
            if(response.ok){
                return await response.json();
            }
            else{
                const error = await response.json();
                if(error.error == "invalid_credentials"){
                    throw new Error("invalid username or password");
                }
                else{
                    throw new Error("unknown error occurred");
                }
            }
        },
        onSuccess: (data) => {
            const token = data.access_token;
            login(token);
        },
        onError: (error) => {
            setErrorMessage(error.message);
        }
    })

    const handleSubmit = (e) => {
        e.preventDefault();
        // console.log(username, password);
        mutation.mutate();
    }

    return (
        <form onSubmit={handleSubmit}>
            <LabelInput
                name="username"
                type="text"
                value={username}
                setValue={setUsername}
            />
            <LabelInput
                name="password"
                type="password"
                value={password}
                setValue={setPassword}
            />
            <LoginError message={errorMessage}/>
            <button type="submit">Login</button>
        </form>
    );
}

LoginError.propTypes = {
    message: PropTypes.string,
};