# SmartParcel NET214 Final Project

SmartParcel is a **serverless parcel delivery system** built on AWS for NET214 Network Programming.  
It demonstrates a scalable, event-driven architecture using fully managed AWS services.

---

## 👨‍🎓 Student Information
- **Name:** Ahmad Aljanahi  
- **Student ID:** 20210001364  
- **AWS Region:** ap-southeast-2  

---

## ☁️ AWS Services Used
- API Gateway (REST API)
- AWS Lambda (Serverless compute)
- DynamoDB (NoSQL database)
- S3 (Object storage)
- SQS (Message queue)
- SNS (Notifications)
- CloudWatch (Monitoring & alarms)
- CloudTrail (Auditing)
- CloudFormation (Infrastructure as Code)
- VPC (Networking)

---

## ⚙️ System Architecture
Client (Postman / CloudShell)
↓
API Gateway (REST API)
↓
Lambda API (Business Logic)
↓
DynamoDB (Parcel Storage)
↓
SQS (Event Queue)
↓
Lambda Notifier
↓
SNS (Email Notification)

---

## 🚀 Features
- Create parcel (POST)
- Get parcel by ID (GET)
- List all parcels (Admin only)
- Filter parcels by status (using GSI)
- Update parcel status (Driver only)
- Delete parcel (Admin only, only if registered)
- Event-driven notification system
- Dead Letter Queue for failed messages
- Concurrent load testing (20 requests)

---

## 🔐 Security
- API Key authentication (API Gateway)
- Role-based access control (Driver / Customer / Admin)
- IAM Least Privilege policies
- S3 encryption (SSE-S3)
- HTTPS for secure communication

---

## 📊 Monitoring & Logging
- CloudWatch Alarms (Lambda errors)
- CloudWatch Dashboard (metrics visualization)
- CloudTrail (API activity auditing)

---

## ⚡ Performance
- Serverless auto-scaling (Lambda + API Gateway)
- DynamoDB On-Demand scaling
- Global Secondary Index (status-index) for fast queries

---

## 🧪 Load Testing
- Implemented using Python ThreadPoolExecutor
- 20 concurrent requests tested
- 100% success rate achieved

---

## 🏗️ Infrastructure as Code
- Full system deployed using **CloudFormation (YAML)**
- Enables repeatable and automated deployments

---

## 📦 Repository Contents
- `smartparcel.yaml` → CloudFormation template  
- `api_lambda.py` → Main API logic  
- `notifier_lambda.py` → Notification handler  
- `load_test.py` → Concurrent testing script  

---

## ✅ Status
✔ API tested successfully  
✔ Notification system working (SQS → SNS → Email)  
✔ Monitoring and logging configured  
✔ Fully serverless deployment  

---

## 📌 Notes
This project follows AWS best practices in:
- Scalability  
- Reliability  
- Security  
- Cost optimization  

---

## 🎯 Conclusion
SmartParcel demonstrates a complete real-world cloud solution using AWS serverless services.  
It showcases how distributed systems can be built efficiently using event-driven architecture.

---
