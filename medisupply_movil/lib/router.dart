import 'package:flutter/material.dart';
import 'package:medisupply_movil/screens/screens.dart';
import 'package:provider/provider.dart';
import 'view_types.dart';
import 'state/app_state.dart';

/// Parser simple que convierte un RouteInformation (location) a AppView
class AppRouteParser extends RouteInformationParser<AppView> {
  @override
  Future<AppView> parseRouteInformation(RouteInformation routeInformation) async {
    final location = routeInformation.location; // analyzer lo considera non-null
    return appViewFromPath(location); // sin fallback
  }

  @override
  RouteInformation? restoreRouteInformation(AppView configuration) {
    return RouteInformation(location: configuration.path);
  }
}

class AppRouterDelegate extends RouterDelegate<AppView>
    with ChangeNotifier, PopNavigatorRouterDelegateMixin<AppView> {
  final AppState appState;
  final GlobalKey<NavigatorState> navigatorKey = GlobalKey<NavigatorState>();

  AppRouterDelegate(this.appState) {
    appState.addListener(notifyListeners);
  }

  @override
  void dispose() {
    appState.removeListener(notifyListeners);
    super.dispose();
  }

  @override
  AppView? get currentConfiguration => appState.currentView;

  @override
  Future<void> setNewRoutePath(AppView configuration) async {
    // Deep link entrante
    appState.setInitialFromPath(configuration.path);
  }

  @override
  Widget build(BuildContext context) {
    final view = appState.currentView;
    final pages = <Page<dynamic>>[];

    Widget screen;
    switch (view) {
      case AppView.login:
        screen = const LoginScreen();
        break;
      case AppView.forgotPassword:
        screen = const ForgotPasswordScreen();
        break;
      case AppView.register:
        screen = const RegisterScreen();
        break;
      case AppView.vendorHome:
        screen = const VendorScreen();
        break;
      case AppView.clientHome:
        screen = const ClientScreen();
        break;
    }

    pages.add(MaterialPage(child: screen, key: ValueKey(view)));

    return Navigator(
      key: navigatorKey,
      pages: pages,
      onPopPage: (route, result) {
        if (!route.didPop(result)) {
          return false;
        }
        if (appState.currentView != AppView.login) {
          appState.navigateTo(AppView.login);
        }
        return true;
      },
    );
  }
}

/// Widget de conveniencia para crear MaterialApp.router
class MediSupplyApp extends StatelessWidget {
  const MediSupplyApp({super.key});

  @override
  Widget build(BuildContext context) {
    final state = context.watch<AppState>();
    return MaterialApp.router(
      debugShowCheckedModeBanner: false,
      title: 'MediSupply',
      routerDelegate: AppRouterDelegate(state),
      routeInformationParser: AppRouteParser(),
      theme: ThemeData(
        textTheme: const TextTheme(
          titleLarge: TextStyle(fontSize: 24, fontWeight: FontWeight.w500, height: 1.3),
          titleMedium: TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
          bodyMedium: TextStyle(fontSize: 16, fontWeight: FontWeight.w400, height: 1.5),
          bodySmall: TextStyle(fontSize: 14, fontWeight: FontWeight.w400, height: 1.5),
          labelLarge: TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
        ),
        colorScheme: ColorScheme.fromSeed(
          primary: Color(0xFF4682B4),
          seedColor: Color(0xFF4682B4),
          surface: Color(0xFFE0E7FF),
        ),
        useMaterial3: true,
      ),
    );
  }
}
