# API Routes for Bus Ticket Booking System
from flask import Blueprint, request, jsonify, render_template
from models import TicketManager
from utils import (
    validate_ticket_data, format_response, sanitize_input,
    format_bus_number, format_seat_number, log_activity,
    get_system_stats, calculate_fare, get_seat_type
)

# Create API routes blueprint
api = Blueprint('api', __name__)

# Initialize ticket manager
ticket_manager = TicketManager()

@api.route('/api/tickets', methods=['GET'])
def get_all_tickets():
    """Get all tickets with optional filtering"""
    try:
        # Get query parameters
        bus_filter = request.args.get('bus')
        status_filter = request.args.get('status', 'confirmed')
        
        # Get all tickets
        all_tickets = ticket_manager.get_all_tickets()
        
        # Apply bus filter if provided
        if bus_filter:
            all_tickets = {
                tid: ticket for tid, ticket in all_tickets.items()
                if ticket.get('bus') == bus_filter.upper()
            }
        
        # Apply status filter
        if status_filter:
            all_tickets = {
                tid: ticket for tid, ticket in all_tickets.items()
                if ticket.get('status') == status_filter
            }
        
        # Log activity
        log_activity("GET_TICKETS", details={"filter_bus": bus_filter, "filter_status": status_filter})
        
        # Return response
        return jsonify(format_response(
            True,                               # Success status
            f"Retrieved {len(all_tickets)} tickets",  # Success message
            {"tickets": all_tickets, "count": len(all_tickets)}  # Data payload
        ))
        
    except Exception as e:
        # Handle any unexpected errors and return error response
        return jsonify(format_response(False, str(e), error_code="GET_TICKETS_ERROR")), 500

@api.route('/api/tickets', methods=['POST'])
def create_ticket():
    """
    POST endpoint to create a new bus ticket
    Expected JSON payload:
    {
        "name": "Passenger Name",
        "bus": "BUS001",
        "seat": "S01"
    }
    
    Returns:
        JSON response with created ticket details or error message
    """
    try:
        # Parse JSON data from request body
        data = request.json
        if not data:
            # Return error if no data is provided
            return jsonify(format_response(False, "No data provided", error_code="NO_DATA")), 400
        
        # Sanitize and format input data to prevent injection attacks
        sanitized_data = {
            'name': sanitize_input(data.get('name', '')),     # Clean passenger name
            'bus': format_bus_number(data.get('bus', '')),    # Format bus number (BUS001)
            'seat': format_seat_number(data.get('seat', ''))  # Format seat number (S01)
        }
        
        # Validate data
        errors = validate_ticket_data(sanitized_data)
        if errors:
            return jsonify(format_response(False, "Validation failed", {"errors": errors}, "VALIDATION_ERROR")), 400
        
        # Check if seat is available
        available_seats = ticket_manager.get_available_seats(sanitized_data['bus'])
        if sanitized_data['seat'] not in available_seats:
            return jsonify(format_response(
                False, 
                f"Seat {sanitized_data['seat']} is not available on {sanitized_data['bus']}", 
                {"available_seats": available_seats},
                "SEAT_NOT_AVAILABLE"
            )), 409
        
        # Create ticket
        ticket = ticket_manager.create_ticket(
            sanitized_data['name'],
            sanitized_data['bus'],
            sanitized_data['seat']
        )
        
        if not ticket:
            return jsonify(format_response(False, "Failed to create ticket", error_code="CREATION_FAILED")), 500
        
        # Calculate fare
        seat_type = get_seat_type(sanitized_data['seat'])
        fare = calculate_fare(sanitized_data['bus'], seat_type)
        
        ticket_data = ticket.to_dict()
        ticket_data['fare'] = fare
        ticket_data['seat_type'] = seat_type
        
        log_activity("CREATE_TICKET", ticket.id, {"passenger": sanitized_data['name'], "bus": sanitized_data['bus']})
        
        return jsonify(format_response(
            True, 
            "Ticket booked successfully!", 
            {"ticket": ticket_data}
        )), 201
        
    except Exception as e:
        return jsonify(format_response(False, str(e), error_code="CREATE_TICKET_ERROR")), 500

