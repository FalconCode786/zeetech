import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';
import '../../core/constants/app_colors.dart';
import '../../core/routes/app_router.dart';
import '../../providers/booking_provider.dart';
import '../../widgets/booking_card.dart';
import '../../widgets/shimmer_loading.dart';

class MyBookingsScreen extends StatefulWidget {
  const MyBookingsScreen({super.key});

  @override
  State<MyBookingsScreen> createState() => _MyBookingsScreenState();
}

class _MyBookingsScreenState extends State<MyBookingsScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final List<String> _tabs = ['All', 'Pending', 'Confirmed', 'In Progress', 'Completed'];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: _tabs.length, vsync: this);
    _tabController.addListener(_onTabChanged);
    
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<BookingProvider>().loadMyBookings(refresh: true);
    });
  }

  @override
  void dispose() {
    _tabController.removeListener(_onTabChanged);
    _tabController.dispose();
    super.dispose();
  }

  void _onTabChanged() {
    if (_tabController.indexIsChanging) {
      final status = _tabController.index == 0
          ? null
          : _tabs[_tabController.index].toLowerCase().replaceAll(' ', '_');
      context.read<BookingProvider>().loadMyBookings(
        status: status,
        refresh: true,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final bookingProvider = context.watch<BookingProvider>();

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: Text(
          'My Bookings',
          style: TextStyle(
            fontSize: 20.sp,
            fontWeight: FontWeight.bold,
          ),
        ),
        centerTitle: true,
        elevation: 0,
        bottom: TabBar(
          controller: _tabController,
          isScrollable: true,
          indicatorColor: AppColors.primary,
          labelColor: AppColors.primary,
          unselectedLabelColor: AppColors.textSecondary,
          tabs: _tabs.map((tab) => Tab(text: tab)).toList(),
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: _tabs.map((tab) {
          return _buildBookingsList(bookingProvider);
        }).toList(),
      ),
    );
  }

  Widget _buildBookingsList(BookingProvider bookingProvider) {
    if (bookingProvider.isLoading && bookingProvider.bookings.isEmpty) {
      return _buildShimmerList();
    }

    if (bookingProvider.bookings.isEmpty) {
      return _buildEmptyState();
    }

    return RefreshIndicator(
      onRefresh: () => bookingProvider.loadMyBookings(refresh: true),
      color: AppColors.primary,
      child: ListView.builder(
        padding: EdgeInsets.all(16.w),
        itemCount: bookingProvider.bookings.length,
        itemBuilder: (context, index) {
          final booking = bookingProvider.bookings[index];
          return BookingCard(
            booking: booking,
            onTap: () {
              context.push(
                AppRoutes.bookingDetail,
                extra: {'bookingId': booking.id},
              );
            },
          )
              .animate()
              .fadeIn(delay: Duration(milliseconds: index * 100))
              .slideX(begin: 0.3, end: 0);
        },
      ),
    );
  }

  Widget _buildShimmerList() {
    return ListView.builder(
      padding: EdgeInsets.all(16.w),
      itemCount: 4,
      itemBuilder: (context, index) {
        return Padding(
          padding: EdgeInsets.only(bottom: 16.h),
          child: ShimmerLoading(
            child: Container(
              height: 150.h,
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16.r),
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.calendar_today_outlined,
            size: 80.w,
            color: AppColors.textHint,
          ),
          SizedBox(height: 24.h),
          Text(
            'No bookings found',
            style: TextStyle(
              fontSize: 20.sp,
              fontWeight: FontWeight.bold,
              color: AppColors.textSecondary,
            ),
          ),
          SizedBox(height: 8.h),
          Text(
            'Book a service to get started',
            style: TextStyle(
              fontSize: 14.sp,
              color: AppColors.textHint,
            ),
          ),
          SizedBox(height: 24.h),
          ElevatedButton(
            onPressed: () {
              context.push(AppRoutes.serviceCategories);
            },
            child: const Text('Book a Service'),
          ),
        ],
      ),
    );
  }
}
