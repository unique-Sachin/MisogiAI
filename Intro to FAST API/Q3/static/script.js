// API Base URL
const API_BASE = '';

// Global state
let venues = [];
let events = [];
let ticketTypes = [];
let bookings = [];

// DOM Elements
const sections = document.querySelectorAll('.section');
const navButtons = document.querySelectorAll('.nav-btn');

// Navigation
navButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        const targetSection = btn.dataset.section;
        showSection(targetSection);
        
        // Update active nav button
        navButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
    });
});

function showSection(sectionId) {
    sections.forEach(section => {
        if (section.id === sectionId) {
            section.classList.add('active');
        } else {
            section.classList.remove('active');
        }
    });
    
    // Load section-specific data
    switch(sectionId) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'venues':
            loadVenues();
            break;
        case 'events':
            loadEvents();
            loadVenuesForSelect();
            break;
        case 'ticket-types':
            loadTicketTypes();
            break;
        case 'bookings':
            loadBookings();
            loadEventsForSelect();
            loadTicketTypesForSelect();
            break;
    }
}

// API Functions
async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(API_BASE + endpoint, options);
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'API Error');
        }
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showMessage(error.message, 'error');
        throw error;
    }
}

// Message System
function showMessage(text, type = 'success') {
    const messageEl = document.getElementById('message');
    messageEl.textContent = text;
    messageEl.className = `message ${type}`;
    messageEl.classList.add('show');
    
    setTimeout(() => {
        messageEl.classList.remove('show');
    }, 3000);
}

