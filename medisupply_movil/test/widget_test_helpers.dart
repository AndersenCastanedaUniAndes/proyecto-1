import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:medisupply_movil/state/app_state.dart';

/// A simple wrapper to pump a widget under MaterialApp with a provided AppState.
class TestHost extends StatelessWidget {
  const TestHost({super.key, required this.child, required this.appState});

  final Widget child;
  final AppState appState;

  @override
  Widget build(BuildContext context) {
    final mediaQueryData = const MediaQueryData(size: Size(1200, 1800));
    return ChangeNotifierProvider<AppState>.value(
      value: appState,
      child: MediaQuery(
        data: mediaQueryData,
        child: MaterialApp(
          debugShowCheckedModeBanner: false,
          theme: ThemeData(
          textTheme: const TextTheme(
            titleLarge: TextStyle(fontSize: 24, fontWeight: FontWeight.w500, height: 1.3),
            titleMedium: TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
            bodyMedium: TextStyle(fontSize: 16, fontWeight: FontWeight.w400, height: 1.5),
            bodySmall: TextStyle(fontSize: 14, fontWeight: FontWeight.w400, height: 1.5),
            labelLarge: TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
          ),
          colorScheme: ColorScheme.fromSeed(
            seedColor: const Color(0xFF4682B4),
            primary: const Color(0xFF4682B4),
            surface: const Color(0xFFE0E7FF),
          ),
          useMaterial3: true,
          ),
          home: Scaffold(body: child),
        ),
      ),
    );
  }
}

/// Find the nth TextFormField in the tree (0-based).
Finder findTextFormFieldAt(int index) {
  final fields = find.byType(TextFormField);
  return fields.at(index);
}
