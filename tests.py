# Test Suite for Bus Ticket Booking System

import unittest
import json
import tempfile
import os
from datetime import datetime
from app import create_app
from models import TicketManager, Ticket, Bus
from utils import (
    validate_passenger_name, validate_bus_number, validate_seat_number,
    format_seat_number, format_bus_number, sanitize_input,
    validate_ticket_data, calculate_fare, get_seat_type
)
from database import DatabaseManager

class TestModels(unittest.TestCase):
    """Test cases for model classes"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.ticket_manager = TicketManager()
    
    def test_ticket_creation(self):
        """Test ticket creation"""
        ticket = Ticket(1, "John Doe", "BUS001", "S01")
        
        self.assertEqual(ticket.id, 1)
        self.assertEqual(ticket.name, "John Doe")
        self.assertEqual(ticket.bus, "BUS001")
        self.assertEqual(ticket.seat, "S01")
        self.assertEqual(ticket.status, "confirmed")
        self.assertIsInstance(ticket.booking_time, datetime)
    
    def test_ticket_to_dict(self):
        """Test ticket dictionary conversion"""
        ticket = Ticket(1, "John Doe", "BUS001", "S01")
        ticket_dict = ticket.to_dict()
        
        self.assertIn("id", ticket_dict)
        self.assertIn("name", ticket_dict)
        self.assertIn("bus", ticket_dict)
        self.assertIn("seat", ticket_dict)
        self.assertIn("booking_time", ticket_dict)
        self.assertIn("status", ticket_dict)
    
    def test_ticket_update(self):
        """Test ticket update functionality"""
        ticket = Ticket(1, "John Doe", "BUS001", "S01")
        ticket.update(name="Jane Doe")
        
        self.assertEqual(ticket.name, "Jane Doe")
        self.assertEqual(ticket.id, 1)  # ID should not change
    
    def test_ticket_cancellation(self):
        """Test ticket cancellation"""
        ticket = Ticket(1, "John Doe", "BUS001", "S01")
        ticket.cancel()
        
        self.assertEqual(ticket.status, "cancelled")
    
    def test_bus_creation(self):
        """Test bus creation"""
        bus = Bus("BUS001", 40)
        
        self.assertEqual(bus.bus_number, "BUS001")
        self.assertEqual(bus.total_seats, 40)
        self.assertEqual(len(bus.booked_seats), 0)
    
    def test_bus_seat_booking(self):
        """Test bus seat booking"""
        bus = Bus("BUS001", 40)
        
        # Test successful booking
        result = bus.book_seat("S01")
        self.assertTrue(result)
        self.assertIn("S01", bus.booked_seats)
        
        # Test double booking
        result = bus.book_seat("S01")
        self.assertFalse(result)
    
    def test_bus_seat_release(self):
        """Test bus seat release"""
        bus = Bus("BUS001", 40)
        bus.book_seat("S01")
        bus.release_seat("S01")
        
        self.assertNotIn("S01", bus.booked_seats)
    
    def test_bus_available_seats(self):
        """Test getting available seats"""
        bus = Bus("BUS001", 40)
        bus.book_seat("S01")
        bus.book_seat("S02")
        
        available_seats = bus.get_available_seats()
        self.assertEqual(len(available_seats), 38)
        self.assertNotIn("S01", available_seats)
        self.assertNotIn("S02", available_seats)
    
    def test_ticket_manager_create_ticket(self):
        """Test ticket manager ticket creation"""
        ticket = self.ticket_manager.create_ticket("John Doe", "BUS001", "S01")
        
        self.assertIsNotNone(ticket)
        self.assertEqual(ticket.name, "John Doe")
        self.assertEqual(ticket.bus, "BUS001")
        self.assertEqual(ticket.seat, "S01")
    
    def test_ticket_manager_duplicate_seat(self):
        """Test duplicate seat booking prevention"""
        # Book first ticket
        ticket1 = self.ticket_manager.create_ticket("John Doe", "BUS001", "S01")
        self.assertIsNotNone(ticket1)
        
        # Try to book same seat
        ticket2 = self.ticket_manager.create_ticket("Jane Doe", "BUS001", "S01")
        self.assertIsNone(ticket2)
    
    def test_ticket_manager_cancel_ticket(self):
        """Test ticket cancellation through manager"""
        ticket = self.ticket_manager.create_ticket("John Doe", "BUS001", "S01")
        result = self.ticket_manager.cancel_ticket(ticket.id)
        
        self.assertTrue(result)
        self.assertNotIn(ticket.id, self.ticket_manager.tickets)


class TestUtils(unittest.TestCase):
    """Test cases for utility functions"""
    
    def test_validate_passenger_name(self):
        """Test passenger name validation"""
        # Valid names
        self.assertTrue(validate_passenger_name("John Doe"))
        self.assertTrue(validate_passenger_name("Mary O'Connor"))
        self.assertTrue(validate_passenger_name("Jean-Pierre"))
        self.assertTrue(validate_passenger_name("Dr. Smith"))
        
        # Invalid names
        self.assertFalse(validate_passenger_name(""))
        self.assertFalse(validate_passenger_name("A"))
        self.assertFalse(validate_passenger_name("John123"))
        self.assertFalse(validate_passenger_name("John@Doe"))
    
    def test_validate_bus_number(self):
        """Test bus number validation"""
        # Valid bus numbers
        self.assertTrue(validate_bus_number("BUS001"))
        self.assertTrue(validate_bus_number("BUS123"))
        self.assertTrue(validate_bus_number("bus001"))  # Should work with lowercase
        
        # Invalid bus numbers
        self.assertFalse(validate_bus_number(""))
        self.assertFalse(validate_bus_number("BUS"))
        self.assertFalse(validate_bus_number("BUS1"))
        self.assertFalse(validate_bus_number("BUSA01"))
    
    def test_validate_seat_number(self):
        """Test seat number validation"""
        # Valid seat numbers
        self.assertTrue(validate_seat_number("S01"))
        self.assertTrue(validate_seat_number("S40"))
        self.assertTrue(validate_seat_number("s15"))  # Should work with lowercase
        
        # Invalid seat numbers
        self.assertFalse(validate_seat_number(""))
        self.assertFalse(validate_seat_number("S"))
        self.assertFalse(validate_seat_number("S1"))
        self.assertFalse(validate_seat_number("SA1"))
    
    def test_format_seat_number(self):
        """Test seat number formatting"""
        self.assertEqual(format_seat_number("1"), "S01")
        self.assertEqual(format_seat_number("15"), "S15")
        self.assertEqual(format_seat_number("seat 5"), "S05")
        self.assertEqual(format_seat_number("s10"), "S10")
        
        # Invalid inputs should return original
        self.assertEqual(format_seat_number(""), "")
        self.assertEqual(format_seat_number("invalid"), "INVALID")
    
    def test_format_bus_number(self):
        """Test bus number formatting"""
        self.assertEqual(format_bus_number("1"), "BUS001")
        self.assertEqual(format_bus_number("123"), "BUS123")
        self.assertEqual(format_bus_number("bus 5"), "BUS005")
        
        # Invalid inputs should return original
        self.assertEqual(format_bus_number(""), "")
        self.assertEqual(format_bus_number("invalid"), "INVALID")
    
    def test_sanitize_input(self):
        """Test input sanitization"""
        self.assertEqual(sanitize_input("John Doe"), "John Doe")
        self.assertEqual(sanitize_input("<script>alert('xss')</script>"), "alert('xss')")
        self.assertEqual(sanitize_input('John "Quote" Doe'), "John Quote Doe")
        self.assertEqual(sanitize_input("  spaced  "), "spaced")
    
    def test_calculate_fare(self):
        """Test fare calculation"""
        # Standard fare
        self.assertEqual(calculate_fare("BUS003", "standard"), 50.0)
        
        # Premium bus
        self.assertEqual(calculate_fare("BUS001", "standard"), 75.0)
        
        # Premium seat
        self.assertEqual(calculate_fare("BUS003", "premium"), 65.0)
        
        # Sleeper seat
        self.assertEqual(calculate_fare("BUS003", "sleeper"), 75.0)
    
    def test_get_seat_type(self):
        """Test seat type determination"""
        self.assertEqual(get_seat_type("S05"), "premium")  # Seats 1-10
        self.assertEqual(get_seat_type("S15"), "standard")  # Seats 11-30
        self.assertEqual(get_seat_type("S35"), "sleeper")   # Seats 31-40
        self.assertEqual(get_seat_type("INVALID"), "standard")
    
    def test_validate_ticket_data(self):
        """Test ticket data validation"""
        # Valid data
        valid_data = {"name": "John Doe", "bus": "BUS001", "seat": "S01"}
        errors = validate_ticket_data(valid_data)
        self.assertEqual(len(errors), 0)
        
        # Missing fields
        invalid_data = {"name": "John Doe"}
        errors = validate_ticket_data(invalid_data)
        self.assertGreater(len(errors), 0)
        
        # Invalid formats
        invalid_data = {"name": "John123", "bus": "INVALID", "seat": "INVALID"}
        errors = validate_ticket_data(invalid_data)
        self.assertGreater(len(errors), 0)


class TestAPI(unittest.TestCase):
    """Test cases for API endpoints"""
    
    def setUp(self):
        """Set up test client"""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up"""
        self.app_context.pop()
    
    def test_home_endpoint(self):
        """Test home page endpoint"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Bus Ticket Booking', response.data)
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_create_ticket_valid(self):
        """Test creating a valid ticket"""
        ticket_data = {
            "name": "John Doe",
            "bus": "BUS001",
            "seat": "S01"
        }
        
        response = self.client.post('/api/tickets',
                                  data=json.dumps(ticket_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('ticket', data['data'])
    
    def test_create_ticket_invalid(self):
        """Test creating an invalid ticket"""
        ticket_data = {
            "name": "",  # Invalid name
            "bus": "INVALID",  # Invalid bus
            "seat": "INVALID"  # Invalid seat
        }
        
        response = self.client.post('/api/tickets',
                                  data=json.dumps(ticket_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    def test_get_tickets(self):
        """Test getting all tickets"""
        response = self.client.get('/api/tickets')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('tickets', data['data'])
    
    def test_get_bus_info(self):
        """Test getting bus information"""
        response = self.client.get('/api/buses/BUS001')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('bus', data['data'])
    
    def test_get_statistics(self):
        """Test getting system statistics"""
        response = self.client.get('/api/stats')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('stats', data['data'])


class TestDatabase(unittest.TestCase):
    """Test cases for database operations"""
    
    def setUp(self):
        """Set up test database"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.db_manager = DatabaseManager(self.temp_db.name)
    
    def tearDown(self):
        """Clean up test database"""
        os.unlink(self.temp_db.name)
    
    def test_database_initialization(self):
        """Test database table creation"""
        # Database should be initialized without errors
        self.assertIsNotNone(self.db_manager)
    
    def test_insert_and_get_ticket(self):
        """Test ticket insertion and retrieval"""
        ticket_id = self.db_manager.insert_ticket(
            "John Doe", "BUS001", "S01", 50.0, "standard", "BKG12345"
        )
        
        self.assertIsNotNone(ticket_id)
        
        ticket = self.db_manager.get_ticket(ticket_id)
        self.assertIsNotNone(ticket)
        self.assertEqual(ticket['passenger_name'], "John Doe")
        self.assertEqual(ticket['bus_number'], "BUS001")
        self.assertEqual(ticket['seat_number'], "S01")
    
    def test_update_ticket(self):
        """Test ticket update"""
        ticket_id = self.db_manager.insert_ticket("John Doe", "BUS001", "S01")
        
        result = self.db_manager.update_ticket(ticket_id, passenger_name="Jane Doe")
        self.assertTrue(result)
        
        updated_ticket = self.db_manager.get_ticket(ticket_id)
        self.assertEqual(updated_ticket['passenger_name'], "Jane Doe")
    
    def test_delete_ticket(self):
        """Test ticket deletion (soft delete)"""
        ticket_id = self.db_manager.insert_ticket("John Doe", "BUS001", "S01")
        
        result = self.db_manager.delete_ticket(ticket_id)
        self.assertTrue(result)
        
        # Ticket should be marked as cancelled, not physically deleted
        ticket = self.db_manager.get_ticket(ticket_id)
        self.assertIsNone(ticket)  # get_ticket filters out cancelled tickets
    
    def test_bus_seat_availability(self):
        """Test bus seat availability calculation"""
        # Book some seats
        self.db_manager.insert_ticket("John Doe", "BUS001", "S01")
        self.db_manager.insert_ticket("Jane Doe", "BUS001", "S02")
        
        availability = self.db_manager.get_bus_seat_availability("BUS001")
        
        self.assertEqual(availability['total_seats'], 40)
        self.assertEqual(availability['booked_count'], 2)
        self.assertEqual(availability['available_count'], 38)
        self.assertIn("S01", availability['booked_seats'])
        self.assertIn("S02", availability['booked_seats'])
        self.assertNotIn("S01", availability['available_seats'])
        self.assertNotIn("S02", availability['available_seats'])
    
    def test_system_statistics(self):
        """Test system statistics calculation"""
        # Insert some test data
        self.db_manager.insert_ticket("John Doe", "BUS001", "S01", 50.0)
        self.db_manager.insert_ticket("Jane Doe", "BUS002", "S01", 75.0)
        
        stats = self.db_manager.get_system_statistics()
        
        self.assertEqual(stats['total_tickets'], 2)
        self.assertEqual(stats['total_revenue'], 125.0)
        self.assertIn('BUS001', stats['tickets_by_bus'])
        self.assertIn('BUS002', stats['tickets_by_bus'])


def run_tests():
    """Run all test suites"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestModels))
    test_suite.addTest(unittest.makeSuite(TestUtils))
    test_suite.addTest(unittest.makeSuite(TestAPI))
    test_suite.addTest(unittest.makeSuite(TestDatabase))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    # Run tests when script is executed directly
    success = run_tests()
    exit(0 if success else 1)
