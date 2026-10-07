import logging
import string
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.models.faq import FaqModel
from app.repositories.faq_repository import FaqRepository

logger = logging.getLogger(__name__)

# Deterministic text matching threshold.
# Above this threshold, FAQs are considered a match.
# Jaccard + Overlap coefficient ratio of 0.60 provides a good balance between matching slight variations
# and avoiding false positives for completely different questions.
MATCH_THRESHOLD = 0.60

class FaqMatchResult(BaseModel):
    matched: bool
    faq: Optional[FaqModel] = None
    answer: Optional[str] = None

class FaqService:
    def __init__(self, repository: Optional[FaqRepository] = None):
        self.repository = repository or FaqRepository()

    def get_active_faqs(self) -> List[FaqModel]:
        """Return restaurant FAQs that are currently active."""
        logger.info("Fetching active FAQs from repository")
        return self.repository.get_active_faqs()

    def create_faq(self, data: dict) -> FaqModel:
        """Create a new FAQ."""
        faq = FaqModel(**data)
        faq.updatedAt = datetime.utcnow()
        faq_id = self.repository.create(faq)
        logger.info(f"FAQ created with ID: {faq_id}")
        
        # Safe to ignore type here because get_by_id returns FaqModel on success
        return self.repository.get_by_id(faq_id)  # type: ignore

    def update_faq(self, faq_id: str, updates: dict) -> Optional[FaqModel]:
        """Update an existing FAQ. Safely handles missing FAQ."""
        if not self.repository.get_by_id(faq_id):
            logger.warning(f"FAQ update failed: ID {faq_id} not found.")
            return None
            
        updates["updatedAt"] = datetime.utcnow()
        success = self.repository.update(faq_id, updates)
        if success:
            logger.info(f"FAQ updated: {faq_id}")
            return self.repository.get_by_id(faq_id)
        return None

    def delete_faq(self, faq_id: str) -> bool:
        """Delete an FAQ. Safely handles missing FAQ."""
        success = self.repository.delete(faq_id)
        if success:
            logger.info(f"FAQ deleted: {faq_id}")
        else:
            logger.warning(f"FAQ delete failed: ID {faq_id} not found.")
        return success

    def _normalize_text(self, text: str) -> set[str]:
        """Internal normalization: lowercase, strip punctuation, return word tokens."""
        text = text.lower()
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        # Return set of words
        return set(text.split())

    def _calculate_similarity(self, q1: str, q2: str) -> float:
        """Calculate similarity using Jaccard index on word sets."""
        tokens1 = self._normalize_text(q1)
        tokens2 = self._normalize_text(q2)
        if not tokens1 or not tokens2:
            return 0.0
        
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        jaccard = len(intersection) / len(union)
        
        # We also compute subset overlap: if all tokens of one are in another
        overlap = len(intersection) / min(len(tokens1), len(tokens2))
        
        return (jaccard + overlap) / 2.0

    def find_faq(self, question: str, language: str = "EN") -> FaqMatchResult:
        """Find the best approved FAQ for a customer's question."""
        logger.info(f"Searching FAQ for question: '{question}' (Lang: {language})")
        
        if not question.strip():
            logger.info("Empty search query. No match.")
            return FaqMatchResult(matched=False)

        active_faqs = self.get_active_faqs()
        
        best_match = None
        best_score = 0.0

        for faq in active_faqs:
            score = self._calculate_similarity(question, faq.question)
            if score > best_score:
                best_score = score
                best_match = faq

        logger.info(f"FAQ match best score: {best_score:.2f} vs threshold {MATCH_THRESHOLD}")

        if best_match and best_score >= MATCH_THRESHOLD:
            # Language Selection
            lang_upper = language.upper()
            answer = None
            
            if lang_upper == "FR":
                answer = best_match.answerFr
            elif lang_upper == "EN":
                answer = best_match.answerEn
            else:
                # Unknown language - do not invent, let upstream handle
                logger.warning(f"Unknown language requested: {language}. Returning no match to prevent hallucination.")
                return FaqMatchResult(matched=False)
                
            logger.info(f"FAQ match found. Question matched: '{best_match.question}'")
            return FaqMatchResult(matched=True, faq=best_match, answer=answer)

        # No hallucination rule
        logger.info("FAQ no match. Below threshold or no active FAQs. Returning safe structured result.")
        return FaqMatchResult(matched=False)
