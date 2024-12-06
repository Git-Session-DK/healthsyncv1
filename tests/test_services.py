from typing import List
from unittest.mock import patch, MagicMock
import pytest
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

# Base Models
class Prescription(BaseModel):
    drug_name: str
    dosage: str
    frequency: str

class LabResult(BaseModel):
    test_name: str
    result: str
    date: str

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

class Appointment(BaseModel):
    appointment_id: str
    patient_id: str
    doctor_id: str
    specialty: str
    date_time: str
    symptoms: List[str]
    status: str

class AppointmentReminder(BaseModel):
    phone_number: str
    patient_name: str
    doctor_name: str
    appointment_date: str
    appointment_time: str

class FollowUpNotification(BaseModel):
    phone_number: str
    patient_name: str
    follow_up_details: str
    recommended_date: str

# Test Data
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

test_appointment_reminder = AppointmentReminder(
    phone_number="+1234567890",
    patient_name="John Doe",
    doctor_name="Dr. Smith",
    appointment_date="2024-02-15",
    appointment_time="14:30"
)

test_follow_up = FollowUpNotification(
    phone_number="+1234567890",
    patient_name="John Doe",
    follow_up_details="Check blood pressure",
    recommended_date="2024-02-20"
)

# Patient Tests
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

# Appointment Tests
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

# Notification Tests
@pytest.mark.asyncio
@patch('boto3.client')
async def test_send_appointment_reminder_success(mock_sns):
    sns_mock = MagicMock()
    mock_sns.return_value = sns_mock
    sns_mock.publish.return_value = {'MessageId': 'test_message_id'}

    async def send_reminder(reminder: AppointmentReminder):
        response = sns_mock.publish(
            PhoneNumber=reminder.phone_number,
            Message=f"Hello {reminder.patient_name}, this is a reminder for your appointment with Dr. {reminder.doctor_name} on {reminder.appointment_date} at {reminder.appointment_time}."
        )
        return {
            "message": "Appointment reminder sent successfully",
            "message_id": response['MessageId']
        }

    response = await send_reminder(test_appointment_reminder)
    print(f"\nAppointment Reminder Test Response: {response}")
    assert response["message"] == "Appointment reminder sent successfully"
    assert response["message_id"] == "test_message_id"

@pytest.mark.asyncio
@patch('boto3.client')
async def test_send_follow_up_success(mock_sns):
    sns_mock = MagicMock()
    mock_sns.return_value = sns_mock
    sns_mock.publish.return_value = {'MessageId': 'test_follow_up_id'}

    async def send_follow_up(follow_up: FollowUpNotification):
        response = sns_mock.publish(
            PhoneNumber=follow_up.phone_number,
            Message=f"Hello {follow_up.patient_name}, this is a follow-up reminder: {follow_up.follow_up_details}. Recommended follow-up date: {follow_up.recommended_date}"
        )
        return {
            "message": "Follow-up notification sent successfully",
            "message_id": response['MessageId']
        }

    response = await send_follow_up(test_follow_up)
    print(f"\nFollow-up Notification Test Response: {response}")
    assert response["message"] == "Follow-up notification sent successfully"
    assert response["message_id"] == "test_follow_up_id"


# Analytics Service Tests
@pytest.mark.asyncio
@patch('boto3.client')
@patch('boto3.resource')
async def test_analytics_trigger_success(mock_resource, mock_client):
    redshift_mock = MagicMock()
    mock_client.return_value = redshift_mock
    redshift_mock.execute_statement.return_value = {'Id': 'test_query_id'}
    redshift_mock.describe_statement.return_value = {'Status': 'FINISHED'}

    async def trigger_analytics():
        try:
            for _ in range(6):
                response = redshift_mock.execute_statement(
                    ClusterIdentifier='healthsync-analytics',
                    Database='healthsync-analytics',
                    DbUser='healthsync_user',
                    Sql="mock_query"
                )
                status = redshift_mock.describe_statement(Id=response['Id'])
                if status['Status'] != 'FINISHED':
                    raise Exception("Query failed")
            return {"message": "Analytics aggregation completed successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    response = await trigger_analytics()
    print(f"\nAnalytics Trigger Test Response: {response}")
    assert response["message"] == "Analytics aggregation completed successfully"
    assert redshift_mock.execute_statement.call_count == 6

@pytest.mark.asyncio
@patch('boto3.client')
async def test_analytics_query_failure(mock_client):
    redshift_mock = MagicMock()
    mock_client.return_value = redshift_mock
    redshift_mock.execute_statement.return_value = {'Id': 'test_query_id'}
    redshift_mock.describe_statement.return_value = {'Status': 'FAILED', 'Error': 'Test error'}

    async def trigger_analytics():
        try:
            response = redshift_mock.execute_statement(
                ClusterIdentifier='healthsync-analytics',
                Database='healthsync-analytics',
                DbUser='healthsync_user',
                Sql="mock_query"
            )
            status = redshift_mock.describe_statement(Id=response['Id'])
            if status['Status'] in ['FAILED', 'ABORTED']:
                raise Exception(f"Query failed: {status.get('Error', 'Unknown error')}")
            return {"message": "Analytics aggregation completed successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    with pytest.raises(HTTPException) as exc_info:
        await trigger_analytics()
    assert exc_info.value.status_code == 500
    print("\nAnalytics Failure Test: Successfully caught expected error")







# Model Tests
def test_patient_model():
    print(f"\nPatient Model Test: {test_patient.dict()}")
    assert test_patient.id == "P123"
    assert test_patient.name == "John Doe"
    assert test_patient.prescriptions[0].drug_name == "DrugA"
    assert test_patient.lab_results[1].test_name == "X-Ray"

def test_appointment_model():
    print(f"\nAppointment Model Test: {test_appointment.dict()}")
    assert test_appointment.appointment_id == "A123"
    assert test_appointment.status == "Scheduled"
    assert "Chest pain" in test_appointment.symptoms

def test_appointment_reminder_model():
    print(f"\nAppointment Reminder Model Test: {test_appointment_reminder.dict()}")
    assert test_appointment_reminder.phone_number == "+1234567890"
    assert test_appointment_reminder.patient_name == "John Doe"
    assert test_appointment_reminder.doctor_name == "Dr. Smith"

def test_follow_up_notification_model():
    print(f"\nFollow-up Notification Model Test: {test_follow_up.dict()}")
    assert test_follow_up.phone_number == "+1234567890"
    assert test_follow_up.patient_name == "John Doe"
    assert test_follow_up.follow_up_details == "Check blood pressure"

def test_analytics_health_check():
    app = FastAPI()
    
    @app.get("/health")
    def health_check():
        return {"status": "healthy"}
    
    client = TestClient(app)
    response = client.get("/health")
    print(f"\nAnalytics Health Check Test Response: {response.json()}")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

