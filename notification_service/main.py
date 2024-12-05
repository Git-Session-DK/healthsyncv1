from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
from datetime import datetime
from typing import Optional

app = FastAPI()
sns = boto3.client('sns')

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

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/notifications/appointment-reminder")
async def send_appointment_reminder(reminder: AppointmentReminder):
    try:
        message = f"Hello {reminder.patient_name}, this is a reminder for your appointment with Dr. {reminder.doctor_name} on {reminder.appointment_date} at {reminder.appointment_time}."
        response = sns.publish(
            PhoneNumber=reminder.phone_number,
            Message=message
        )
        return {
            "message": "Appointment reminder sent successfully",
            "message_id": response['MessageId']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/notifications/follow-up")
async def send_follow_up(follow_up: FollowUpNotification):
    try:
        message = f"Hello {follow_up.patient_name}, this is a follow-up reminder: {follow_up.follow_up_details}. Recommended follow-up date: {follow_up.recommended_date}"
        response = sns.publish(
            PhoneNumber=follow_up.phone_number,
            Message=message
        )
        return {
            "message": "Follow-up notification sent successfully",
            "message_id": response['MessageId']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
