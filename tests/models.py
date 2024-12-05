from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Patient(BaseModel):
    id: str
    name: str
    date_of_birth: str
    contact: str
    medical_history: Optional[str]

class Appointment(BaseModel):
    appointment_id: str
    patient_id: str
    doctor_id: str
    appointment_date: str
    status: str
