import boto3
import logging
from datetime import datetime
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI()

# AWS clients
redshift_client = boto3.client('redshift-data', region_name='ap-south-1')
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')

appointments_table = dynamodb.Table('Appointments')
patients_table = dynamodb.Table('PatientRecords')

async def wait_for_query_completion(query_id):
    while True:
        status = redshift_client.describe_statement(Id=query_id)
        if status['Status'] == 'FINISHED':
            return True
        if status['Status'] in ['FAILED', 'ABORTED']:
            logger.error(f"Query failed: {status.get('Error', 'Unknown error')}")
            return False
        await asyncio.sleep(2)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/run-analytics")
async def trigger_analytics():
    try:
        # Create tables if they don't exist
        create_tables_queries = [
            """
            CREATE TABLE IF NOT EXISTS doctor_metrics (
                doctor_id VARCHAR(50),
                specialty VARCHAR(100),
                appointment_count INT,
                date_range_start DATE,
                date_range_end DATE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS time_metrics (
                date DATE,
                specialty VARCHAR(100),
                daily_appointments INT,
                weekly_appointments INT,
                monthly_appointments INT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS specialty_insights (
                specialty VARCHAR(100),
                symptom VARCHAR(100),
                condition VARCHAR(100),
                occurrence_count INT,
                percentage DECIMAL(5,2)
            )
            """
        ]

        # Run aggregation queries
        metrics_queries = [
            """
            INSERT INTO doctor_metrics
            SELECT 
                doctor_id,
                specialty,
                COUNT(*) as appointment_count,
                MIN(date) as date_range_start,
                MAX(date) as date_range_end
            FROM appointments
            GROUP BY doctor_id, specialty
            """,
            """
            INSERT INTO time_metrics
            SELECT 
                date,
                specialty,
                COUNT(*) as daily_appointments,
                COUNT(*) OVER (PARTITION BY specialty, DATE_TRUNC('week', date)) as weekly_appointments,
                COUNT(*) OVER (PARTITION BY specialty, DATE_TRUNC('month', date)) as monthly_appointments
            FROM appointments
            GROUP BY date, specialty
            """,
            """
            INSERT INTO specialty_insights
            SELECT 
                specialty,
                symptoms as symptom,
                NULL as condition,
                COUNT(*) as occurrence_count,
                100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY specialty) as percentage
            FROM appointments
            GROUP BY specialty, symptoms
            """
        ]

        all_queries = create_tables_queries + metrics_queries
        
        for query in all_queries:
            logger.info(f"Executing query: {query[:100]}...")
            response = redshift_client.execute_statement(
                ClusterIdentifier='healthsync-analytics',
                Database='healthsync-analytics',
                DbUser='healthsync_user',
                Sql=query
            )
            success = await wait_for_query_completion(response['Id'])
            if not success:
                raise HTTPException(status_code=500, detail="Query execution failed")

        return {"message": "Analytics aggregation completed successfully"}
        
    except Exception as e:
        logger.error(f"Error during analytics aggregation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Aggregator Service Running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)

