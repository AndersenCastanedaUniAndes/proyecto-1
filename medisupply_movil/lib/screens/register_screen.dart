import 'package:flutter/material.dart';
import 'package:medisupply_movil/styles/styles.dart';
import 'package:medisupply_movil/widgets/widgets.dart';
import 'package:medisupply_movil/state/app_state.dart';
import 'package:medisupply_movil/view_types.dart';
import 'package:medisupply_movil/utils/utils.dart';
import 'package:provider/provider.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _empresaCtrl = TextEditingController();
  final _contactoCtrl = TextEditingController();
  final _correoCtrl = TextEditingController();
  final _telefonoCtrl = TextEditingController();
  final _direccionCtrl = TextEditingController();
  final _ciudadCtrl = TextEditingController();
  final _passwordCtrl = TextEditingController();
  final _confirmPasswordCtrl = TextEditingController();

  bool _showPassword = false;
  bool _showConfirmPassword = false;
  bool _isLoading = false;

  @override
  void dispose() {
    _empresaCtrl.dispose();
    _contactoCtrl.dispose();
    _correoCtrl.dispose();
    _telefonoCtrl.dispose();
    _direccionCtrl.dispose();
    _ciudadCtrl.dispose();
    _passwordCtrl.dispose();
    _confirmPasswordCtrl.dispose();
    super.dispose();
  }

  String? _required(String? v, {String label = 'Este campo'}) {
    if (v == null || v.trim().isEmpty) return '$label es requerido';
    return null;
  }

  String? _emailValidator(String? v) {
    final base = _required(v, label: 'El correo electrónico');
    if (base != null) return base;
    final email = v!.trim();
    final regex = RegExp(r'^\S+@\S+\.\S+$');
    if (!regex.hasMatch(email)) return 'El correo electrónico no es válido';
    return null;
  }

  String? _passwordValidator(String? v) {
    final base = _required(v, label: 'La contraseña');
    if (base != null) return base;
    if (v!.length < 6) return 'La contraseña debe tener al menos 6 caracteres';
    return null;
  }

  String? _confirmPasswordValidator(String? v) {
    final base = _required(v, label: 'Confirmar contraseña');
    if (base != null) return base;
    if (v != _passwordCtrl.text) return 'Las contraseñas no coinciden';
    return null;
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() => _isLoading = true);

    var response = await register({
      'empresa': _empresaCtrl.text.trim(),
      'nombre_usuario': _contactoCtrl.text.trim(),
      'email': _correoCtrl.text.trim(),
      'contrasena': _passwordCtrl.text.trim(),
      'telefono': _telefonoCtrl.text.trim(),
      'direccion': _direccionCtrl.text.trim(),
      'ciudad': _ciudadCtrl.text.trim(),
    });

    setState(() => _isLoading = false);

    if (response.statusCode != 200) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error ${response.statusCode}: ${response.body}'),
        ),
      );
      return;
    }

    final appState = context.read<AppState>();
    appState.registerNewClient(username: _contactoCtrl.text.trim());
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;

    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(12),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 480),
              child: Container(
                decoration: AppStyles.decoration.copyWith(color: Colors.white),
                child: Padding(
                  padding: const EdgeInsets.all(24.0),
                  child: Form(
                    key: _formKey,
                    autovalidateMode: AutovalidateMode.onUserInteraction,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        AppIcon(colorScheme: colorScheme),
                        const SizedBox(height: 26),

                        AppTitleAndSubtitle(
                          textTheme: textTheme,
                          titleLabel: 'Crear Cuenta Cliente',
                          subtitleLabel: 'Regístrate para acceder a nuestros servicios farmacéuticos',
                        ),
                        const SizedBox(height: 24),

                        Text('Nombre de la Empresa', style: textTheme.titleMedium),
                        SizedBox(height: 2),
                        AppTextFormField(
                          controller: _empresaCtrl,
                          prefixIconData: AppIcons.building,
                          label: 'Nombre de tu farmacia o empresa',
                          validator: (v) => _required(v, label: 'El nombre de la empresa'),
                        ),
                        const SizedBox(height: 14),

                        Text('Nombre de Contacto', style: textTheme.titleMedium),
                        SizedBox(height: 2),
                        AppTextFormField(
                          controller: _contactoCtrl,
                          prefixIconData: AppIcons.user,
                          label:'Tu nombre completo',
                          validator: (v) => _required(v, label: 'El nombre de la empresa'),
                        ),
                        const SizedBox(height: 14),

                        Text('Correo Electrónico', style: textTheme.titleMedium),
                        SizedBox(height: 2),
                        AppTextFormField(
                          controller: _correoCtrl,
                          prefixIconData: AppIcons.mail,
                          label:'correo@empresa.com',
                          keyboardType: TextInputType.emailAddress,
                          validator: _emailValidator,
                        ),
                        const SizedBox(height: 14),

                        Text('Teléfono', style: textTheme.titleMedium),
                        SizedBox(height: 2),
                        AppTextFormField(
                          controller: _telefonoCtrl,
                          prefixIconData: AppIcons.phone,
                          label:'+57 1 234-5678',
                          keyboardType: TextInputType.phone,
                          validator: (v) => _required(v, label: 'El teléfono'),
                        ),
                        const SizedBox(height: 14),

                        Text('Dirección', style: textTheme.titleMedium),
                        SizedBox(height: 2),
                        AppTextFormField(
                          controller: _direccionCtrl,
                          prefixIconData: AppIcons.pin,
                          label:'Dirección completa',
                          validator: (v) => _required(v, label: 'La dirección'),
                        ),
                        const SizedBox(height: 14),

                        Text('Ciudad', style: textTheme.titleMedium),
                        SizedBox(height: 2),
                        AppTextFormField(
                          controller: _ciudadCtrl,
                          label:'Ciudad',
                          validator: (v) => _required(v, label: 'La ciudad'),
                        ),
                        const SizedBox(height: 14),

                        Text('Contraseña', style: textTheme.titleMedium),
                        SizedBox(height: 2),
                        AppTextFormField(
                          controller: _passwordCtrl,
                          label: 'Mínimo 6 caracteres',
                          prefixIconData: AppIcons.lock,
                          suffixIcon: IconButton(
                            icon: Icon(_showPassword ? AppIcons.eyeOff : AppIcons.eye),
                            onPressed: () => setState(() => _showPassword = !_showPassword),
                          ),
                          obscureText: !_showPassword,
                          validator: _passwordValidator,
                        ),
                        const SizedBox(height: 16),

                        Text('Confirmar Contraseña', style: textTheme.titleMedium),
                        SizedBox(height: 2),
                        AppTextFormField(
                          controller: _confirmPasswordCtrl,
                          label: 'Confirma tu contraseña',
                          prefixIconData: AppIcons.lock,
                          suffixIcon: IconButton(
                            icon: Icon(_showConfirmPassword ? AppIcons.eyeOff : AppIcons.eye),
                            onPressed: () => setState(() => _showConfirmPassword = !_showConfirmPassword),
                          ),
                          obscureText: !_showConfirmPassword,
                          validator: _confirmPasswordValidator,
                        ),
                        const SizedBox(height: 16),

                        ConfirmationButton(
                          isLoading: _isLoading,
                          onTap: _submit,
                          idleLabel: 'Crear Cuenta',
                          onTapLabel: 'Creando cuenta...',
                        ),
                        const SizedBox(height: 20),

                        AppClickableText(
                          onTap: () => context.read<AppState>().navigateTo(AppView.login),
                          label: '¿Ya tienes cuenta? Inicia sesión aquí',
                          textTheme: textTheme
                        ),
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