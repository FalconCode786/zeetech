import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:go_router/go_router.dart';
import '../../core/constants/app_colors.dart';
import '../../widgets/custom_app_bar.dart';

class ServiceDetailScreen extends StatelessWidget {
  final int subcategoryId;

  const ServiceDetailScreen({super.key, required this.subcategoryId});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: CustomAppBar(
        title: 'Service Details',
        showBackButton: true,
        onBackPressed: () => context.pop(),
      ),
      body: Center(
        child: Text(
          'Service Detail - ID: $subcategoryId',
          style: TextStyle(fontSize: 18.sp),
        ),
      ),
    );
  }
}
