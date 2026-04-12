import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';
import '../../core/constants/app_colors.dart';
import '../../core/routes/app_router.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/custom_text_field.dart';
import '../../widgets/custom_button.dart';
import '../../widgets/loading_overlay.dart';

class ForgotPasswordScreen extends StatefulWidget {
  const ForgotPasswordScreen({super.key});

  @override
  State<ForgotPasswordScreen> createState() => _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends State<ForgotPasswordScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();

  @override
  void dispose() {
    _emailController.dispose();
    super.dispose();
  }

  Future<void> _sendOTP() async {
    if (!_formKey.currentState!.validate()) return;

    final authProvider = context.read<AuthProvider>();
    
    final success = await authProvider.requestPasswordReset(
      _emailController.text.trim(),
    );

    if (success && mounted) {
      context.push(
        AppRoutes.otpVerification,
        extra: {
          'email': _emailController.text.trim(),
          'purpose': 'reset',
        },
      );
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
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Icon
                  Center(
                    child: Container(
                      width: 100.w,
                      height: 100.w,
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: AppColors.primaryGradient,
                        ),
                        borderRadius: BorderRadius.circular(24.r),
                      ),
                      child: Icon(
                        Icons.lock_reset,
                        size: 50.w,
                        color: Colors.white,
                      ),
                    ),
                  )
                      .animate()
                      .scale(duration: const Duration(milliseconds: 600)),
                  
                  SizedBox(height: 40.h),
                  
                  // Title
                  Text(
                    'Forgot Password?',
                    style: TextStyle(
                      fontSize: 28.sp,
                      fontWeight: FontWeight.bold,
                      color: AppColors.textPrimary,
                    ),
                  )
                      .animate()
                      .fadeIn()
                      .slideX(begin: -0.3, end: 0),
                  
                  SizedBox(height: 12.h),
                  
                  // Description
                  Text(
                    'Enter your email address and we\'ll send you an OTP to reset your password.',
                    style: TextStyle(
                      fontSize: 16.sp,
                      color: AppColors.textSecondary,
                      height: 1.5,
                    ),
                  )
                      .animate()
                      .fadeIn(delay: const Duration(milliseconds: 100)),
                  
                  SizedBox(height: 32.h),
                  
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
                    )
                        .animate()
                        .shake(),
                  
                  // Email Field
                  CustomTextField(
                    controller: _emailController,
                    label: 'Email',
                    hint: 'Enter your email',
                    keyboardType: TextInputType.emailAddress,
                    prefixIcon: Icon(Icons.email_outlined),
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return 'Please enter your email';
                      }
                      if (!value.contains('@')) {
                        return 'Please enter a valid email';
                      }
                      return null;
                    },
                  )
                      .animate()
                      .fadeIn(delay: const Duration(milliseconds: 200)),
                  
                  SizedBox(height: 32.h),
                  
                  // Submit Button
                  CustomButton(
                    text: 'Send OTP',
                    onPressed: _sendOTP,
                  )
                      .animate()
                      .fadeIn(delay: const Duration(milliseconds: 300)),
                  
                  SizedBox(height: 24.h),
                  
                  // Back to Login
                  Center(
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          'Remember your password? ',
                          style: TextStyle(
                            color: AppColors.textSecondary,
                            fontSize: 14.sp,
                          ),
                        ),
                        GestureDetector(
                          onTap: () => context.pop(),
                          child: Text(
                            'Login',
                            style: TextStyle(
                              color: AppColors.primary,
                              fontSize: 14.sp,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ],
                    ),
                  )
                      .animate()
                      .fadeIn(delay: const Duration(milliseconds: 400)),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
