import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:pin_code_fields/pin_code_fields.dart';
import 'package:provider/provider.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_constants.dart';
import '../../core/routes/app_router.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/custom_button.dart';
import '../../widgets/loading_overlay.dart';

class OTPVerificationScreen extends StatefulWidget {
  final String email;
  final String purpose;

  const OTPVerificationScreen({
    super.key,
    required this.email,
    this.purpose = 'verification',
  });

  @override
  State<OTPVerificationScreen> createState() => _OTPVerificationScreenState();
}

class _OTPVerificationScreenState extends State<OTPVerificationScreen> {
  final _otpController = PinInputController();
  final _formKey = GlobalKey<FormState>();

  int _resendSeconds = AppConstants.otpResendSeconds;
  Timer? _timer;
  bool _canResend = false;

  @override
  void initState() {
    super.initState();
    _startResendTimer();
  }

  @override
  void dispose() {
    _otpController.dispose();
    _timer?.cancel();
    super.dispose();
  }

  void _startResendTimer() {
    _canResend = false;
    _resendSeconds = AppConstants.otpResendSeconds;

    _timer?.cancel();
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_resendSeconds > 0) {
        setState(() {
          _resendSeconds--;
        });
      } else {
        setState(() {
          _canResend = true;
        });
        timer.cancel();
      }
    });
  }

  Future<void> _verifyOTP() async {
    if (!_formKey.currentState!.validate()) return;

    final authProvider = context.read<AuthProvider>();

    if (widget.purpose == 'verification') {
      final success = await authProvider.verifyOTP(
        email: widget.email,
        otpCode: _otpController.text,
      );

      if (success && mounted) {
        context.go(AppRoutes.login);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Email verified successfully! Please login.'),
            backgroundColor: AppColors.success,
          ),
        );
      }
    } else {
      // For password reset, navigate to reset screen
      context.go(
        AppRoutes.forgotPassword,
        extra: {'email': widget.email, 'otpCode': _otpController.text},
      );
    }
  }

  Future<void> _resendOTP() async {
    if (!_canResend) return;

    final authProvider = context.read<AuthProvider>();
    final success = await authProvider.resendOTP(widget.email);

    if (success) {
      _startResendTimer();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('OTP resent successfully!'),
            backgroundColor: AppColors.success,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();

    return LoadingOverlay(
      isLoading: authProvider.isLoading,
      child: Scaffold(
        backgroundColor: AppColors.background,
        appBar: AppBar(
          backgroundColor: Colors.transparent,
          elevation: 0,
          leading: IconButton(
            icon: Icon(Icons.arrow_back, color: AppColors.textPrimary),
            onPressed: () => context.pop(),
          ),
        ),
        body: SafeArea(
          child: SingleChildScrollView(
            padding: EdgeInsets.all(24.w),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  // Icon
                  Container(
                    width: 120.w,
                    height: 120.w,
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: AppColors.primaryGradient,
                      ),
                      borderRadius: BorderRadius.circular(30.r),
                    ),
                    child: Icon(Icons.email, size: 60.w, color: Colors.white),
                  ).animate().scale(
                    duration: const Duration(milliseconds: 600),
                  ),

                  SizedBox(height: 32.h),

                  // Title
                  Text(
                    'Verify Your Email',
                    style: TextStyle(
                      fontSize: 28.sp,
                      fontWeight: FontWeight.bold,
                      color: AppColors.textPrimary,
                    ),
                  ).animate().fadeIn().slideY(begin: 0.3, end: 0),

                  SizedBox(height: 12.h),

                  // Description
                  Text(
                    'We\'ve sent a 6-digit verification code to',
                    style: TextStyle(
                      fontSize: 14.sp,
                      color: AppColors.textSecondary,
                    ),
                    textAlign: TextAlign.center,
                  ).animate().fadeIn(delay: const Duration(milliseconds: 100)),

                  SizedBox(height: 4.h),

                  Text(
                    widget.email,
                    style: TextStyle(
                      fontSize: 16.sp,
                      fontWeight: FontWeight.w600,
                      color: AppColors.primary,
                    ),
                  ).animate().fadeIn(delay: const Duration(milliseconds: 200)),

                  SizedBox(height: 40.h),

                  // Error Message
                  if (authProvider.error != null)
                    Container(
                      padding: EdgeInsets.all(12.w),
                      margin: EdgeInsets.only(bottom: 20.h),
                      decoration: BoxDecoration(
                        color: AppColors.error.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(8.r),
                      ),
                      child: Row(
                        children: [
                          Icon(
                            Icons.error_outline,
                            color: AppColors.error,
                            size: 20.w,
                          ),
                          SizedBox(width: 8.w),
                          Expanded(
                            child: Text(
                              authProvider.error!,
                              style: TextStyle(
                                color: AppColors.error,
                                fontSize: 14.sp,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ).animate().shake(),

                  // OTP Input
                  MaterialPinFormField(
                    length: AppConstants.otpLength,
                    pinController: _otpController,
                    keyboardType: TextInputType.number,
                    theme: MaterialPinTheme(
                      shape: MaterialPinShape.outlined,
                      cellSize: Size(50.w, 60.h),
                      borderRadius: BorderRadius.circular(12.r),
                      fillColor: AppColors.inputBackground,
                      focusedFillColor: AppColors.primary.withOpacity(0.1),
                      borderColor: AppColors.inputBorder,
                      focusedBorderColor: AppColors.primary,
                      filledBorderColor: AppColors.primary,
                      animationDuration: const Duration(milliseconds: 300),
                    ),
                    onChanged: (_) {},
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return 'Please enter OTP';
                      }
                      if (value.length != AppConstants.otpLength) {
                        return 'Enter complete OTP';
                      }
                      return null;
                    },
                  ).animate().fadeIn(delay: const Duration(milliseconds: 300)),

                  SizedBox(height: 32.h),

                  // Verify Button
                  CustomButton(
                    text: 'Verify',
                    onPressed: _verifyOTP,
                  ).animate().fadeIn(delay: const Duration(milliseconds: 400)),

                  SizedBox(height: 24.h),

                  // Resend OTP
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        'Didn\'t receive code? ',
                        style: TextStyle(
                          color: AppColors.textSecondary,
                          fontSize: 14.sp,
                        ),
                      ),
                      GestureDetector(
                        onTap: _canResend ? _resendOTP : null,
                        child: Text(
                          _canResend
                              ? 'Resend'
                              : 'Resend in ${_resendSeconds}s',
                          style: TextStyle(
                            color: _canResend
                                ? AppColors.primary
                                : AppColors.textHint,
                            fontSize: 14.sp,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ],
                  ).animate().fadeIn(delay: const Duration(milliseconds: 500)),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
