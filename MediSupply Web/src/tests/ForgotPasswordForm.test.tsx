import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor, act } from "@testing-library/react";
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
    jest.useFakeTimers();
    fireEvent.click(sendButton);
    // Avanza temporizador simulado del componente (2000ms)
    await act(async () => {
      jest.runAllTimers();
    });
    // Debe mostrar la vista de "Correo Enviado"
    expect(await screen.findByText(/Correo Enviado/i)).toBeInTheDocument();
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