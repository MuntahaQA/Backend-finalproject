# Programs Model Setup Guide

## Overview
تم إنشاء مودل Programs مع CRUD operations كاملة وملء قاعدة البيانات بالبرامج الحكومية.

## Changes Made

### 1. Model Updates (`main_app/models.py`)
- ✅ Added `estimated_beneficiaries` field to Program model
- ✅ Made `eligibility_criteria` optional (blank=True)
- ✅ Added verbose names for admin panel

### 2. Serializer Updates (`main_app/serializers.py`)
- ✅ Added `estimated_beneficiaries` to ProgramSerializer fields

### 3. ViewSet Updates (`main_app/views.py`)
- ✅ Changed ProgramViewSet from ReadOnlyModelViewSet to ModelViewSet (full CRUD)
- ✅ Added permissions: Only superusers can create/update/delete
- ✅ All authenticated users can view active programs
- ✅ Kept the `apply` action for beneficiaries

### 4. Admin Panel (`main_app/admin.py`)
- ✅ Enhanced ProgramAdmin with better organization
- ✅ Added list filters and search fields

### 5. Management Command (`main_app/management/commands/load_programs.py`)
- ✅ Created command to load initial programs data

## Programs Data

البرامج التي سيتم تحميلها:

1. **برنامج الضمان الاجتماعي المطور** - أكثر من 1.8 مليون أسرة
2. **برنامج سكني (Sakani)** - أكثر من 150 ألف أسرة سنويًا
3. **برنامج دعم الغذاء** - قرابة 1.2 مليون أسرة
4. **برنامج تمويل الأسر المنتجة** - أكثر من 17 ألف أسرة
5. **برنامج ترميم المنازل للأسر الفقيرة** - حوالي 10 آلاف أسرة سنويًا

## Setup Instructions

### Step 1: Create Migrations
```bash
cd backend
python manage.py makemigrations
```

### Step 2: Apply Migrations
```bash
python manage.py migrate
```

### Step 3: Load Programs Data
```bash
python manage.py load_programs
```

## API Endpoints

### List All Programs (GET)
```
GET /api/programs/
```
- **Access**: All authenticated users
- **Returns**: List of active programs (all programs for superusers)

### Get Program Details (GET)
```
GET /api/programs/{id}/
```

### Create Program (POST) - Superuser Only
```
POST /api/programs/
Content-Type: application/json

{
  "name": "Program Name",
  "description": "Program description",
  "ministry_owner": "Ministry Name",
  "estimated_beneficiaries": "Number of beneficiaries",
  "status": "ACTIVE",
  "eligibility_criteria": "Criteria details"
}
```

### Update Program (PUT/PATCH) - Superuser Only
```
PUT /api/programs/{id}/
PATCH /api/programs/{id}/
```

### Delete Program (DELETE) - Superuser Only
```
DELETE /api/programs/{id}/
```

### Apply to Program (POST)
```
POST /api/programs/{id}/apply/
```
- **Access**: Beneficiaries only
- Creates a ProgramApplication with status 'PENDING'

## Example API Responses

### List Programs
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "برنامج الضمان الاجتماعي المطور",
      "description": "يوفّر دعمًا ماليًا شهريًا...",
      "ministry_owner": "وزارة الموارد البشرية والتنمية الاجتماعية",
      "estimated_beneficiaries": "أكثر من 1.8 مليون أسرة",
      "status": "ACTIVE",
      "eligibility_criteria": "الأسر الأشد احتياجًا...",
      "application_count": 0,
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

## Permissions

- **Superusers**: Full CRUD access
- **Charity Admins**: Read-only access to active programs
- **Beneficiaries**: Read-only access to active programs + can apply
- **Unauthenticated**: No access

