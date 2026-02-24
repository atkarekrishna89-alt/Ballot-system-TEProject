/**
 * API Module — Fetch wrapper with JWT authentication
 * Tokens stored in sessionStorage (cleared when tab closes).
 */

const API_BASE = '/api';

// --- Token Management (sessionStorage for cross-page persistence) ---
function setTokens(access, refresh) {
    sessionStorage.setItem('access_token', access);
    sessionStorage.setItem('refresh_token', refresh);
}

function getAccessToken() {
    return sessionStorage.getItem('access_token');
}

function getRefreshToken() {
    return sessionStorage.getItem('refresh_token');
}

function clearTokens() {
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('refresh_token');
}

function isLoggedIn() {
    return !!sessionStorage.getItem('access_token');
}

// --- Core Fetch Wrapper ---
async function apiFetch(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    const accessToken = getAccessToken();
    if (accessToken) {
        headers['Authorization'] = `Bearer ${accessToken}`;
    }

    try {
        let response = await fetch(url, { ...options, headers });

        // If 401 and we have a refresh token, try to refresh
        if (response.status === 401 && getRefreshToken()) {
            const refreshed = await refreshAccessToken();
            if (refreshed) {
                headers['Authorization'] = `Bearer ${getAccessToken()}`;
                response = await fetch(url, { ...options, headers });
            } else {
                clearTokens();
                window.location.href = '/static/login.html';
                return null;
            }
        }

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: response.statusText }));
            throw new ApiError(response.status, error.detail || 'Request failed');
        }

        return await response.json();
    } catch (err) {
        if (err instanceof ApiError) throw err;
        throw new ApiError(0, 'Network error. Please check your connection.');
    }
}

async function refreshAccessToken() {
    try {
        const response = await fetch(`${API_BASE}/auth/refresh`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: getRefreshToken() }),
        });
        if (response.ok) {
            const data = await response.json();
            setTokens(data.access_token, data.refresh_token);
            return true;
        }
        return false;
    } catch {
        return false;
    }
}

// Custom error class
class ApiError extends Error {
    constructor(status, message) {
        super(message);
        this.status = status;
    }
}

// --- API Methods ---
const api = {
    // Auth
    login: (email, password) =>
        apiFetch('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password }),
        }),

    register: (email, password, full_name, emp_id) =>
        apiFetch('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ email, password, full_name, emp_id }),
        }),

    getMe: () => apiFetch('/auth/me'),

    // Users
    listUsers: () => apiFetch('/users/'),
    assignRole: (userId, roleName) =>
        apiFetch(`/users/${userId}/roles`, {
            method: 'PUT',
            body: JSON.stringify({ role_name: roleName }),
        }),

    // Organizations
    createOrganization: (name, description) =>
        apiFetch('/organizations/', {
            method: 'POST',
            body: JSON.stringify({ name, description }),
        }),
    listOrganizations: () => apiFetch('/organizations/'),
    getOrganization: (id) => apiFetch(`/organizations/${id}`),
    deleteOrganization: (id) =>
        apiFetch(`/organizations/${id}`, { method: 'DELETE' }),

    // Elections
    createElection: (data) =>
        apiFetch('/elections/', {
            method: 'POST',
            body: JSON.stringify(data),
        }),
    listElections: () => apiFetch('/elections/'),
    getElection: (id) => apiFetch(`/elections/${id}`),
    updateElection: (id, data) =>
        apiFetch(`/elections/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        }),
    activateElection: (id) =>
        apiFetch(`/elections/${id}/activate`, { method: 'PUT' }),
    closeElection: (id) =>
        apiFetch(`/elections/${id}/close`, { method: 'PUT' }),
    deleteElection: (id) =>
        apiFetch(`/elections/${id}`, { method: 'DELETE' }),

    // Candidates
    addCandidate: (electionId, name, description) =>
        apiFetch(`/elections/${electionId}/candidates`, {
            method: 'POST',
            body: JSON.stringify({ name, description }),
        }),
    listCandidates: (electionId) =>
        apiFetch(`/elections/${electionId}/candidates`),
    deleteCandidate: (candidateId) =>
        apiFetch(`/elections/candidates/${candidateId}`, { method: 'DELETE' }),

    // Voters
    addVoter: (electionId, identifier) =>
        apiFetch(`/elections/${electionId}/voters`, {
            method: 'POST',
            body: JSON.stringify({ identifier }),
        }),
    listVoters: (electionId) =>
        apiFetch(`/elections/${electionId}/voters`),
    removeVoter: (electionId, userId) =>
        apiFetch(`/elections/${electionId}/voters/${userId}`, { method: 'DELETE' }),

    // Voting
    castVote: (electionId, candidateId) =>
        apiFetch('/vote/', {
            method: 'POST',
            body: JSON.stringify({ election_id: electionId, candidate_id: candidateId }),
        }),
    getResults: (electionId) => apiFetch(`/vote/results/${electionId}`),
    getVoteStatus: (electionId) => apiFetch(`/vote/status/${electionId}`),
};

// --- Toast Notifications ---
function showToast(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const icons = { success: '✓', error: '✕', warning: '⚠', info: 'ℹ' };
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<span>${icons[type] || 'ℹ'}</span> ${message}`;
    container.appendChild(toast);

    setTimeout(() => toast.remove(), 5000);
}

// --- Utility ---
function formatDate(dateStr) {
    if (!dateStr) return '—';
    const d = new Date(dateStr);
    return d.toLocaleString('en-US', {
        year: 'numeric', month: 'short', day: 'numeric',
        hour: '2-digit', minute: '2-digit',
    });
}

function getStatusBadge(status) {
    const classes = { draft: 'badge-draft', active: 'badge-active', closed: 'badge-closed' };
    const icons = { draft: '📝', active: '🟢', closed: '🔴' };
    return `<span class="badge ${classes[status] || ''}">${icons[status] || ''} ${status}</span>`;
}

function requireAuth() {
    if (!isLoggedIn()) {
        window.location.href = '/static/login.html';
        return false;
    }
    return true;
}
