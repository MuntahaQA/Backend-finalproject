## 🏛️ SILA – Backend (API & Data Infrastructure)

The **SILA Backend** powers the unified charity data ecosystem by providing secure APIs, role-based authentication, and integrated data management for **Charities**, **Beneficiaries**, and **Program-Owner Ministries**.  
It enables transparent collaboration between the **Ministry of Human Resources and Social Development (HRSD)** — the superuser authority — and other **ministries** responsible for specific programs (e.g., *Sakani* by the Ministry of Housing, *Takaful* by the Ministry of Education).

This repository focuses on the **server-side logic** — including database models, API endpoints, and administrative control through **Django Admin**.

## 📘 Project & Repository Description

The SILA Backend forms the foundation of the system’s operations. It manages data exchange between government ministries and local charities and ensures that beneficiaries can securely access programs and events.

### Key Responsibilities
- Provide RESTful APIs consumed by the React Frontend  
- Handle authentication using JWT tokens  
- Manage CRUD operations for charities, beneficiaries, events, and program applications  
- Serve as the central integration point for ministries and charity data  
- Offer a secure admin interface for HRSD via Django Admin  

### System Roles
- **HRSD (Super User):** Full access via Django Admin; manages charities and national programs.  
- **Charity Admin:** Manages beneficiaries and events; read-only access to program status.  
- **Beneficiary:** Logs in to manage their own data, register for events, and apply for available programs.

---
## 🧩 Tech Stack

- **Programming Language:** Python 3.11  
- **Framework:** Django 5 + Django REST Framework (DRF)  
- **Authentication:** JWT (SimpleJWT)  
- **Database:** PostgreSQL  
- **Containerization:** Docker 
- **Admin Interface:** Django Admin  
- **Deployment:** 
- **Development Environment:** Visual Studio Code  


## 🔗 Related Repositories & Links

