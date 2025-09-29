"""Analytics service for tracking user events with PostHog."""

import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for tracking user analytics events."""
    
    def track_acta_generated(self, posthog, email: str, filename: str, file_size: int, 
                           duration_minutes: float, total_cost: float, 
                           cost_breakdown: Dict[str, Any], openai_usage: Dict[str, Any], 
                           assemblyai_usage: Dict[str, Any], email_sent: bool) -> None:
        """Track final acta generation."""
        if not posthog:
            logger.warning("PostHog no disponible, saltando tracking de acta_generated")
            return
            
        try:
            posthog.capture(
                distinct_id=email,
                event='acta_generated',
                properties={
                    'filename': filename,
                    'duration_minutes': duration_minutes,
                    'file_size_mb': round(file_size / 1024 / 1024, 2),
                    'cost_usd': total_cost,
                    'cost_breakdown': cost_breakdown,
                    'openai_usage': openai_usage,
                    'assemblyai_usage': assemblyai_usage,
                    'email_sent': email_sent,
                    'timestamp': datetime.now().isoformat()
                }
            )
            logger.info("Tracking acta_generated enviado a PostHog")
        except Exception as e:
            logger.error(f"Error enviando tracking acta_generated: {e}")


# Instancia global del servicio de analytics
analytics_service = AnalyticsService()
