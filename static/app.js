// API base URL
const API_BASE = '/api';

// Navigation
document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const view = btn.dataset.view;
        switchView(view);
    });
});

function switchView(viewName) {
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    
    document.getElementById(`${viewName}-view`).classList.add('active');
    document.querySelector(`[data-view="${viewName}"]`).classList.add('active');
    
    // Load data for the view
    if (viewName === 'artists') loadArtists();
    if (viewName === 'venues') loadVenues();
}

// Search functions
async function searchVenuesForArtist() {
    const artistId = document.getElementById('artist-search-id').value;
    const minScore = document.getElementById('artist-min-score').value;
    
    if (!artistId) {
        showError('Please enter an artist ID');
        return;
    }
    
    try {
        const url = `${API_BASE}/search/venues-for-artist/${artistId}${minScore ? `?min_score=${minScore}` : ''}`;
        const response = await fetch(url);
        const data = await response.json();
        
        if (!response.ok) throw new Error(data.detail?.message || 'Search failed');
        
        displaySearchResults(data, 'venue');
    } catch (error) {
        showError(error.message);
    }
}

async function searchArtistsForVenue() {
    const venueId = document.getElementById('venue-search-id').value;
    const minScore = document.getElementById('venue-min-score').value;
    
    if (!venueId) {
        showError('Please enter a venue ID');
        return;
    }
    
    try {
        const url = `${API_BASE}/search/artists-for-venue/${venueId}${minScore ? `?min_score=${minScore}` : ''}`;
        const response = await fetch(url);
        const data = await response.json();
        
        if (!response.ok) throw new Error(data.detail?.message || 'Search failed');
        
        displaySearchResults(data, 'artist');
    } catch (error) {
        showError(error.message);
    }
}

function displaySearchResults(results, type) {
    const container = document.getElementById('search-results');
    
    if (results.length === 0) {
        container.innerHTML = '<p>No matches found</p>';
        return;
    }
    
    container.innerHTML = `<h3>Found ${results.length} match(es)</h3>`;
    
    results.forEach(match => {
        const profile = type === 'venue' ? match.venue : match.artist;
        const card = document.createElement('div');
        card.className = 'result-card';
        card.innerHTML = `
            <h4>${profile.name}</h4>
            <p><strong>ID:</strong> ${profile.id}</p>
            <p><strong>Email:</strong> ${profile.email}</p>
            <p><strong>Art Types:</strong> ${profile.art_types?.join(', ') || 'N/A'}</p>
            <span class="score">Score: ${(match.compatibility_score * 100).toFixed(0)}%</span>
            <p><strong>Common Availabilities:</strong> ${match.common_availabilities.length}</p>
            ${match.unmatched_requirements.length > 0 ? 
                `<p><strong>Unmatched:</strong> ${match.unmatched_requirements.join(', ')}</p>` : ''}
        `;
        container.appendChild(card);
    });
}

// Artists functions
async function loadArtists() {
    try {
        const response = await fetch(`${API_BASE}/artists/`);
        const artists = await response.json();
        
        const container = document.getElementById('artists-list');
        container.innerHTML = '';
        
        if (artists.length === 0) {
            container.innerHTML = '<p>No artists found. Create one to get started!</p>';
            return;
        }
        
        artists.forEach(artist => {
            const card = document.createElement('div');
            card.className = 'profile-card';
            card.innerHTML = `
                <h4>${artist.name}</h4>
                <p><strong>ID:</strong> ${artist.id}</p>
                <p><strong>Email:</strong> ${artist.email}</p>
                <p><strong>Art Types:</strong> ${artist.art_types?.join(', ') || 'N/A'}</p>
                <button onclick="deleteArtist('${artist.id}')">Delete</button>
            `;
            container.appendChild(card);
        });
    } catch (error) {
        showError('Failed to load artists');
    }
}

function showCreateArtistForm() {
    const form = `
        <h3>Create Artist Profile</h3>
        <form onsubmit="createArtist(event)">
            <input type="text" name="id" placeholder="ID" required>
            <input type="text" name="name" placeholder="Name" required>
            <input type="email" name="email" placeholder="Email" required>
            <input type="text" name="art_types" placeholder="Art Types (comma-separated)">
            <button type="submit">Create</button>
        </form>
    `;
    showModal(form);
}

async function createArtist(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    
    const profile = {
        id: formData.get('id'),
        name: formData.get('name'),
        email: formData.get('email'),
        art_types: formData.get('art_types')?.split(',').map(s => s.trim()).filter(Boolean) || [],
        availabilities: []
    };
    
    try {
        const response = await fetch(`${API_BASE}/artists/`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(profile)
        });
        
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail?.message || 'Failed to create artist');
        
        showSuccess('Artist created successfully');
        closeModal();
        loadArtists();
    } catch (error) {
        showError(error.message);
    }
}