| Item | Link |
|------|------|
| **Frontend Repository** | [SILA Frontend Repo](https://github.com/MuntahaQA/sila_frontend) |
| **Backend Repository** | [SILA Backend Repo](https://github.com/MuntahaQA/sila_backend) |
| **Live Backend Site (API)** | 

## 🗺️ ERD Diagram
![ERD](./assets/sila_ERD.svg)
**Main Entities:**
- `User` → base authentication model (roles: superuser(HRSD),Charity Admin, Beneficiary)  
- `Charity` → organization profile  
- `Beneficiary` → person registered under a charity  
- `Event` → charity event for beneficiaries  
- `Program` → government support program  

## 🧭 Routing Table

| Route | Method | Access | Role | Description |
|---------|---------|---------|---------|-------------|
| `/` | GET | Public | Any | Landing page with overview and login entry. |
| `/login` | GET / POST | Public | Charity Admin, Beneficiary | Display login and submit credentials. |
| `/logout` | POST | Protected | All | End user session and redirect to the landing page. |
| `/admin` | GET | Protected | Ministry | Django Admin: manage charities and government programs. |
| `/ministry/dashboard` | GET | Protected | Ministry | Dashboard showing all charities, programs, and overall stats. |
| `/charity/dashboard` | GET | Protected | Charity Admin | KPIs for one charity (beneficiaries, events, programs). |
| `/charity/settings` | GET / PATCH | Protected | Charity Admin | View or update charity information and settings. |
| `/beneficiaries` | GET | Protected | Charity Admin | List and search beneficiaries. |
| `/beneficiaries/new` | POST | Protected | Charity Admin | Create a new beneficiary record. |
| `/beneficiaries/:id` | GET | Protected | Charity Admin | View beneficiary details. |
| `/beneficiaries/:id/edit` | PATCH / PUT | Protected | Charity Admin | Update beneficiary information. |
| `/beneficiaries/:id/delete` | DELETE | Protected | Charity Admin | Delete a beneficiary (with confirmation). |
| `/events` | GET | Protected | Charity Admin | List events created by this charity. |
| `/events/new` | POST | Protected | Charity Admin | Create a new event. |
| `/events/:id` | GET | Protected | Charity Admin, Beneficiary | View event details. |
| `/events/:id/edit` | PATCH / PUT | Protected | Charity Admin | Edit existing event. |
| `/events/:id/delete` | DELETE | Protected | Charity Admin | Delete an event. |
| `/events/:id/register` | POST | Protected | Beneficiary | Register for an event (check capacity/waitlist). |
| `/events/:id/cancel` | POST / DELETE | Protected | Beneficiary | Cancel an event registration. |
| `/events/:id/registrations` | GET | Protected | Charity Admin | Manage event registrations (confirm, mark attended, export). |
| `/programs` | GET | Protected | Charity Admin, Beneficiary | View available government support programs. |
| `/programs/:id` | GET | Protected | Charity Admin, Beneficiary | View detailed info about a program. |
| `/programs/:id/apply` | POST | Protected | Beneficiary | Apply to a program. |
| `/programs/:id/application` | GET | Protected | Beneficiary | View or edit the beneficiary’s own application. |
| `/programs/:id/application/submit` | POST | Protected | Beneficiary | Submit a completed application (to Ministry). |
| `/programs/:id/application/cancel` | POST / DELETE | Protected | Beneficiary | Cancel or withdraw an application. |
| `/profile/programs` | GET | Protected | Beneficiary | View my program applications and statuses. |
| `/beneficiaries/:id/programs` | GET | Protected | Charity Admin | Read-only: see which programs this beneficiary has applied to and their current status. |
| `/Profile` | GET | Protected | Beneficiary | View own profile information. |
| `/Profile/edit` | PATCH / PUT | Protected | Beneficiary | Edit personal info (contact, address, etc.). |
| `/Profile/events` | GET | Protected | Beneficiary | View charity events available to this beneficiary. |
| `/Profile/programs` | GET | Protected | Beneficiary | View support programs available to this beneficiary. |

---

**Access:**  
- *Public* = No login required  
- *Protected* = Requires login (JWT)

**Roles:**  
- **Ministry (Super User):** Uses Django Admin `/admin` to manage charities & programs  
- **Charity Admin:** Manages beneficiaries, events, and reviews program applications  
- **Beneficiary:** Can log in to view/edit data, register for events, and apply to programs  

**Methods:**  
- `GET` → Retrieve or display data  
- `POST` → Create or submit data  
- `PUT / PATCH` → Update existing data  
- `DELETE` → Remove data  

## 🚀 Installation Instructions

### Option 1: Using Docker (Recommended)

1. **Clone the Repository**
   ```bash
   git clone https://github.com/MuntahaQA/sila_backend
   cd sila_backend
   ```

2. **Create Environment File**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

3. **Start Services with Docker Compose**
   ```bash
   docker-compose up --build
   ```

   This will:
   - Start PostgreSQL database
   - Run Django migrations
   - Start the Django development server on `http://localhost:8000`

4. **Create Superuser (in another terminal)**
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

### Option 2: Manual Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/MuntahaQA/sila_backend
   cd sila_backend
   ```

2. **Install Dependencies**
   ```bash
   pip install pipenv
   pipenv install
   pipenv shell
   ```

3. **Set up Environment Variables**
   Create a `.env` file in the backend directory:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   DB_NAME=sila
   DB_USER=postgres
   DB_PASSWORD=your-password
   DB_HOST=localhost
   DB_PORT=5432
   CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
   ```

4. **Set up Database**
   ```bash
   python manage.py migrate
   ```

5. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

### API Endpoints

The API will be available at:
- Home: `http://localhost:8000/`
- API Root: `http://localhost:8000/api/`
- Admin: `http://localhost:8000/admin/`
- Token Obtain: `http://localhost:8000/api/token/`
- Token Refresh: `http://localhost:8000/api/token/refresh/`

### Testing

Run tests with:
```bash
python manage.py test
```

## 🧊 IceBox Features

Future enhancements planned for the SILA Backend:
- AI-powered beneficiary prioritization algorithms
- Advanced analytics and reporting endpoints
- Real-time notifications system
- Integration with external government APIs
- Mobile API optimizations
- Rate limiting and advanced security features