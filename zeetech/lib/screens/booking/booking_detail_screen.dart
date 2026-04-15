import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:go_router/go_router.dart';
import '../../core/constants/app_colors.dart';
import '../../widgets/custom_app_bar.dart';

class BookingDetailScreen extends StatelessWidget {
  final int bookingId;

  const BookingDetailScreen({super.key, required this.bookingId});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: CustomAppBar(
        title: 'Booking Details',
        showBackButton: true,
        onBackPressed: () => context.pop(),
      ),
      body: Center(
        child: Text(
          'Booking Detail - ID: $bookingId',
          style: TextStyle(fontSize: 18.sp),
        ),
      ),
    );
  }
}
