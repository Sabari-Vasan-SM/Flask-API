// Modern Bus Ticket Booking System with Enhanced Animations and Interactions
// This JavaScript file handles all frontend functionality for the bus booking system

class ModernBusTicketManager {
    constructor() {
        // Initialize instance variables to track user selections and system state
        this.selectedBus = '';              // Currently selected bus number (e.g., 'BUS001')
        this.selectedSeat = '';             // Currently selected seat number (e.g., 'S01')
        this.availableSeats = {};           // Cache of available seats per bus
        
        // Initialize statistics object to track system metrics
        this.stats = {
            totalTickets: 0,                // Total number of tickets booked
            totalBuses: 5,                  // Number of buses in the system
            bookedSeats: 0,                 // Total number of booked seats
            availableSeats: 200,            // Total number of available seats
            occupancyRate: 0                // Percentage of seats occupied
        };
        
        // Define bus data with routes, pricing, and capacity information
        this.busData = {
            'BUS001': { route: 'Mumbai → Delhi', seats: 40, price: 1200 },        // Long distance, premium route
            'BUS002': { route: 'Delhi → Bangalore', seats: 40, price: 1800 },     // Cross-country route
            'BUS003': { route: 'Chennai → Hyderabad', seats: 40, price: 900 },    // Regional route
            'BUS004': { route: 'Pune → Goa', seats: 40, price: 600 },             // Popular tourist route
            'BUS005': { route: 'Kolkata → Bhubaneswar', seats: 40, price: 800 }   // Eastern region route
        };
        
        // Initialize the application once the object is created
        this.init();
    }

    init() {
        // Set up all event listeners for user interactions
        this.setupEventListeners();
        
        // Load current system statistics from the server
        this.loadStats();
        
        // Generate the visual bus selection interface
        this.generateBusSelector();
        
        // Animate the statistics cards for visual appeal
        this.animateStatsCards();
        
        // Display welcome message to indicate system is ready
        this.updateOutput('🚌 Welcome to Modern Bus Ticket Booking System!\\n\\nSystem initialized successfully. Ready to serve you!', 'success');
        this.startParticleAnimation();
    }

    setupEventListeners() {
        // Form submissions with enhanced validation
        document.getElementById('book-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.bookTicketWithAnimation();
        });

