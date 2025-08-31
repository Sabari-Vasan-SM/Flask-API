# Bus Ticket Booking Models

from datetime import datetime
from typing import Dict, List, Optional
import json

class Ticket:
    """Ticket model for bus reservations"""
    
    def __init__(self, ticket_id: int, name: str, bus: str, seat: str, 
                 booking_time: Optional[datetime] = None):
        self.id = ticket_id
        self.name = name
        self.bus = bus
        self.seat = seat
        self.booking_time = booking_time or datetime.now()
        self.status = "confirmed"
    
    def to_dict(self) -> Dict:
        """Convert ticket to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "bus": self.bus,
            "seat": self.seat,
            "booking_time": self.booking_time.isoformat(),
            "status": self.status
        }
    
    def update(self, **kwargs):
        """Update ticket attributes"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key != 'id':
                setattr(self, key, value)
    
    def cancel(self):
        """Cancel the ticket"""
        self.status = "cancelled"
    
    def __repr__(self):
        return f"<Ticket {self.id}: {self.name} - {self.bus} Seat {self.seat}>"

class Bus:
    """Bus model with seat management"""
    
    def __init__(self, bus_number: str, total_seats: int = 40):
        self.bus_number = bus_number
        self.total_seats = total_seats
        self.booked_seats = set()
        self.routes = []
    
    def is_seat_available(self, seat_number: str) -> bool:
        """Check if a seat is available"""
        return seat_number not in self.booked_seats
    
    def book_seat(self, seat_number: str) -> bool:
        """Book a seat if available"""
        if self.is_seat_available(seat_number):
            self.booked_seats.add(seat_number)
            return True
        return False
    
    def release_seat(self, seat_number: str):
        """Release a booked seat"""
        self.booked_seats.discard(seat_number)
    
    def get_available_seats(self) -> List[str]:
        """Get list of available seats"""
        all_seats = [f"S{i:02d}" for i in range(1, self.total_seats + 1)]
        return [seat for seat in all_seats if seat not in self.booked_seats]
    
    def get_occupancy_rate(self) -> float:
        """Get bus occupancy rate as percentage"""
        return (len(self.booked_seats) / self.total_seats) * 100
    
    def to_dict(self) -> Dict:
        """Convert bus to dictionary"""
        return {
            "bus_number": self.bus_number,
            "total_seats": self.total_seats,
            "booked_seats": len(self.booked_seats),
            "available_seats": len(self.get_available_seats()),
            "occupancy_rate": round(self.get_occupancy_rate(), 2)
        }

class TicketManager:
    """Manager class for handling ticket operations"""
    
    def __init__(self):
        self.tickets: Dict[int, Ticket] = {}
        self.buses: Dict[str, Bus] = {}
        self.next_ticket_id = 1
        self._initialize_buses()
    
    def _initialize_buses(self):
        """Initialize available buses"""
        bus_numbers = ['BUS001', 'BUS002', 'BUS003', 'BUS004', 'BUS005']
        for bus_num in bus_numbers:
            self.buses[bus_num] = Bus(bus_num)
    
    def create_ticket(self, name: str, bus: str, seat: str) -> Optional[Ticket]:
        """Create a new ticket"""
        if bus not in self.buses:
            return None
        
        if not self.buses[bus].book_seat(seat):
            return None
        
        ticket = Ticket(self.next_ticket_id, name, bus, seat)
        self.tickets[self.next_ticket_id] = ticket
        self.next_ticket_id += 1
        return ticket
    
    def get_ticket(self, ticket_id: int) -> Optional[Ticket]:
        """Get ticket by ID"""
        return self.tickets.get(ticket_id)
    
    def get_all_tickets(self) -> Dict[int, Dict]:
        """Get all tickets as dictionary"""
        return {tid: ticket.to_dict() for tid, ticket in self.tickets.items()}
    
    def update_ticket(self, ticket_id: int, **kwargs) -> Optional[Ticket]:
        """Update ticket information"""
        ticket = self.get_ticket(ticket_id)
        if ticket:
            ticket.update(**kwargs)
        return ticket
    
    def cancel_ticket(self, ticket_id: int) -> bool:
        """Cancel a ticket and release the seat"""
        ticket = self.get_ticket(ticket_id)
        if ticket:
            bus = self.buses.get(ticket.bus)
            if bus:
                bus.release_seat(ticket.seat)
            ticket.cancel()
            del self.tickets[ticket_id]
            return True
        return False
    
    def get_bus_info(self, bus_number: str) -> Optional[Dict]:
        """Get bus information"""
        bus = self.buses.get(bus_number)
        return bus.to_dict() if bus else None
    
    def get_all_buses_info(self) -> Dict[str, Dict]:
        """Get information for all buses"""
        return {bus_num: bus.to_dict() for bus_num, bus in self.buses.items()}
    
    def get_available_seats(self, bus_number: str) -> List[str]:
        """Get available seats for a specific bus"""
        bus = self.buses.get(bus_number)
        return bus.get_available_seats() if bus else []
