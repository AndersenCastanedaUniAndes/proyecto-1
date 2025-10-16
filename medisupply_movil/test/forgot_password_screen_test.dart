import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:medisupply_movil/screens/forgot_password_screen.dart';
import 'package:medisupply_movil/state/app_state.dart';
import 'package:medisupply_movil/view_types.dart';

import 'widget_test_helpers.dart';

void main() {
  group('ForgotPasswordScreen', () {
    testWidgets('requires valid email', (tester) async {
      final state = AppState();
      await tester.pumpWidget(TestHost(child: const ForgotPasswordScreen(), appState: state));

  final sendBtn = find.widgetWithText(FilledButton, 'Enviar Instrucciones');
  await tester.ensureVisible(sendBtn);
  await tester.tap(sendBtn);
      await tester.pump();
      expect(find.text('Ingresa tu correo'), findsOneWidget);

      await tester.enterText(find.byType(TextFormField).first, 'noemail');
  await tester.ensureVisible(sendBtn);
  await tester.tap(sendBtn);
      await tester.pump();
      expect(find.text('Correo inválido'), findsOneWidget);
    });

    testWidgets('submission shows success and allows sending another', (tester) async {
      final state = AppState();
      await tester.pumpWidget(TestHost(child: const ForgotPasswordScreen(), appState: state));

      await tester.enterText(find.byType(TextFormField).first, 'user@test.com');
  final sendBtn2 = find.widgetWithText(FilledButton, 'Enviar Instrucciones');
  await tester.ensureVisible(sendBtn2);
  await tester.tap(sendBtn2);
      await tester.pump();
      expect(find.text('Enviando...'), findsOneWidget);

      await tester.pump(const Duration(seconds: 2));
      await tester.pumpAndSettle();

      expect(find.text('Correo Enviado'), findsOneWidget);
  final another = find.widgetWithText(OutlinedButton, 'Enviar otro correo');
  await tester.ensureVisible(another);
  await tester.tap(another);
      await tester.pump();
      // Back to form state
      expect(find.text('Recuperar Contraseña'), findsOneWidget);
    });

    testWidgets('back to login navigates', (tester) async {
      final state = AppState();
      await tester.pumpWidget(TestHost(child: const ForgotPasswordScreen(), appState: state));

  final back = find.text('Volver al inicio de sesión');
  await tester.ensureVisible(back);
  await tester.tap(back);
      await tester.pump();
      expect(state.currentView, AppView.login);
    });
  });
}
