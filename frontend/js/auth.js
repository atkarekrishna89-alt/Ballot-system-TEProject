/**
 * Auth Module — Login, Register, and session management
 */

// --- Login ---
async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value;
    const loginType = document.querySelector('input[name="login-type"]:checked').value;
    const btn = e.target.querySelector('button[type="submit"]');

    if (!email || !password) {
        showToast('Please fill in all fields', 'warning');
        return;
    }

    btn.disabled = true;
    btn.innerHTML = '<span class="loading-spinner"></span> Signing in...';

    try {
        const data = await api.login(email, password);
        setTokens(data.access_token, data.refresh_token);

        // verify user role matches selected type
        const user = await api.getMe();
        const isAdmin = user.roles.some(r => ['SUPER_ADMIN','ORG_ADMIN','ELECTION_MANAGER'].includes(r));
        if (loginType === 'ADMIN' && !isAdmin) {
            clearTokens();
            throw new Error('Account does not have admin privileges');
        }
        if (loginType === 'VOTER' && isAdmin) {
            clearTokens();
            throw new Error('Please use the Admin option to sign in');
        }

        showToast('Login successful!', 'success');
        setTimeout(() => window.location.href = '/static/dashboard.html', 500);
    } catch (err) {
        showToast(err.message || 'Login failed', 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = 'Sign In';
    }
}

// --- Register ---
async function handleRegister(e) {
    e.preventDefault();
    const fullName = document.getElementById('reg-name').value.trim();
    const empId = document.getElementById('reg-emp-id').value.trim();
    const email = document.getElementById('reg-email').value.trim();
    const password = document.getElementById('reg-password').value;
    const confirmPassword = document.getElementById('reg-confirm-password').value;
    const btn = e.target.querySelector('button[type="submit"]');

    if (!fullName || !empId || !email || !password) {
        showToast('Please fill in all fields', 'warning');
        return;
    }

    if (password !== confirmPassword) {
        showToast('Passwords do not match', 'error');
        return;
    }

    if (password.length < 6) {
        showToast('Password must be at least 6 characters', 'warning');
        return;
    }

    btn.disabled = true;
    btn.innerHTML = '<span class="loading-spinner"></span> Creating account...';

    try {
        await api.register(email, password, fullName, empId);
        showToast('Account created! Please sign in.', 'success');
        showLoginForm();
    } catch (err) {
        showToast(err.message || 'Registration failed', 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = 'Create Account';
    }
}

// show/hide voter registration link when selecting user type
function toggleRegisterLink() {
    const loginType = document.querySelector('input[name="login-type"]:checked').value;
    const span = document.getElementById('register-link');
    if (span) {
        span.style.display = loginType === 'ADMIN' ? 'none' : '';
    }
}

// wire up on page load
window.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('input[name="login-type"]').forEach(r => {
        r.addEventListener('change', toggleRegisterLink);
    });
    toggleRegisterLink();
});

// --- Toggle Forms ---
function showLoginForm() {
    document.getElementById('login-form-container').classList.remove('hidden');
    document.getElementById('register-form-container').classList.add('hidden');
}

function showRegisterForm() {
    document.getElementById('login-form-container').classList.add('hidden');
    document.getElementById('register-form-container').classList.remove('hidden');
}

// --- Logout ---
function logout() {
    clearTokens();
    showToast('Logged out', 'info');
    window.location.href = '/static/login.html';
}

// --- Load Navbar User Info ---
async function loadNavbarUser() {
    if (!isLoggedIn()) return;
    try {
        const user = await api.getMe();
        const badge = document.getElementById('user-badge');
        if (badge) {
            const topRole = user.roles[0] || 'VOTER';
            badge.innerHTML = `
                <span>${user.full_name || user.email}</span>
                <span class="role-tag">${topRole.replace('_', ' ')}</span>
            `;
        }
        return user;
    } catch {
        return null;
    }
}
