/// Structured logging service for production-ready apps
import 'package:flutter/foundation.dart';
import '../config/environment.dart';

enum LogLevel { debug, info, warning, error, critical }

class AppLogger {
  static final AppLogger _instance = AppLogger._internal();

  factory AppLogger() {
    return _instance;
  }

  AppLogger._internal();

  static void debug(String message, {Map<String, dynamic>? extra}) {
    _log(LogLevel.debug, message, extra: extra);
  }

  static void info(String message, {Map<String, dynamic>? extra}) {
    _log(LogLevel.info, message, extra: extra);
  }

  static void warning(String message, {Map<String, dynamic>? extra}) {
    _log(LogLevel.warning, message, extra: extra);
  }

  static void error(
    String message, {
    dynamic exception,
    StackTrace? stackTrace,
    Map<String, dynamic>? extra,
  }) {
    _log(
      LogLevel.error,
      message,
      exception: exception,
      stackTrace: stackTrace,
      extra: extra,
    );
  }

  static void critical(
    String message, {
    dynamic exception,
    StackTrace? stackTrace,
    Map<String, dynamic>? extra,
  }) {
    _log(
      LogLevel.critical,
      message,
      exception: exception,
      stackTrace: stackTrace,
      extra: extra,
    );
  }

  static void _log(
    LogLevel level,
    String message, {
    dynamic exception,
    StackTrace? stackTrace,
    Map<String, dynamic>? extra,
  }) {
    // Only log in development/staging
    if (!AppEnvironment.enableLogging) {
      // In production, still report critical errors
      if (level == LogLevel.critical && AppEnvironment.enableCrashReporting) {
        // TODO: Send to crash reporting service (Firebase Crashlytics, Sentry, etc.)
      }
      return;
    }

    final timestamp = DateTime.now().toIso8601String();
    final prefix = '[${level.name.toUpperCase()}] [$timestamp]';

    final buffer = StringBuffer('$prefix $message');

    if (extra != null && extra.isNotEmpty) {
      buffer.write('\nExtra: ${_formatMap(extra)}');
    }

    if (exception != null) {
      buffer.write('\nException: $exception');
    }

    if (stackTrace != null) {
      buffer.write('\nStackTrace:\n$stackTrace');
    }

    if (kDebugMode) {
      print(buffer.toString());
    }
  }

  static String _formatMap(Map<String, dynamic> map) {
    return map.entries.map((e) => '${e.key}: ${_sanitize(e.value)}').join(', ');
  }

  static dynamic _sanitize(dynamic value) {
    if (value is String) {
      // Hide sensitive data
      if (value.contains('password') ||
          value.contains('token') ||
          value.contains('Bearer')) {
        return '***REDACTED***';
      }
    }
    return value;
  }
}
