from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# In-memory "database"
tickets = {}
ticket_id_counter = 1

# Route 1: Home (serves frontend HTML)
@app.route('/')
def home():
    return render_template('index.html')

# Route 2: Get all tickets
@app.route('/tickets', methods=['GET'])
def get_tickets():
    return jsonify(tickets)

# Route 3: Book a new ticket (POST)
@app.route('/tickets', methods=['POST'])
def book_ticket():
    global ticket_id_counter
    data = request.json
    ticket_id = ticket_id_counter
    tickets[ticket_id] = {
        "id": ticket_id,
        "name": data.get("name"),
        "bus": data.get("bus"),
        "seat": data.get("seat")
    }
    ticket_id_counter += 1
    return jsonify({"message": "Ticket booked successfully!", "ticket": tickets[ticket_id]}), 201

# Route 4: Update ticket details (PUT)
@app.route('/tickets/<int:ticket_id>', methods=['PUT'])
def update_ticket(ticket_id):
    if ticket_id not in tickets:
        return jsonify({"error": "Ticket not found"}), 404
    data = request.json
    tickets[ticket_id].update(data)
    return jsonify({"message": "Ticket updated", "ticket": tickets[ticket_id]})

# Route 5: Delete (Cancel) a ticket
@app.route('/tickets/<int:ticket_id>', methods=['DELETE'])
def delete_ticket(ticket_id):
    if ticket_id not in tickets:
        return jsonify({"error": "Ticket not found"}), 404
    del tickets[ticket_id]
    return jsonify({"message": "Ticket cancelled"})

if __name__ == '__main__':
    app.run(debug=True)
