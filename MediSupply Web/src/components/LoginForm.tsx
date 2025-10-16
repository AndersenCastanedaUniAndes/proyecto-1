import { useState } from "react";
import config from "../config/config";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Eye, EyeOff, Mail, Lock, Pill } from "lucide-react";

interface LoginFormProps {
  onForgotPassword: () => void;
  onLoginSuccess: () => void;
}

export function LoginForm({ onForgotPassword, onLoginSuccess }: LoginFormProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMessage("");

    try {
      // Llamada al microservicio de autenticación
      //const response = await fetch(`${config.API_BASE_URL}/productos/proveedores`);
      const response = await fetch(`${config.API_BASE_LOGIN_URL}/token`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({
          username: email,
          password: password,
        }),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Error al iniciar sesión");
      }

      const data = await response.json();
      //console.log("Token recibido:", data);

      // Guardar token en localStorage
      localStorage.setItem("user", email);
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("token_type", data.token_type);

      onLoginSuccess();
    } catch (err: any) {
      console.error(" Error de autenticación:", err);
      setErrorMessage(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-md">
      <CardHeader className="space-y-4 text-center">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-primary">
          <Pill className="h-8 w-8 text-primary-foreground" />
        </div>
        <div>
          <CardTitle className="text-2xl">Bienvenido a MediSupply</CardTitle>
          <CardDescription>
            Inicia sesión en tu cuenta de distribución farmacéutica
          </CardDescription>
        </div>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">Correo Electrónico</Label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                id="email"
                type="email"
                placeholder="Ingresa tu correo electrónico"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="pl-10"
                required
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">Contraseña</Label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                id="password"
                type={showPassword ? "text" : "password"}
                placeholder="Ingresa tu contraseña"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="pl-10 pr-10"
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                {showPassword ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </button>
            </div>
          </div>

          {errorMessage && (
            <p className="text-sm text-red-600 text-center">{errorMessage}</p>
          )}

          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? "Iniciando sesión..." : "Iniciar Sesión"}
          </Button>

          <div className="text-center">
            <button
              type="button"
              onClick={onForgotPassword}
              className="text-sm text-muted-foreground hover:text-primary transition-colors"
            >
              ¿Olvidaste tu contraseña?
            </button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
