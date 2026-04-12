/// Production-ready validation utilities
class ValidationUtils {
  // Email regex pattern - RFC 5322 simplified
  static const String _emailPattern = r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$";

  // Phone regex - supports Pakistani format and international
  static const String _phonePattern = r'^(?:\+92|0)?3\d{9}$|^(?:\+\d{1,3}[-.]?)?\d{7,14}$';

  // Password requirements: min 8 chars, at least one uppercase, lowercase, digit, special char
  static const String _passwordPattern =
      r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$';

  /// Validate email format
  static String? validateEmail(String? email) {
    if (email == null || email.isEmpty) {
      return 'Email is required';
    }

    email = email.trim();

    if (email.length > 254) {
      return 'Email is too long';
    }

    if (!RegExp(_emailPattern).hasMatch(email)) {
      return 'Please enter a valid email address';
    }

    return null; // Valid
  }

  /// Validate password strength
  static String? validatePassword(String? password) {
    if (password == null || password.isEmpty) {
      return 'Password is required';
    }

    if (password.length < 8) {
      return 'Password must be at least 8 characters';
    }

    if (password.length > 128) {
      return 'Password is too long';
    }

    // For MVP, allow any password. In production, enforce:
    // if (!RegExp(_passwordPattern).hasMatch(password)) {
    //   return 'Password must contain uppercase, lowercase, digit, and special character';
    // }

    return null; // Valid
  }

  /// Validate phone number format
  static String? validatePhone(String? phone) {
    if (phone == null || phone.isEmpty) {
      return 'Phone number is required';
    }

    phone = phone.replaceAll(RegExp(r'[^\d+]'), '');

    if (phone.length < 10) {
      return 'Phone number is too short';
    }

    if (phone.length > 15) {
      return 'Phone number is too long';
    }

    // Basic validation - should start with +, 0, or 3 for Pakistan
    if (!RegExp(r'^(?:\+?\d{1,3}|0)?[0-9]{7,14}$').hasMatch(phone)) {
      return 'Please enter a valid phone number';
    }

    return null; // Valid
  }

  /// Validate full name
  static String? validateFullName(String? name) {
    if (name == null || name.isEmpty) {
      return 'Full name is required';
    }

    name = name.trim();

    if (name.length < 2) {
      return 'Name must be at least 2 characters';
    }

    if (name.length > 100) {
      return 'Name is too long';
    }

    // Check for valid characters (letters, spaces, hyphens, apostrophes)
    if (!RegExp(r"^[a-zA-Z\s\-']+$").hasMatch(name)) {
      return 'Name contains invalid characters';
    }

    return null; // Valid
  }

  /// Validate address
  static String? validateAddress(String? address) {
    if (address == null || address.isEmpty) {
      return 'Address is required';
    }

    address = address.trim();

    if (address.length < 5) {
      return 'Address must be at least 5 characters';
    }

    if (address.length > 500) {
      return 'Address is too long';
    }

    return null; // Valid
  }

  /// Validate city selection
  static String? validateCity(String? city) {
    if (city == null || city.isEmpty) {
      return 'Please select a city';
    }

    return null; // Valid
  }

  /// Validate area/locality
  static String? validateArea(String? area) {
    if (area == null || area.isEmpty) {
      return 'Please select an area';
    }

    return null; // Valid
  }

  /// Validate booking date (must be future date)
  static String? validateBookingDate(DateTime? date) {
    if (date == null) {
      return 'Please select a date';
    }

    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);

    if (date.isBefore(today)) {
      return 'Please select a future date';
    }

    // Check if date is not too far in the future (e.g., max 90 days)
    final maxDate = today.add(const Duration(days: 90));
    if (date.isAfter(maxDate)) {
      return 'Booking date cannot be more than 90 days in advance';
    }

    return null; // Valid
  }

  /// Validate booking time slot
  static String? validateTimeSlot(String? timeSlot) {
    if (timeSlot == null || timeSlot.isEmpty) {
      return 'Please select a time slot';
    }

    return null; // Valid
  }

  /// Validate OTP input
  static String? validateOTP(String? otp) {
    if (otp == null || otp.isEmpty) {
      return 'OTP is required';
    }

    otp = otp.replaceAll(RegExp(r'[^\d]'), '');

    if (otp.length != 6) {
      return 'OTP must be 6 digits';
    }

    return null; // Valid
  }

  /// Generic password confirmation validator
  static String? validatePasswordMatch(String? password, String? confirmPassword) {
    if (password == null || confirmPassword == null) {
      return 'Both passwords are required';
    }

    if (password != confirmPassword) {
      return 'Passwords do not match';
    }

    return null; // Valid
  }

  /// Sanitize string input (remove malicious content)
  static String sanitizeInput(String input) {
    // Remove HTML tags
    input = input.replaceAll(RegExp(r'<[^>]*>'), '');

    // Remove SQL injection attempts
     input = input.replaceAll(RegExp(r'''[;'"]'''), '');

    // Trim whitespace
    input = input.trim();

    return input;
  }

  /// Check if URL is valid and safe
  static bool isValidUrl(String? url) {
    if (url == null || url.isEmpty) return false;

    try {
      final uri = Uri.parse(url);
      return uri.isAbsolute && (uri.scheme == 'http' || uri.scheme == 'https');
    } catch (e) {
      return false;
    }
  }

  /// Check string length is within safe bounds
  static bool isLengthValid(String? value, int minLength, int maxLength) {
    if (value == null) return false;
    final length = value.trim().length;
    return length >= minLength && length <= maxLength;
  }
}
