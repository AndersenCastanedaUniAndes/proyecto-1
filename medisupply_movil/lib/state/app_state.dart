import 'dart:convert';

import 'package:flutter/foundation.dart';
import '../view_types.dart';

class AppState extends ChangeNotifier {
  AppView _currentView = AppView.login;
  UserType? _userType; // null mientras no haya login
  String _id = '';
  String _token = '';
  String _userName = '';

  AppView get currentView => _currentView;
  UserType? get userType => _userType;
  bool get isAuthenticated => _userType != null;
  String get id => _id;
  String get token => _token;
  String get userName => _userName;

  void navigateTo(AppView view) {
    if (_currentView == view) return;
    _currentView = view;
    notifyListeners();
  }

  void login({required String body, required UserType asType}) async {
    _userType = asType;

    var json = jsonDecode(body);
    _id = json['id'].toString();
    _token = json['access_token'];
    _userName = json['nombre_usuario'];

    // Redirigir según tipo de usuario
    switch (asType) {
      case UserType.vendedor:
        _currentView = AppView.vendorHome;
        break;
      case UserType.cliente:
        _currentView = AppView.clientHome;
        break;
    }

    notifyListeners();
  }

  void logout() {
    _userType = null;
    _currentView = AppView.login;
    notifyListeners();
  }

  void registerNewClient({required String username}) {
    _userName = username;
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
