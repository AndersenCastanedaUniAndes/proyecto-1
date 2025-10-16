// Enumeraciones centrales para navegación y tipo de usuario

/// Vistas (pantallas) disponibles en la app.
/// Equivalente al type ViewType de React.
enum AppView {
  login,
  forgotPassword,
  register,
  adminHome,
  vendorHome,
  clientHome,
}

/// Tipos de usuario soportados.
enum UserType {
  vendedor,
  cliente,
}

extension AppViewPath on AppView {
  String get path {
    switch (this) {
      case AppView.login:
        return '/login';
      case AppView.forgotPassword:
        return '/forgot-password';
      case AppView.register:
        return '/register';
      case AppView.adminHome:
        return '/admin';
      case AppView.vendorHome:
        return '/vendor';
      case AppView.clientHome:
        return '/client';
    }
  }
}

AppView appViewFromPath(String path) {
  switch (path) {
    case '/login':
      return AppView.login;
    case '/forgot-password':
      return AppView.forgotPassword;
    case '/register':
      return AppView.register;
    case '/admin':
      return AppView.adminHome;
    case '/vendor':
      return AppView.vendorHome;
    case '/client':
      return AppView.clientHome;
    default:
      return AppView.login;
  }
}
