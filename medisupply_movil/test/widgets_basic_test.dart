import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:medisupply_movil/widgets/widgets.dart';

void main() {
  group('Basic widgets', () {
    testWidgets('AppClickableText calls onTap', (tester) async {
      var tapped = false;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppClickableText(
              label: 'Click aquí',
              textTheme: const TextTheme(),
              onTap: () => tapped = true,
            ),
          ),
        ),
      );

      await tester.tap(find.text('Click aquí'));
      await tester.pump();
      expect(tapped, isTrue);
    });

    testWidgets('ConfirmationButton shows loading label', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: ConfirmationButton(
              isLoading: true,
              idleLabel: 'Enviar',
              onTapLabel: 'Enviando...',
              onTap: () {},
            ),
          ),
        ),
      );

      expect(find.text('Enviando...'), findsOneWidget);
    });
  });
}