// Dashboard Functions
async function loadDashboardData() {
    try {
        const stats = await apiCall('/bookings/stats');
        
        document.getElementById('total-bookings').textContent = stats.total_bookings;
        document.getElementById('total-events').textContent = stats.total_events;
        document.getElementById('total-venues').textContent = stats.total_venues;
        document.getElementById('total-revenue').textContent = `$${stats.total_revenue.toFixed(2)}`;
        document.getElementById('available-tickets').textContent = stats.available_tickets;
        
        // Load recent events and top venues
        await loadRecentEvents();
        await loadTopVenues();
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

async function loadRecentEvents() {
    try {
        const eventsData = await apiCall('/events?limit=5');
        const container = document.getElementById('recent-events');
        
        container.innerHTML = eventsData.map(event => `
            <div class="data-item">
                <h4>${event.name}</h4>
                <p>📅 ${new Date(event.event_date).toLocaleDateString()}</p>
                <p>🎫 Max: ${event.max_tickets}</p>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading recent events:', error);
    }
}

async function loadTopVenues() {
    try {
        const venuesData = await apiCall('/venues?limit=5');
        const container = document.getElementById('top-venues');
        
        container.innerHTML = venuesData.map(venue => `
            <div class="data-item">
                <h4>${venue.name}</h4>
                <p>📍 ${venue.address}</p>
                <p>👥 Capacity: ${venue.capacity}</p>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading top venues:', error);
    }
}

// Venue Functions
async function loadVenues() {
    try {
        venues = await apiCall('/venues');
        displayVenues();
    } catch (error) {
        console.error('Error loading venues:', error);
    }
}

function displayVenues() {
    const container = document.getElementById('venues-list');
    container.innerHTML = venues.map(venue => `
        <div class="data-item">
            <h4>🏛️ ${venue.name}</h4>
            <p>📍 ${venue.address}</p>
            <p>👥 Capacity: ${venue.capacity}</p>
            <p>ℹ️ ${venue.description || 'No description'}</p>
            <div class="action-buttons">
                <button class="action-btn btn-view" onclick="viewVenueOccupancy(${venue.id})">Occupancy</button>
                <button class="action-btn btn-delete" onclick="deleteVenue(${venue.id})">Delete</button>
            </div>
        </div>
    `).join('');
}

async function viewVenueOccupancy(venueId) {
    try {
        const occupancy = await apiCall(`/venues/${venueId}/occupancy`);
        alert(`Occupancy Rate: ${occupancy.occupancy_rate}%\nTotal Bookings: ${occupancy.total_bookings}\nTotal Events: ${occupancy.total_events}`);
    } catch (error) {
        console.error('Error loading venue occupancy:', error);
    }
}

async function deleteVenue(venueId) {
    if (confirm('Are you sure you want to delete this venue?')) {
        try {
            await apiCall(`/venues/${venueId}`, 'DELETE');
            showMessage('Venue deleted successfully');
            loadVenues();
        } catch (error) {
            console.error('Error deleting venue:', error);
        }
    }
}

// Event Functions
async function loadEvents() {
    try {
        events = await apiCall('/events');
        displayEvents();
    } catch (error) {
        console.error('Error loading events:', error);
    }
}

function displayEvents() {
    const container = document.getElementById('events-list');
    container.innerHTML = events.map(event => `
        <div class="data-item">
            <h4>🎭 ${event.name}</h4>
            <p>📅 ${new Date(event.event_date).toLocaleString()}</p>
            <p>🎫 Max Tickets: ${event.max_tickets}</p>
            <p>ℹ️ ${event.description || 'No description'}</p>
            <div class="action-buttons">
                <button class="action-btn btn-view" onclick="viewEventRevenue(${event.id})">Revenue</button>
                <button class="action-btn btn-view" onclick="viewAvailableTickets(${event.id})">Availability</button>
                <button class="action-btn btn-delete" onclick="deleteEvent(${event.id})">Delete</button>
            </div>
        </div>
    `).join('');
}

async function viewEventRevenue(eventId) {
    try {
        const revenue = await apiCall(`/events/${eventId}/revenue`);
        alert(`Total Revenue: $${revenue.total_revenue.toFixed(2)}\nTotal Bookings: ${revenue.total_bookings}\nTickets Sold: ${revenue.tickets_sold}\nAvailable: ${revenue.available_tickets}`);
    } catch (error) {
        console.error('Error loading event revenue:', error);
    }
}

async function viewAvailableTickets(eventId) {
    try {
        const availability = await apiCall(`/events/${eventId}/available-tickets`);
        alert(`Available Tickets: ${availability.available_tickets}\nTickets Sold: ${availability.tickets_sold}\nMax Tickets: ${availability.max_tickets}`);
    } catch (error) {
        console.error('Error loading ticket availability:', error);
    }
}

async function deleteEvent(eventId) {
    if (confirm('Are you sure you want to delete this event? This will also delete all associated bookings.')) {
        try {
            await apiCall(`/events/${eventId}`, 'DELETE');
            showMessage('Event deleted successfully');
            loadEvents();
        } catch (error) {
            console.error('Error deleting event:', error);
        }
    }
}

// Ticket Type Functions
async function loadTicketTypes() {
    try {
        ticketTypes = await apiCall('/ticket-types');
        displayTicketTypes();
    } catch (error) {
        console.error('Error loading ticket types:', error);
    }
}

function displayTicketTypes() {
    const container = document.getElementById('ticket-types-list');
    container.innerHTML = ticketTypes.map(ticketType => `
        <div class="data-item">
            <h4>🎟️ ${ticketType.name}</h4>
            <p>💰 Price: $${ticketType.price}</p>
            <p>ℹ️ ${ticketType.description || 'No description'}</p>
            <div class="action-buttons">
                <button class="action-btn btn-delete" onclick="deleteTicketType(${ticketType.id})">Delete</button>
            </div>
        </div>
    `).join('');
}

async function deleteTicketType(ticketTypeId) {
    if (confirm('Are you sure you want to delete this ticket type?')) {
        try {
            await apiCall(`/ticket-types/${ticketTypeId}`, 'DELETE');
            showMessage('Ticket type deleted successfully');
            loadTicketTypes();
        } catch (error) {
            console.error('Error deleting ticket type:', error);
        }
    }
}

// Booking Functions
async function loadBookings() {
    try {
        bookings = await apiCall('/bookings');
        displayBookings(bookings);
    } catch (error) {
        console.error('Error loading bookings:', error);
    }
}

function displayBookings(bookingsToShow = bookings) {
    const container = document.getElementById('bookings-list');
    container.innerHTML = bookingsToShow.map(booking => `
        <div class="data-item booking-item">
            <div class="booking-status status-${booking.status}">${booking.status.toUpperCase()}</div>
            <h4>📋 ${booking.confirmation_code}</h4>
            <p>👤 ${booking.customer_name} (${booking.customer_email})</p>
            <p>🎭 ${booking.event?.name || 'Unknown Event'}</p>
            <p>🏛️ ${booking.event?.venue?.name || 'Unknown Venue'}</p>
            <p>🎟️ ${booking.ticket_type?.name || 'Unknown Type'} x${booking.quantity}</p>
            <p>💰 Total: $${booking.total_amount}</p>
            <p>📅 ${new Date(booking.booking_date).toLocaleString()}</p>
            <div class="action-buttons">
                <button class="action-btn btn-edit" onclick="updateBookingStatus(${booking.id})">Update Status</button>
                <button class="action-btn btn-delete" onclick="deleteBooking(${booking.id})">Cancel</button>
            </div>
        </div>
    `).join('');
}

async function updateBookingStatus(bookingId) {
    const newStatus = prompt('Enter new status (pending, confirmed, cancelled):');
    if (newStatus && ['pending', 'confirmed', 'cancelled'].includes(newStatus)) {
        try {
            await apiCall(`/bookings/${bookingId}/status`, 'PATCH', { status: newStatus });
            showMessage('Booking status updated successfully');
            loadBookings();
        } catch (error) {
            console.error('Error updating booking status:', error);
        }
    }
}

async function deleteBooking(bookingId) {
    if (confirm('Are you sure you want to cancel this booking?')) {
        try {
            await apiCall(`/bookings/${bookingId}`, 'DELETE');
            showMessage('Booking cancelled successfully');
            loadBookings();
        } catch (error) {
            console.error('Error cancelling booking:', error);
        }
    }
}

// Search Functions
async function searchBookings() {
    const event = document.getElementById('search-event').value;
    const venue = document.getElementById('search-venue').value;
    const ticketType = document.getElementById('search-ticket-type').value;
    const status = document.getElementById('search-status').value;
    
    const params = new URLSearchParams();
    if (event) params.append('event', event);
    if (venue) params.append('venue', venue);
    if (ticketType) params.append('ticket_type', ticketType);
    if (status) params.append('status', status);
    
    try {
        const results = await apiCall(`/bookings/search?${params}`);
        displaySearchResults(results);
    } catch (error) {
        console.error('Error searching bookings:', error);
    }
}

function displaySearchResults(results) {
    const container = document.getElementById('search-results');
    if (results.length === 0) {
        container.innerHTML = '<p>No bookings found matching your criteria.</p>';
        return;
    }
    
    container.innerHTML = results.map(booking => `
        <div class="data-item booking-item">
            <div class="booking-status status-${booking.status}">${booking.status.toUpperCase()}</div>
            <h4>📋 ${booking.confirmation_code}</h4>
            <p>👤 ${booking.customer_name} (${booking.customer_email})</p>
            <p>🎭 ${booking.event?.name || 'Unknown Event'}</p>
            <p>🏛️ ${booking.event?.venue?.name || 'Unknown Venue'}</p>
            <p>🎟️ ${booking.ticket_type?.name || 'Unknown Type'} x${booking.quantity}</p>
            <p>💰 Total: $${booking.total_amount}</p>
            <p>📅 ${new Date(booking.booking_date).toLocaleString()}</p>
        </div>
    `).join('');
}

function clearSearch() {
    document.getElementById('search-event').value = '';
    document.getElementById('search-venue').value = '';
    document.getElementById('search-ticket-type').value = '';
    document.getElementById('search-status').value = '';
    document.getElementById('search-results').innerHTML = '';
}

// Form Handlers
document.getElementById('venue-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = {
        name: document.getElementById('venue-name').value,
        address: document.getElementById('venue-address').value,
        capacity: parseInt(document.getElementById('venue-capacity').value),
        description: document.getElementById('venue-description').value
    };
    
    try {
        await apiCall('/venues', 'POST', formData);
        showMessage('Venue created successfully');
        e.target.reset();
        loadVenues();
    } catch (error) {
        console.error('Error creating venue:', error);
    }
});

document.getElementById('event-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = {
        name: document.getElementById('event-name').value,
        description: document.getElementById('event-description').value,
        event_date: document.getElementById('event-date').value,
        venue_id: parseInt(document.getElementById('event-venue').value),
        max_tickets: parseInt(document.getElementById('event-max-tickets').value)
    };
    
    try {
        await apiCall('/events', 'POST', formData);
        showMessage('Event created successfully');
        e.target.reset();
        loadEvents();
    } catch (error) {
        console.error('Error creating event:', error);
    }
});

