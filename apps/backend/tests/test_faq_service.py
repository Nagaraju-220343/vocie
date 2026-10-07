from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from app.models.faq import FaqModel
from app.services.faq_service import FaqService


@pytest.fixture
def mock_repo():
    return MagicMock()

@pytest.fixture
def service(mock_repo):
    return FaqService(repository=mock_repo)

def test_get_active_faqs(service, mock_repo):
    """Test 1 - Get active FAQs"""
    faq1 = FaqModel(question="Q1", answerFr="A1_FR", answerEn="A1_EN", category="HOURS", active=True)
    mock_repo.get_active_faqs.return_value = [faq1]
    
    result = service.get_active_faqs()
    assert len(result) == 1
    assert result[0].question == "Q1"

def test_exact_faq_match(service, mock_repo):
    """Test 2 - Exact FAQ match"""
    faq1 = FaqModel(question="What time do you open?", answerFr="A_FR", answerEn="A_EN", category="HOURS")
    mock_repo.get_active_faqs.return_value = [faq1]
    
    res = service.find_faq("What time do you open?")
    assert res.matched is True
    assert res.faq is faq1

def test_case_normalization(service, mock_repo):
    """Test 3 - Case normalization"""
    faq1 = FaqModel(question="What time do you open?", answerFr="A_FR", answerEn="A_EN", category="HOURS")
    mock_repo.get_active_faqs.return_value = [faq1]
    
    res = service.find_faq("WHAT TIME DO YOU OPEN?")
    assert res.matched is True
    assert res.faq is faq1

def test_punctuation_normalization(service, mock_repo):
    """Test 4 - Punctuation normalization"""
    faq1 = FaqModel(question="What time do you open?", answerFr="A_FR", answerEn="A_EN", category="HOURS")
    mock_repo.get_active_faqs.return_value = [faq1]
    
    res = service.find_faq("What time do you open!!!")
    assert res.matched is True
    assert res.faq is faq1

def test_whitespace_normalization(service, mock_repo):
    """Test 5 - Whitespace normalization"""
    faq1 = FaqModel(question="What time do you open?", answerFr="A_FR", answerEn="A_EN", category="HOURS")
    mock_repo.get_active_faqs.return_value = [faq1]
    
    res = service.find_faq("   What   time   do   you   open?   ")
    assert res.matched is True
    assert res.faq is faq1

def test_english_answer(service, mock_repo):
    """Test 6 - English answer"""
    faq1 = FaqModel(question="Q", answerFr="A_FR", answerEn="A_EN", category="HOURS")
    mock_repo.get_active_faqs.return_value = [faq1]
    
    res = service.find_faq("Q", language="EN")
    assert res.answer == "A_EN"

def test_french_answer(service, mock_repo):
    """Test 7 - French answer"""
    faq1 = FaqModel(question="Q", answerFr="A_FR", answerEn="A_EN", category="HOURS")
    mock_repo.get_active_faqs.return_value = [faq1]
    
    res = service.find_faq("Q", language="FR")
    assert res.answer == "A_FR"

def test_unknown_question(service, mock_repo):
    """Test 8 - Unknown question"""
    faq1 = FaqModel(question="What time do you open?", answerFr="A", answerEn="B", category="HOURS")
    mock_repo.get_active_faqs.return_value = [faq1]
    
    res = service.find_faq("Do you have a helicopter landing pad?")
    assert res.matched is False
    assert res.answer is None
    assert res.faq is None

def test_unrelated_question(service, mock_repo):
    """Test 9 - Unrelated question"""
    faq1 = FaqModel(question="What time do you open?", answerFr="A", answerEn="B", category="HOURS")
    mock_repo.get_active_faqs.return_value = [faq1]
    
    res = service.find_faq("Do you offer parking?")
    assert res.matched is False

def test_inactive_faq(service, mock_repo):
    """Test 10 - Inactive FAQ"""
    # Active FAQs should not include inactive ones. The repository filters them.
    # We test that the service relies on what the repository returns for active faqs.
    mock_repo.get_active_faqs.return_value = []
    
    res = service.find_faq("What time do you open?")
    assert res.matched is False

def test_create_faq(service, mock_repo):
    """Test 11 - Create FAQ"""
    mock_repo.create.return_value = "new_id"
    created_faq = FaqModel(**{"_id": "new_id", "question": "Q", "answerFr": "FR", "answerEn": "EN", "category": "MENU"})
    mock_repo.get_by_id.return_value = created_faq

    faq = service.create_faq({
        "question": "Q", "answerFr": "FR", "answerEn": "EN", "category": "MENU"
    })

    assert faq.id == "new_id"
    mock_repo.create.assert_called_once()

def test_invalid_faq(service, mock_repo):
    """Test 12 - Invalid FAQ"""
    with pytest.raises(ValidationError):
        service.create_faq({"question": ""}) # Missing required fields

def test_update_faq(service, mock_repo):
    """Test 13 - Update FAQ"""
    existing_faq = FaqModel(id="some_id", question="Q", answerFr="FR", answerEn="EN", category="MENU")
    updated_faq = FaqModel(id="some_id", question="Q", answerFr="FR", answerEn="NEW_EN", category="MENU")
    
    mock_repo.get_by_id.side_effect = [existing_faq, updated_faq]
    mock_repo.update.return_value = True
    
    res = service.update_faq("some_id", {"answerEn": "NEW_EN"})
    assert res is not None
    assert res.answerEn == "NEW_EN"
    mock_repo.update.assert_called_once()

def test_update_nonexistent_faq(service, mock_repo):
    """Test 14 - Update nonexistent FAQ"""
    mock_repo.get_by_id.return_value = None
    res = service.update_faq("bad_id", {"answerEn": "NEW"})
    assert res is None
    mock_repo.update.assert_not_called()

def test_delete_faq(service, mock_repo):
    """Test 15 - Delete FAQ"""
    mock_repo.delete.return_value = True
    res = service.delete_faq("some_id")
    assert res is True
    mock_repo.delete.assert_called_once_with("some_id")

def test_bilingual_integrity(service, mock_repo):
    """Test 16 - Bilingual integrity"""
    # Updating English must not overwrite French
    existing_faq = FaqModel(id="some_id", question="Q", answerFr="FR", answerEn="EN", category="MENU")
    updated_faq = FaqModel(id="some_id", question="Q", answerFr="FR", answerEn="NEW_EN", category="MENU")
    
    mock_repo.get_by_id.side_effect = [existing_faq, updated_faq]
    mock_repo.update.return_value = True
    
    res = service.update_faq("some_id", {"answerEn": "NEW_EN"})
    assert res is not None
    assert res.answerFr == "FR"  # French unchanged
    assert res.answerEn == "NEW_EN" # English updated

def test_unknown_language(service, mock_repo):
    faq1 = FaqModel(question="Q", answerFr="A_FR", answerEn="A_EN", category="HOURS")
    mock_repo.get_active_faqs.return_value = [faq1]
    
    res = service.find_faq("Q", language="UNKNOWN")
    assert res.matched is False # handled safely, prevented hallucination
