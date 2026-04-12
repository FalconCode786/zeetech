import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import '../core/constants/app_colors.dart';

class Helpers {
  static void showSnackBar(
    BuildContext context, {
    required String message,
    bool isError = false,
  }) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: isError ? AppColors.error : AppColors.success,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12.r),
        ),
        margin: EdgeInsets.all(16.w),
      ),
    );
  }

  static String formatCurrency(double amount) {
    return 'PKR ${amount.toStringAsFixed(0)}';
  }

  static String formatPhoneNumber(String phone) {
    if (phone.length == 11) {
      return '${phone.substring(0, 4)}-${phone.substring(4, 11)}';
    }
    return phone;
  }
}
