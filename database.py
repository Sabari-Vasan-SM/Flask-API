# Database Manager for Bus Ticket Booking System

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from contextlib import contextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database manager for handling SQLite operations"""
    
    def __init__(self, db_path: str = "bus_tickets.db"):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def init_database(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            # Create tickets table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    passenger_name TEXT NOT NULL,
                    bus_number TEXT NOT NULL,
                    seat_number TEXT NOT NULL,
                    booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'confirmed',
                    fare REAL DEFAULT 0.0,
                    seat_type TEXT DEFAULT 'standard',
                    booking_reference TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create buses table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS buses (
                    bus_number TEXT PRIMARY KEY,
                    total_seats INTEGER DEFAULT 40,
                    bus_type TEXT DEFAULT 'standard',
                    route TEXT,
                    driver_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create audit log table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    record_id INTEGER,
                    old_values TEXT,
                    new_values TEXT,
                    user_id TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tickets_bus ON tickets(bus_number)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tickets_booking_time ON tickets(booking_time)")
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def insert_ticket(self, passenger_name: str, bus_number: str, seat_number: str,
                     fare: float = 0.0, seat_type: str = 'standard',
                     booking_reference: str = '') -> Optional[int]:
        """Insert a new ticket"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO tickets (passenger_name, bus_number, seat_number, fare, seat_type, booking_reference)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (passenger_name, bus_number, seat_number, fare, seat_type, booking_reference))
                
                ticket_id = cursor.lastrowid
                conn.commit()
                
                # Log the action
                self.log_action('INSERT', 'tickets', ticket_id, {}, {
                    'passenger_name': passenger_name,
                    'bus_number': bus_number,
                    'seat_number': seat_number
                })
                
                logger.info(f"Ticket {ticket_id} created for {passenger_name}")
                return ticket_id
                
        except Exception as e:
            logger.error(f"Error inserting ticket: {e}")
            return None
    
    def get_ticket(self, ticket_id: int) -> Optional[Dict]:
        """Get a ticket by ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT * FROM tickets WHERE id = ? AND status != 'deleted'
                """, (ticket_id,))
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
                
        except Exception as e:
            logger.error(f"Error getting ticket {ticket_id}: {e}")
            return None
    
    def get_all_tickets(self, bus_filter: str = None, status_filter: str = 'confirmed') -> List[Dict]:
        """Get all tickets with optional filters"""
        try:
            with self.get_connection() as conn:
                query = "SELECT * FROM tickets WHERE status = ?"
                params = [status_filter]
                
                if bus_filter:
                    query += " AND bus_number = ?"
                    params.append(bus_filter)
                
                query += " ORDER BY booking_time DESC"
                
                cursor = conn.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error getting tickets: {e}")
            return []
    
    def update_ticket(self, ticket_id: int, **kwargs) -> bool:
        """Update ticket information"""
        try:
            # Get old values for audit
            old_ticket = self.get_ticket(ticket_id)
            if not old_ticket:
                return False
            
            # Build update query
            set_clauses = []
            values = []
            
            allowed_fields = ['passenger_name', 'bus_number', 'seat_number', 'status', 'fare']
            for field, value in kwargs.items():
                if field in allowed_fields:
                    set_clauses.append(f"{field} = ?")
                    values.append(value)
            
            if not set_clauses:
                return False
            
            # Add updated_at timestamp
            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            values.append(ticket_id)
            
            with self.get_connection() as conn:
                query = f"UPDATE tickets SET {', '.join(set_clauses)} WHERE id = ?"
                conn.execute(query, values)
                conn.commit()
                
                # Log the action
                self.log_action('UPDATE', 'tickets', ticket_id, old_ticket, kwargs)
                
                logger.info(f"Ticket {ticket_id} updated")
                return True
                
        except Exception as e:
            logger.error(f"Error updating ticket {ticket_id}: {e}")
            return False
    
    def delete_ticket(self, ticket_id: int) -> bool:
        """Soft delete a ticket"""
        return self.update_ticket(ticket_id, status='cancelled')
    
    def get_bus_seat_availability(self, bus_number: str) -> Dict:
        """Get seat availability for a specific bus"""
        try:
            with self.get_connection() as conn:
                # Get all booked seats for the bus
                cursor = conn.execute("""
                    SELECT seat_number FROM tickets 
                    WHERE bus_number = ? AND status = 'confirmed'
                """, (bus_number,))
                
                booked_seats = {row['seat_number'] for row in cursor.fetchall()}
                
                # Generate all possible seats (S01 to S40)
                all_seats = {f"S{i:02d}" for i in range(1, 41)}
                available_seats = all_seats - booked_seats
                
                return {
                    'bus_number': bus_number,
                    'total_seats': 40,
                    'booked_seats': list(booked_seats),
                    'available_seats': list(available_seats),
                    'booked_count': len(booked_seats),
                    'available_count': len(available_seats),
                    'occupancy_rate': round((len(booked_seats) / 40) * 100, 2)
                }
                
        except Exception as e:
            logger.error(f"Error getting bus availability for {bus_number}: {e}")
            return {}
    
    def get_system_statistics(self) -> Dict:
        """Get system-wide statistics"""
        try:
            with self.get_connection() as conn:
                # Total tickets
                cursor = conn.execute("SELECT COUNT(*) as count FROM tickets WHERE status = 'confirmed'")
                total_tickets = cursor.fetchone()['count']
                
                # Tickets by bus
                cursor = conn.execute("""
                    SELECT bus_number, COUNT(*) as count 
                    FROM tickets 
                    WHERE status = 'confirmed' 
                    GROUP BY bus_number
                """)
                tickets_by_bus = {row['bus_number']: row['count'] for row in cursor.fetchall()}
                
                # Total revenue
                cursor = conn.execute("SELECT SUM(fare) as total FROM tickets WHERE status = 'confirmed'")
                total_revenue = cursor.fetchone()['total'] or 0.0
                
                # Recent bookings (last 24 hours)
                cursor = conn.execute("""
                    SELECT COUNT(*) as count 
                    FROM tickets 
                    WHERE status = 'confirmed' 
                    AND booking_time >= datetime('now', '-1 day')
                """)
                recent_bookings = cursor.fetchone()['count']
                
                return {
                    'total_tickets': total_tickets,
                    'tickets_by_bus': tickets_by_bus,
                    'total_revenue': round(total_revenue, 2),
                    'recent_bookings': recent_bookings,
                    'total_buses': 5,  # Fixed number of buses
                    'system_uptime': self.get_system_uptime()
                }
                
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
    
    def log_action(self, action: str, table_name: str, record_id: int,
                  old_values: Dict, new_values: Dict, user_id: str = 'system'):
        """Log an action to the audit table"""
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT INTO audit_log (action, table_name, record_id, old_values, new_values, user_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    action, table_name, record_id,
                    json.dumps(old_values), json.dumps(new_values), user_id
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error logging action: {e}")
    
    def get_audit_log(self, limit: int = 100) -> List[Dict]:
        """Get recent audit log entries"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT * FROM audit_log 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (limit,))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error getting audit log: {e}")
            return []
    
    def get_system_uptime(self) -> str:
        """Get system uptime information"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT MIN(timestamp) as first_log 
                    FROM audit_log
                """)
                
                first_log = cursor.fetchone()
                if first_log and first_log['first_log']:
                    # Calculate uptime
                    first_time = datetime.fromisoformat(first_log['first_log'])
                    uptime = datetime.now() - first_time
                    return str(uptime).split('.')[0]  # Remove microseconds
                
                return "Unknown"
                
        except Exception as e:
            logger.error(f"Error getting uptime: {e}")
            return "Unknown"
    
    def cleanup_old_data(self, days: int = 30):
        """Clean up old audit logs and cancelled tickets"""
        try:
            with self.get_connection() as conn:
                # Clean old audit logs
                conn.execute("""
                    DELETE FROM audit_log 
                    WHERE timestamp < datetime('now', '-? days')
                """, (days,))
                
                # Clean old cancelled tickets
                conn.execute("""
                    DELETE FROM tickets 
                    WHERE status = 'cancelled' 
                    AND updated_at < datetime('now', '-? days')
                """, (days,))
                
                conn.commit()
                logger.info(f"Cleaned up data older than {days} days")
                
        except Exception as e:
            logger.error(f"Error cleaning up data: {e}")

    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Database backed up to {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Error backing up database: {e}")
            return False
