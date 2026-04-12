# ZeeTech Flutter Integration Guide

This guide shows how to integrate the Flask backend with your Flutter application.

## Table of Contents

- [Setup](#setup)
- [API Client Configuration](#api-client-configuration)
- [Authentication Flow](#authentication-flow)
- [Making API Requests](#making-api-requests)
- [Example Implementations](#example-implementations)
- [Error Handling](#error-handling)
- [Network Configuration](#network-configuration)

## Setup

### Dependencies

Ensure you have these dependencies in `pubspec.yaml`:

```yaml
dependencies:
  dio: ^5.3.0
  get: ^4.6.0
  shared_preferences: ^2.2.0
  uuid: ^4.0.0
```

### Environment Configuration

Create different API base URLs for development vs. production:

```dart
// lib/core/constants/api_constants.dart

class ApiConstants {
  // Development
  static const String apiBaseUrlDev = 'http://localhost:5000/api';
  
  // Production
  static const String apiBaseUrlProd = 'https://api.zeetech.com/api';
  
  // Endpoints
  static const String authRegister = '/auth/register';
  static const String authLogin = '/auth/login';
  static const String authLogout = '/auth/logout';
  static const String authVerify = '/auth/verify';
  static const String authChangePassword = '/auth/change-password';
  
  static const String usersProfile = '/users';
  static const String usersMe = '/users/me';
  static const String usersRatings = '/users/{userId}/ratings';
  
  static const String servicesCategories = '/services/categories';
  static const String servicesSubcategories = '/services/categories/{categoryId}/subcategories';
  
  static const String bookings = '/bookings';
  static const String bookingDetail = '/bookings/{bookingId}';
  static const String bookingStatus = '/bookings/{bookingId}/status';
  
  static const String ratings = '/ratings/bookings/{bookingId}';
  static const String providerRatings = '/ratings/providers/{providerId}';
  
  static const String paymentsCreateIntent = '/payments/create-intent';
  static const String paymentsConfirm = '/payments/confirm';
  static const String paymentsRefund = '/payments/refund';
  
  static const String uploads = '/uploads';
}
```

## API Client Configuration

### Setup Dio with Session Cookies

```dart
// lib/services/api_service.dart

import 'package:dio/dio.dart';
import 'package:get/get.dart';
import '../core/constants/api_constants.dart';

class ApiService {
  late Dio dio;
  static const String _storageKey = 'api_base_url';

  ApiService() {
    _initializeDio();
  }

  void _initializeDio() {
    // Get base URL from shared preferences or use development default
    String baseUrl = ApiConstants.apiBaseUrlDev;
    
    dio = Dio(
      BaseOptions(
        baseUrl: baseUrl,
        connectTimeout: const Duration(seconds: 30),
        receiveTimeout: const Duration(seconds: 30),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        validateStatus: (status) {
          return status != null && status < 500; // Don't throw on 4xx
        },
      ),
    );

    // Add cookie manager for session handling
    dio.interceptors.add(
      CookieManager(
        PersistCookieJar(
          ignoreExpires: true,
          storage: FileStorage("${(await getApplicationDocumentsDirectory()).path}/.cookies/"),
        ),
      ),
    );

    // Add logging interceptor for debugging
    if (kDebugMode) {
      dio.interceptors.add(
        LoggingInterceptor(),
      );
    }
  }

  // Get singleton instance
  static final ApiService _instance = ApiService._internal();

  ApiService._internal();

  factory ApiService() {
    return _instance;
  }
}

// Custom logging interceptor
class LoggingInterceptor extends Interceptor {
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    print('REQUEST: ${options.method} ${options.path}');
    print('Headers: ${options.headers}');
    if (options.data != null) {
      print('Body: ${options.data}');
    }
    handler.next(options);
  }

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    print('RESPONSE: ${response.statusCode}');
    print('Data: ${response.data}');
    handler.next(response);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    print('ERROR: ${err.message}');
    print('Data: ${err.response?.data}');
    handler.next(err);
  }
}
```

## Authentication Flow

### Register User

```dart
// lib/providers/auth_provider.dart

class AuthProvider extends GetxController {
  final ApiService _apiService = Get.find();
  
  var user = Rx<UserModel?>(null);
  var isAuthenticated = false.obs;

  Future<bool> registerUser({
    required String email,
    required String phone,
    required String fullName,
    required String password,
    required String role, // 'customer' or 'provider'
  }) async {
    try {
      final response = await _apiService.dio.post(
        ApiConstants.authRegister,
        data: {
          'email': email,
          'phone': phone,
          'fullName': fullName,
          'password': password,
          'role': role,
        },
      );

      if (response.statusCode == 201) {
        final userData = response.data['data']['user'];
        user.value = UserModel.fromJson(userData);
        isAuthenticated.value = true;
        return true;
      } else {
        Get.snackbar(
          'Error',
          response.data['error'] ?? 'Registration failed',
          snackPosition: SnackPosition.BOTTOM,
        );
        return false;
      }
    } on DioException catch (e) {
      Get.snackbar('Error', 'Network error: ${e.message}');
      return false;
    }
  }

  Future<bool> login({
    required String email,
    required String password,
    bool rememberMe = false,
  }) async {
    try {
      final response = await _apiService.dio.post(
        ApiConstants.authLogin,
        data: {
          'email': email,
          'password': password,
          'rememberMe': rememberMe,
        },
      );

      if (response.statusCode == 200) {
        final userData = response.data['data']['user'];
        user.value = UserModel.fromJson(userData);
        isAuthenticated.value = true;
        
        // Save user locally
        await _saveUserLocally(userData);
        return true;
      } else {
        Get.snackbar('Error', response.data['error'] ?? 'Login failed');
        return false;
      }
    } on DioException catch (e) {
      Get.snackbar('Error', 'Network error: ${e.message}');
      return false;
    }
  }

  Future<bool> logout() async {
    try {
      await _apiService.dio.post(ApiConstants.authLogout);
      user.value = null;
      isAuthenticated.value = false;
      await _clearUserLocally();
      return true;
    } catch (e) {
      Get.snackbar('Error', 'Logout failed');
      return false;
    }
  }

  Future<void> verifySession() async {
    try {
      final response = await _apiService.dio.get(ApiConstants.authVerify);
      
      if (response.statusCode == 200) {
        final userData = response.data['data']['user'];
        user.value = UserModel.fromJson(userData);
        isAuthenticated.value = true;
      } else {
        isAuthenticated.value = false;
      }
    } on DioException {
      isAuthenticated.value = false;
    }
  }

  Future<void> _saveUserLocally(Map<String, dynamic> userData) async {
    // Save to shared preferences or local database
  }

  Future<void> _clearUserLocally() async {
    // Clear local data
  }
}
```

## Making API Requests

### Get Service Categories

```dart
// lib/providers/service_provider.dart

class ServiceProvider extends GetxController {
  final ApiService _apiService = Get.find();
  
  var categories = <ServiceCategory>[].obs;
  var isLoading = false.obs;

  Future<void> fetchCategories({
    String? search,
    int page = 1,
    int limit = 10,
  }) async {
    try {
      isLoading.value = true;
      
      final params = {
        'page': page,
        'limit': limit,
        if (search != null) 'search': search,
      };

      final response = await _apiService.dio.get(
        ApiConstants.servicesCategories,
        queryParameters: params,
      );

      if (response.statusCode == 200) {
        final data = response.data['data']['categories'] as List;
        categories.value = data
            .map((c) => ServiceCategory.fromJson(c))
            .toList();
      }
    } on DioException catch (e) {
      print('Error: ${e.message}');
    } finally {
      isLoading.value = false;
    }
  }

  Future<ServiceCategory?> getCategoryDetail(String categoryId) async {
    try {
      final response = await _apiService.dio.get(
        '${ApiConstants.servicesCategories}/$categoryId',
      );

      if (response.statusCode == 200) {
        return ServiceCategory.fromJson(response.data['data']['category']);
      }
    } on DioException catch (e) {
      print('Error: ${e.message}');
    }
    return null;
  }
}
```

### Create a Booking

```dart
// lib/services/booking_service.dart

class BookingService {
  final ApiService _apiService = Get.find();

  Future<Booking?> createBooking({
    required String subcategoryName,
    required double baseAmount,
    required String preferredDate,
    required String preferredTimeSlot,
    required String address,
    required String city,
    required String area,
    required String problemDescription,
    String? specialInstructions,
    double additionalCharges = 0,
    double discountAmount = 0,
  }) async {
    try {
      final response = await _apiService.dio.post(
        ApiConstants.bookings,
        data: {
          'subcategoryName': subcategoryName,
          'baseAmount': baseAmount,
          'preferredDate': preferredDate,
          'preferredTimeSlot': preferredTimeSlot,
          'location': {
            'address': address,
            'city': city,
            'area': area,
          },
          'problemDescription': problemDescription,
          if (specialInstructions != null)
            'specialInstructions': specialInstructions,
          'additionalCharges': additionalCharges,
          'discountAmount': discountAmount,
        },
      );

      if (response.statusCode == 201) {
        return Booking.fromJson(response.data['data']['booking']);
      } else {
        print('Error: ${response.data['error']}');
      }
    } on DioException catch (e) {
      print('Error: ${e.message}');
    }
    return null;
  }

  Future<List<Booking>?> getBookings({
    String? status,
    int page = 1,
    int limit = 10,
  }) async {
    try {
      final params = {
        'page': page,
        'limit': limit,
        if (status != null) 'status': status,
      };

      final response = await _apiService.dio.get(
        ApiConstants.bookings,
        queryParameters: params,
      );

      if (response.statusCode == 200) {
        final data = response.data['data']['bookings'] as List;
        return data.map((b) => Booking.fromJson(b)).toList();
      }
    } on DioException catch (e) {
      print('Error: ${e.message}');
    }
    return null;
  }

  Future<Booking?> getBookingDetail(String bookingId) async {
    try {
      final response = await _apiService.dio.get(
        '${ApiConstants.bookings}/$bookingId',
      );

      if (response.statusCode == 200) {
        return Booking.fromJson(response.data['data']['booking']);
      }
    } on DioException catch (e) {
      print('Error: ${e.message}');
    }
    return null;
  }

  Future<bool> updateBookingStatus({
    required String bookingId,
    required String status,
  }) async {
    try {
      final response = await _apiService.dio.put(
        '${ApiConstants.bookings}/$bookingId/status',
        data: {'status': status},
      );

      return response.statusCode == 200;
    } on DioException catch (e) {
      print('Error: ${e.message}');
      return false;
    }
  }
}
```

### Payment Integration

```dart
// lib/services/payment_service.dart

class PaymentService {
  final ApiService _apiService = Get.find();

  Future<PaymentIntent?> createPaymentIntent({
    required String bookingId,
    String currency = 'usd',
  }) async {
    try {
      final response = await _apiService.dio.post(
        ApiConstants.paymentsCreateIntent,
        data: {
          'bookingId': bookingId,
          'currency': currency,
        },
      );

      if (response.statusCode == 200) {
        return PaymentIntent.fromJson(response.data['data']);
      }
    } on DioException catch (e) {
      print('Error: ${e.message}');
    }
    return null;
  }

  Future<bool> confirmPayment({
    required String bookingId,
    required String paymentIntentId,
  }) async {
    try {
      final response = await _apiService.dio.post(
        ApiConstants.paymentsConfirm,
        data: {
          'bookingId': bookingId,
          'paymentIntentId': paymentIntentId,
        },
      );

      if (response.statusCode == 200) {
        final data = response.data['data'];
        return data['success'] == true;
      }
    } on DioException catch (e) {
      print('Error: ${e.message}');
    }
    return false;
  }
}
```

### File Upload

```dart
// lib/services/upload_service.dart

class UploadService {
  final ApiService _apiService = Get.find();

  Future<String?> uploadImage(File imageFile) async {
    try {
      final fileName = imageFile.path.split('/').last;
      
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(
          imageFile.path,
          filename: fileName,
        ),
      });

      final response = await _apiService.dio.post(
        ApiConstants.uploads,
        data: formData,
      );

      if (response.statusCode == 201) {
        return response.data['data']['url'];
      }
    } on DioException catch (e) {
      print('Error: ${e.message}');
    }
    return null;
  }

  Future<bool> deleteImage(String filename) async {
    try {
      final response = await _apiService.dio.delete(
        '${ApiConstants.uploads}/$filename',
      );

      return response.statusCode == 200;
    } on DioException catch (e) {
      print('Error: ${e.message}');
      return false;
    }
  }
}
```

## Example Implementations

### Complete Login Screen

```dart
// lib/screens/auth/login_screen.dart

class LoginScreen extends StatefulWidget {
  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final AuthProvider authProvider = Get.find();
  final emailController = TextEditingController();
  final passwordController = TextEditingController();
  bool isLoading = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Login')),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(
              controller: emailController,
              decoration: InputDecoration(
                labelText: 'Email',
                border: OutlineInputBorder(),
              ),
            ),
            SizedBox(height: 16),
            TextField(
              controller: passwordController,
              obscureText: true,
              decoration: InputDecoration(
                labelText: 'Password',
                border: OutlineInputBorder(),
              ),
            ),
            SizedBox(height: 24),
            ElevatedButton(
              onPressed: isLoading ? null : _handleLogin,
              child: isLoading
                  ? CircularProgressIndicator()
                  : Text('Login'),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _handleLogin() async {
    setState(() => isLoading = true);
    
    final success = await authProvider.login(
      email: emailController.text,
      password: passwordController.text,
    );

    setState(() => isLoading = false);

    if (success) {
      Get.offNamed('/home');
    }
  }

  @override
  void dispose() {
    emailController.dispose();
    passwordController.dispose();
    super.dispose();
  }
}
```

### Complete Booking Creation Flow

```dart
// lib/screens/booking/create_booking_screen.dart

class CreateBookingScreen extends StatefulWidget {
  final String categoryId;

  CreateBookingScreen({required this.categoryId});

  @override
  _CreateBookingScreenState createState() => _CreateBookingScreenState();
}

class _CreateBookingScreenState extends State<CreateBookingScreen> {
  final BookingService _bookingService = Get.find();
  final ServiceProvider _serviceProvider = Get.find();
  
  late TextEditingController dateController;
  late TextEditingController addressController;
  late TextEditingController descriptionController;
  
  String? selectedTimeSlot;
  String? selectedSubcategory;
  double baseAmount = 0;

  @override
  void initState() {
    super.initState();
    dateController = TextEditingController();
    addressController = TextEditingController();
    descriptionController = TextEditingController();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Create Booking')),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            // Subcategory selection
            _buildSubcategoryDropdown(),
            SizedBox(height: 16),
            
            // Date picker
            TextField(
              controller: dateController,
              decoration: InputDecoration(
                labelText: 'Preferred Date',
                border: OutlineInputBorder(),
                suffixIcon: Icon(Icons.calendar_today),
              ),
              readOnly: true,
              onTap: _selectDate,
            ),
            SizedBox(height: 16),
            
            // Time slot selection
            _buildTimeSlotDropdown(),
            SizedBox(height: 16),
            
            // Address
            TextField(
              controller: addressController,
              decoration: InputDecoration(
                labelText: 'Address',
                border: OutlineInputBorder(),
              ),
              maxLines: 2,
            ),
            SizedBox(height: 16),
            
            // Problem description
            TextField(
              controller: descriptionController,
              decoration: InputDecoration(
                labelText: 'Problem Description',
                border: OutlineInputBorder(),
              ),
              maxLines: 3,
            ),
            SizedBox(height: 24),
            
            // Create button
            ElevatedButton(
              onPressed: _handleCreateBooking,
              child: Text('Create Booking'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSubcategoryDropdown() {
    return Obx(() {
      final categories = _serviceProvider.categories;
      final allSubcategories = categories
          .firstWhere(
            (c) => c.id == widget.categoryId,
            orElse: () => ServiceCategory(),
          )
          .subcategories ??
          [];

      return DropdownButton<String>(
        value: selectedSubcategory,
        hint: Text('Select Service'),
        isExpanded: true,
        items: allSubcategories.map((subcat) {
          return DropdownMenuItem(
            value: subcat.name,
            child: Text(subcat.name ?? ''),
          );
        }).toList(),
        onChanged: (value) {
          setState(() {
            selectedSubcategory = value;
            final subcat = allSubcategories.firstWhere(
              (s) => s.name == value,
              orElse: () => ServiceSubCategory(),
            );
            baseAmount = double.tryParse(subcat.basePrice?.toString() ?? '0') ?? 0;
          });
        },
      );
    });
  }

  Widget _buildTimeSlotDropdown() {
    final timeSlots = [
      '08:00-09:00',
      '09:00-10:00',
      '10:00-11:00',
      '14:00-15:00',
      '15:00-16:00',
    ];

    return DropdownButton<String>(
      value: selectedTimeSlot,
      hint: Text('Select Time Slot'),
      isExpanded: true,
      items: timeSlots.map((slot) {
        return DropdownMenuItem(value: slot, child: Text(slot));
      }).toList(),
      onChanged: (value) => setState(() => selectedTimeSlot = value),
    );
  }

  Future<void> _selectDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: DateTime.now().add(Duration(days: 1)),
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(Duration(days: 30)),
    );

    if (picked != null) {
      setState(() {
        dateController.text = picked.toString().split(' ')[0];
      });
    }
  }

  Future<void> _handleCreateBooking() async {
    if (selectedSubcategory == null ||
        dateController.text.isEmpty ||
        selectedTimeSlot == null ||
        addressController.text.isEmpty) {
      Get.snackbar('Error', 'Please fill all fields');
      return;
    }

    final booking = await _bookingService.createBooking(
      subcategoryName: selectedSubcategory!,
      baseAmount: baseAmount,
      preferredDate: dateController.text,
      preferredTimeSlot: selectedTimeSlot!,
      address: addressController.text,
      city: 'Karachi',
      area: 'Downtown',
      problemDescription: descriptionController.text,
    );

    if (booking != null) {
      Get.snackbar('Success', 'Booking created successfully');
      Get.back(result: booking);
    }
  }

  @override
  void dispose() {
    dateController.dispose();
    addressController.dispose();
    descriptionController.dispose();
    super.dispose();
  }
}
```

## Error Handling

### Centralized Error Handler

```dart
// lib/services/error_handler.dart

class ErrorHandler {
  static String getErrorMessage(dynamic error) {
    if (error is DioException) {
      switch (error.type) {
        case DioExceptionType.connectionTimeout:
          return 'Connection timeout. Please try again.';
        case DioExceptionType.sendTimeout:
          return 'Request timeout. Please try again.';
        case DioExceptionType.receiveTimeout:
          return 'Response timeout. Please try again.';
        case DioExceptionType.badResponse:
          return _handleResponseError(error.response);
        case DioExceptionType.cancel:
          return 'Request was cancelled';
        default:
          return 'An unexpected error occurred';
      }
    }
    return 'An unexpected error occurred';
  }

  static String _handleResponseError(Response? response) {
    if (response == null) return 'Unknown error';

    final data = response.data;
    if (data is Map<String, dynamic>) {
      // Handle specific error codes
      final errorCode = data['code'] as String? ?? '';
      final errorMessage = data['error'] as String? ?? 'Unknown error';

      switch (errorCode) {
        case 'VALIDATION_ERROR':
          return 'Invalid input: $errorMessage';
        case 'NOT_FOUND':
          return 'Resource not found';
        case 'UNAUTHORIZED':
          return 'Please login first';
        case 'FORBIDDEN':
          return 'You do not have permission';
        case 'CONFLICT':
          return errorMessage;
        default:
          return errorMessage;
      }
    }

    return 'HTTP ${response.statusCode}: ${response.statusMessage}';
  }
}

// Usage in providers
Future<bool> login({required String email, required String password}) async {
  try {
    // ... api call
  } catch (e) {
    final errorMessage = ErrorHandler.getErrorMessage(e);
    Get.snackbar('Error', errorMessage);
    return false;
  }
}
```

## Network Configuration

### Handle Network Changes

```dart
// lib/services/connectivity_service.dart

class ConnectivityService extends GetxService {
  final connectivity = Connectivity();
  late StreamSubscription<ConnectivityResult> subscription;
  
  var hasConnection = true.obs;

  @override
  void onInit() {
    super.onInit();
    _checkConnection();
    _listenToConnectivityChanges();
  }

  Future<void> _checkConnection() async {
    final result = await connectivity.checkConnectivity();
    hasConnection.value = result != ConnectivityResult.none;
  }

  void _listenToConnectivityChanges() {
    subscription = connectivity.onConnectivityChanged.listen(
      (ConnectivityResult result) {
        hasConnection.value = result != ConnectivityResult.none;
        
        if (!hasConnection.value) {
          Get.snackbar(
            'Network Error',
            'No internet connection',
            snackPosition: SnackPosition.BOTTOM,
          );
        } else {
          Get.snackbar(
            'Connected',
            'Internet connection restored',
            snackPosition: SnackPosition.BOTTOM,
            duration: Duration(seconds: 2),
          );
        }
      },
    );
  }

  @override
  void onClose() {
    subscription.cancel();
    super.onClose();
  }
}
```

### Initialize Services on App Start

```dart
// lib/main.dart

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize services
  await initServices();
  
  runApp(MyApp());
}

Future<void> initServices() async {
  Get.put(ApiService());
  Get.put(ConnectivityService());
  Get.put(AuthProvider());
  Get.put(ServiceProvider());
  Get.put(BookingService());
  Get.put(PaymentService());
  
  // Verify session on startup
  final authProvider = Get.find<AuthProvider>();
  await authProvider.verifySession();
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return GetMaterialApp(
      title: 'ZeeTech',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
      ),
      home: GetBuilder<AuthProvider>(
        builder: (authProvider) {
          return authProvider.isAuthenticated.value
              ? HomeScreen()
              : LoginScreen();
        },
      ),
    );
  }
}
```

---

**Note:** Replace sample values with your actual API endpoints and ensure proper error handling throughout your application.
