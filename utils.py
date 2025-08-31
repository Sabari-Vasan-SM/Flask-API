# Utility functions for Bus Ticket Booking API

import re
from datetime import datetime
from typing import List, Dict, Any, Optional
import json
import hashlib

def validate_passenger_name(name: str) -> bool:
    """Validate passenger name format"""
    if not name or len(name.strip()) < 2:
        return False
    # Allow letters, spaces, hyphens, and apostrophes
    pattern = r"^[a-zA-Z\s\-'\.]+$"
    return bool(re.match(pattern, name.strip()))

def validate_bus_number(bus_number: str) -> bool:
    """Validate bus number format"""
    if not bus_number:
        return False
    # Expected format: BUS001, BUS002, etc.
    pattern = r"^BUS\d{3}$"
    return bool(re.match(pattern, bus_number.upper()))

def validate_seat_number(seat_number: str) -> bool:
    """Validate seat number format"""
    if not seat_number:
        return False
    # Expected format: S01, S02, ..., S40
    pattern = r"^S\d{2}$"
    return bool(re.match(pattern, seat_number.upper()))

def format_seat_number(seat_input: str) -> str:
    """Format seat number to standard format"""
    if not seat_input:
        return ""
    
    # Remove all non-alphanumeric characters
    clean_input = re.sub(r'[^a-zA-Z0-9]', '', seat_input)
    
    # Extract number part
    numbers = re.findall(r'\d+', clean_input)
    if numbers:
        seat_num = int(numbers[0])
        if 1 <= seat_num <= 40:
            return f"S{seat_num:02d}"
    
    return seat_input.upper()

def format_bus_number(bus_input: str) -> str:
    """Format bus number to standard format"""
    if not bus_input:
        return ""
    
    # Extract numbers from input
    numbers = re.findall(r'\d+', bus_input)
    if numbers:
        bus_num = int(numbers[0])
        if 1 <= bus_num <= 999:
            return f"BUS{bus_num:03d}"
    
    return bus_input.upper()

def sanitize_input(input_str: str) -> str:
    """Sanitize user input by removing potentially harmful characters"""
    if not input_str:
        return ""
    
    # Remove HTML tags and special characters
    clean_str = re.sub(r'<[^>]*>', '', str(input_str))
    clean_str = re.sub(r'[<>"\']', '', clean_str)
    return clean_str.strip()

def generate_booking_reference(ticket_id: int, passenger_name: str) -> str:
    """Generate a unique booking reference"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    data = f"{ticket_id}-{passenger_name}-{timestamp}"
    hash_object = hashlib.md5(data.encode())
    return f"BKG{hash_object.hexdigest()[:8].upper()}"

def format_datetime(dt: datetime) -> str:
    """Format datetime for display"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def parse_datetime(date_str: str) -> Optional[datetime]:
    """Parse datetime string"""
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return None

def calculate_fare(bus_number: str, seat_type: str = "standard") -> float:
    """Calculate fare based on bus and seat type"""
    base_fare = 50.0  # Base fare
    
    # Premium buses cost more
    if bus_number in ['BUS001', 'BUS002']:
        base_fare *= 1.5
    
    # Seat type multiplier
    seat_multipliers = {
        "standard": 1.0,
        "premium": 1.3,
        "sleeper": 1.5
    }
    
    return base_fare * seat_multipliers.get(seat_type, 1.0)

def get_seat_type(seat_number: str) -> str:
    """Determine seat type based on seat number"""
    if not validate_seat_number(seat_number):
        return "standard"
    
    seat_num = int(seat_number[1:])
    
    if seat_num <= 10:
        return "premium"
    elif seat_num > 30:
        return "sleeper"
    else:
        return "standard"

def format_response(success: bool, message: str, data: Any = None, 
                   error_code: Optional[str] = None) -> Dict:
    """Format API response consistently"""
    response = {
        "success": success,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    
    if data is not None:
        response["data"] = data
    
    if error_code:
        response["error_code"] = error_code
    
    return response

def validate_ticket_data(data: Dict) -> List[str]:
    """Validate ticket booking data and return list of errors"""
    errors = []
    
    # Check required fields
    required_fields = ['name', 'bus', 'seat']
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"Field '{field}' is required")
    
    # Validate individual fields if present
    if 'name' in data and data['name']:
        if not validate_passenger_name(data['name']):
            errors.append("Invalid passenger name format")
    
    if 'bus' in data and data['bus']:
        formatted_bus = format_bus_number(data['bus'])
        if not validate_bus_number(formatted_bus):
            errors.append("Invalid bus number format")
    
    if 'seat' in data and data['seat']:
        formatted_seat = format_seat_number(data['seat'])
        if not validate_seat_number(formatted_seat):
            errors.append("Invalid seat number format")
    
    return errors

def log_activity(action: str, ticket_id: Optional[int] = None, 
                details: Optional[Dict] = None):
    """Log activity for audit purposes"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "ticket_id": ticket_id,
        "details": details or {}
    }
    
    # In a real application, this would write to a proper logging system
    print(f"[LOG] {json.dumps(log_entry)}")

def get_system_stats(ticket_manager) -> Dict:
    """Get system statistics"""
    total_tickets = len(ticket_manager.get_all_tickets())
    buses_info = ticket_manager.get_all_buses_info()
    
    total_seats = sum(bus['total_seats'] for bus in buses_info.values())
    booked_seats = sum(bus['booked_seats'] for bus in buses_info.values())
    
    return {
        "total_tickets": total_tickets,
        "total_buses": len(buses_info),
        "total_seats": total_seats,
        "booked_seats": booked_seats,
        "available_seats": total_seats - booked_seats,
        "overall_occupancy": round((booked_seats / total_seats) * 100, 2) if total_seats > 0 else 0
    }
