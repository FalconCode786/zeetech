/// Environment configuration for different deployment targets
enum Environment { development, staging, production }

class AppEnvironment {
  static Environment _environment = Environment.development;

  static Environment get environment => _environment;

  static void setEnvironment(Environment env) {
    _environment = env;
  }

  static String get baseUrl {
    switch (_environment) {
      case Environment.development:
        // For Android Emulator: http://10.0.2.2:5000/api
        // For Physical Device: http://192.168.x.x:5000/api
        // For iOS Simulator: http://localhost:5000/api
        // For Web/Desktop: http://localhost:5000/api
        return const String.fromEnvironment(
          'BASE_URL',
          defaultValue: 'http://192.168.100.4:5000/api',
        );
      case Environment.staging:
        return 'https://staging-api.zeetech.com/api';
      case Environment.production:
        return 'https://api.zeetech.com/api';
    }
  }

  static bool get isDevelopment => _environment == Environment.development;
  static bool get isStaging => _environment == Environment.staging;
  static bool get isProduction => _environment == Environment.production;

  static bool get enableLogging => isDevelopment || isStaging;
  static bool get enableCrashReporting => isProduction;

  static int get connectTimeout => 30000; // milliseconds
  static int get receiveTimeout => 30000;
  static int get maxRetries => isDevelopment ? 1 : 3;
  static Duration get retryDelay => const Duration(milliseconds: 500);
}
