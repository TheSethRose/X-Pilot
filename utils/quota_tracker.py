"""
Utility for tracking 𝕏 API quota usage.
"""
from datetime import datetime, timedelta
from flask import current_app
from app.models import db, QuotaUsage

class QuotaTracker:
    """Utility for tracking 𝕏 API quota usage."""

    MONTHLY_LIMIT = 1500  # Standard 𝕏 API limit for posts

    @staticmethod
    def track_api_call(user, call_type="post"):
        """
        Track an API call for a user.

        Args:
            user: The user making the API call
            call_type: Type of API call (default: "post")

        Returns:
            dict: Information about quota status
        """
        current_app.logger.info(f"Tracking API call for user {user.username}, type: {call_type}")

        now = datetime.utcnow()
        current_month = now.month
        current_year = now.year

        # Calculate reset date (first day of next month)
        if current_month == 12:
            reset_month = 1
            reset_year = current_year + 1
        else:
            reset_month = current_month + 1
            reset_year = current_year

        reset_date = f"{reset_year}-{reset_month:02d}-01"

        # Get or create quota usage for current month
        quota = QuotaUsage.query.filter_by(
            user_id=user.id,
            month=current_month,
            year=current_year
        ).first()

        if not quota:
            # Create a new quota usage record
            quota = QuotaUsage()
            quota.user_id = user.id
            quota.month = current_month
            quota.year = current_year
            quota.posts_used = 0
            quota.reset_date = reset_date
            db.session.add(quota)

        # Update posts used based on call type
        if call_type == "post":
            quota.posts_used += 1

        db.session.commit()

        # Calculate percentage used
        percentage = min(round((quota.posts_used / QuotaTracker.MONTHLY_LIMIT) * 100), 100)

        return {
            "posts_used": quota.posts_used,
            "limit": QuotaTracker.MONTHLY_LIMIT,
            "percentage": percentage,
            "reset_date": quota.reset_date
        }

    @staticmethod
    def get_quota_status(user):
        """
        Get the current quota status for a user.

        Args:
            user: The user to check quota for

        Returns:
            dict: Information about quota status
        """
        now = datetime.utcnow()
        current_month = now.month
        current_year = now.year

        # Calculate reset date (first day of next month)
        if current_month == 12:
            reset_month = 1
            reset_year = current_year + 1
        else:
            reset_month = current_month + 1
            reset_year = current_year

        reset_date = f"{reset_year}-{reset_month:02d}-01"

        # Get or create quota usage for current month
        quota = QuotaUsage.query.filter_by(
            user_id=user.id,
            month=current_month,
            year=current_year
        ).first()

        if not quota:
            # Create a new quota usage record
            quota = QuotaUsage()
            quota.user_id = user.id
            quota.month = current_month
            quota.year = current_year
            quota.posts_used = 0
            quota.reset_date = reset_date
            db.session.add(quota)
            db.session.commit()

        # Calculate percentage used
        percentage = min(round((quota.posts_used / QuotaTracker.MONTHLY_LIMIT) * 100), 100)

        return {
            "posts_used": quota.posts_used,
            "limit": QuotaTracker.MONTHLY_LIMIT,
            "percentage": percentage,
            "reset_date": quota.reset_date
        }
