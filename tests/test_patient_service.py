import pytest
from patient_record_service.main import create_patient
from models import Patient
from uuid import uuid4

@pytest.fixture
def sample_patient():
    return Patient(
        id=str(uuid4()),
        name="John Doe",
        date_of_birth="1990-01-01",
        contact="123-456-7890",
        medical_history="No major issues"
    )

@pytest.mark.asyncio
async def test_create_patient(sample_patient):
    response = await create_patient(sample_patient)
    assert response["message"] == "Patient record created"
    assert response["patient_id"] == sample_patient.id
