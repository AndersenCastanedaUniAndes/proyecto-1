import 'package:flutter/material.dart';
import 'package:medisupply_movil/styles/styles.dart';

class Loading extends StatelessWidget {
  const Loading({super.key});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: EdgeInsets.all(24.0),
        child: CircularProgressIndicator(
          color: AppStyles.blue3,
        ),
      ),
    );
  }
}
