import { useState } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Mail, ArrowLeft, CheckCircle, Pill } from "lucide-react";

interface ForgotPasswordFormProps {
  onBackToLogin: () => void;
}

export function ForgotPasswordForm({ onBackToLogin }: ForgotPasswordFormProps) {
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isEmailSent, setIsEmailSent] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    // Simulate sending recovery email
    setTimeout(() => {
      setIsLoading(false);
      setIsEmailSent(true);
      console.log("Recovery email sent to:", email);
    }, 2000);
  };

  const handleSendAnother = () => {
    setIsEmailSent(false);
    setEmail("");
  };

  if (isEmailSent) {
    return (
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-4 text-center">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
            <CheckCircle className="h-8 w-8 text-green-600" />
          </div>
          <div>
            <CardTitle className="text-2xl">Correo Enviado</CardTitle>
            <CardDescription>
              Hemos enviado las instrucciones de recuperación a tu correo
            </CardDescription>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-sm text-blue-800">
              Revisa tu bandeja de entrada y la carpeta de spam. El correo puede tardar algunos minutos en llegar.
            </p>
          </div>
          
          <div className="space-y-3">
            <Button 
              onClick={handleSendAnother}
              variant="outline" 
              className="w-full"
            >
              Enviar otro correo
            </Button>
            
            <Button 
              onClick={onBackToLogin}
              variant="ghost" 
              className="w-full"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Volver al inicio de sesión
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-md">
      <CardHeader className="space-y-4 text-center">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-primary">
          <Pill className="h-8 w-8 text-primary-foreground" />
        </div>
        <div>
          <CardTitle className="text-2xl">Recuperar Contraseña</CardTitle>
          <CardDescription>
            Ingresa tu correo y te enviaremos instrucciones para restablecer tu contraseña
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

          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? "Enviando..." : "Enviar Instrucciones"}
          </Button>

          <div className="text-center">
            <button
              type="button"
              onClick={onBackToLogin}
              className="text-sm text-muted-foreground hover:text-primary transition-colors inline-flex items-center"
            >
              <ArrowLeft className="h-3 w-3 mr-1" />
              Volver al inicio de sesión
            </button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}