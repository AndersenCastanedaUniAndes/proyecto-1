import 'package:flutter/material.dart';

class AppClickableText extends StatelessWidget {
  const AppClickableText({
    super.key,
    this.mainAxisAlignment = MainAxisAlignment.center,
    required this.onTap,
    required this.label,
    required this.textTheme,
    this.icon,
    this.iconSize = 14,
    this.overrideColor,
    this.spacing = 4,
    this.overrideFontWeight,
  });

  final MainAxisAlignment mainAxisAlignment;
  final VoidCallback onTap;
  final IconData? icon;
  final double iconSize;
  final String label;
  final TextTheme textTheme;
  final Color? overrideColor;
  final double spacing;
  final FontWeight? overrideFontWeight;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Row(
        mainAxisAlignment: mainAxisAlignment,
        spacing: spacing,
        children: [
          if (icon != null) ...[
            Icon(icon, size: iconSize, color: overrideColor ?? textTheme.bodySmall?.color),
          ],

          Text(
            label,
            style: textTheme.bodySmall?.copyWith(
              color: overrideColor ?? textTheme.bodySmall?.color,
              fontWeight: overrideFontWeight ?? textTheme.bodySmall?.fontWeight,
            ),
          ),
        ],
      ),
    );
  }
}