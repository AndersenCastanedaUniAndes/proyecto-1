import { useEffect, useState } from "react";
import { LoginForm } from "./components/LoginForm";
import { ForgotPasswordForm } from "./components/ForgotPasswordForm";
import { HomeView } from "./components/HomeView";
import { Toaster } from "./components/ui/sonner";

export default function App() {
  const [currentView, setCurrentView] = useState<"login" | "forgot-password" | "home">("login");

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      setCurrentView("home");
    }
  }, []);

  const showForgotPassword = () => setCurrentView("forgot-password");
  const showLogin = () => {
    localStorage.removeItem("user");
    localStorage.removeItem("access_token");
    localStorage.removeItem("token_type");
    setCurrentView("login");
  };
  const showHome = () => setCurrentView("home");

  if (currentView === "home") {
    return (
      <>
        <HomeView onLogout={showLogin} />
        <Toaster />
      </>
    );
  }

  return (
    <>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          {currentView === "login" ? (
            <LoginForm 
              onForgotPassword={showForgotPassword} 
              onLoginSuccess={showHome}
            />
          ) : (
            <ForgotPasswordForm onBackToLogin={showLogin} />
          )}
        </div>
      </div>
      <Toaster />
    </>
  );
}