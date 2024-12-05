from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
from datetime import datetime
from typing import List

app = FastAPI()
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Appointments')

class DoctorAvailability(BaseModel):
    doctor_id: str
    specialty: str
    available_slots: List[str]

class Appointment(BaseModel):
    appointment_id: str
    patient_id: str
    doctor_id: str
    specialty: str
    date_time: str
    symptoms: List[str]
    status: str

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/appointments/")
async def create_appointment(appointment: Appointment):
    try:
        table.put_item(Item=appointment.dict())
        return {"message": "Appointment scheduled", "appointment_id": appointment.appointment_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/doctors/{specialty}/availability")
async def get_doctor_availability(specialty: str):
    try:
        # Add availability check logic
        return {"available_slots": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))