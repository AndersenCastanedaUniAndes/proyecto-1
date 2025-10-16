import 'package:flutter/material.dart';

class AppTextFormField extends StatelessWidget {
  const AppTextFormField({
    super.key,
    required this.controller,
    required this.label,
    this.prefixIconData,
    this.suffixIcon,
    this.keyboardType,
    this.obscureText = false,
    this.validator,
  });

  final TextEditingController controller;
  final String label;
  final IconData? prefixIconData;
  final Widget? suffixIcon;
  final TextInputType? keyboardType;
  final bool obscureText;
  final String? Function(String?)? validator;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        TextFormField(
          controller: controller,
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
          keyboardType: keyboardType,
          obscureText: obscureText,
          validator: validator,
        ),
      ],
    );
  }
}