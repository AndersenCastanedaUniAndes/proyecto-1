import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:medisupply_movil/view_types.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

Future<http.Response> register(Object body) async {
  final userServiceUrl = dotenv.env['USER_SERVICE_URL'];
  final url = Uri.parse('$userServiceUrl/users/clients');

  final response = await http.post(
    url,
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode(body),
  );

  return response;
}

Future<http.Response> login(
  String email,
  String password,
  UserType userType) async {
  final userServiceUrl = dotenv.env['USER_SERVICE_URL'];

  final endpoint = switch (userType) {
    UserType.vendedor => '/token',
    UserType.cliente => '/clients/login',
  };

  final url = Uri.parse('$userServiceUrl$endpoint');

  final response = await http.post(
    url,
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: Uri(queryParameters: {
      'username': email,
      'password': password,
    }).query,
  );

  return response;
}

Future<http.Response> getSailes(String id, String token) async {
  final userServiceUrl = dotenv.env['USER_SERVICE_URL'];
  final url = Uri.parse('$userServiceUrl/vendedor/$id');

  final response = await http.get(
    url,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token'
    },
  );

  return response;
}

Future<http.Response> getClientsSmall(String id, String token) async {
  final userServiceUrl = dotenv.env['USER_SERVICE_URL'];
  final url = Uri.parse('$userServiceUrl/clients-small/$id');

  final response = await http.get(
    url,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token'
    },
  );

  await Future.delayed(const Duration(seconds: 1));

  return response;
}

Future<http.Response> getClients(String id, String token) async {
  final userServiceUrl = dotenv.env['USER_SERVICE_URL'];
  final url = Uri.parse('$userServiceUrl/clients/$id');

  final response = await http.get(
    url,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token'
    },
  );

  await Future.delayed(const Duration(seconds: 1));

  return response;
}

Future<http.Response> getVisits(String id, String token) async {
  final informesServiceUrl = dotenv.env['INFORMES_SERVICE_URL'];
  final visitas = Uri.parse('$informesServiceUrl/ventas/visitas/vendedor/$id');

  final response = await http.get(
    visitas,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token'
    },
  );

  await Future.delayed(const Duration(seconds: 1));

  return response;
}

