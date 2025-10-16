import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor, act } from "@testing-library/react";
import { LoginForm } from "../components/LoginForm";

// Mock global fetch
globalThis.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({ token: "fake-token" }),
  })
) as jest.Mock;

jest.useFakeTimers();

describe("LoginForm", () => {
  beforeEach(() => {
    // Limpia mocks y localStorage antes de cada prueba
    jest.resetAllMocks();
    localStorage.clear();
  });

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
    expect(passwordInput.type).toBe('password');

    const toggleBtn = passwordInput.parentElement?.querySelector('button') as HTMLButtonElement;
    expect(toggleBtn).toBeTruthy();

    await act(async () => {
      toggleBtn.click();
    });

    expect(passwordInput.type).toBe('text');
  });

  it("muestra estado de carga al enviar", async () => {
    render(<LoginForm onForgotPassword={jest.fn()} onLoginSuccess={jest.fn()} />);

    fireEvent.change(screen.getByPlaceholderText(/Ingresa tu correo electrónico/i), { target: { value: "a@b.com" } });
    fireEvent.change(screen.getByPlaceholderText(/Ingresa tu contraseña/i), { target: { value: "123" } });

    const submit = screen.getByRole('button', { name: /Iniciar Sesión/i });
    fireEvent.click(submit);

    expect(submit).toBeDisabled();
    expect(submit).toHaveTextContent(/Iniciando sesión/i);
  });

  it("llama a onLoginSuccess después de iniciar sesión correctamente", async () => {
    const onLoginSuccess = jest.fn();

    // 🔹 Mock del fetch exitoso
    globalThis.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          access_token: "fake_token",
          token_type: "bearer"
        }),
      })
    ) as jest.Mock;

    render(<LoginForm onForgotPassword={jest.fn()} onLoginSuccess={onLoginSuccess} />);

    fireEvent.change(screen.getByPlaceholderText(/Ingresa tu correo electrónico/i), { target: { value: "test@email.com" } });
    fireEvent.change(screen.getByPlaceholderText(/Ingresa tu contraseña/i), { target: { value: "123456" } });
    fireEvent.click(screen.getByRole('button', { name: /Iniciar Sesión/i }));

    await act(async () => {
      jest.runAllTimers();
    });

    await waitFor(() => expect(onLoginSuccess).toHaveBeenCalled());
    expect(localStorage.getItem("access_token")).toBe("fake_token");
  });

  it("muestra mensaje de error si las credenciales son inválidas", async () => {
    // 🔹 Mock del fetch con error
    globalThis.fetch = jest.fn(() =>
      Promise.resolve({
        ok: false,
        json: () => Promise.resolve({ detail: "Credenciales inválidas" }),
      })
    ) as jest.Mock;

    render(<LoginForm onForgotPassword={jest.fn()} onLoginSuccess={jest.fn()} />);

    fireEvent.change(screen.getByPlaceholderText(/Ingresa tu correo electrónico/i), { target: { value: "fail@email.com" } });
    fireEvent.change(screen.getByPlaceholderText(/Ingresa tu contraseña/i), { target: { value: "wrongpass" } });
    fireEvent.click(screen.getByRole('button', { name: /Iniciar Sesión/i }));

    await act(async () => {
      jest.runAllTimers();
    });

    await waitFor(() => {
      expect(screen.getByText(/Credenciales inválidas/i)).toBeInTheDocument();
    });
  });
});
