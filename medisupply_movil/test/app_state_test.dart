import 'package:flutter_test/flutter_test.dart';
import 'package:medisupply_movil/state/app_state.dart';
import 'package:medisupply_movil/view_types.dart';

void main() {
  test('AppState navigateTo changes currentView', () async {
    final s = AppState();
    expect(s.currentView, AppView.login);
    s.navigateTo(AppView.forgotPassword);
    expect(s.currentView, AppView.forgotPassword);
  });

  test('AppState login sets userType and view accordingly', () async {
    final s = AppState();
    // Simula una respuesta exitosa del backend
    const fakeBody = '{"id": 1, "access_token": "tok", "nombre_usuario": "a"}';
    s.login(body: fakeBody, asType: UserType.cliente);
    expect(s.userType, UserType.cliente);
    expect(s.currentView, AppView.clientHome);
  });

  test('setInitialFromPath respects auth gates', () {
    final s = AppState();
    s.setInitialFromPath('/vendor');
    // Not authenticated -> redirected to login
    expect(s.currentView, AppView.login);

    // Authenticated as vendor
    s.navigateTo(AppView.vendorHome);
    s.setInitialFromPath('/register');
    expect(s.currentView, AppView.register);
  });
}
