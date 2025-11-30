import 'package:flutter/material.dart';
import 'package:medisupply_movil/utils/utils.dart';
import 'package:medisupply_movil/widgets/widgets.dart';
import 'package:medisupply_movil/screens/screens.dart';

class ClientScreen extends StatefulWidget {
  const ClientScreen({super.key});

  @override
  State<ClientScreen> createState() => _ClientScreenState();
}

class _ClientScreenState extends State<ClientScreen> {
  ClientView _current = ClientView.entregas;
  bool _showUserMenu = false;

  void _goHome() => setState(() => _current = ClientView.home);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Stack(
        children: [
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(12.0),
              child: switch (_current) {
                ClientView.pedidos => ClientOrdersScreen(onBack: _goHome),
                ClientView.entregas => ClientDeliveriesScreen(onBack: _goHome),
                ClientView.home => ClientHomeScreen(
                  onOpenMenu: () => setState(() => _showUserMenu = true),
                  onTapCard: (v) => setState(() => _current = v)
                ),
              },
            ),
          ),
          if (_showUserMenu)
            UserMenuOverlay(onClose: () => setState(() => _showUserMenu = false)),
        ],
      ),
    );
  }
}