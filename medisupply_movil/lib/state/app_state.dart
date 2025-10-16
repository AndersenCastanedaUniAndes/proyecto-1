import 'package:flutter/foundation.dart';
import '../view_types.dart';

class AppState extends ChangeNotifier {
  AppView _currentView = AppView.login;
  UserType? _userType; // null mientras no haya login
  bool _isLoading = false; // futuro: podría usarse para llamadas async reales

  AppView get currentView => _currentView;
  UserType? get userType => _userType;
  bool get isAuthenticated => _userType != null;
  bool get isLoading => _isLoading;

  void navigateTo(AppView view) {
    if (_currentView == view) return;
    _currentView = view;
    notifyListeners();
  }

  Future<void> login({required String email, required String password, required UserType asType}) async {
    _isLoading = true;
    notifyListeners();

    // Simula retardo de autenticación
    await Future.delayed(const Duration(milliseconds: 800));

    _userType = asType;
    // Redirigir según tipo de usuario
    switch (asType) {
      case UserType.vendedor:
        _currentView = AppView.vendorHome;
        break;
      case UserType.cliente:
        _currentView = AppView.clientHome;
        break;
    }
    _isLoading = false;
    notifyListeners();
  }

  void logout() {
    _userType = null;
    _currentView = AppView.login;
    notifyListeners();
  }

  void registerNewClient({required String email}) {
    // Para futura implementación real
    _userType = UserType.cliente;
    _currentView = AppView.clientHome;
    notifyListeners();
  }

  // Para deep linking inicial
  void setInitialFromPath(String path) {
    final view = appViewFromPath(path);
    if (view == AppView.vendorHome || view == AppView.clientHome || view == AppView.adminHome) {
      // Necesitaría autenticación; por ahora redirigimos a login si no autenticado
      if (!isAuthenticated) {
        _currentView = AppView.login;
        notifyListeners();
        return;
      }
    }
    _currentView = view;
    notifyListeners();
  }
}
