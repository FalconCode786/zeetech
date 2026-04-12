import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../core/constants/app_constants.dart';

class StorageService {
  static final StorageService _instance = StorageService._internal();
  factory StorageService() => _instance;
  StorageService._internal();

  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage();
  SharedPreferences? _prefs;

  Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
  }

  // Token Methods
  Future<void> setToken(String token) async {
    await _secureStorage.write(key: AppConstants.tokenKey, value: token);
  }

  Future<String?> getToken() async {
    return await _secureStorage.read(key: AppConstants.tokenKey);
  }

  Future<void> deleteToken() async {
    await _secureStorage.delete(key: AppConstants.tokenKey);
  }

  // Refresh Token Methods
  Future<void> setRefreshToken(String token) async {
    await _secureStorage.write(key: AppConstants.refreshTokenKey, value: token);
  }

  Future<String?> getRefreshToken() async {
    return await _secureStorage.read(key: AppConstants.refreshTokenKey);
  }

  // User Data Methods
  Future<void> setUser(Map<String, dynamic> userData) async {
    await _prefs?.setString(AppConstants.userKey, jsonEncode(userData));
  }

  Future<Map<String, dynamic>?> getUser() async {
    final userStr = _prefs?.getString(AppConstants.userKey);
    if (userStr != null) {
      return jsonDecode(userStr);
    }
    return null;
  }

  Future<void> deleteUser() async {
    await _prefs?.remove(AppConstants.userKey);
  }

  // Onboarding
  Future<void> setOnboardingSeen(bool value) async {
    await _prefs?.setBool(AppConstants.onboardingKey, value);
  }

  Future<bool> getOnboardingSeen() async {
    return _prefs?.getBool(AppConstants.onboardingKey) ?? false;
  }

  // Clear All
  Future<void> clearAll() async {
    await _secureStorage.deleteAll();
    await _prefs?.clear();
  }
}
