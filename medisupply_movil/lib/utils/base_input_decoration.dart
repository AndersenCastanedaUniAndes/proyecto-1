import 'package:flutter/material.dart';
import 'package:medisupply_movil/styles/styles.dart';

InputDecoration baseInputDecoration({bool useConstraints = true}) {
  return InputDecoration(
    constraints: useConstraints ? BoxConstraints.expand(height: 36) : null,
    filled: true,
    fillColor: AppStyles.grey1.withAlpha(25),
    contentPadding: const EdgeInsets.symmetric(
      vertical: 12,
      horizontal: 12,
    ),
    border: OutlineInputBorder(
      borderRadius: BorderRadius.circular(8.0),
      borderSide: BorderSide.none,
    ),
  );
}