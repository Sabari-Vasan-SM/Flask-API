// Modern Bus Ticket Booking System JavaScript

class BusTicketManager {
    constructor() {
        this.selectedBus = '';
        this.selectedSeat = '';
        this.availableSeats = {};
        this.stats = {};
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadStats();
        this.loadBusInfo();
        this.updateOutput('System initialized. Ready to book tickets!', 'info');
    }

    setupEventListeners() {
        // Form submissions
        document.getElementById('book-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.bookTicket();
        });

        document.getElementById('update-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.updateTicket();
        });

        document.getElementById('delete-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.deleteTicket();
        });

        // Bus selection
        document.querySelectorAll('.bus-option').forEach(bus => {
            bus.addEventListener('click', () => {
                this.selectBus(bus.dataset.bus);
            });
        });

        // Auto-format inputs
        document.getElementById('bus').addEventListener('input', this.formatBusInput);
        document.getElementById('seat').addEventListener('input', this.formatSeatInput);
        document.getElementById('updateBus').addEventListener('input', this.formatBusInput);
        document.getElementById('updateSeat').addEventListener('input', this.formatSeatInput);
    }

    formatBusInput(e) {
        let value = e.target.value.replace(/[^0-9]/g, '');
        if (value) {
            value = parseInt(value);
            if (value >= 1 && value <= 999) {
                e.target.value = `BUS${value.toString().padStart(3, '0')}`;
            }
        }
    }

    formatSeatInput(e) {
        let value = e.target.value.replace(/[^0-9]/g, '');
        if (value) {
            value = parseInt(value);
            if (value >= 1 && value <= 40) {
                e.target.value = `S${value.toString().padStart(2, '0')}`;
            }
        }
    }

    selectBus(busNumber) {
        this.selectedBus = busNumber;
        
        // Update UI
        document.querySelectorAll('.bus-option').forEach(bus => {
            bus.classList.remove('selected');
        });
        document.querySelector(`[data-bus="${busNumber}"]`).classList.add('selected');
        
        // Update bus input
        document.getElementById('bus').value = busNumber;
        
        // Load seat map
        this.loadSeatMap(busNumber);
    }

    async loadSeatMap(busNumber) {
        try {
            const response = await this.makeRequest(`/api/buses/${busNumber}`);
            if (response.success) {
                this.renderSeatMap(response.data.bus, busNumber);
            }
        } catch (error) {
            console.error('Error loading seat map:', error);
        }
    }

    renderSeatMap(busInfo, busNumber) {
        const seatGrid = document.getElementById('seat-grid');
        seatGrid.innerHTML = '';

        // Generate all seats (S01 to S40)
        for (let i = 1; i <= 40; i++) {
            const seatNumber = `S${i.toString().padStart(2, '0')}`;
            const seatElement = document.createElement('div');
            seatElement.className = 'seat';
            seatElement.textContent = seatNumber;
            seatElement.dataset.seat = seatNumber;

            // Check if seat is available
            if (busInfo.available_seats_list && busInfo.available_seats_list.includes(seatNumber)) {
                seatElement.classList.add('available');
                seatElement.addEventListener('click', () => this.selectSeat(seatNumber));
            } else {
                seatElement.classList.add('booked');
            }

            seatGrid.appendChild(seatElement);
        }
    }

    selectSeat(seatNumber) {
        this.selectedSeat = seatNumber;
        
        // Update UI
        document.querySelectorAll('.seat').forEach(seat => {
            seat.classList.remove('selected');
        });
        document.querySelector(`[data-seat="${seatNumber}"]`).classList.add('selected');
        
        // Update seat input
        document.getElementById('seat').value = seatNumber;
    }

    async makeRequest(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        const response = await fetch(url, { ...defaultOptions, ...options });
        return await response.json();
    }

    async bookTicket() {
        const submitBtn = document.querySelector('#book-form button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        
        try {
            submitBtn.innerHTML = '<span class="loading"></span> Booking...';
            submitBtn.disabled = true;

            const formData = {
                name: document.getElementById('name').value.trim(),
                bus: document.getElementById('bus').value.trim(),
                seat: document.getElementById('seat').value.trim()
            };

            // Validate form
            if (!formData.name || !formData.bus || !formData.seat) {
                throw new Error('All fields are required');
            }

            const response = await this.makeRequest('/api/tickets', {
                method: 'POST',
                body: JSON.stringify(formData)
            });

            if (response.success) {
                this.updateOutput(JSON.stringify(response, null, 2), 'success');
                this.clearForm('book-form');
                this.loadStats();
                if (this.selectedBus) {
                    this.loadSeatMap(this.selectedBus);
                }
                this.showAlert('Ticket booked successfully!', 'success');
            } else {
                this.updateOutput(JSON.stringify(response, null, 2), 'error');
                this.showAlert(response.message || 'Booking failed', 'error');
            }

        } catch (error) {
            this.updateOutput(`Error: ${error.message}`, 'error');
            this.showAlert(error.message, 'error');
        } finally {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }

    async getTickets() {
        try {
            const busFilter = document.getElementById('filterBus').value;
            let url = '/api/tickets';
            if (busFilter) {
                url += `?bus=${busFilter}`;
            }

            const response = await this.makeRequest(url);
            this.updateOutput(JSON.stringify(response, null, 2), response.success ? 'success' : 'error');
        } catch (error) {
            this.updateOutput(`Error: ${error.message}`, 'error');
        }
    }

    async updateTicket() {
        const submitBtn = document.querySelector('#update-form button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        
        try {
            submitBtn.innerHTML = '<span class="loading"></span> Updating...';
            submitBtn.disabled = true;

            const ticketId = document.getElementById('updateId').value;
            const newName = document.getElementById('updateName').value.trim();

            if (!ticketId || !newName) {
                throw new Error('Ticket ID and new name are required');
            }

            const response = await this.makeRequest(`/api/tickets/${ticketId}`, {
                method: 'PUT',
                body: JSON.stringify({ name: newName })
            });

            if (response.success) {
                this.updateOutput(JSON.stringify(response, null, 2), 'success');
                this.clearForm('update-form');
                this.showAlert('Ticket updated successfully!', 'success');
            } else {
                this.updateOutput(JSON.stringify(response, null, 2), 'error');
                this.showAlert(response.message || 'Update failed', 'error');
            }

        } catch (error) {
            this.updateOutput(`Error: ${error.message}`, 'error');
            this.showAlert(error.message, 'error');
        } finally {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }

    async deleteTicket() {
        const submitBtn = document.querySelector('#delete-form button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        
        try {
            const ticketId = document.getElementById('deleteId').value;
            if (!ticketId) {
                throw new Error('Ticket ID is required');
            }

            if (!confirm(`Are you sure you want to cancel ticket #${ticketId}?`)) {
                return;
            }

            submitBtn.innerHTML = '<span class="loading"></span> Cancelling...';
            submitBtn.disabled = true;

            const response = await this.makeRequest(`/api/tickets/${ticketId}`, {
                method: 'DELETE'
            });

            if (response.success) {
                this.updateOutput(JSON.stringify(response, null, 2), 'success');
                this.clearForm('delete-form');
                this.loadStats();
                if (this.selectedBus) {
                    this.loadSeatMap(this.selectedBus);
                }
                this.showAlert('Ticket cancelled successfully!', 'success');
            } else {
                this.updateOutput(JSON.stringify(response, null, 2), 'error');
                this.showAlert(response.message || 'Cancellation failed', 'error');
            }

        } catch (error) {
            this.updateOutput(`Error: ${error.message}`, 'error');
            this.showAlert(error.message, 'error');
        } finally {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }

    async loadStats() {
        try {
            const response = await this.makeRequest('/api/stats');
            if (response.success) {
                this.updateStatsDisplay(response.data.stats);
            }
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    updateStatsDisplay(stats) {
        const elements = {
            'total-tickets': stats.total_tickets,
            'total-buses': stats.total_buses,
            'booked-seats': stats.booked_seats,
            'available-seats': stats.available_seats,
            'occupancy-rate': `${stats.overall_occupancy}%`
        };

        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
    }

    async loadBusInfo() {
        try {
            const response = await this.makeRequest('/api/buses');
            if (response.success) {
                this.renderBusOptions(response.data.buses);
            }
        } catch (error) {
            console.error('Error loading bus info:', error);
        }
    }

    renderBusOptions(buses) {
        const busSelector = document.getElementById('bus-selector');
        if (!busSelector) return;

        busSelector.innerHTML = '';
        Object.keys(buses).forEach(busNumber => {
            const busOption = document.createElement('div');
            busOption.className = 'bus-option';
            busOption.dataset.bus = busNumber;
            busOption.innerHTML = `
                <div>${busNumber}</div>
                <small>${buses[busNumber].available_seats} seats</small>
            `;
            busOption.addEventListener('click', () => this.selectBus(busNumber));
            busSelector.appendChild(busOption);
        });
    }

    updateOutput(content, type = 'info') {
        const output = document.getElementById('output');
        output.textContent = content;
        output.className = `output ${type}`;
        output.scrollTop = output.scrollHeight;
    }

    clearForm(formId) {
        const form = document.getElementById(formId);
        if (form) {
            form.reset();
        }
        
        // Clear selections
        if (formId === 'book-form') {
            this.selectedBus = '';
            this.selectedSeat = '';
            document.querySelectorAll('.bus-option').forEach(bus => {
                bus.classList.remove('selected');
            });
            document.querySelectorAll('.seat').forEach(seat => {
                seat.classList.remove('selected');
            });
        }
    }

    showAlert(message, type = 'info') {
        // Remove existing alerts
        document.querySelectorAll('.alert').forEach(alert => alert.remove());

        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.textContent = message;

        const container = document.querySelector('.container');
        container.insertBefore(alert, container.firstChild);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            alert.remove();
        }, 5000);
    }

    async getTicketById() {
        const ticketId = prompt('Enter ticket ID:');
        if (!ticketId) return;

        try {
            const response = await this.makeRequest(`/api/tickets/${ticketId}`);
            this.updateOutput(JSON.stringify(response, null, 2), response.success ? 'success' : 'error');
        } catch (error) {
            this.updateOutput(`Error: ${error.message}`, 'error');
        }
    }

    async getBusInfo() {
        const busNumber = prompt('Enter bus number (e.g., BUS001):');
        if (!busNumber) return;

        try {
            const response = await this.makeRequest(`/api/buses/${busNumber}`);
            this.updateOutput(JSON.stringify(response, null, 2), response.success ? 'success' : 'error');
        } catch (error) {
            this.updateOutput(`Error: ${error.message}`, 'error');
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.ticketManager = new BusTicketManager();
});

// Global functions for backward compatibility
function getTickets() {
    window.ticketManager.getTickets();
}

function bookTicket() {
    window.ticketManager.bookTicket();
}

function updateTicket() {
    window.ticketManager.updateTicket();
}

function deleteTicket() {
    window.ticketManager.deleteTicket();
}

function getStats() {
    window.ticketManager.loadStats();
}

function getTicketById() {
    window.ticketManager.getTicketById();
}

function getBusInfo() {
    window.ticketManager.getBusInfo();
}
