import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { ForgotPasswordForm } from "../components/ForgotPasswordForm";

// Mock global fetch
globalThis.fetch = jest.fn();

describe("ForgotPasswordForm", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renderiza el formulario y permite enviar el correo", async () => {
    const onBackToLogin = jest.fn();

    // Mock de respuesta exitosa del backend
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ message: "Correo enviado correctamente" }),
    });

    render(<ForgotPasswordForm onBackToLogin={onBackToLogin} />);

    // Verifica que el título esté presente
    expect(screen.getByText(/Recuperar Contraseña/i)).toBeInTheDocument();

    // Ingresa un correo
    const emailInput = screen.getByRole("textbox", {
      name: /Correo Electrónico/i,
    });
    fireEvent.change(emailInput, { target: { value: "test@email.com" } });

    // Envía el formulario
    const sendButton = screen.getByRole("button", {
      name: /Enviar Instrucciones/i,
    });
    fireEvent.click(sendButton);

    // Espera a que aparezca la vista de "Correo Enviado"
    await waitFor(() => {
      expect(screen.getByText(/Correo Enviado/i)).toBeInTheDocument();
    });

    // Verifica que fetch haya sido llamado con el correo correcto
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("forgotPassword?email=test@email.com"),
      expect.objectContaining({ method: "POST" })
    );
  });

  it("muestra mensaje de error si el backend responde con error", async () => {
    const onBackToLogin = jest.fn();

    // Mock de error del backend
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: "Correo no encontrado" }),
    });

    render(<ForgotPasswordForm onBackToLogin={onBackToLogin} />);

    const emailInput = screen.getByRole("textbox", {
      name: /Correo Electrónico/i,
    });
    fireEvent.change(emailInput, { target: { value: "invalido@email.com" } });

    const sendButton = screen.getByRole("button", {
      name: /Enviar Instrucciones/i,
    });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText(/Correo no encontrado/i)).toBeInTheDocument();
    });
  });

  it("permite volver al inicio de sesión", () => {
    const onBackToLogin = jest.fn();
    render(<ForgotPasswordForm onBackToLogin={onBackToLogin} />);

    const backButton = screen.getByRole("button", {
      name: /Volver al inicio de sesión/i,
    });
    fireEvent.click(backButton);

    expect(onBackToLogin).toHaveBeenCalled();
  });
});
