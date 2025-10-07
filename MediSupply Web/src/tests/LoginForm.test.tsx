import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { LoginForm } from "../components/LoginForm";

jest.useFakeTimers();

describe("LoginForm", () => {
  it("renderiza el título y la descripción", () => {
    render(<LoginForm onForgotPassword={jest.fn()} onLoginSuccess={jest.fn()} />);
    expect(screen.getByText(/Bienvenido a MediSupply/i)).toBeInTheDocument();
    expect(screen.getByText(/Inicia sesión en tu cuenta de distribución farmacéutica/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Iniciar Sesión/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /¿Olvidaste tu contraseña\?/i })).toBeInTheDocument();
  });

  it("llama a onForgotPassword al hacer clic en el enlace", () => {
    const onForgotPassword = jest.fn();
    render(<LoginForm onForgotPassword={onForgotPassword} onLoginSuccess={jest.fn()} />);
    fireEvent.click(screen.getByRole('button', { name: /¿Olvidaste tu contraseña\?/i }));
    expect(onForgotPassword).toHaveBeenCalled();
  });

 it("llama a onLoginSuccess después de iniciar sesión", async () => {
    const onLoginSuccess = jest.fn();
    render(<LoginForm onForgotPassword={jest.fn()} onLoginSuccess={onLoginSuccess} />);
    fireEvent.change(screen.getByPlaceholderText(/Ingresa tu correo electrónico/i), { target: { value: "test@email.com" } });
    fireEvent.change(screen.getByPlaceholderText(/Ingresa tu contraseña/i), { target: { value: "123456" } });
    fireEvent.click(screen.getByRole('button', { name: /Iniciar Sesión/i }));
    jest.runAllTimers();
    await waitFor(() => expect(onLoginSuccess).toHaveBeenCalled());
  });
});