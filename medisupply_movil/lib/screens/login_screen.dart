import 'package:flutter/material.dart';
import 'package:medisupply_movil/styles/styles.dart';
import 'package:medisupply_movil/widgets/widgets.dart';
import 'package:provider/provider.dart';
import '../state/app_state.dart';
import '../view_types.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailCtrl = TextEditingController();
  final _passwordCtrl = TextEditingController();
  UserType _selectedType = UserType.vendedor;
  bool _showPassword = false;

  @override
  void dispose() {
    _emailCtrl.dispose();
    _passwordCtrl.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    final appState = context.read<AppState>();
    await appState.login(
      email: _emailCtrl.text,
      password: _passwordCtrl.text,
      asType: _selectedType,
    );
  }

  @override
  Widget build(BuildContext context) {
    final appState = context.watch<AppState>();
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;

    return Scaffold(
      body: SafeArea(
        child: Center(
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
                          textTheme: textTheme,
                          titleLabel: 'Bienvenido a MediSupply',
                          subtitleLabel: 'Inicia sesión en tu cuenta de distribución farmacéutica',
                        ),
                        const SizedBox(height: 24),
        
                        Text('Tipo de Usuario', style: textTheme.titleMedium),
                        const SizedBox(height: 8),
        
                        Row(
                          spacing: 12,
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Expanded(
                              child: UserTypeWidget(
                                onTap: () {
                                  setState(() {
                                    _selectedType = UserType.vendedor;
                                  });
                                },
                                selectedType: _selectedType == UserType.vendedor,
                                iconData: AppIcons.user,
                                label: 'Vendedor'
                              ),
                            ),
                            Expanded(
                              child: UserTypeWidget(
                                onTap: () {
                                  setState(() {
                                    _selectedType = UserType.cliente;
                                  });
                                },
                                selectedType: _selectedType == UserType.cliente,
                                iconData: AppIcons.shoppingCart,
                                label: 'Cliente'
                              ),
                            )
                          ]
                        ),
                        const SizedBox(height: 32),
        
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
                        const SizedBox(height: 16),
        
                        Text('Contraseña', style: textTheme.titleMedium),
                        SizedBox(height: 2),
                        AppTextFormField(
                          controller: _passwordCtrl,
                          label: 'Ingresa tu contraseña',
                          prefixIconData: AppIcons.lock,
                          suffixIcon: IconButton(
                            icon: Icon(_showPassword ? AppIcons.eye : AppIcons.eyeOff),
                            onPressed: () => setState(() => _showPassword = !_showPassword),
                          ),
                          obscureText: !_showPassword,
                          validator: (v) {
                            if (v == null || v.isEmpty) return 'Ingresa tu contraseña';
                            if (v.length < 4) return 'Mínimo 4 caracteres';
                            return null;
                          }
                        ),
                        const SizedBox(height: 16),
        
                        // Iniciar sesión
                        ConfirmationButton(
                          isLoading: appState.isLoading,
                          onTap: _submit,
                          idleLabel: 'Iniciar Sesión',
                          onTapLabel: 'Iniciando sesión...',
                        ),
                        const SizedBox(height: 20),
        
                        // Olvidaste contraseña
                        AppClickableText(
                          onTap: () => context.read<AppState>().navigateTo(AppView.forgotPassword),
                          label: '¿Olvidaste tu contraseña?',
                          textTheme: textTheme
                        ),
        
                        // Registrarse
                        if (_selectedType == UserType.cliente) ...[
                          const SizedBox(height: 12),
                          AppClickableText(
                            onTap: () => context.read<AppState>().navigateTo(AppView.register),
                            label: '¿No tienes cuenta? Regístrate aquí',
                            textTheme: textTheme,
                            overrideColor: colorScheme.primary,
                            overrideFontWeight: FontWeight.w600,
                          ),
                        ],
                      ],
                    ),
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