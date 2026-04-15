import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:go_router/go_router.dart';
import '../../core/constants/app_colors.dart';
import '../../widgets/custom_app_bar.dart';

class PrivacyPolicyScreen extends StatelessWidget {
  const PrivacyPolicyScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: CustomAppBar(
        title: 'Privacy Policy',
        onBackPressed: () => context.pop(),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: EdgeInsets.all(16.w),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildSection(
                'Privacy Policy',
                'Last Updated: April 2025',
                isHeader: true,
              ),
              SizedBox(height: 16.h),
              _buildSection(
                '1. Information We Collect',
                'We collect information you provide directly, such as name, email, phone number, address, and payment information. We also collect usage information about how you interact with our app.',
              ),
              SizedBox(height: 16.h),
              _buildSection(
                '2. How We Use Your Information',
                'We use your information to provide, maintain, and improve our services, process transactions, send updates, and comply with legal obligations.',
              ),
              SizedBox(height: 16.h),
              _buildSection(
                '3. Data Security',
                'We implement appropriate technical and organizational measures to protect your personal information against unauthorized access, alteration, disclosure, or destruction.',
              ),
              SizedBox(height: 16.h),
              _buildSection(
                '4. Third-Party Sharing',
                'We do not sell your personal information. We may share it with service providers who assist us in operating our platform and providing services to you.',
              ),
              SizedBox(height: 16.h),
              _buildSection(
                '5. Your Rights',
                'You have the right to access, correct, or delete your personal information. You may also opt-out of certain communications. Contact us for any requests.',
              ),
              SizedBox(height: 16.h),
              _buildSection(
                '6. Cookies',
                'We use cookies and similar tracking technologies to enhance your experience, remember your preferences, and analyze usage patterns.',
              ),
              SizedBox(height: 16.h),
              _buildSection(
                '7. Changes to Privacy Policy',
                'We may update this privacy policy from time to time. We will notify you of any significant changes by posting the updated policy and updating the "Last Updated" date.',
              ),
              SizedBox(height: 16.h),
              _buildSection(
                '8. Contact Us',
                'If you have questions about this privacy policy or our privacy practices, please contact us at info.zeetech26@gmail.com or call 03005518622.',
              ),
              SizedBox(height: 24.h),
              Container(
                padding: EdgeInsets.all(12.w),
                decoration: BoxDecoration(
                  color: AppColors.primary.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8.r),
                ),
                child: Text(
                  'By using ZeeTech, you agree to this Privacy Policy. If you do not agree, please do not use our services.',
                  style: TextStyle(
                    fontSize: 12.sp,
                    fontStyle: FontStyle.italic,
                    color: AppColors.textSecondary,
                  ),
                ),
              ),
              SizedBox(height: 24.h),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSection(String title, String content, {bool isHeader = false}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: TextStyle(
            fontSize: isHeader ? 24.sp : 14.sp,
            fontWeight: FontWeight.bold,
            color: AppColors.textPrimary,
          ),
        ),
        if (!isHeader) SizedBox(height: 8.h),
        if (!isHeader)
          Text(
            content,
            style: TextStyle(
              fontSize: 13.sp,
              color: AppColors.textSecondary,
              height: 1.6,
            ),
          ),
        if (isHeader)
          Text(
            content,
            style: TextStyle(fontSize: 13.sp, color: AppColors.textSecondary),
          ),
      ],
    );
  }
}
