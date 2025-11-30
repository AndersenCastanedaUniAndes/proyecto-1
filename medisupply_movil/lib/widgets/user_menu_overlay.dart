import 'package:flutter/material.dart';
import 'package:medisupply_movil/styles/styles.dart';
import 'package:medisupply_movil/widgets/widgets.dart';
import 'package:provider/provider.dart';
import '../state/app_state.dart';

class UserMenuOverlay extends StatelessWidget {
  final VoidCallback onClose;
  const UserMenuOverlay({
    super.key,
    required this.onClose
  });

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Positioned.fill(
      child: GestureDetector(
        onTap: onClose,
        child: Container(
          color: Colors.black.withAlpha(128),
          child: Center(
            child: GestureDetector(
              onTap: () {},
              child: Container(
                margin: const EdgeInsets.symmetric(horizontal: 24),
                padding: const EdgeInsets.all(26),
                decoration: AppStyles.decoration.copyWith(color: Colors.white),
                width: 360,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Container(
                      height: 64,
                      width: 64,
                      decoration: BoxDecoration(color: Color(0xFFDBEAFE), shape: BoxShape.circle),
                      child: Icon(AppIcons.user, size: 36, color: AppStyles.blue1),
                    ),
                    const SizedBox(height: 16),

                    Text('Usuario', style: textTheme.bodyLarge?.copyWith(fontSize: 18, fontWeight: FontWeight.w600)),
                    Text('MediSupply', style: textTheme.bodyMedium?.copyWith(fontSize: 14, fontWeight: FontWeight.w400)),
                    const SizedBox(height: 36),

                    Align(
                      alignment: Alignment.centerLeft,
                      child: Padding(
                        padding: const EdgeInsets.only(left: 12.0),
                        child: AppClickableText(
                          mainAxisAlignment: MainAxisAlignment.start,
                          onTap: () {
                            onClose();
                            context.read<AppState>().logout();
                          },
                          label: 'Cerrar Sesión',
                          icon: AppIcons.logout,
                          iconSize: 18,
                          spacing: 22,
                          overrideColor: AppStyles.red1,
                          overrideFontWeight: FontWeight.w500,
                          textTheme: textTheme.copyWith(bodySmall: textTheme.bodySmall?.copyWith(fontSize: 15))
                        ),
                      ),
                    )
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}