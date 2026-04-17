import 'api_service.dart';
import 'storage_service.dart';
import '../models/user_model.dart';

class AuthService {
  final ApiService _apiService = ApiService();
  final StorageService _storageService = StorageService();

  Future<Map<String, dynamic>> register({
    required String email,
    required String phone,
    required String fullName,
    required String password,
    String? city,
    String? area,
    String? address,
  }) async {
    final response = await _apiService.post(
      '/api/auth/register',
      data: {
        'fullName': fullName,
        'email': email,
        'phone': phone,
        'password': password,
        'city': city ?? 'Islamabad',
      },
    );

    final data = response.data as Map<String, dynamic>;

    // Extract token from nested data structure: { data: { token, user } }
    final tokenData = data['data'] as Map<String, dynamic>?;
    if (tokenData != null) {
      // Store token if returned by backend
      if (tokenData['token'] != null) {
        await _storageService.setToken(tokenData['token'] as String);
      }

      // Also store refresh token if returned
      if (tokenData['refreshToken'] != null) {
        await _storageService.setRefreshToken(
          tokenData['refreshToken'] as String,
        );
      }
    }

    return data;
  }

  Future<Map<String, dynamic>> login({
    String? email,
    String? phone,
    required String password,
  }) async {
    final response = await _apiService.post(
      '/api/auth/login',
      data: {'email': email, 'phone': phone, 'password': password},
    );

    final data = response.data as Map<String, dynamic>;

    // Extract token from nested data structure: { data: { token, user } }
    final tokenData = data['data'] as Map<String, dynamic>?;
    if (tokenData != null) {
      // Store token if returned by backend
      if (tokenData['token'] != null) {
        await _storageService.setToken(tokenData['token'] as String);
      }

      // Also store refresh token if returned
      if (tokenData['refreshToken'] != null) {
        await _storageService.setRefreshToken(
          tokenData['refreshToken'] as String,
        );
      }
    }

    return data;
  }

  Future<void> verifyOTP({
    required String email,
    required String otpCode,
  }) async {
    // OTP verification endpoint not yet implemented in backend
    // await _apiService.post(
    //   '/auth/otp/verify',
    //   data: {'email': email, 'otp_code': otpCode},
    // );
  }

  Future<void> resendOTP(String email) async {
    // OTP resend endpoint not yet implemented in backend
    // await _apiService.post('/auth/otp/send', data: {'email': email});
  }

  Future<void> requestPasswordReset(String email) async {
    // Password reset request endpoint not yet implemented in backend
    // await _apiService.post(
    //   '/auth/password-reset/request',
    //   data: {'email': email},
    // );
  }

  Future<void> resetPassword({
    required String email,
    required String otpCode,
    required String newPassword,
  }) async {
    // Password reset confirm endpoint not yet implemented in backend
    // await _apiService.post(
    //   '/auth/password-reset/confirm',
    //   data: {'email': email, 'otp_code': otpCode, 'new_password': newPassword},
    // );
  }

  Future<UserModel> updateProfile(Map<String, dynamic> data) async {
    final response = await _apiService.put('users/profile', data: data);
    return UserModel.fromJson(response.data as Map<String, dynamic>);
  }
}
