// This is for the login form
import PropTypes from "prop-types";
import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { useAuth } from "../hooks";
import LabelInput from "./LabelInput";
import { Link } from "react-router-dom";

function LoginError({ message }) {
  if (message) {
    return <p className="text-red-600 text-sm mt-2">{message}</p>;
  }
  return null;
}

export default function LoginForm() {
  const { login } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState(null);

  // Form validation
  const isFormValid = username && password;

  const mutation = useMutation({
    mutationFn: async () => {
      const response = await fetch("http://localhost:8000/auth/token", {
        method: "POST",
        headers: { "content-type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ username, password }),
      });
      
      if (response.ok) {
        return await response.json();
      } else {
        const error = await response.json();
        if (error.error === "invalid_credentials") {
          throw new Error("Invalid username or password");
        } else {
          throw new Error("An unknown error occurred");
        }
      }
    },
    onSuccess: (data) => {
      const token = data.access_token;
      login(token);
    },
    onError: (error) => {
      setErrorMessage(error.message);
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    mutation.mutate();
  };

  return (
    <div className="max-w-md w-full px-6 py-8 bg-white rounded-lg shadow-md">
      <h1 className="text-2xl font-bold text-center mb-6">Pony Express</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
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
        <LoginError message={errorMessage} />
        <button
          type="submit"
          disabled={!isFormValid}
          className="w-full py-2 px-4 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          login
        </button>
        <div className="text-center mt-4">
          <Link to="/register" className="text-indigo-600 hover:text-indigo-800">
            register new account
          </Link>
        </div>
      </form>
    </div>
  );
}

LoginError.propTypes = {
  message: PropTypes.string,
};