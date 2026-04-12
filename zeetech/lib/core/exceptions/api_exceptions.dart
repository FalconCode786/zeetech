/// Custom exception classes for API errors
class ApiException implements Exception {
  final String message;
  final int? statusCode;
  final dynamic originalError;
  final StackTrace? stackTrace;

  ApiException({
    required this.message,
    this.statusCode,
    this.originalError,
    this.stackTrace,
  });

  @override
  String toString() => message;
}

class NetworkException extends ApiException {
  NetworkException({
    required String message,
    dynamic error,
    StackTrace? stackTrace,
  }) : super(message: message, originalError: error, stackTrace: stackTrace);
}

class TimeoutException extends ApiException {
  TimeoutException({required String message}) : super(message: message);
}

class UnauthorizedException extends ApiException {
  UnauthorizedException({required String message})
    : super(message: message, statusCode: 401);
}

class ValidationException extends ApiException {
  ValidationException({required String message})
    : super(message: message, statusCode: 400);
}

class ServerException extends ApiException {
  ServerException({required String message, int? statusCode})
    : super(message: message, statusCode: statusCode);
}
