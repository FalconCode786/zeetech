class AppConstants {
  // App Info
  static const String appName = 'Zeetech';
  static const String appTagline = 'Your Trusted Service Partner';
  static const String appVersion = '1.0.0';

  // API Configuration
  // For Android Emulator: use 10.0.2.2 (special alias for host machine)
  // For Physical Device: use 192.168.18.69 (your machine's IP on network)
  // For Web/Desktop: use localhost:5000
  static const String baseUrl = ' http://192.168.100.4:5000/api';
  static const int apiTimeout = 3000; // milliseconds

  // Storage Keys
  static const String tokenKey = 'auth_token';
  static const String refreshTokenKey = 'refresh_token';
  static const String userKey = 'user_data';
  static const String onboardingKey = 'onboarding_seen';

  // Supported Cities
  static const List<String> supportedCities = [
    'Islamabad',
    'Rawalpindi',
    'Peshawar',
  ];

  // Time Slots
  static const List<String> timeSlots = [
    '09:00 AM - 11:00 AM',
    '11:00 AM - 01:00 PM',
    '01:00 PM - 03:00 PM',
    '03:00 PM - 05:00 PM',
    '05:00 PM - 07:00 PM',
  ];

  // Animation Durations
  static const int splashDuration = 3000;
  static const int animationDuration = 300;
  static const int pageTransitionDuration = 400;

  // Pagination
  static const int defaultPageSize = 10;

  // OTP Configuration
  static const int otpLength = 6;
  static const int otpResendSeconds = 60;
}
