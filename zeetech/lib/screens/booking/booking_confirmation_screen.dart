import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../../core/constants/app_colors.dart';
import '../../core/routes/app_router.dart';
import '../../widgets/custom_button.dart';

class BookingConfirmationScreen extends StatelessWidget {
  final String bookingNumber;

  const BookingConfirmationScreen({super.key, required this.bookingNumber});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: Padding(
          padding: EdgeInsets.all(24.w),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Success Animation
              Container(
                width: 200.w,
                height: 200.w,
                decoration: BoxDecoration(
                  color: AppColors.success.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  Icons.check_circle,
                  size: 120.w,
                  color: AppColors.success,
                ),
              ).animate().scale(
                duration: const Duration(milliseconds: 600),
                curve: Curves.elasticOut,
              ),

              SizedBox(height: 40.h),

              // Title
              Text(
                'Booking Confirmed!',
                style: TextStyle(
                  fontSize: 28.sp,
                  fontWeight: FontWeight.bold,
                  color: AppColors.textPrimary,
                ),
              ).animate().fadeIn(delay: const Duration(milliseconds: 300)),

              SizedBox(height: 16.h),

              // Description
              Text(
                'Your service has been booked successfully. We will assign a technician soon.',
                style: TextStyle(
                  fontSize: 16.sp,
                  color: AppColors.textSecondary,
                  height: 1.5,
                ),
                textAlign: TextAlign.center,
              ).animate().fadeIn(delay: const Duration(milliseconds: 400)),

              SizedBox(height: 32.h),

              // Booking Number Card
              Container(
                padding: EdgeInsets.all(20.w),
                decoration: BoxDecoration(
                  color: AppColors.surface,
                  borderRadius: BorderRadius.circular(16.r),
                  border: Border.all(color: AppColors.inputBorder),
                ),
                child: Column(
                  children: [
                    Text(
                      'Booking Number',
                      style: TextStyle(
                        fontSize: 14.sp,
                        color: AppColors.textSecondary,
                      ),
                    ),
                    SizedBox(height: 8.h),
                    Text(
                      bookingNumber,
                      style: TextStyle(
                        fontSize: 24.sp,
                        fontWeight: FontWeight.bold,
                        color: AppColors.primary,
                        letterSpacing: 2,
                      ),
                    ),
                  ],
                ),
              ).animate().fadeIn(delay: const Duration(milliseconds: 500)),

              SizedBox(height: 48.h),

              // Buttons
              CustomButton(
                text: 'View My Bookings',
                onPressed: () {
                  context.go(AppRoutes.myBookings);
                },
              ).animate().fadeIn(delay: const Duration(milliseconds: 600)),

              SizedBox(height: 16.h),

              // Back to Home
              TextButton(
                onPressed: () {
                  context.go(AppRoutes.home);
                },
                child: Text(
                  'Back to Home',
                  style: TextStyle(
                    color: AppColors.primary,
                    fontSize: 16.sp,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ).animate().fadeIn(delay: const Duration(milliseconds: 700)),
            ],
          ),
        ),
      ),
    );
  }
}
