# CLI Management Tool for Bus Ticket Booking System

import sys
import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests
import os

class BusTicketCLI:
    """Command-line interface for managing bus ticket booking system"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'BusTicketCLI/1.0'
        })
    
    def make_request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """Make HTTP request to the API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error making request: {e}")
            return {"success": False, "message": str(e)}
    
    def list_tickets(self, bus_filter: str = None, output_format: str = 'table'):
        """List all tickets"""
        endpoint = "/api/tickets"
        if bus_filter:
            endpoint += f"?bus={bus_filter}"
        
        response = self.make_request('GET', endpoint)
        
        if not response.get('success'):
            print(f"Error: {response.get('message', 'Unknown error')}")
            return
        
        tickets = response.get('data', {}).get('tickets', {})
        
        if not tickets:
            print("No tickets found.")
            return
        
        if output_format == 'json':
            print(json.dumps(tickets, indent=2))
        elif output_format == 'csv':
            self._print_tickets_csv(tickets)
        else:
            self._print_tickets_table(tickets)
    
    def _print_tickets_table(self, tickets: dict):
        """Print tickets in table format"""
        print(f"{'ID':<5} {'Name':<20} {'Bus':<8} {'Seat':<6} {'Status':<10} {'Booking Time':<20}")
        print("-" * 75)
        
        for ticket_id, ticket in tickets.items():
            print(f"{ticket_id:<5} {ticket['name'][:19]:<20} {ticket['bus']:<8} "
                  f"{ticket['seat']:<6} {ticket['status']:<10} {ticket['booking_time'][:19]:<20}")
    
    def _print_tickets_csv(self, tickets: dict):
        """Print tickets in CSV format"""
        print("ID,Name,Bus,Seat,Status,BookingTime")
        for ticket_id, ticket in tickets.items():
            print(f"{ticket_id},{ticket['name']},{ticket['bus']},"
                  f"{ticket['seat']},{ticket['status']},{ticket['booking_time']}")
    
    def book_ticket(self, name: str, bus: str, seat: str):
        """Book a new ticket"""
        data = {
            "name": name,
            "bus": bus,
            "seat": seat
        }
        
        response = self.make_request('POST', '/api/tickets', data)
        
        if response.get('success'):
            ticket = response.get('data', {}).get('ticket', {})
            print(f"Ticket booked successfully!")
            print(f"Ticket ID: {ticket.get('id')}")
            print(f"Passenger: {ticket.get('name')}")
            print(f"Bus: {ticket.get('bus')}")
            print(f"Seat: {ticket.get('seat')}")
            print(f"Fare: ${ticket.get('fare', 0):.2f}")
        else:
            print(f"Booking failed: {response.get('message', 'Unknown error')}")
    
    def update_ticket(self, ticket_id: int, name: str):
        """Update ticket name"""
        data = {"name": name}
        
        response = self.make_request('PUT', f'/api/tickets/{ticket_id}', data)
        
        if response.get('success'):
            print(f"Ticket {ticket_id} updated successfully!")
        else:
            print(f"Update failed: {response.get('message', 'Unknown error')}")
    
    def cancel_ticket(self, ticket_id: int):
        """Cancel a ticket"""
        response = self.make_request('DELETE', f'/api/tickets/{ticket_id}')
        
        if response.get('success'):
            print(f"Ticket {ticket_id} cancelled successfully!")
        else:
            print(f"Cancellation failed: {response.get('message', 'Unknown error')}")
    
    def show_bus_info(self, bus_number: str = None):
        """Show bus information"""
        if bus_number:
            response = self.make_request('GET', f'/api/buses/{bus_number}')
            if response.get('success'):
                bus = response.get('data', {}).get('bus', {})
                self._print_bus_info(bus_number, bus)
            else:
                print(f"Error: {response.get('message', 'Unknown error')}")
        else:
            response = self.make_request('GET', '/api/buses')
            if response.get('success'):
                buses = response.get('data', {}).get('buses', {})
                for bus_num, bus_info in buses.items():
                    self._print_bus_info(bus_num, bus_info)
                    print("-" * 50)
            else:
                print(f"Error: {response.get('message', 'Unknown error')}")
    
    def _print_bus_info(self, bus_number: str, bus_info: dict):
        """Print bus information"""
        print(f"Bus: {bus_number}")
        print(f"Total Seats: {bus_info.get('total_seats', 0)}")
        print(f"Booked Seats: {bus_info.get('booked_seats', 0)}")
        print(f"Available Seats: {bus_info.get('available_seats', 0)}")
        print(f"Occupancy Rate: {bus_info.get('occupancy_rate', 0)}%")
        
        if 'available_seats_list' in bus_info:
            available = bus_info['available_seats_list'][:10]  # Show first 10
            if len(available) > 0:
                print(f"Available Seats: {', '.join(available)}")
                if len(bus_info['available_seats_list']) > 10:
                    print(f"... and {len(bus_info['available_seats_list']) - 10} more")
    
    def show_stats(self):
        """Show system statistics"""
        response = self.make_request('GET', '/api/stats')
        
        if response.get('success'):
            stats = response.get('data', {}).get('stats', {})
            print("=== System Statistics ===")
            print(f"Total Tickets: {stats.get('total_tickets', 0)}")
            print(f"Total Buses: {stats.get('total_buses', 0)}")
            print(f"Booked Seats: {stats.get('booked_seats', 0)}")
            print(f"Available Seats: {stats.get('available_seats', 0)}")
            print(f"Occupancy Rate: {stats.get('overall_occupancy', 0)}%")
        else:
            print(f"Error: {response.get('message', 'Unknown error')}")
    
    def bulk_book_tickets(self, csv_file: str):
        """Bulk book tickets from CSV file"""
        try:
            with open(csv_file, 'r') as f:
                lines = f.readlines()
            
            # Skip header if present
            if lines[0].strip().lower().startswith('name'):
                lines = lines[1:]
            
            successful = 0
            failed = 0
            
            for line_num, line in enumerate(lines, 1):
                try:
                    parts = [part.strip() for part in line.strip().split(',')]
                    if len(parts) < 3:
                        print(f"Line {line_num}: Invalid format (need: name,bus,seat)")
                        failed += 1
                        continue
                    
                    name, bus, seat = parts[0], parts[1], parts[2]
                    
                    data = {"name": name, "bus": bus, "seat": seat}
                    response = self.make_request('POST', '/api/tickets', data)
                    
                    if response.get('success'):
                        ticket = response.get('data', {}).get('ticket', {})
                        print(f"✓ Booked: {name} - {bus} {seat} (ID: {ticket.get('id')})")
                        successful += 1
                    else:
                        print(f"✗ Failed: {name} - {response.get('message', 'Unknown error')}")
                        failed += 1
                
                except Exception as e:
                    print(f"Line {line_num}: Error - {e}")
                    failed += 1
            
            print(f"\nBulk booking completed: {successful} successful, {failed} failed")
            
        except FileNotFoundError:
            print(f"Error: File '{csv_file}' not found")
        except Exception as e:
            print(f"Error reading file: {e}")
    
    def export_tickets(self, output_file: str, format_type: str = 'csv'):
        """Export tickets to file"""
        response = self.make_request('GET', '/api/tickets')
        
        if not response.get('success'):
            print(f"Error: {response.get('message', 'Unknown error')}")
            return
        
        tickets = response.get('data', {}).get('tickets', {})
        
        try:
            with open(output_file, 'w') as f:
                if format_type.lower() == 'csv':
                    f.write("ID,Name,Bus,Seat,Status,BookingTime\n")
                    for ticket_id, ticket in tickets.items():
                        f.write(f"{ticket_id},{ticket['name']},{ticket['bus']},"
                               f"{ticket['seat']},{ticket['status']},{ticket['booking_time']}\n")
                elif format_type.lower() == 'json':
                    json.dump(tickets, f, indent=2)
                else:
                    print(f"Unsupported format: {format_type}")
                    return
            
            print(f"Tickets exported to {output_file}")
            
        except Exception as e:
            print(f"Error writing file: {e}")


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description='Bus Ticket Booking System CLI')
    parser.add_argument('--url', default='http://localhost:5000', 
                       help='API base URL (default: http://localhost:5000)')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List tickets command
    list_parser = subparsers.add_parser('list', help='List tickets')
    list_parser.add_argument('--bus', help='Filter by bus number')
    list_parser.add_argument('--format', choices=['table', 'csv', 'json'], 
                           default='table', help='Output format')
    
    # Book ticket command
    book_parser = subparsers.add_parser('book', help='Book a ticket')
    book_parser.add_argument('name', help='Passenger name')
    book_parser.add_argument('bus', help='Bus number (e.g., BUS001)')
    book_parser.add_argument('seat', help='Seat number (e.g., S01)')
    
    # Update ticket command
    update_parser = subparsers.add_parser('update', help='Update ticket')
    update_parser.add_argument('ticket_id', type=int, help='Ticket ID')
    update_parser.add_argument('name', help='New passenger name')
    
    # Cancel ticket command
    cancel_parser = subparsers.add_parser('cancel', help='Cancel ticket')
    cancel_parser.add_argument('ticket_id', type=int, help='Ticket ID')
    
    # Bus info command
    bus_parser = subparsers.add_parser('buses', help='Show bus information')
    bus_parser.add_argument('--bus', help='Specific bus number')
    
    # Stats command
    subparsers.add_parser('stats', help='Show system statistics')
    
    # Bulk book command
    bulk_parser = subparsers.add_parser('bulk-book', help='Bulk book from CSV')
    bulk_parser.add_argument('csv_file', help='CSV file path')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export tickets')
    export_parser.add_argument('output_file', help='Output file path')
    export_parser.add_argument('--format', choices=['csv', 'json'], 
                              default='csv', help='Export format')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = BusTicketCLI(args.url)
    
    try:
        if args.command == 'list':
            cli.list_tickets(args.bus, args.format)
        elif args.command == 'book':
            cli.book_ticket(args.name, args.bus, args.seat)
        elif args.command == 'update':
            cli.update_ticket(args.ticket_id, args.name)
        elif args.command == 'cancel':
            cli.cancel_ticket(args.ticket_id)
        elif args.command == 'buses':
            cli.show_bus_info(args.bus)
        elif args.command == 'stats':
            cli.show_stats()
        elif args.command == 'bulk-book':
            cli.bulk_book_tickets(args.csv_file)
        elif args.command == 'export':
            cli.export_tickets(args.output_file, args.format)
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == '__main__':
    main()