async function deleteArtist(id) {
    if (!confirm('Are you sure you want to delete this artist?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/artists/${id}`, {method: 'DELETE'});
        if (!response.ok) throw new Error('Failed to delete artist');
        
        showSuccess('Artist deleted successfully');
        loadArtists();
    } catch (error) {
        showError(error.message);
    }
}

// Venues functions
async function loadVenues() {
    try {
        const response = await fetch(`${API_BASE}/venues/`);
        const venues = await response.json();
        
        const container = document.getElementById('venues-list');
        container.innerHTML = '';
        
        if (venues.length === 0) {
            container.innerHTML = '<p>No venues found. Create one to get started!</p>';
            return;
        }
        
        venues.forEach(venue => {
            const card = document.createElement('div');
            card.className = 'profile-card';
            card.innerHTML = `
                <h4>${venue.name}</h4>
                <p><strong>ID:</strong> ${venue.id}</p>
                <p><strong>Email:</strong> ${venue.email}</p>
                <p><strong>Art Types:</strong> ${venue.art_types?.join(', ') || 'N/A'}</p>
                <button onclick="deleteVenue('${venue.id}')">Delete</button>
            `;
            container.appendChild(card);
        });
    } catch (error) {
        showError('Failed to load venues');
    }
}

function showCreateVenueForm() {
    const form = `
        <h3>Create Venue Profile</h3>
        <form onsubmit="createVenue(event)">
            <input type="text" name="id" placeholder="ID" required>
            <input type="text" name="name" placeholder="Name" required>
            <input type="email" name="email" placeholder="Email" required>
            <input type="text" name="art_types" placeholder="Art Types (comma-separated)">
            <button type="submit">Create</button>
        </form>
    `;
    showModal(form);
}

async function createVenue(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    
    const profile = {
        id: formData.get('id'),
        name: formData.get('name'),
        email: formData.get('email'),
        art_types: formData.get('art_types')?.split(',').map(s => s.trim()).filter(Boolean) || [],
        availabilities: []
    };
    
    try {
        const response = await fetch(`${API_BASE}/venues/`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(profile)
        });
        
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail?.message || 'Failed to create venue');
        
        showSuccess('Venue created successfully');
        closeModal();
        loadVenues();
    } catch (error) {
        showError(error.message);
    }
}

async function deleteVenue(id) {
    if (!confirm('Are you sure you want to delete this venue?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/venues/${id}`, {method: 'DELETE'});
        if (!response.ok) throw new Error('Failed to delete venue');
        
        showSuccess('Venue deleted successfully');
        loadVenues();
    } catch (error) {
        showError(error.message);
    }
}

// Calendar functions
async function loadArtistCalendar() {
    const artistId = document.getElementById('artist-calendar-id').value;
    if (!artistId) {
        showError('Please enter an artist ID');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/calendar/artist/${artistId}`);
        const events = await response.json();
        
        const container = document.getElementById('artist-calendar-events');
        container.innerHTML = '';
        
        if (events.length === 0) {
            container.innerHTML = '<p>No events found</p>';
            return;
        }
        
        events.forEach(event => {
            const item = document.createElement('div');
            item.className = 'event-item';
            item.innerHTML = `
                <strong>${event.title}</strong><br>
                ${event.start} - ${event.end}<br>
                ${event.description || ''}
            `;
            container.appendChild(item);
        });
    } catch (error) {
        showError('Failed to load calendar');
    }
}

async function loadVenueCalendar() {
    const venueId = document.getElementById('venue-calendar-id').value;
    if (!venueId) {
        showError('Please enter a venue ID');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/calendar/venue/${venueId}`);
        const events = await response.json();
        
        const container = document.getElementById('venue-calendar-events');
        container.innerHTML = '';
        
        if (events.length === 0) {
            container.innerHTML = '<p>No events found</p>';
            return;
        }
        
        events.forEach(event => {
            const item = document.createElement('div');
            item.className = 'event-item';
            item.innerHTML = `
                <strong>${event.title}</strong><br>
                ${event.start} - ${event.end}<br>
                ${event.description || ''}
            `;
            container.appendChild(item);
        });
    } catch (error) {
        showError('Failed to load calendar');
    }
}

// Modal functions
function showModal(content) {
    document.getElementById('modal-body').innerHTML = content;
    document.getElementById('modal').classList.add('active');
}

function closeModal() {
    document.getElementById('modal').classList.remove('active');
}

// Notification functions
function showError(message) {
    const div = document.createElement('div');
    div.className = 'error';
    div.textContent = message;
    document.querySelector('main').prepend(div);
    setTimeout(() => div.remove(), 5000);
}

function showSuccess(message) {
    const div = document.createElement('div');
    div.className = 'success';
    div.textContent = message;
    document.querySelector('main').prepend(div);
    setTimeout(() => div.remove(), 3000);
}

// Check API health on load
fetch(`${API_BASE}/health`)
    .then(r => r.json())
    .then(data => console.log('API Status:', data))
    .catch(e => showError('API connection failed'));
