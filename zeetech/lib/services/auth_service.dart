import 'api_service.dart';
import '../models/user_model.dart';

class AuthService {
  final ApiService _apiService = ApiService();

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
      '/auth/register',
      data: {
        'fullName': fullName,
        'email': email,
        'phone': phone,
        'password': password,
        'city': city ?? 'Islamabad',
      },
    );
    return response.data;
  }

  Future<Map<String, dynamic>> login({
    String? email,
    String? phone,
    required String password,
  }) async {
    final response = await _apiService.post(
      '/auth/login',
      data: {'email': email, 'phone': phone, 'password': password},
    );
    return response.data;
  }

  Future<void> verifyOTP({
    required String email,
    required String otpCode,
  }) async {
    await _apiService.post(
      '/auth/otp/verify',
      data: {'email': email, 'otp_code': otpCode},
    );
  }

  Future<void> resendOTP(String email) async {
    await _apiService.post('/auth/otp/send', data: {'email': email});
  }

  Future<void> requestPasswordReset(String email) async {
    await _apiService.post(
      '/auth/password-reset/request',
      data: {'email': email},
    );
  }

  Future<void> resetPassword({
    required String email,
    required String otpCode,
    required String newPassword,
  }) async {
    await _apiService.post(
      '/auth/password-reset/confirm',
      data: {'email': email, 'otp_code': otpCode, 'new_password': newPassword},
    );
  }

  Future<UserModel> updateProfile(
    String token,
    Map<String, dynamic> data,
  ) async {
    final response = await _apiService.put('/auth/profile', data: data);
    return UserModel.fromJson(response.data);
  }
}