        document.getElementById('update-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.updateTicketWithAnimation();
        });

        document.getElementById('delete-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.deleteTicketWithAnimation();
        });

        // Real-time input formatting and validation
        this.setupInputValidation();
        this.setupHoverEffects();
        this.setupKeyboardShortcuts();
    }

    setupInputValidation() {
        const inputs = document.querySelectorAll('.form-input');
        inputs.forEach(input => {
            input.addEventListener('input', (e) => {
                this.validateInput(e.target);
                this.addInputAnimation(e.target);
            });

            input.addEventListener('focus', (e) => {
                this.addFocusAnimation(e.target);
            });

            input.addEventListener('blur', (e) => {
                this.removeFocusAnimation(e.target);
            });
        });

        // Auto-format bus and seat inputs
        document.getElementById('bus').addEventListener('input', this.formatBusInput);
        document.getElementById('seat').addEventListener('input', this.formatSeatInput);
    }

    setupHoverEffects() {
        // Add hover effects to buttons
        document.querySelectorAll('.btn').forEach(btn => {
            btn.addEventListener('mouseenter', (e) => {
                this.addButtonHoverEffect(e.target);
            });

            btn.addEventListener('mouseleave', (e) => {
                this.removeButtonHoverEffect(e.target);
            });
        });

        // Add hover effects to cards
        document.querySelectorAll('.card').forEach((card, index) => {
            card.style.setProperty('--delay', index);
        });
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case 'b':
                        e.preventDefault();
                        document.getElementById('name').focus();
                        break;
                    case 'v':
                        e.preventDefault();
                        this.getTickets();
                        break;
                }
            }
        });
    }

    validateInput(input) {
        const value = input.value;
        const pattern = input.getAttribute('pattern');
        
        if (pattern) {
            const regex = new RegExp(pattern);
            if (regex.test(value) || value === '') {
                input.classList.remove('error');
                input.classList.add('valid');
            } else {
                input.classList.remove('valid');
                input.classList.add('error');
            }
        }
    }

    addInputAnimation(input) {
        input.style.transform = 'scale(1.02)';
        setTimeout(() => {
            input.style.transform = 'scale(1)';
        }, 150);
    }

    addFocusAnimation(input) {
        input.parentElement.classList.add('focused');
    }

    removeFocusAnimation(input) {
        input.parentElement.classList.remove('focused');
    }

    addButtonHoverEffect(button) {
        button.style.transform = 'translateY(-3px) scale(1.05)';
    }

    removeButtonHoverEffect(button) {
        button.style.transform = '';
    }

    generateBusSelector() {
        const selector = document.getElementById('bus-selector');
        if (!selector) return;
        
        selector.innerHTML = '';

        Object.keys(this.busData).forEach((busId, index) => {
            const busOption = document.createElement('div');
            busOption.className = 'bus-option';
            busOption.dataset.bus = busId;
            busOption.innerHTML = `
                <div class="bus-id">${busId}</div>
                <div class="bus-route">${this.busData[busId].route}</div>
                <div class="bus-price">₹${this.busData[busId].price}</div>
            `;
            
            busOption.style.animationDelay = `${index * 0.1}s`;
            busOption.addEventListener('click', () => this.selectBusWithAnimation(busId));
            
            selector.appendChild(busOption);
        });
    }

    selectBusWithAnimation(busId) {
        // Remove previous selection
        document.querySelectorAll('.bus-option').forEach(option => {
            option.classList.remove('selected');
        });

        // Add selection with animation
        const selectedOption = document.querySelector(`[data-bus="${busId}"]`);
        if (selectedOption) {
            selectedOption.classList.add('selected');
            
            // Animate selection
            selectedOption.style.transform = 'scale(1.1)';
            setTimeout(() => {
                selectedOption.style.transform = 'scale(1.05)';
            }, 200);

            this.selectedBus = busId;
            document.getElementById('bus').value = busId;
            this.generateSeatMap(busId);
            this.showNotification(`Bus ${busId} selected! Route: ${this.busData[busId].route}`, 'info');
        }
    }

    generateSeatMap(busId) {
        const seatGrid = document.getElementById('seat-grid');
        if (!seatGrid) return;
        
        seatGrid.innerHTML = '';
        
        const totalSeats = this.busData[busId].seats;
        
        for (let i = 1; i <= totalSeats; i++) {
            const seatId = `S${i.toString().padStart(2, '0')}`;
            const seat = document.createElement('div');
            seat.className = 'seat available';
            seat.textContent = seatId;
            seat.dataset.seat = seatId;
            
            // Random booking status for demo
            if (Math.random() < 0.3) {
                seat.className = 'seat booked';
            }
            
            seat.style.animationDelay = `${i * 0.02}s`;
            seat.addEventListener('click', () => this.selectSeatWithAnimation(seatId, seat));
            
            seatGrid.appendChild(seat);
        }
    }

    selectSeatWithAnimation(seatId, seatElement) {
        if (seatElement.classList.contains('booked')) {
            this.showNotification('This seat is already booked!', 'error');
            seatElement.style.animation = 'shake 0.5s ease-in-out';
            setTimeout(() => {
                seatElement.style.animation = '';
            }, 500);
            return;
        }

        // Remove previous selection
        document.querySelectorAll('.seat').forEach(seat => {
            seat.classList.remove('selected');
        });

        // Add selection
        seatElement.classList.remove('available');
        seatElement.classList.add('selected');
        
        this.selectedSeat = seatId;
        document.getElementById('seat').value = seatId;
        
        // Animate selection
        seatElement.style.animation = 'bounce 0.6s ease-in-out';
        this.showNotification(`Seat ${seatId} selected!`, 'success');
    }

    async bookTicketWithAnimation() {
        const name = document.getElementById('name').value;
        const bus = document.getElementById('bus').value;
        const seat = document.getElementById('seat').value;
        
        if (!this.validateBookingForm({name, bus, seat})) {
            return;
        }

        // Show loading animation
        const submitBtn = document.querySelector('#book-form .btn');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<span class="loading"></span> Booking...';
        submitBtn.disabled = true;

        try {
            const response = await this.makeAPICall('/api/tickets', 'POST', {name, bus, seat});
            
            if (response.id || response.success) {
                // Success animation
                submitBtn.innerHTML = '✅ Booked Successfully!';
                submitBtn.style.background = 'linear-gradient(135deg, #10b981, #059669)';
                
                this.updateOutput(`🎉 Ticket booked successfully!\\n\\n${this.formatTicketInfo(response)}`, 'success');
                this.animateStatsUpdate();
                this.resetForm('book-form');
                this.showSuccessConfetti();
                
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.style.background = '';
                    submitBtn.disabled = false;
                }, 3000);
            }
        } catch (error) {
            submitBtn.innerHTML = '❌ Booking Failed';
            submitBtn.style.background = 'linear-gradient(135deg, #ef4444, #dc2626)';
            this.updateOutput(`❌ Error: ${error.message}`, 'error');
            
            setTimeout(() => {
                submitBtn.innerHTML = originalText;
                submitBtn.style.background = '';
                submitBtn.disabled = false;
            }, 3000);
        }
    }

    async updateTicketWithAnimation() {
        const id = document.getElementById('updateId').value;
        const name = document.getElementById('updateName').value;
        
        if (!id || !name) {
            this.showNotification('Please fill in all required fields', 'error');
            return;
        }

        const submitBtn = document.querySelector('#update-form .btn');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<span class="loading"></span> Updating...';
        submitBtn.disabled = true;

        try {
            const response = await this.makeAPICall(`/api/tickets/${id}`, 'PUT', {name});
            
            submitBtn.innerHTML = '✅ Updated Successfully!';
            this.updateOutput(`✏️ Ticket updated successfully!\\n\\n${this.formatTicketInfo(response)}`, 'success');
            this.resetForm('update-form');
            
        } catch (error) {
            submitBtn.innerHTML = '❌ Update Failed';
            this.updateOutput(`❌ Error: ${error.message}`, 'error');
        }

        setTimeout(() => {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }, 3000);
    }

    async deleteTicketWithAnimation() {
        const id = document.getElementById('deleteId').value;
        
        if (!id) {
            this.showNotification('Please enter a ticket ID', 'error');
            return;
        }

        if (!confirm('Are you sure you want to cancel this ticket?')) {
            return;
        }

        const submitBtn = document.querySelector('#delete-form .btn');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<span class="loading"></span> Cancelling...';
        submitBtn.disabled = true;

        try {
            await this.makeAPICall(`/api/tickets/${id}`, 'DELETE');
            
            submitBtn.innerHTML = '✅ Cancelled Successfully!';
            this.updateOutput(`🗑️ Ticket cancelled successfully!\\n\\nTicket ID: ${id}`, 'success');
            this.animateStatsUpdate();
            this.resetForm('delete-form');
            
        } catch (error) {
            submitBtn.innerHTML = '❌ Cancellation Failed';
            this.updateOutput(`❌ Error: ${error.message}`, 'error');
        }

        setTimeout(() => {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }, 3000);
    }

    validateBookingForm(data) {
        if (!data.name || data.name.length < 2) {
            this.showNotification('Please enter a valid name (at least 2 characters)', 'error');
            return false;
        }
        
        if (!data.bus || !data.bus.match(/^BUS\\d{3}$/)) {
            this.showNotification('Please enter a valid bus number (format: BUS001)', 'error');
            return false;
        }
        
        if (!data.seat || !data.seat.match(/^S\\d{2}$/)) {
            this.showNotification('Please enter a valid seat number (format: S01)', 'error');
            return false;
        }
        
        return true;
    }

    async makeAPICall(url, method, data = null) {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(url, options);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    formatTicketInfo(ticket) {
        return `Ticket ID: ${ticket.id || 'Generated'}
Passenger: ${ticket.name}
Bus: ${ticket.bus}
Seat: ${ticket.seat}
Status: Confirmed
Booked: ${new Date().toLocaleString()}`;
    }

    resetForm(formId) {
        document.getElementById(formId).reset();
        
        // Reset seat selection
        document.querySelectorAll('.seat.selected').forEach(seat => {
            seat.classList.remove('selected');
            seat.classList.add('available');
        });
        
        // Reset bus selection
        document.querySelectorAll('.bus-option.selected').forEach(option => {
            option.classList.remove('selected');
        });
    }

    animateStatsCards() {
        const cards = document.querySelectorAll('.stat-card');
        cards.forEach((card, index) => {
            card.style.setProperty('--delay', index);
            card.style.animation = `slideInUp 0.6s ease-out ${index * 0.1}s both`;
        });
    }

    animateStatsUpdate() {
        // Simulate stats update
        this.stats.totalTickets += 1;
        this.stats.bookedSeats += 1;
        this.stats.availableSeats -= 1;
        this.updateStatsDisplay();
        
        // Add pulse animation to updated stats
        document.querySelectorAll('.stat-card').forEach(card => {
            card.style.animation = 'pulse 0.5s ease-in-out';
            setTimeout(() => {
                card.style.animation = '';
            }, 500);
        });
    }

    animateCounter(elementId, targetValue, suffix = '') {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const startValue = parseInt(element.textContent) || 0;
        const duration = 1000;
        const stepTime = 50;
        const steps = duration / stepTime;
        const stepValue = (targetValue - startValue) / steps;
        
        let currentValue = startValue;
        const timer = setInterval(() => {
            currentValue += stepValue;
            if (
                (stepValue > 0 && currentValue >= targetValue) ||
                (stepValue < 0 && currentValue <= targetValue)
            ) {
                currentValue = targetValue;
                clearInterval(timer);
            }
            element.textContent = Math.round(currentValue) + suffix;
        }, stepTime);
    }

    updateStatsDisplay() {
        this.animateCounter('total-tickets', this.stats.totalTickets);
        this.animateCounter('total-buses', this.stats.totalBuses);
        this.animateCounter('booked-seats', this.stats.bookedSeats);
        this.animateCounter('available-seats', this.stats.availableSeats);
        
        const occupancyRate = this.stats.totalTickets > 0 ? 
            Math.round((this.stats.bookedSeats / (this.stats.bookedSeats + this.stats.availableSeats)) * 100) : 0;
        this.animateCounter('occupancy-rate', occupancyRate, '%');
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <span>${message}</span>
            <button onclick="this.parentElement.remove()">×</button>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
            notification.style.opacity = '1';
        }, 10);
        
        // Auto remove
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            notification.style.opacity = '0';
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, 300);
        }, 5000);
    }

    showSuccessConfetti() {
        // Create confetti effect
        for (let i = 0; i < 50; i++) {
            const confetti = document.createElement('div');
            confetti.className = 'confetti';
            confetti.style.left = Math.random() * 100 + '%';
            confetti.style.backgroundColor = ['#6366f1', '#10b981', '#f59e0b', '#ef4444'][Math.floor(Math.random() * 4)];
            confetti.style.animationDelay = Math.random() * 3 + 's';
            document.body.appendChild(confetti);
            
            setTimeout(() => {
                if (confetti.parentElement) {
                    confetti.remove();
                }
            }, 3000);
        }
    }

    startParticleAnimation() {
        // Add floating particles effect
        setInterval(() => {
            if (document.querySelectorAll('.particle').length < 10) {
                const particle = document.createElement('div');
                particle.className = 'particle';
                particle.style.left = Math.random() * 100 + '%';
                particle.style.animationDuration = (Math.random() * 10 + 5) + 's';
                document.body.appendChild(particle);
                
                setTimeout(() => {
                    if (particle.parentElement) {
                        particle.remove();
                    }
                }, 15000);
            }
        }, 2000);
    }

    updateOutput(message, type = 'info') {
        const output = document.getElementById('output');
        const timestamp = new Date().toLocaleTimeString();
        
        // Add typing animation
        output.style.opacity = '0.5';
        setTimeout(() => {
            output.textContent = `[${timestamp}] ${message}`;
            output.style.opacity = '1';
            
            // Add color coding based on type
            switch(type) {
                case 'success':
                    output.style.borderLeft = '4px solid #10b981';
                    break;
                case 'error':
                    output.style.borderLeft = '4px solid #ef4444';
                    break;
                case 'info':
                default:
                    output.style.borderLeft = '4px solid #6366f1';
                    break;
            }
        }, 100);
        
        // Scroll to output
        output.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    async loadStats() {
        try {
            const response = await fetch('/api/stats');
            if (response.ok) {
                this.stats = await response.json();
            }
        } catch (error) {
            console.log('Stats endpoint not available, using mock data');
        }
        this.updateStatsDisplay();
    }

    async getTickets() {
        try {
            const filterBus = document.getElementById('filterBus').value;
            let url = '/api/tickets';
            if (filterBus) {
                url += `?bus=${filterBus}`;
            }
            
            const response = await this.makeAPICall(url, 'GET');
            this.updateOutput(`📋 All Tickets:\\n\\n${this.formatTicketsList(response)}`, 'info');
        } catch (error) {
            this.updateOutput(`❌ Error fetching tickets: ${error.message}`, 'error');
        }
    }

    async getTicketById() {
        const id = prompt('Enter Ticket ID:');
        if (!id) return;

        try {
            const response = await this.makeAPICall(`/api/tickets/${id}`, 'GET');
            this.updateOutput(`🎫 Ticket Details:\\n\\n${this.formatTicketInfo(response)}`, 'info');
        } catch (error) {
            this.updateOutput(`❌ Error fetching ticket: ${error.message}`, 'error');
        }
    }

    async getBusInfo() {
        try {
            const response = await this.makeAPICall('/api/buses', 'GET');
            this.updateOutput(`🚌 Bus Information:\\n\\n${this.formatBusList(response)}`, 'info');
        } catch (error) {
            this.updateOutput(`❌ Error fetching bus info: ${error.message}`, 'error');
        }
    }

    formatTicketsList(tickets) {
        if (!tickets || tickets.length === 0) {
            return 'No tickets found.';
        }
        
        return tickets.map(ticket => 
            `ID: ${ticket.id} | ${ticket.name} | ${ticket.bus} | ${ticket.seat}`
        ).join('\\n');
    }

    formatBusList(buses) {
        if (!buses || buses.length === 0) {
            return 'No buses found.';
        }
        
        return buses.map(bus => 
            `${bus.bus} | ${bus.available_seats}/${bus.total_seats} seats available`
        ).join('\\n');
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
    window.busManager = new ModernBusTicketManager();
});

