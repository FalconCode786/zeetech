import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:go_router/go_router.dart';
import '../../core/constants/app_colors.dart';
import '../../widgets/custom_app_bar.dart';

class HelpCenterScreen extends StatefulWidget {
  const HelpCenterScreen({super.key});

  @override
  State<HelpCenterScreen> createState() => _HelpCenterScreenState();
}

class _HelpCenterScreenState extends State<HelpCenterScreen> {
  final List<Map<String, String>> faqs = [
    {
      'question': 'How do I book a service?',
      'answer':
          'Select a service from the categories, enter your details, choose a date and time slot, and confirm booking.',
    },
    {
      'question': 'What is the cancellation policy?',
      'answer':
          'You can cancel bookings up to 24 hours before the scheduled time for a full refund.',
    },
    {
      'question': 'How do I pay for services?',
      'answer':
          'We accept all major credit cards and digital wallets. Payment is secure and encrypted.',
    },
    {
      'question': 'How do I become a provider?',
      'answer':
          'Sign up, complete your profile, and verify your identity. After approval, you can start offering services.',
    },
    {
      'question': 'Is my payment information safe?',
      'answer':
          'Yes, we use industry-standard encryption to protect all payment and personal information.',
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: CustomAppBar(
        title: 'Help Center',
        onBackPressed: () => context.pop(),
      ),
      body: SafeArea(
        child: ListView(
          padding: EdgeInsets.all(16.w),
          children: [
            TextField(
              decoration: InputDecoration(
                hintText: 'Search FAQs...',
                prefixIcon: const Icon(Icons.search),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8.r),
                ),
              ),
            ),
            SizedBox(height: 24.h),
            Text(
              'Frequently Asked Questions',
              style: TextStyle(
                fontSize: 18.sp,
                fontWeight: FontWeight.bold,
                color: AppColors.textPrimary,
              ),
            ),
            SizedBox(height: 16.h),
            ...faqs.asMap().entries.map((entry) {
              final index = entry.key;
              final faq = entry.value;
              return _buildFaqCard(faq, index);
            }).toList(),
            SizedBox(height: 24.h),
            Container(
              padding: EdgeInsets.all(16.w),
              decoration: BoxDecoration(
                color: AppColors.primary.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12.r),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Still need help?',
                    style: TextStyle(
                      fontSize: 16.sp,
                      fontWeight: FontWeight.bold,
                      color: AppColors.textPrimary,
                    ),
                  ),
                  SizedBox(height: 8.h),
                  Text(
                    'Contact our support team anytime',
                    style: TextStyle(
                      fontSize: 13.sp,
                      color: AppColors.textSecondary,
                    ),
                  ),
                  SizedBox(height: 12.h),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: () => context.go('/profile/contact-us'),
                      child: const Text('Contact Support'),
                    ),
                  ),
                ],
              ),
            ),
            SizedBox(height: 24.h),
          ],
        ),
      ),
    );
  }

  Widget _buildFaqCard(Map<String, String> faq, int index) {
    return Container(
      margin: EdgeInsets.only(bottom: 12.h),
      child: ExpansionTile(
        title: Text(
          faq['question'] ?? '',
          style: TextStyle(
            fontSize: 14.sp,
            fontWeight: FontWeight.w600,
            color: AppColors.textPrimary,
          ),
        ),
        backgroundColor: AppColors.surface,
        collapsedBackgroundColor: AppColors.surface,
        children: [
          Padding(
            padding: EdgeInsets.all(12.w),
            child: Text(
              faq['answer'] ?? '',
              style: TextStyle(
                fontSize: 13.sp,
                color: AppColors.textSecondary,
                height: 1.5,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
