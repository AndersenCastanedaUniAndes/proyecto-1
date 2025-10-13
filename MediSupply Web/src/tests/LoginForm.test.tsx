import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor, act } from "@testing-library/react";
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

  it("permite alternar la visibilidad de la contraseña", async () => {
    render(<LoginForm onForgotPassword={jest.fn()} onLoginSuccess={jest.fn()} />);
    const passwordInput = screen.getByPlaceholderText(/Ingresa tu contraseña/i) as HTMLInputElement;
    // Por defecto, tipo password
    expect(passwordInput.type).toBe('password');
    // Busca el botón de toggle dentro del contenedor del input de contraseña
    const passwordContainer = passwordInput.parentElement as HTMLElement;
    const toggleBtn = passwordContainer.querySelector('button') as HTMLButtonElement;
    expect(toggleBtn).toBeTruthy();
    await act(async () => {
      toggleBtn.click();
    });
    expect(passwordInput.type).toBe('text');
  });

  it("muestra estado de carga al enviar", () => {
    render(<LoginForm onForgotPassword={jest.fn()} onLoginSuccess={jest.fn()} />);
    // Completa el formulario
    fireEvent.change(screen.getByPlaceholderText(/Ingresa tu correo electrónico/i), { target: { value: "a@b.com" } });
    fireEvent.change(screen.getByPlaceholderText(/Ingresa tu contraseña/i), { target: { value: "123" } });
    // Envía y verifica texto de carga antes de resolver timers
    const submit = screen.getByRole('button', { name: /Iniciar Sesión/i });
    fireEvent.click(submit);
    expect(submit).toBeDisabled();
    expect(submit).toHaveTextContent(/Iniciando sesión/i);
  });
 it("llama a onLoginSuccess después de iniciar sesión", async () => {
    const onLoginSuccess = jest.fn();
    render(<LoginForm onForgotPassword={jest.fn()} onLoginSuccess={onLoginSuccess} />);
    fireEvent.change(screen.getByPlaceholderText(/Ingresa tu correo electrónico/i), { target: { value: "test@email.com" } });
    fireEvent.change(screen.getByPlaceholderText(/Ingresa tu contraseña/i), { target: { value: "123456" } });
    fireEvent.click(screen.getByRole('button', { name: /Iniciar Sesión/i }));
    await act(async () => {
      jest.runAllTimers();
    });
    await waitFor(() => expect(onLoginSuccess).toHaveBeenCalled());
  });
});