import 'package:flutter/material.dart';

class AppInputField extends StatelessWidget {
  const AppInputField({
    super.key,
    required this.label,
    this.prefixIconData,
    this.suffixIcon,
    this.onChanged,
  });

  final String label;
  final IconData? prefixIconData;
  final Widget? suffixIcon;

  final Function(String)? onChanged;

  @override
  Widget build(BuildContext context) {
    return TextField(
      decoration: InputDecoration(
        isDense: true,
        hintText: label,
        prefixIcon: prefixIconData != null ? Icon(prefixIconData, size: 18,) : null,
        suffixIcon: suffixIcon,
        filled: true,
        fillColor: const Color(0xFFF3F3F5),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide.none,
        ),
      ),
      onChanged: onChanged,
    );
  }
}