document.getElementById('ticket-type-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = {
        name: document.getElementById('ticket-type-name').value,
        price: parseFloat(document.getElementById('ticket-type-price').value),
        description: document.getElementById('ticket-type-description').value
    };
    
    try {
        await apiCall('/ticket-types', 'POST', formData);
        showMessage('Ticket type created successfully');
        e.target.reset();
        loadTicketTypes();
    } catch (error) {
        console.error('Error creating ticket type:', error);
    }
});

document.getElementById('booking-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = {
        customer_name: document.getElementById('booking-customer-name').value,
        customer_email: document.getElementById('booking-customer-email').value,
        event_id: parseInt(document.getElementById('booking-event').value),
        ticket_type_id: parseInt(document.getElementById('booking-ticket-type').value),
        quantity: parseInt(document.getElementById('booking-quantity').value)
    };
    
    try {
        await apiCall('/bookings', 'POST', formData);
        showMessage('Booking created successfully');
        e.target.reset();
        updateBookingTotal();
        loadBookings();
    } catch (error) {
        console.error('Error creating booking:', error);
    }
});

// Helper Functions
async function loadVenuesForSelect() {
    try {
        const venuesData = await apiCall('/venues');
        const select = document.getElementById('event-venue');
        select.innerHTML = '<option value="">Select Venue</option>' + 
            venuesData.map(venue => `<option value="${venue.id}">${venue.name}</option>`).join('');
    } catch (error) {
        console.error('Error loading venues for select:', error);
    }
}