// Global functions for HTML onclick events
function getTickets() {
    window.busManager.getTickets();
}

function getTicketById() {
    window.busManager.getTicketById();
}

function getBusInfo() {
    window.busManager.getBusInfo();
}

// Add CSS for enhanced animations and effects
const enhancedStyles = `
.notification {
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 1rem 1.5rem;
    border-radius: 0.75rem;
    color: white;
    font-weight: 500;
    transform: translateX(100%);
    opacity: 0;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 1000;
    display: flex;
    align-items: center;
    gap: 1rem;
    min-width: 300px;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    backdrop-filter: blur(10px);
}

.notification.success {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.9), rgba(5, 150, 105, 0.9));
}

.notification.error {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.9), rgba(220, 38, 38, 0.9));
}

.notification.info {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.9), rgba(79, 70, 229, 0.9));
}

.notification button {
    background: none;
    border: none;
    color: white;
    font-size: 1.2rem;
    cursor: pointer;
    padding: 0;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: background-color 0.2s;
}

.notification button:hover {
    background-color: rgba(255, 255, 255, 0.2);
}

.confetti {
    position: fixed;
    width: 8px;
    height: 8px;
    background: #6366f1;
    animation: confettiFall 3s linear infinite;
    z-index: 1000;
    pointer-events: none;
    border-radius: 2px;
}

@keyframes confettiFall {
    0% {
        transform: translateY(-100vh) rotate(0deg);
        opacity: 1;
    }
    100% {
        transform: translateY(100vh) rotate(720deg);
        opacity: 0;
    }
}

.particle {
    position: fixed;
    width: 3px;
    height: 3px;
    background: rgba(255, 255, 255, 0.6);
    border-radius: 50%;
    animation: particleFloat linear infinite;
    z-index: -1;
    pointer-events: none;
}

@keyframes particleFloat {
    0% {
        transform: translateY(100vh) translateX(0);
        opacity: 0;
    }
    10% {
        opacity: 1;
    }
    90% {
        opacity: 1;
    }
    100% {
        transform: translateY(-100vh) translateX(50px);
        opacity: 0;
    }
}

@keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
}

.form-input.valid {
    border-color: #10b981;
    box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.form-input.error {
    border-color: #ef4444;
    box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
    animation: shake 0.5s ease-in-out;
}

.loading {
    display: inline-block;
    width: 16px;
    height: 16px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    border-top-color: white;
    animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

.bus-option {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
    padding: 1.5rem;
    border: 2px solid rgba(255, 255, 255, 0.2);
    border-radius: 1rem;
    background: var(--card-background);
    backdrop-filter: blur(10px);
    text-align: center;
    position: relative;
    overflow: hidden;
}

.bus-option::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
    transition: all 0.3s ease;
}

.bus-option:hover {
    transform: translateY(-5px) scale(1.02);
    box-shadow: var(--shadow-lg);
    border-color: var(--primary-color);
}

.bus-option:hover::before {
    left: 100%;
}

.bus-option.selected {
    background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
    color: white;
    border-color: var(--primary-color);
    transform: scale(1.05);
    animation: pulse 1s ease-in-out;
}

.bus-id {
    font-weight: 700;
    font-size: 1.2rem;
    margin-bottom: 0.5rem;
}

.bus-route {
    font-size: 0.875rem;
    opacity: 0.8;
    margin: 0.5rem 0;
    font-weight: 500;
}

.bus-price {
    font-weight: 600;
    color: var(--success-color);
    font-size: 1.1rem;
}

.bus-option.selected .bus-price {
    color: white;
}

.form-group.focused .form-label {
    color: var(--primary-color);
    transform: translateY(-2px);
}

.seat {
    position: relative;
    overflow: hidden;
}

.seat::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(circle, rgba(255, 255, 255, 0.3) 0%, transparent 70%);
    opacity: 0;
    transition: opacity 0.3s ease;
}

.seat:hover::before {
    opacity: 1;
}

/* Enhanced card animations */
.card {
    animation: slideInUp 0.8s ease-out calc(var(--delay, 0) * 0.2s) both;
}

@keyframes slideInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Accessibility improvements */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* Mobile enhancements */
@media (max-width: 768px) {
    .notification {
        right: 10px;
        left: 10px;
        min-width: auto;
        transform: translateY(-100%);
    }
    
    .notification.show {
        transform: translateY(0);
    }
}
`;

// Inject enhanced styles
const styleSheet = document.createElement('style');
styleSheet.textContent = enhancedStyles;
document.head.appendChild(styleSheet);
