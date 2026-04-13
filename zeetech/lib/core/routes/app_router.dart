import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../screens/splash/splash_screen.dart';
import '../../screens/onboarding/onboarding_screen.dart';
import '../../screens/auth/login_screen.dart';
import '../../screens/auth/signup_screen.dart';
import '../../screens/auth/otp_verification_screen.dart';
import '../../screens/auth/forgot_password_screen.dart';
import '../../screens/home/home_screen.dart';
import '../../screens/services/service_categories_screen.dart';
import '../../screens/services/service_subcategories_screen.dart';
import '../../screens/services/service_detail_screen.dart';
import '../../screens/booking/booking_screen.dart';
import '../../screens/booking/booking_confirmation_screen.dart';
import '../../screens/booking/my_bookings_screen.dart';
import '../../screens/booking/booking_detail_screen.dart';
import '../../screens/profile/profile_screen.dart';
import '../../screens/profile/edit_profile_screen.dart';
import '../../screens/main/main_screen.dart';
import '../../screens/provider/provider_dashboard_screen.dart';
import '../../screens/provider/provider_services_screen.dart';
import '../../screens/provider/provider_bookings_screen.dart';

class AppRoutes {
  static const String splash = '/';
  static const String onboarding = '/onboarding';
  static const String login = '/login';
  static const String signup = '/signup';
  static const String otpVerification = '/otp-verification';
  static const String forgotPassword = '/forgot-password';
  static const String main = '/main';
  static const String home = '/home';
  static const String serviceCategories = '/services';
  static const String serviceSubcategories = '/services/subcategories';
  static const String serviceDetail = '/services/detail';
  static const String booking = '/booking';
  static const String bookingConfirmation = '/booking/confirmation';
  static const String myBookings = '/my-bookings';
  static const String bookingDetail = '/booking/detail';
  static const String profile = '/profile';
  static const String editProfile = '/profile/edit';
  static const String providerDashboard = '/provider';
  static const String providerServices = '/provider/services';
  static const String providerBookings = '/provider/bookings';
  static const String providerBookingDetail = '/provider/bookings/detail';
}

class AppRouter {
  static final _rootNavigatorKey = GlobalKey<NavigatorState>();
  static final _shellNavigatorKey = GlobalKey<NavigatorState>();

  static final router = GoRouter(
    navigatorKey: _rootNavigatorKey,
    initialLocation: AppRoutes.splash,
    debugLogDiagnostics: true,
    routes: [
      // Splash
      GoRoute(
        path: AppRoutes.splash,
        builder: (context, state) => const SplashScreen(),
      ),

      // Onboarding
      GoRoute(
        path: AppRoutes.onboarding,
        builder: (context, state) => const OnboardingScreen(),
      ),

      // Auth Routes
      GoRoute(
        path: AppRoutes.login,
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: AppRoutes.signup,
        builder: (context, state) => const SignupScreen(),
      ),
      GoRoute(
        path: AppRoutes.otpVerification,
        builder: (context, state) {
          final extra = state.extra as Map<String, dynamic>?;
          return OTPVerificationScreen(
            email: extra?['email'] ?? '',
            purpose: extra?['purpose'] ?? 'verification',
          );
        },
      ),
      GoRoute(
        path: AppRoutes.forgotPassword,
        builder: (context, state) => const ForgotPasswordScreen(),
      ),

      // Main Shell Route with Bottom Navigation
      ShellRoute(
        navigatorKey: _shellNavigatorKey,
        builder: (context, state, child) => MainScreen(child: child),
        routes: [
          GoRoute(
            path: AppRoutes.home,
            builder: (context, state) => const HomeScreen(),
          ),
          GoRoute(
            path: AppRoutes.serviceCategories,
            builder: (context, state) => const ServiceCategoriesScreen(),
          ),
          GoRoute(
            path: AppRoutes.myBookings,
            builder: (context, state) => const MyBookingsScreen(),
          ),
          GoRoute(
            path: AppRoutes.profile,
            builder: (context, state) => const ProfileScreen(),
          ),
        ],
      ),

      // Service Routes
      GoRoute(
        path: AppRoutes.serviceSubcategories,
        builder: (context, state) {
          final extra = state.extra as Map<String, dynamic>?;
          return ServiceSubcategoriesScreen(
            categoryId: extra?['categoryId'] ?? 0,
            categoryName: extra?['categoryName'] ?? '',
          );
        },
      ),
      GoRoute(
        path: AppRoutes.serviceDetail,
        builder: (context, state) {
          final extra = state.extra as Map<String, dynamic>?;
          return ServiceDetailScreen(
            subcategoryId: extra?['subcategoryId'] ?? 0,
          );
        },
      ),

      // Booking Routes
      GoRoute(
        path: AppRoutes.booking,
        builder: (context, state) {
          final extra = state.extra as Map<String, dynamic>?;
          return BookingScreen(
            subcategoryId: extra?['subcategoryId'] ?? 0,
            subcategoryName: extra?['subcategoryName'] ?? '',
            basePrice: extra?['basePrice'] ?? 0.0,
          );
        },
      ),
      GoRoute(
        path: AppRoutes.bookingConfirmation,
        builder: (context, state) {
          final extra = state.extra as Map<String, dynamic>?;
          return BookingConfirmationScreen(
            bookingNumber: extra?['bookingNumber'] ?? '',
          );
        },
      ),
      GoRoute(
        path: AppRoutes.bookingDetail,
        builder: (context, state) {
          final extra = state.extra as Map<String, dynamic>?;
          return BookingDetailScreen(bookingId: extra?['bookingId'] ?? 0);
        },
      ),

      // Profile Routes
      GoRoute(
        path: AppRoutes.editProfile,
        builder: (context, state) => const EditProfileScreen(),
      ),

      // Provider Routes
      GoRoute(
        path: AppRoutes.providerDashboard,
        builder: (context, state) => const ProviderDashboardScreen(),
      ),
      GoRoute(
        path: AppRoutes.providerServices,
        builder: (context, state) => const ProviderServicesScreen(),
      ),
      GoRoute(
        path: AppRoutes.providerBookings,
        builder: (context, state) => const ProviderBookingsScreen(),
      ),
      GoRoute(
        path: '${AppRoutes.providerBookingDetail}/:bookingId',
        builder: (context, state) {
          return const ProviderBookingsScreen();
        },
      ),
    ],
  );
}
