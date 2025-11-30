import 'package:flutter/material.dart';

class Tag extends StatelessWidget {
  const Tag({
    super.key,
    required this.title,
    required this.textTheme,
    this.backgroundColor = Colors.grey,
    this.foregroundColor = Colors.black,
  });

  final String title;
  final TextStyle textTheme;
  final Color backgroundColor;
  final Color foregroundColor;

  @override
  Widget build(BuildContext context) {
    return Flexible(
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
          color: backgroundColor,
          borderRadius: BorderRadius.circular(12)
        ),
        child: Text(title, style: textTheme.copyWith(color: foregroundColor)),
      ),
    );
  }
}