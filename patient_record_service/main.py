from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
from typing import Optional, List

app = FastAPI()
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('PatientRecords')

class LabResult(BaseModel):
    date: str
    test_name: str
    result: str

class Prescription(BaseModel):
    medication: str
    dosage: str
    duration: str
    date_prescribed: str

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

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/patients/")
async def create_patient(patient: Patient):
    try:
        table.put_item(Item=patient.dict())
        return {"message": "Patient record created", "patient_id": patient.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/patients/{patient_id}")
async def get_patient(patient_id: str):
    try:
        response = table.get_item(Key={'id': patient_id})
        if 'Item' not in response:
            raise HTTPException(status_code=404, detail="Patient not found")
        return response['Item']
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/patients/{patient_id}")
async def update_patient(patient_id: str, patient: Patient):
    try:
        patient_dict = patient.dict()
        patient_dict['id'] = patient_id
        table.put_item(Item=patient_dict)
        return {"message": "Patient record updated", "patient_id": patient_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/patients/{patient_id}")
async def delete_patient(patient_id: str):
    try:
        table.delete_item(Key={'id': patient_id})
        return {"message": "Patient record deleted", "patient_id": patient_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# test commit