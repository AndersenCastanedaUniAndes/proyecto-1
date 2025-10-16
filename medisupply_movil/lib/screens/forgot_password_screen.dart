import 'package:flutter/material.dart';
import 'package:medisupply_movil/styles/styles.dart';
import 'package:medisupply_movil/widgets/widgets.dart';
import 'package:provider/provider.dart';
import '../state/app_state.dart';
import '../view_types.dart';

class ForgotPasswordScreen extends StatefulWidget {
  const ForgotPasswordScreen({super.key});

  @override
  State<ForgotPasswordScreen> createState() => _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends State<ForgotPasswordScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailCtrl = TextEditingController();
  bool _isLoading = false;
  bool _emailSent = false;

  @override
  void dispose() {
    _emailCtrl.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _isLoading = true);
    await Future.delayed(const Duration(seconds: 2));
    setState(() {
      _isLoading = false;
      _emailSent = true;
    });
  }

  void _sendAnother() {
    setState(() {
      _emailSent = false;
      _emailCtrl.clear();
    });
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;

    if (_emailSent) {
      return Scaffold(
        body: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(12),
            child: Container(
              decoration: AppStyles.decoration.copyWith(color: Colors.white),
              child: Padding(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Container(
                      height: 64,
                      width: 64,
                      decoration: BoxDecoration(
                        color: const Color(0xffdcfce7),
                        shape: BoxShape.circle,
                      ),
                      child: Icon(AppIcons.circleCheck, size: 32, color: AppStyles.green1),
                    ),
                    const SizedBox(height: 20),

                    AppTitleAndSubtitle(
                      textTheme: textTheme,
                      titleLabel: 'Correo Enviado',
                      subtitleLabel: 'Hemos enviado las instrucciones de recuperación a tu correo',
                    ),
                    const SizedBox(height: 24),

                    Container(
                      width: double.infinity,
                      decoration: BoxDecoration(
                        color: Color(0xffeff6ff),
                        border: Border.all(color: Color(0xffbedbff)),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      padding: const EdgeInsets.all(16),
                      child: Text(
                        'Revisa tu bandeja de entrada y la carpeta de spam. El correo puede tardar algunos minutos en llegar.',
                        style: Theme.of(context)
                            .textTheme
                            .bodySmall
                            ?.copyWith(color: Color(0xff193cb8)),
                      ),
                    ),
                    const SizedBox(height: 14),

                    OutlinedButton(
                      onPressed: _sendAnother,
                      style: ButtonStyle(
                        shape: WidgetStateProperty.all<RoundedRectangleBorder>(
                          RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8.0),
                          ),
                        ),
                      ),
                      child: Text('Enviar otro correo', style: textTheme.bodySmall,),
                    ),
                    const SizedBox(height: 20),

                    AppClickableText(
                        onTap: () => context.read<AppState>().navigateTo(AppView.login),
                        icon: AppIcons.arrowLeft,
                        label: 'Volver al inicio de sesión',
                        textTheme: textTheme,
                      ),
                  ],
                ),
              ),
            ),
          ),
        ),
      );
    }

    return Scaffold(
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(12),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 420),
            child: Container(
              decoration: AppStyles.decoration.copyWith(color: Colors.white),
              child: Padding(
                padding: const EdgeInsets.all(24.0),
                child: Form(
                  key: _formKey,
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      AppIcon(colorScheme: colorScheme),
                      const SizedBox(height: 26),

                      AppTitleAndSubtitle(
                        titleLabel: 'Recuperar Contraseña',
                        subtitleLabel: 'Ingresa tu correo y te enviaremos\ninstrucciones para restablecer tu contraseña',
                        textTheme: textTheme
                      ),
                      const SizedBox(height: 24),

                      Text('Correo Electrónico', style: textTheme.titleMedium),
                      SizedBox(height: 2),
                      AppTextFormField(
                        controller: _emailCtrl,
                        prefixIconData: AppIcons.mail,
                        label: 'Ingresa tu correo electrónico',
                        validator: (v) {
                          if (v == null || v.isEmpty) return 'Ingresa tu correo';
                          if (!v.contains('@')) return 'Correo inválido';
                          return null;
                        },
                      ),
                      const SizedBox(height: 24),

                      ConfirmationButton(
                        isLoading: _isLoading,
                        onTap: _submit,
                        idleLabel: 'Enviar Instrucciones',
                        onTapLabel: 'Enviando...',
                      ),
                      const SizedBox(height: 20),

                      AppClickableText(
                        onTap: () => context.read<AppState>().navigateTo(AppView.login),
                        icon: AppIcons.arrowLeft,
                        label: 'Volver al inicio de sesión',
                        textTheme: textTheme,
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}