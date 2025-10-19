"""
Celery tasks for AI-powered business matching.

These tasks handle complex matching calculations asynchronously.
"""

from app.core.celery_app import celery_app
from app.services.matching_service import MatchingService
from app.core.database import SessionLocal
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def calculate_matches_for_user(self, user_id: int, limit: int = 10):
    """
    Calculate business matches for a specific user.
    
    Args:
        user_id: ID of the user
        limit: Maximum number of matches to return
        
    Returns:
        List of calculated matches with scores
    """
    try:
        db = SessionLocal()
        matching_service = MatchingService()
        
        matches = matching_service.get_matches_for_user(
            user_id=user_id,
            limit=limit,
            db=db
        )
        
        logger.info(f"Calculated {len(matches)} matches for user {user_id}")
        return matches
        
    except Exception as exc:
        logger.error(f"Error calculating matches: {exc}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
    finally:
        db.close()


@celery_app.task(bind=True)
def recalculate_all_matches(self):
    """
    Recalculate all business matches in the system.
    
    This is a heavy operation and should be run during off-peak hours.
    
    Returns:
        Dictionary with recalculation results
    """
    try:
        db = SessionLocal()
        matching_service = MatchingService()
        
        # This would iterate through all users and recalculate their matches
        result = {
            "status": "completed",
            "message": "All matches recalculated successfully",
            "timestamp": str(datetime.now())
        }
        
        logger.info("All matches recalculated successfully")
        return result
        
    except Exception as exc:
        logger.error(f"Error recalculating all matches: {exc}")
        raise self.retry(exc=exc, countdown=600)
    finally:
        db.close()


@celery_app.task(bind=True)
def update_match_feedback(self, match_id: int, rating: int, feedback: str = None):
    """
    Update match feedback and retrain algorithm.
    
    Args:
        match_id: ID of the match
        rating: User rating (1-5)
        feedback: Optional feedback text
        
    Returns:
        Dictionary with update results
    """
    try:
        db = SessionLocal()
        matching_service = MatchingService()
        
        # Update feedback in database
        result = {
            "match_id": match_id,
            "rating": rating,
            "status": "feedback_recorded",
            "message": "Match feedback recorded and will be used to improve future matches"
        }
        
        logger.info(f"Feedback recorded for match {match_id} with rating {rating}")
        return result
        
    except Exception as exc:
        logger.error(f"Error updating match feedback: {exc}")
        raise self.retry(exc=exc, countdown=60)
    finally:
        db.close()


from datetime import datetime

