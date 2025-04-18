// This is the Registration Form component.
import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { useAuth } from "../hooks";
import LabelInput from "./LabelInput";
import { Link } from "react-router-dom";
import PropTypes from "prop-types";

function RegistrationError({ message }) {
  if (message) {
    return <p className="text-red-600 text-sm mt-2">{message}</p>;
  }
  return null;
}

export default function RegisterForm() {
  const { login } = useAuth();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState(null);

  // Checking if the passwords match
  const passwordsMatch = password === confirmPassword;
  const passwordsError = !passwordsMatch && confirmPassword.length > 0 ? "Passwords do not match" : null;

  // Determining if the form is valid
  const isFormValid = username && email && password && confirmPassword && passwordsMatch;

  const mutation = useMutation({
    mutationFn: async () => {
      const response = await fetch("http://localhost:8000/auth/registration", {
        method: "POST",
        headers: { "content-type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ username, email, password }),
      });

      if (response.ok) {
        return await response.json();
      } else {
        const error = await response.json();
        throw new Error(error.message);
      }
    },
    onSuccess: () => {
      // After registration is complete, log the user in
      fetch("http://localhost:8000/auth/token", {
        method: "POST",
        headers: { "content-type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ username, password }),
      })
        .then((response) => response.json())
        .then((data) => {
          login(data.access_token);
        })
        .catch((error) => {
          setErrorMessage(error.message);
        });
    },
    onError: (error) => {
      setErrorMessage(error.message);
    },
    onMutate: () => {
      setErrorMessage(null);
    }
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (isFormValid) {
      mutation.mutate();
    }
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
          name="email"
          type="email"
          value={email}
          setValue={setEmail}
        />
        <LabelInput
          name="password"
          type="password"
          value={password}
          setValue={setPassword}
        />
        <LabelInput
          name="confirm password"
          type="password"
          value={confirmPassword}
          setValue={setConfirmPassword}
        />
        {passwordsError && <p className="text-red-600 text-sm">{passwordsError}</p>}
        <RegistrationError message={errorMessage} />
        <button
          type="submit"
          disabled={!isFormValid}
          className="w-full py-2 px-4 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          register
        </button>
        <div className="text-center mt-4">
          <Link to="/login" className="text-indigo-600 hover:text-indigo-800">
            login to account
          </Link>
        </div>
      </form>
    </div>
  );
}

RegistrationError.propTypes = {
  message: PropTypes.string,
};