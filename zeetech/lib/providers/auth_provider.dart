import 'package:flutter/material.dart';
import '../models/user_model.dart';
import '../services/auth_service.dart';
import '../services/storage_service.dart';

class AuthProvider extends ChangeNotifier {
  final AuthService _authService = AuthService();
  final StorageService _storageService = StorageService();

  UserModel? _user;
  bool _isLoading = false;
  String? _error;

  UserModel? get user => _user;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get isAuthenticated => _user != null;

  AuthProvider() {
    _loadUserFromStorage();
  }

  Future<void> _loadUserFromStorage() async {
    final userData = await _storageService.getUser();
    if (userData != null) {
      _user = UserModel.fromJson(userData);
    }
    notifyListeners();
  }

  void _setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }

  void _setError(String? value) {
    _error = value;
    notifyListeners();
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }

  Future<bool> register({
    required String email,
    required String phone,
    required String fullName,
    required String password,
    String? city,
    String? area,
    String? address,
  }) async {
    try {
      _setLoading(true);
      _setError(null);

      final response = await _authService.register(
        email: email,
        phone: phone,
        fullName: fullName,
        password: password,
        city: city,
        area: area,
        address: address,
      );

      print('[AuthProvider] Register response: $response');

      // Backend returns: { data: { user } }
      final userData = response['data']?['user'];

      if (userData != null) {
        _user = UserModel.fromJson(userData);
        await _storageService.setUser(_user!.toJson());

        _setLoading(false);
        return true;
      }

      _setLoading(false);
      return false;
    } catch (e) {
      _setLoading(false);
      _setError(e.toString());
      print('[AuthProvider] Register error: $e');
      return false;
    }
  }

  Future<bool> login({
    String? email,
    String? phone,
    required String password,
  }) async {
    try {
      _setLoading(true);
      _setError(null);

      final response = await _authService.login(
        email: email,
        phone: phone,
        password: password,
      );

      print('[AuthProvider] Login response: $response');

      // Backend returns: { data: { user } }
      final userData = response['data']?['user'];
      if (userData == null) {
        throw Exception('No user data in response');
      }
      _user = UserModel.fromJson(userData);

      await _storageService.setUser(_user!.toJson());

      _setLoading(false);
      notifyListeners();
      return true;
    } catch (e) {
      _setLoading(false);
      _setError(e.toString());
      print('[AuthProvider] Login error: $e');
      return false;
    }
  }

  Future<bool> verifyOTP({
    required String email,
    required String otpCode,
  }) async {
    try {
      _setLoading(true);
      _setError(null);

      await _authService.verifyOTP(email: email, otpCode: otpCode);

      _setLoading(false);
      return true;
    } catch (e) {
      _setLoading(false);
      _setError(e.toString());
      return false;
    }
  }

  Future<bool> resendOTP(String email) async {
    try {
      _setLoading(true);
      _setError(null);

      await _authService.resendOTP(email);

      _setLoading(false);
      return true;
    } catch (e) {
      _setLoading(false);
      _setError(e.toString());
      return false;
    }
  }

  Future<bool> requestPasswordReset(String email) async {
    try {
      _setLoading(true);
      _setError(null);

      await _authService.requestPasswordReset(email);

      _setLoading(false);
      return true;
    } catch (e) {
      _setLoading(false);
      _setError(e.toString());
      return false;
    }
  }

  Future<bool> resetPassword({
    required String email,
    required String otpCode,
    required String newPassword,
  }) async {
    try {
      _setLoading(true);
      _setError(null);

      await _authService.resetPassword(
        email: email,
        otpCode: otpCode,
        newPassword: newPassword,
      );

      _setLoading(false);
      return true;
    } catch (e) {
      _setLoading(false);
      _setError(e.toString());
      return false;
    }
  }

  Future<void> logout() async {
    _user = null;
    await _storageService.clearAll();
    notifyListeners();
  }

  Future<bool> updateProfile(Map<String, dynamic> data) async {
    try {
      _setLoading(true);
      _setError(null);

      final updatedUser = await _authService.updateProfile(data);
      _user = updatedUser;
      await _storageService.setUser(_user!.toJson());

      _setLoading(false);
      notifyListeners();
      return true;
    } catch (e) {
      _setLoading(false);
      _setError(e.toString());
      return false;
    }
  }

  // DELETE User Account
  Future<bool> deleteAccount() async {
    try {
      _setLoading(true);
      _setError(null);

      // await _authService.deleteAccount(_token!); // if endpoint available
      await logout();

      _setLoading(false);
      return true;
    } catch (e) {
      _setLoading(false);
      _setError(e.toString());
      return false;
    }
  }
}
