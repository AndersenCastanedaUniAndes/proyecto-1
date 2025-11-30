import 'package:flutter/material.dart';
import 'package:medisupply_movil/screens/screens.dart';
import 'package:medisupply_movil/widgets/widgets.dart';
import 'package:medisupply_movil/utils/utils.dart';

class VendorScreen extends StatefulWidget {
  const VendorScreen({super.key});

  @override
  State<VendorScreen> createState() => _VendorScreenState();
}

class _VendorScreenState extends State<VendorScreen> {
  VendorScreenEnum _current = VendorScreenEnum.home;
  bool _showUserMenu = false;

  void _goHome() => setState(() => _current = VendorScreenEnum.home);

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
                VendorScreenEnum.clientes => VendorClientsScreen(onBack: _goHome),
                VendorScreenEnum.visitas => VendorVisitsScreen(onBack: _goHome),
                VendorScreenEnum.pedidos => VendorOrderScreen(onBack: _goHome),
                VendorScreenEnum.recomendaciones => _SimpleSubViewScreen(
                  title: 'Recomendaciones',
                  onBack: _goHome,
                  child: const Text('Generación de recomendaciones próximamente...')
                ),
                VendorScreenEnum.home => VendorHomeScreen(
                  onOpenMenu: () => setState(() => _showUserMenu = true),
                  onTapCard: (view) => setState(() => _current = view)
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

class _SimpleSubViewScreen extends StatelessWidget {
  final String title;
  final Widget child;
  final VoidCallback onBack;
  const _SimpleSubViewScreen({required this.title, required this.child, required this.onBack});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            IconButton(onPressed: onBack, icon: const Icon(Icons.arrow_back)),
            Text(title, style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
          ],
        ),
        const SizedBox(height: 12),
        Expanded(
          child: Center(
            child: child,
          ),
        ),
      ],
    );
  }
}