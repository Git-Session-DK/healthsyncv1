# **Runbook: Guide for Deploying and Testing the MediTrack Platform**
![External Image](https://www.appletechsoft.com/wp-content/uploads/2020/06/Hospital-Management-System.jpg)

This document provides a detailed and step-by-step approach to deploy, test, and maintain the MediTrack platform using Amazon EKS, Kubernetes, and GitHub Actions. The solution ensures scalability, fault tolerance, and efficient automation in a microservices architecture. 

---

## **1. Prerequisites**

### **AWS Cloud Infrastructure**
- **Amazon EKS Cluster**:
  - Cluster Name: `healthsync-cluster`
  - Region: `ap-south-1`
  - Nodes: Managed node group with autoscaling enabled.
- **Amazon DynamoDB Tables**:
  - `PatientRecords`: Stores patient demographics, medical history, and prescriptions.
  - `Appointments`: Handles doctor availability and appointment bookings.
- **Amazon Redshift Cluster**:
  - Name: `healthsync-analytics`
  - Use Case: Aggregated analytics and reporting.
- **Amazon SNS**:
  - Notification Topics for appointment reminders and patient follow-ups.

### **Development Environment**
- **Tools Installed**:
  - [AWS CLI](https://aws.amazon.com/cli/) configured with appropriate IAM roles.
  - `kubectl` for Kubernetes cluster management.
  - Docker for building and managing container images.
  - `pytest` for automated test execution.
  - Git for version control.
- **GitHub Repository**:
  - Contains:
    - Service source code (Python-based microservices).
    - Kubernetes YAML manifests.
    - CI/CD pipeline definitions.
    - Test automation scripts.

### **Access Details**:
- AWS Console and CLI credentials with administrative privileges.
- Access to the GitHub repository with write permissions.

---

## **2. Deployment Process**

### **Step 1: Clone the Repository**
1. Clone the MediTrack repository to your local environment:
    ```bash
    git clone https://github.com/<username>/healthsync.git
    cd healthsync
    ```

### **Step 2: AWS Configuration**
1. Clone the MediTrack repository to your local environment:
    ```bash
    aws configure
    # Enter your AWS Access Key
    # Enter your AWS Secret Key
    # Region: ap-south-1
    # Output format: json
    ```

### **Step 3: Build Docker Images**
1. Login to Amazon ECR: Use AWS CLI to log in to Amazon ECR:
    ```bash
    aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin <ecr-repo-url>
    ```
2. Build and tag Docker images for each service:
    ```bash
    cd healthsync/patient_service
    docker build -t <ecr-repo-url>/patient-service:latest .
    docker push <ecr-repo-url>/patient-service:latest
    
    cd ../appointment_service
    docker build -t <ecr-repo-url>/appointment-service:latest .
    docker push <ecr-repo-url>/appointment-service:latest
    
    cd ../notification_service
    docker build -t <ecr-repo-url>/notification-service:latest .
    docker push <ecr-repo-url>/notification-service:latest

    cd ../aggregator_service
    docker build -t <ecr-repo-url>/aggregator-service:latest .
    docker push <ecr-repo-url>/aggregator-service:latest
    
    ```


### **Step 4: Deploy to Kubernetes**
1. Apply Kubernetes manifests for microservices:
    ```bash
    kubectl apply -f kubernetes/patient-service-blue.yml -n healthsync
    kubectl apply -f kubernetes/patient-service-green.yml -n healthsync
    kubectl apply -f kubernetes/appointment-service-blue.yml -n healthsync
    kubectl apply -f kubernetes/appointment-service-green.yml -n healthsync
    kubectl apply -f kubernetes/notification-service-blue.yml -n healthsync
    kubectl apply -f kubernetes/notification-service-green.yml -n healthsync
    kubectl apply -f kubernetes/aggregator-service-blue.yml -n healthsync
    kubectl apply -f kubernetes/aggregator-service-green.yml -n healthsync
    ```
2. Deploy blue-green strategy for traffic management:
    ```bash
    kubectl apply -f kubernetes/router-services.yml -n healthsync
    ```

### **Step 5: Verify Deployment**
1. Check pod statuses:
    ```bash
    kubectl get pods -n healthsync
    ```
2. Retrieve service endpoints:
    ```bash
    kubectl get services -n healthsync
    ```

---

## **3. Post-Deployment Testing**

### **Step 1: API Validation**
- Test microservice endpoints using Postman/Thunder Client or `curl`:
    - **Patient Service**:
        ```bash
        curl -X POST <load-balancer-url>/patients/ -d '<json-data>'
        curl <load-balancer-url>/patients/{patient_id}
        ```
    - **Appointment Service**:
        ```bash
        curl -X POST <load-balancer-url>/appointments/ -d '<json-data>'
        ```
    - **Notification Service**:
        ```bash
        curl -X POST <load-balancer-url>/notifications/appointment reminder/ -d '<json-data>'
        ```

### **Step 2: Automated Test Execution**
1. Run the test suite from your local environment:
    ```bash
    pytest tests/
    ```
2. View GitHub Actions for CI pipeline results.

### **Step 3: Monitoring and Metrics**
1. Access Prometheus and Grafana dashboards:
    ```bash
    kubectl port-forward svc/prometheus-grafana -n monitoring 3000:80
    ```
2. Login credentials:
   - Default Username: `admin`
   - Default Password: `prom-operator`
3. Validate service health and resource utilization.

---

## **4. Analytics and Visualization**

### **Step 1: Amazon Redshift Integration**
1. Verify data ingestion:
    - Tables: `doctor_metrics`, `time_metrics`, `specialty_insights`.
    - Query data using SQL Workbench or AWS Redshift Query Editor.

2. Sample query for patient trends:
    ```sql
    SELECT doctor_specialty, COUNT(appointment_id) AS total_appointments
    FROM time_metrics
    GROUP BY doctor_specialty
    ORDER BY total_appointments DESC;
    ```

### **Step 2: Visualization with AWS QuickSight**
1. Create datasets from Redshift tables.
2. Build dashboards for:
   - Doctor performance metrics.
   - Speciality Insights and Symptom Analysis
   - Appointment trends.
   

---

## **5. Rollback Strategy**

In case of failures, revert to a stable deployment using the blue-green approach:
1. Scale down the green deployment:
    ```bash
    kubectl scale deployment patient-service-green --replicas=0 -n healthsync
    ```
2. Redirect traffic to the blue environment:
    ```bash
    kubectl edit svc patient-service-blue -n healthsync
    ```

---

## **6. Troubleshooting Guide**

### **Common Issues**
1. **Pipeline Failures**:
   - Inspect GitHub Actions logs.
2. **Service Unavailability**:
   - Check pod logs:
        ```bash
        kubectl logs <pod-name> -n healthsync
        ```
3. **AWS CLI Errors**:
   - Reconfigure credentials:
        ```bash
        aws configure
        ```

### **Debugging Tips**
- Verify Kubernetes DNS:
    ```bash
    kubectl get configmap -n kube-system
    ```
- Test service connectivity using `nslookup` within the cluster:
    ```bash
    kubectl exec -it <pod-name> -- nslookup patient-service
    ```

---

## **7. Key File Structure**

- **Source Code**:
  - `/healthsync/`
    - patient_record_service
    - appointment_scheduling_service
    - notification_service
    - aggregator_service
- **Kubernetes Manifests**:
  - `/kubernetes/`
    - Deployment files for services.
    - Router configuration.
- **CI/CD Pipelines**:
  - `/.github/workflows/`
    - `servicename-service-ci.yml`
    - `deploy-cd.yml`
- **Test Suite**:
  - `/tests/`
    - Unit tests for microservices.
    - Integration tests.

---

## **8. Best Practices**

1. **Security**:
   - Enable IAM roles for service accounts.
   - Enforce least-privilege access for resources.
2. **Scalability**:
   - Use horizontal pod autoscaling.
   - Enable DynamoDB on-demand capacity mode.
3. **Observability**:
   - Integrate with AWS CloudWatch for centralized logging.

---

## **9. Summary**

This runbook ensures a seamless deployment and testing experience for the MediTrack platform. Following these steps will guarantee a reliable, scalable, and secure system to manage patient records and appointments effectively.

**Author**: Dumindu Mahai Waduge  
**Date**: 07-12-2024  
**Contact**: [duminyk95@gmail.com](mailto:duminyk95@gmail.com)
