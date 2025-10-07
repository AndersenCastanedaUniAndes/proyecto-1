import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { ForgotPasswordForm } from "../components/ForgotPasswordForm";

describe("ForgotPasswordForm", () => {
  it("renderiza el formulario y permite enviar el correo", async () => {
    const onBackToLogin = jest.fn();
    render(<ForgotPasswordForm onBackToLogin={onBackToLogin} />);

    // Verifica que el título esté presente
    expect(screen.getByText(/Recuperar Contraseña/i)).toBeInTheDocument();

    // Ingresa un correo y envía el formulario
    // Cambia el placeholder si es diferente en tu componente
    const emailInput = screen.getByRole('textbox');
    fireEvent.change(emailInput, {
      target: { value: "test@email.com" },
    });

    // Cambia el texto del botón si es diferente en tu componente
    const sendButton = screen.getByRole('button', { name: /Enviar Instrucciones/i });
    fireEvent.click(sendButton);

  });
   

  it("permite volver al inicio de sesión", () => {
    const onBackToLogin = jest.fn();
    render(<ForgotPasswordForm onBackToLogin={onBackToLogin} />);
    // Cambia el texto del botón si es diferente en tu componente
    const backButton = screen.getByRole('button', { name: /Volver al inicio de sesión/i });
    fireEvent.click(backButton);
    expect(onBackToLogin).toHaveBeenCalled();
  });
});