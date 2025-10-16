import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:medisupply_movil/screens/register_screen.dart';
import 'package:medisupply_movil/state/app_state.dart';
import 'package:medisupply_movil/view_types.dart';

import 'widget_test_helpers.dart';

void main() {
  group('RegisterScreen', () {
    testWidgets('validates required fields and email format', (tester) async {
      final state = AppState();
      await tester.pumpWidget(TestHost(child: const RegisterScreen(), appState: state));

      // Tap create without filling
  final createBtn = find.widgetWithText(FilledButton, 'Crear Cuenta');
  await tester.ensureVisible(createBtn);
  await tester.tap(createBtn);
      await tester.pump();

      // Some required messages appear (not necessarily all visible at once depending on autovalidate)
  // At least one required error should show
  expect(find.textContaining('requerido'), findsAtLeastNWidgets(1));

      // Fill invalid email
      await tester.enterText(find.byType(TextFormField).at(2), 'invalid');
      await tester.pump();
      expect(find.text('El correo electrónico no es válido'), findsOneWidget);
    });

    testWidgets('password confirmation mismatch shows error', (tester) async {
      final state = AppState();
      await tester.pumpWidget(TestHost(child: const RegisterScreen(), appState: state));

      // Fill minimum required fields quickly
      await tester.enterText(find.byType(TextFormField).at(0), 'Mi Empresa');
      await tester.enterText(find.byType(TextFormField).at(1), 'Juan Perez');
      await tester.enterText(find.byType(TextFormField).at(2), 'test@correo.com');
      await tester.enterText(find.byType(TextFormField).at(3), '+57 1111111');
      await tester.enterText(find.byType(TextFormField).at(4), 'Calle 1 #2-3');
      await tester.enterText(find.byType(TextFormField).at(5), 'Bogotá');
      await tester.enterText(find.byType(TextFormField).at(6), 'secret1');
      await tester.enterText(find.byType(TextFormField).at(7), 'secret2');
    await tester.pump();

    final createBtn = find.widgetWithText(FilledButton, 'Crear Cuenta');
    await tester.ensureVisible(createBtn);
    await tester.tap(createBtn);
      await tester.pump();
      expect(find.text('Las contraseñas no coinciden'), findsOneWidget);
    });

    testWidgets('successful register navigates to client home', (tester) async {
      final state = AppState();
      await tester.pumpWidget(TestHost(child: const RegisterScreen(), appState: state));

      // Fill valid values
      final values = [
        'Empresa X',
        'Ana Gomez',
        'ana@empresa.com',
        '+57 123',
        'Calle 1',
        'Bogotá',
        'secret1',
        'secret1',
      ];
      for (var i = 0; i < values.length; i++) {
        await tester.enterText(find.byType(TextFormField).at(i), values[i]);
      }

      final createBtn = find.widgetWithText(FilledButton, 'Crear Cuenta');
      await tester.ensureVisible(createBtn);
      await tester.tap(createBtn);
      await tester.pump();
      expect(find.text('Creando cuenta...'), findsOneWidget);

      await tester.pump(const Duration(seconds: 2));
      await tester.pumpAndSettle();

      expect(state.userType, UserType.cliente);
      expect(state.currentView, AppView.clientHome);
    });

    testWidgets('back to login clickable text navigates', (tester) async {
      final state = AppState();
      await tester.pumpWidget(TestHost(child: const RegisterScreen(), appState: state));

  final backToLogin = find.text('¿Ya tienes cuenta? Inicia sesión aquí');
  await tester.ensureVisible(backToLogin);
  await tester.tap(backToLogin);
      await tester.pump();
      expect(state.currentView, AppView.login);
    });
  });
}
