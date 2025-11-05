from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Charity, Beneficiary, Program, Event, EventRegistration, ProgramApplication
from datetime import date, datetime, timedelta


class CharityModelTest(TestCase):
    """Test Charity model"""
    
    def setUp(self):
        self.charity = Charity.objects.create(
            name='Test Charity',
            registration_number='REG123',
            email='test@charity.com',
            phone='1234567890',
            address='123 Test St',
            city='Riyadh',
            region='Riyadh'
        )

    def test_charity_str(self):
        self.assertEqual(str(self.charity), 'Test Charity')

    def test_charity_creation(self):
        self.assertEqual(self.charity.name, 'Test Charity')
        self.assertEqual(self.charity.registration_number, 'REG123')
        self.assertTrue(self.charity.is_active)


class BeneficiaryModelTest(TestCase):
    """Test Beneficiary model"""
    
    def setUp(self):
        self.charity = Charity.objects.create(
            name='Test Charity',
            registration_number='REG123',
            email='test@charity.com',
            phone='1234567890',
            address='123 Test St',
            city='Riyadh',
            region='Riyadh'
        )
        self.user = User.objects.create_user(
            username='beneficiary1',
            email='ben@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Beneficiary'
        )
        self.beneficiary = Beneficiary.objects.create(
            user=self.user,
            charity=self.charity,
            national_id='1234567890',
            phone='0987654321',
            address='456 Beneficiary Ave',
            city='Riyadh',
            region='Riyadh',
            date_of_birth=date(1990, 1, 1)
        )

    def test_beneficiary_str(self):
        expected = f"{self.user.get_full_name()} - {self.beneficiary.national_id}"
        self.assertEqual(str(self.beneficiary), expected)

    def test_beneficiary_creation(self):
        self.assertEqual(self.beneficiary.user, self.user)
        self.assertEqual(self.beneficiary.charity, self.charity)
        self.assertEqual(self.beneficiary.national_id, '1234567890')


class ProgramModelTest(TestCase):
    """Test Program model"""
    
    def setUp(self):
        self.program = Program.objects.create(
            name='Test Program',
            description='A test program',
            ministry_owner='Ministry of Test',
            status='ACTIVE',
            eligibility_criteria='Must be eligible',
            max_capacity=100
        )

    def test_program_str(self):
        self.assertEqual(str(self.program), 'Test Program')

    def test_program_creation(self):
        self.assertEqual(self.program.name, 'Test Program')
        self.assertEqual(self.program.status, 'ACTIVE')


class EventModelTest(TestCase):
    """Test Event model"""
    
    def setUp(self):
        self.charity = Charity.objects.create(
            name='Test Charity',
            registration_number='REG123',
            email='test@charity.com',
            phone='1234567890',
            address='123 Test St',
            city='Riyadh',
            region='Riyadh'
        )
        self.event = Event.objects.create(
            charity=self.charity,
            title='Test Event',
            description='A test event',
            event_date=datetime.now() + timedelta(days=30),
            location='Test Location',
            city='Riyadh',
            max_capacity=50
        )

    def test_event_str(self):
        expected = f"{self.event.title} - {self.charity.name}"
        self.assertEqual(str(self.event), expected)

    def test_event_available_spots(self):
        self.assertEqual(self.event.available_spots(), 50)
        self.event.current_registrations = 30
        self.event.save()
        self.assertEqual(self.event.available_spots(), 20)


class APITest(TestCase):
    """Test API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.charity = Charity.objects.create(
            name='Test Charity',
            registration_number='REG123',
            email='test@charity.com',
            phone='1234567890',
            address='123 Test St',
            city='Riyadh',
            region='Riyadh'
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='adminpass123'
        )

    def test_home_endpoint(self):
        """Test home endpoint is accessible"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

    def test_charities_list_requires_auth(self):
        """Test that charities endpoint requires authentication"""
        response = self.client.get('/api/charities/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_programs_list_requires_auth(self):
        """Test that programs endpoint requires authentication"""
        response = self.client.get('/api/programs/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_jwt_token_obtain(self):
        """Test JWT token obtain endpoint"""
        response = self.client.post('/api/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_authenticated_charities_access(self):
        """Test authenticated user can access charities"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/charities/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)