async function loadEventsForSelect() {
    try {
        const eventsData = await apiCall('/events');
        const select = document.getElementById('booking-event');
        select.innerHTML = '<option value="">Select Event</option>' + 
            eventsData.map(event => `<option value="${event.id}">${event.name} - ${new Date(event.event_date).toLocaleDateString()}</option>`).join('');
    } catch (error) {
        console.error('Error loading events for select:', error);
    }
}

async function loadTicketTypesForSelect() {
    try {
        const ticketTypesData = await apiCall('/ticket-types');
        const select = document.getElementById('booking-ticket-type');
        select.innerHTML = '<option value="">Select Ticket Type</option>' + 
            ticketTypesData.map(type => `<option value="${type.id}">${type.name} - $${type.price}</option>`).join('');
    } catch (error) {
        console.error('Error loading ticket types for select:', error);
    }
}

function updateBookingTotal() {
    const ticketTypeSelect = document.getElementById('booking-ticket-type');
    const quantityInput = document.getElementById('booking-quantity');
    const totalDiv = document.getElementById('booking-total');
    
    const selectedOption = ticketTypeSelect.options[ticketTypeSelect.selectedIndex];
    if (selectedOption && selectedOption.value) {
        const price = parseFloat(selectedOption.text.split('$')[1]);
        const quantity = parseInt(quantityInput.value) || 0;
        const total = price * quantity;
        totalDiv.textContent = `Total: $${total.toFixed(2)}`;
    } else {
        totalDiv.textContent = 'Total: $0.00';
    }
}

// Event Listeners for Total Calculation
document.getElementById('booking-ticket-type').addEventListener('change', updateBookingTotal);
document.getElementById('booking-quantity').addEventListener('input', updateBookingTotal);

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadDashboardData();
}); 