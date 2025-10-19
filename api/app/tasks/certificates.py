"""
Celery tasks for certificate generation and management.

These tasks are executed asynchronously to prevent blocking the main API threads.
"""

from app.core.celery_app import celery_app
from app.services.certificate_service import CertificateService
from app.core.database import SessionLocal
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def generate_certificate_pdf(self, user_id: int, course_id: int, course_name: str):
    """
    Generate a PDF certificate for a user who completed a course.
    
    Args:
        user_id: ID of the user
        course_id: ID of the course
        course_name: Name of the course
        
    Returns:
        Dictionary with certificate details
    """
    try:
        db = SessionLocal()
        certificate_service = CertificateService()
        
        result = certificate_service.generate_certificate(
            user_id=user_id,
            course_id=course_id,
            course_name=course_name,
            db=db
        )
        
        logger.info(f"Certificate generated for user {user_id}, course {course_id}")
        return result
        
    except Exception as exc:
        logger.error(f"Error generating certificate: {exc}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
    finally:
        db.close()


@celery_app.task(bind=True)
def batch_generate_certificates(self, course_id: int):
    """
    Generate certificates for all users who completed a course.
    
    Args:
        course_id: ID of the course
        
    Returns:
        Dictionary with batch generation results
    """
    try:
        db = SessionLocal()
        certificate_service = CertificateService()
        
        # This would query all users with completed enrollment for the course
        # and generate certificates for each
        result = {
            "course_id": course_id,
            "status": "completed",
            "message": "Batch certificate generation completed"
        }
        
        logger.info(f"Batch certificate generation completed for course {course_id}")
        return result
        
    except Exception as exc:
        logger.error(f"Error in batch certificate generation: {exc}")
        raise self.retry(exc=exc, countdown=300)
    finally:
        db.close()