@api.route('/api/tickets/<int:ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    """Get a specific ticket by ID"""
    try:
        ticket = ticket_manager.get_ticket(ticket_id)
        if not ticket:
            return jsonify(format_response(False, "Ticket not found", error_code="TICKET_NOT_FOUND")), 404
        
        ticket_data = ticket.to_dict()
        seat_type = get_seat_type(ticket.seat)
        fare = calculate_fare(ticket.bus, seat_type)
        
        ticket_data['fare'] = fare
        ticket_data['seat_type'] = seat_type
        
        log_activity("GET_TICKET", ticket_id)
        
        return jsonify(format_response(True, "Ticket retrieved", {"ticket": ticket_data}))
        
    except Exception as e:
        return jsonify(format_response(False, str(e), error_code="GET_TICKET_ERROR")), 500

@api.route('/api/tickets/<int:ticket_id>', methods=['PUT'])
def update_ticket(ticket_id):
    """Update ticket information"""
    try:
        ticket = ticket_manager.get_ticket(ticket_id)
        if not ticket:
            return jsonify(format_response(False, "Ticket not found", error_code="TICKET_NOT_FOUND")), 404
        
        data = request.json
        if not data:
            return jsonify(format_response(False, "No data provided", error_code="NO_DATA")), 400
        
        # Sanitize allowed update fields
        allowed_fields = ['name']
        update_data = {}
        
        for field in allowed_fields:
            if field in data:
                update_data[field] = sanitize_input(data[field])
        
        if not update_data:
            return jsonify(format_response(False, "No valid fields to update", error_code="NO_VALID_FIELDS")), 400
        
        # Update ticket
        updated_ticket = ticket_manager.update_ticket(ticket_id, **update_data)
        
        log_activity("UPDATE_TICKET", ticket_id, {"updated_fields": list(update_data.keys())})
        
        return jsonify(format_response(
            True, 
            "Ticket updated successfully", 
            {"ticket": updated_ticket.to_dict()}
        ))
        
    except Exception as e:
        return jsonify(format_response(False, str(e), error_code="UPDATE_TICKET_ERROR")), 500

@api.route('/api/tickets/<int:ticket_id>', methods=['DELETE'])
def cancel_ticket(ticket_id):
    """Cancel a ticket"""
    try:
        success = ticket_manager.cancel_ticket(ticket_id)
        if not success:
            return jsonify(format_response(False, "Ticket not found", error_code="TICKET_NOT_FOUND")), 404
        
        log_activity("CANCEL_TICKET", ticket_id)
        
        return jsonify(format_response(True, "Ticket cancelled successfully"))
        
    except Exception as e:
        return jsonify(format_response(False, str(e), error_code="CANCEL_TICKET_ERROR")), 500

@api.route('/api/buses', methods=['GET'])
def get_buses_info():
    """Get information about all buses"""
    try:
        buses_info = ticket_manager.get_all_buses_info()
        
        return jsonify(format_response(
            True, 
            "Bus information retrieved", 
            {"buses": buses_info, "count": len(buses_info)}
        ))
        
    except Exception as e:
        return jsonify(format_response(False, str(e), error_code="GET_BUSES_ERROR")), 500

@api.route('/api/buses/<bus_number>', methods=['GET'])
def get_bus_info(bus_number):
    """Get information about a specific bus"""
    try:
        formatted_bus = format_bus_number(bus_number)
        bus_info = ticket_manager.get_bus_info(formatted_bus)
        
        if not bus_info:
            return jsonify(format_response(False, "Bus not found", error_code="BUS_NOT_FOUND")), 404
        
        # Add available seats info
        available_seats = ticket_manager.get_available_seats(formatted_bus)
        bus_info['available_seats_list'] = available_seats
        
        return jsonify(format_response(True, "Bus information retrieved", {"bus": bus_info}))
        
    except Exception as e:
        return jsonify(format_response(False, str(e), error_code="GET_BUS_ERROR")), 500

@api.route('/api/stats', methods=['GET'])
def get_statistics():
    """Get system statistics"""
    try:
        stats = get_system_stats(ticket_manager)
        return jsonify(format_response(True, "Statistics retrieved", {"stats": stats}))
        
    except Exception as e:
        return jsonify(format_response(False, str(e), error_code="GET_STATS_ERROR")), 500

# Error handlers
@api.errorhandler(404)
def not_found(error):
    return jsonify(format_response(False, "Endpoint not found", error_code="NOT_FOUND")), 404

@api.errorhandler(405)
def method_not_allowed(error):
    return jsonify(format_response(False, "Method not allowed", error_code="METHOD_NOT_ALLOWED")), 405

@api.errorhandler(500)
def internal_error(error):
    return jsonify(format_response(False, "Internal server error", error_code="INTERNAL_ERROR")), 500
