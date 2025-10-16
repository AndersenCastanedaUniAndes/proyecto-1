import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:medisupply_movil/screens/placeholders.dart';
import 'package:medisupply_movil/state/app_state.dart';
import 'package:medisupply_movil/view_types.dart';
import 'package:provider/provider.dart';

Widget _wrapWithApp(Widget child, AppState state) {
  return ChangeNotifierProvider.value(
    value: state,
    child: MediaQuery(
      data: const MediaQueryData(size: Size(1200, 1800)),
      child: MaterialApp(home: child),
    ),
  );
}

void main() {
  group('Vendor and Client Home placeholders', () {
    testWidgets('VendorScreen opens user menu and logout returns to login', (tester) async {
      final state = AppState();
      // Simulate already on vendor home (no need for async login)
      state.navigateTo(AppView.vendorHome);

      await tester.pumpWidget(_wrapWithApp(const VendorScreen(), state));

      await tester.pumpAndSettle();

      // Tap the header user IconButton (it's the rightmost IconButton inside HomeCard)
  final buttons = find.byType(IconButton);
      expect(buttons, findsWidgets);
      await tester.tap(buttons.last);
      await tester.pump();

      // Overlay should appear with 'Cerrar Sesión'
      expect(find.text('Cerrar Sesión'), findsOneWidget);
      await tester.tap(find.text('Cerrar Sesión'));
      await tester.pumpAndSettle();
      expect(state.currentView, AppView.login);
    });

    testWidgets('VendorScreen menu cards navigate to subviews and back', (tester) async {
      final state = AppState();
      state.navigateTo(AppView.vendorHome);
      await tester.pumpWidget(_wrapWithApp(const VendorScreen(), state));

      await tester.pumpAndSettle();

      // Tap Clientes card
      final clientes = find.text('Clientes');
      await tester.ensureVisible(clientes);
      await tester.tap(clientes);
      await tester.pumpAndSettle();
      expect(find.text('Mis Clientes'), findsOneWidget);

      // Back
      await tester.tap(find.byType(IconButton).first);
      await tester.pumpAndSettle();
      expect(find.text('Clientes'), findsOneWidget);
    });

    testWidgets('ClientHomeScreen shows Recent Activity and cards navigate', (tester) async {
      final state = AppState();
      state.navigateTo(AppView.clientHome);
      await tester.pumpWidget(_wrapWithApp(const ClientHomeScreen(), state));

      await tester.pumpAndSettle();

      expect(find.text('Actividad Reciente'), findsOneWidget);

      // Navigate to Pedidos subview
      final pedidos = find.text('Pedidos');
      await tester.ensureVisible(pedidos);
      await tester.tap(pedidos);
      await tester.pumpAndSettle();
      expect(find.text('Mis Pedidos'), findsOneWidget);

      // Back
      await tester.tap(find.byType(IconButton).first);
      await tester.pumpAndSettle();
      expect(find.text('Actividad Reciente'), findsOneWidget);
    });
  });
}
