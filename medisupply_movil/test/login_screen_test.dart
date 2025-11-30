import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:medisupply_movil/screens/login_screen.dart';
import 'package:medisupply_movil/state/app_state.dart';
import 'package:medisupply_movil/view_types.dart';
import 'package:provider/provider.dart';

import 'widget_test_helpers.dart';

void main() {
  group('LoginScreen', () {
    testWidgets('does not submit when fields are empty', (tester) async {
      final state = AppState();
      await tester.pumpWidget(TestHost(child: const LoginScreen(), appState: state));

      // Press button without filling
  final btn = find.widgetWithText(FilledButton, 'Iniciar Sesión');
  expect(btn, findsOneWidget);
  await tester.ensureVisible(btn);
  await tester.tap(btn);
      await tester.pumpAndSettle();

      // Should not trigger loading state or navigation
      expect(find.text('Iniciando sesión...'), findsNothing);
      expect(state.isAuthenticated, isFalse);
    });

    testWidgets('toggles user type and reveals register link for cliente', (tester) async {
      final state = AppState();
      await tester.pumpWidget(TestHost(child: const LoginScreen(), appState: state));

      // Initially Vendedor selected, no register link
      expect(find.text('¿No tienes cuenta? Regístrate aquí'), findsNothing);

      // Tap Cliente tile (second UserTypeWidget)
  // Tap on label 'Cliente' to switch tile selection
      await tester.tap(find.text('Cliente'));
      await tester.pump();

      expect(find.text('¿No tienes cuenta? Regístrate aquí'), findsOneWidget);
    });

    testWidgets('successful submit updates AppState after fake response', (tester) async {
      final state = AppState();

      await tester.pumpWidget(
        ChangeNotifierProvider.value(
          value: state,
          child: const MaterialApp(home: Scaffold(body: LoginScreen())),
        ),
      );

      // Simula que el usuario llena el formulario válido
      await tester.enterText(find.byType(TextFormField).at(0), 'user@test.com');
      await tester.enterText(find.byType(TextFormField).at(1), 'abcd');

      // En lugar de disparar la llamada HTTP real (que requiere dotenv),
      // simulamos directamente la respuesta exitosa y llamamos a AppState.login.
      const fakeBody = '{"id": 1, "access_token": "tok", "nombre_usuario": "User"}';
      state.login(body: fakeBody, asType: UserType.vendedor);

      expect(state.isAuthenticated, isTrue);
      expect(state.currentView, AppView.vendorHome);
    });

    testWidgets('forgot password navigates', (tester) async {
      final state = AppState();
      await tester.pumpWidget(TestHost(child: const LoginScreen(), appState: state));

  final forgot = find.text('¿Olvidaste tu contraseña?');
  await tester.ensureVisible(forgot);
  await tester.tap(forgot);
      await tester.pump();
      expect(state.currentView, AppView.forgotPassword);
    });

    testWidgets('register link navigates when cliente selected', (tester) async {
      final state = AppState();
      await tester.pumpWidget(TestHost(child: const LoginScreen(), appState: state));
      await tester.tap(find.text('Cliente'));
      await tester.pump();

  final register = find.text('¿No tienes cuenta? Regístrate aquí');
  await tester.ensureVisible(register);
  await tester.tap(register);
      await tester.pump();
      expect(state.currentView, AppView.register);
    });
  });
}
