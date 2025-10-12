import 'package:flutter/material.dart';
import 'package:medisupply_movil/styles/styles.dart';

class AppIcon extends StatelessWidget {
  const AppIcon({
    super.key,
    required this.colorScheme
  });

  final ColorScheme colorScheme;

  @override
  Widget build(BuildContext context) {
    return CircleAvatar(
      radius: 36,
      backgroundColor: colorScheme.primary,
      child: Icon(AppIcons.main, color: colorScheme.onPrimary, size: 34),
    );
  }
}