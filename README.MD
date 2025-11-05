# 🏛️ SILA – Backend 

The **SILA Backend** powers the unified national platform that connects **Government Ministries** and **Local Charities** to coordinate and deliver social support programs.  
It provides secure APIs, robust data models, and centralized management to ensure **unified and synchronized data** across all entities within the SILA ecosystem.

---

## 📘 Project Description

The **SILA Backend** forms the operational core of the SILA system — managing all server-side processes, authentication, and data exchange between ministries and charities.  
Built with **Django**, it ensures security, scalability, and transparency in managing social assistance programs and beneficiary records.  
All data within the platform is **centrally managed**, maintaining consistency between ministry dashboards, charity records, and event data.

- 🏢 **Ministry Users** can create and manage **government support programs**, monitor applications, and access detailed analytics dashboards.  
- 🕊️ **Charity Users** can register and manage **beneficiaries**, organize **charity events**, and track participation and outcomes.  

The backend serves as the main communication layer between the database and the frontend client, handling API requests, business logic, and user role management — ensuring seamless and secure data flow across all connected systems.

---

## 🗂️ Repository Description

This repository contains all **server-side code** and logic for the SILA platform, including:

- **Core Applications:** Django apps for charities, ministries, beneficiaries, programs, and events.  
- **API Endpoints:** Secure RESTful endpoints for CRUD operations and data synchronization.  
- **Authentication System:** JWT-based role management for ministries and charities.  
- **Database Models:** Centralized schema ensuring consistent data across all system modules.  
- **Admin Interface:** Django Admin for superuser and ministry-level management.  
- **Unified Data Layer:** Guarantees accurate and synchronized information shared across all user types.

---
## ⚙️ Tech Stack

| Category | Technology |
|-----------|-------------|
| **Language** | Python |
| **Framework** | Django 5 |
| **API Toolkit** | Django REST Framework |
| **Authentication** | JWT (SimpleJWT) |
| **Database** | PostgreSQL |
|

| Repository | Link |
|-------------|------|
| **Frontend Repository** | [Fawatiri Frontend Repo](https://github.com/MuntahaQA/Frontend-finalproject) |
| **Backend Repository** | [Fawatiri Backend Repo](https://github.com/MuntahaQA/Backend-finalproject) | |
| **Live Backend** | http://localhost:8000
 |


## 🗺️ ERD Diagram
![ERD](./assets/sila_ERD.svg)

## 🧭 Routing Table


### 🏠 Home
| Route | Method | Access | Role | Description |
|--------|--------|--------|--------|-------------|
| `/` | GET | Public | Any | Landing page (Home). |

---

### 🏢 Charities
| Route | Method | Access | Role | Description |
|--------|--------|--------|--------|-------------|
| `/charities/` | GET | Public | Any | List all registered charities. |
| `/charities/<int:charity_id>/` | GET | Public | Any | Display detailed information about a specific charity. |

---

### 🕊️ Beneficiaries (Managed by Charity)
| Route | Method | Access | Role | Description |
|--------|--------|--------|--------|-------------|
| `/beneficiaries/` | GET, POST | Protected | Charity Admin | List or create beneficiaries under the logged-in charity. |
| `/beneficiaries/<int:beneficiary_id>/` | GET, PATCH, DELETE | Protected | Charity Admin | Retrieve, update, or delete beneficiary details. |

---

### 🏛️ Programs (Managed by Ministry)
| Route | Method | Access | Role | Description |
|--------|--------|--------|--------|-------------|
| `/programs/` | GET, POST | Protected | Ministry | List or create government support programs. |
| `/programs/<int:program_id>/` | GET, PATCH, DELETE | Protected | Ministry | Retrieve, update, or delete a program. |
| `/programs/<int:program_id>/applications/` | GET, POST | Protected | Ministry | View or create applications for this program *(feature under development)*. |
| `/programs/<int:program_id>/statistics/` | GET | Protected | Ministry | View performance metrics and KPIs for a specific program. |

---

### 📊 Analytics & Statistics
| Route | Method | Access | Role | Description |
|--------|--------|--------|--------|-------------|
| `/ministry/statistics/` | GET | Protected | Ministry | Ministry-wide analytics dashboard. |
| `/charity/statistics/` | GET | Protected | Charity Admin | Analytics for charity performance (beneficiaries, events, etc.). |

---

### 🎉 Events (Managed by Charity)
| Route | Method | Access | Role | Description |
|--------|--------|--------|--------|-------------|
| `/events/` | GET, POST | Protected | Charity Admin | List or create events for the charity. |
| `/events/<int:event_id>/` | GET, PATCH, DELETE | Protected | Charity Admin | Retrieve, update, or delete event details. |
| `/events/<int:event_id>/registrations/` | GET | Protected | Charity Admin | View and manage registrations for a specific event. |
| `/events/<int:event_id>/registrations/<int:registration_id>/` | DELETE | Protected | Charity Admin | Delete or cancel a specific registration. |

---

### 🔐 Authentication & User Management
| Route | Method | Access | Role | Description |
|--------|--------|--------|--------|-------------|
| `/users/signup/` | POST | Public | Any | Create a general user account. |
| `/users/login/` | POST | Public | Any | Authenticate user and issue access tokens. |
| `/users/token/refresh/` | POST | Public* | Any | Refresh access token using a valid refresh token. |
| `/users/profile/` | GET | Protected | Any (Authenticated) | Retrieve current user profile. |
| `/charities/register/` | POST | Public | Any | Register a charity organization account. |
| `/ministries/register/` | POST | Public | Any | Register a ministry organization account. |



---

✅ **Summary**
- **Ministry**: Can manage programs and view analytics.  
- **Charity Admin**: Can manage beneficiaries, create events, and view analytics.  
- **Beneficiary**: (Future Phase) Will be able to register for programs/events once B2C features are added.

---

## 🚀 Installation Instructions Using Docker


1. **Clone the repository**
   ```bash
   git clone https://github.com/MuntahaQA/Backend-finalproject
   ```

2. **Start with Docker Compose**

    ```bash
   docker-compose up
   ```

The application will be available at http://localhost:8000



## 🧊 IceBox Features

Future enhancements planned for the **SILA Backend** include:
- 📱 **Mobile API Optimization:** Enhance API performance and structure for seamless integration with future iOS and Android applications.  
- 🤖 **AI-Powered Beneficiary Prioritization:** Automatically rank and match beneficiaries to the most suitable programs based on eligibility and needs.  
- 👤 **Beneficiary Portal (B2C Expansion):** Allow beneficiaries to Login , apply directly to ministry programs and charity events, and track their application status.  
- 🛡️ **Rate Limiting & Security Enhancements:** Implement advanced request throttling, JWT refresh tokens, and audit logging for maximum system protection.  
- 🔔 **Real-Time Notifications System:** Enable instant alerts for new program openings, approvals, and event updates.  

- 💪 **Volunteer Management API:**  
  Extend the backend to support **volunteer registration and event participation tracking**.  
  Charities will be able to post volunteering opportunities, and users can register or track their volunteering activities through API endpoints.

- 💰 **Donation Management System:**  
  Implement secure **donation endpoints** that allow individuals and organizations to donate to verified charities.  
  This includes transaction tracking, reporting for transparency, and integration with national payment gateways (e.g., Mada, Apple Pay).



