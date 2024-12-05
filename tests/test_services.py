from typing import List
from unittest.mock import patch, MagicMock
import pytest
from pydantic import BaseModel

# Dummy classes for Prescription and LabResult
class Prescription(BaseModel):
    drug_name: str
    dosage: str
    frequency: str

class LabResult(BaseModel):
    test_name: str
    result: str
    date: str

# Updated Patient model
class Patient(BaseModel):
    id: str
    name: str
    age: int
    email: str
    phone: str
    medical_history: List[str]
    prescriptions: List[Prescription]
    lab_results: List[LabResult]
    conditions: List[str]

# Updated Appointment model
class Appointment(BaseModel):
    appointment_id: str
    patient_id: str
    doctor_id: str
    specialty: str
    date_time: str
    symptoms: List[str]
    status: str

# Test data
test_patient = Patient(
    id="P123",
    name="John Doe",
    age=33,
    email="johndoe@example.com",
    phone="+1234567890",
    medical_history=["Hypertension"],
    prescriptions=[
        Prescription(drug_name="DrugA", dosage="10mg", frequency="Once daily"),
        Prescription(drug_name="DrugB", dosage="5mg", frequency="Twice daily")
    ],
    lab_results=[
        LabResult(test_name="Blood Test", result="Normal", date="2024-01-01"),
        LabResult(test_name="X-Ray", result="No issues", date="2024-01-05")
    ],
    conditions=["Allergy to pollen"]
)

test_appointment = Appointment(
    appointment_id="A123",
    patient_id="P123",
    doctor_id="D456",
    specialty="Cardiology",
    date_time="2024-02-15T14:30:00",
    symptoms=["Chest pain", "Fatigue"],
    status="Scheduled"
)

# Test patient creation
@pytest.mark.asyncio
@patch('boto3.resource', MagicMock())
async def test_create_patient_success():
    table_mock = MagicMock()
    with patch('boto3.resource.Table', return_value=table_mock):
        table_mock.put_item.return_value = {}

        async def create_patient(patient: Patient):
            table_mock.put_item(Item=patient.dict())
            return {"message": "Patient record created", "patient_id": patient.id}

        response = await create_patient(test_patient)
        print(f"\nCreate Patient Test Response: {response}")
        table_mock.put_item.assert_called_once_with(Item=test_patient.dict())
        assert response["message"] == "Patient record created"
        assert response["patient_id"] == test_patient.id

# Test appointment creation
@pytest.mark.asyncio
@patch('boto3.resource', MagicMock())
async def test_create_appointment_success():
    table_mock = MagicMock()
    with patch('boto3.resource.Table', return_value=table_mock):
        table_mock.put_item.return_value = {}

        async def create_appointment(appointment: Appointment):
            table_mock.put_item(Item=appointment.dict())
            return {"message": "Appointment scheduled", "appointment_id": appointment.appointment_id}

        response = await create_appointment(test_appointment)
        print(f"\nCreate Appointment Test Response: {response}")
        table_mock.put_item.assert_called_once_with(Item=test_appointment.dict())
        assert response["message"] == "Appointment scheduled"
        assert response["appointment_id"] == test_appointment.appointment_id

# Test the Patient model
def test_patient_model():
    print(f"\nPatient Model Test: {test_patient.dict()}")
    assert test_patient.id == "P123"
    assert test_patient.name == "John Doe"
    assert test_patient.prescriptions[0].drug_name == "DrugA"
    assert test_patient.lab_results[1].test_name == "X-Ray"

# Test the Appointment model
def test_appointment_model():
    print(f"\nAppointment Model Test: {test_appointment.dict()}")
    assert test_appointment.appointment_id == "A123"
    assert test_appointment.status == "Scheduled"
    assert "Chest pain" in test_appointment.symptoms
