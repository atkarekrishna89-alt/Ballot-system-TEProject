/**
 * Election Module — CRUD, candidates, voters management
 */

// --- Load Elections List ---
async function loadElections() {
    const container = document.getElementById('elections-list');
    if (!container) return;

    container.innerHTML = '<div class="text-center"><span class="loading-spinner"></span></div>';

    try {
        const elections = await api.listElections();
        if (!elections.length) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">🗳️</div>
                    <h3>No Elections Yet</h3>
                    <p>Create your first election to get started.</p>
                </div>`;
            return;
        }

        container.innerHTML = elections.map((e, i) => `
            <div class="election-card animate-in" style="animation-delay: ${i * 0.05}s">
                <div style="display:flex;justify-content:space-between;align-items:flex-start">
                    <div>
                        <div class="election-title">${escapeHtml(e.title)}</div>
                        <div class="election-org">📅 Created ${formatDate(e.created_at)}</div>
                    </div>
                    ${getStatusBadge(e.status)}
                </div>
                ${e.description ? `<p style="color:var(--text-secondary);font-size:0.9rem;margin-bottom:var(--space-md)">${escapeHtml(e.description)}</p>` : ''}
                <div class="election-dates">
                    <span>🟢 Start: ${formatDate(e.start_time)}</span>
                    <span>🔴 End: ${formatDate(e.end_time)}</span>
                    ${e.total_votes !== undefined ? `<span>📊 ${e.total_votes} votes</span>` : ''}
                </div>
                <div class="election-card-footer">
                    <span style="font-size:0.85rem;color:var(--text-muted)">
                        ${e.candidates ? e.candidates.length : 0} candidates
                    </span>
                    <div class="btn-group">
                        ${e.status === 'active' ? `<a href="/static/vote.html?id=${e.id}" class="btn btn-primary btn-sm">🗳️ Vote</a>` : ''}
                        ${e.status === 'draft' ? `
                            <button class="btn btn-secondary btn-sm" onclick="openManageElection('${e.id}')">⚙️ Manage</button>
                            <button class="btn btn-success btn-sm" onclick="activateElection('${e.id}')">▶ Activate</button>
                        ` : ''}
                        ${e.status === 'active' ? `<button class="btn btn-warning btn-sm" onclick="closeElection('${e.id}')">⏹ Close</button>` : ''}
                        ${e.status === 'closed' ? `<a href="/static/results.html?id=${e.id}" class="btn btn-secondary btn-sm">📊 Results</a>` : ''}
                        ${e.status === 'closed' ? `<button class="btn btn-danger btn-sm" onclick="deleteElection('${e.id}')">✕ Delete</button>` : ''}
                    </div>
                </div>
            </div>
        `).join('');
    } catch (err) {
        container.innerHTML = `<div class="empty-state"><p class="text-danger">${err.message}</p></div>`;
    }
}

// --- Create Election ---
async function handleCreateElection(e) {
    e.preventDefault();
    const btn = e.target.querySelector('button[type="submit"]');
    btn.disabled = true;

    try {
        const data = {
            organization_id: document.getElementById('election-org').value,
            title: document.getElementById('election-title').value.trim(),
            description: document.getElementById('election-desc').value.trim(),
            start_time: new Date(document.getElementById('election-start').value).toISOString(),
            end_time: new Date(document.getElementById('election-end').value).toISOString(),
        };

        if (!data.title || !data.organization_id || !data.start_time || !data.end_time) {
            showToast('Please fill all required fields', 'warning');
            return;
        }

        const election = await api.createElection(data);
        showToast('Election created!', 'success');
        window.location.href = `/static/manage-election.html?id=${election.id}`;
    } catch (err) {
        showToast(err.message, 'error');
    } finally {
        btn.disabled = false;
    }
}

// --- Activate / Close ---
async function activateElection(id) {
    if (!confirm('Activate this election? Voting will begin based on the start time.')) return;
    try {
        await api.activateElection(id);
        showToast('Election activated!', 'success');
        loadElections();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function closeElection(id) {
    if (!confirm('Close this election? No more votes will be accepted.')) return;
    try {
        await api.closeElection(id);
        showToast('Election closed!', 'success');
        loadElections();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function deleteElection(id) {
    if (!confirm('Delete this election? This action cannot be undone.')) return;
    try {
        await api.deleteElection(id);
        showToast('Election deleted', 'success');
        loadElections();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

// --- Manage Election Detail ---
async function loadElectionDetail(id) {
    try {
        const election = await api.getElection(id);

        const titleEl = document.getElementById('detail-title');
        if (titleEl) titleEl.textContent = election.title;

        const statusEl = document.getElementById('detail-status');
        if (statusEl) statusEl.innerHTML = getStatusBadge(election.status);

        const descEl = document.getElementById('detail-desc');
        if (descEl) descEl.textContent = election.description || 'No description';

        const startEl = document.getElementById('detail-start');
        if (startEl) startEl.textContent = formatDate(election.start_time);

        const endEl = document.getElementById('detail-end');
        if (endEl) endEl.textContent = formatDate(election.end_time);

        // Load candidates
        loadCandidatesList(id);
        // voters are no longer per-election; skip loading

        return election;
    } catch (err) {
        showToast(err.message, 'error');
    }
}

// --- Candidates ---
async function loadCandidatesList(electionId) {
    const container = document.getElementById('candidates-list');
    if (!container) return;

    try {
        const candidates = await api.listCandidates(electionId);
        if (!candidates.length) {
            container.innerHTML = '<div class="empty-state"><p>No candidates added yet.</p></div>';
            return;
        }

        container.innerHTML = candidates.map(c => `
            <div class="card" style="padding:var(--space-md);margin-bottom:var(--space-sm);display:flex;justify-content:space-between;align-items:center">
                <div>
                    <strong>${escapeHtml(c.name)}</strong>
                    ${c.description ? `<p style="font-size:0.85rem;color:var(--text-secondary);margin-top:2px">${escapeHtml(c.description)}</p>` : ''}
                </div>
                <button class="btn btn-danger btn-sm" onclick="deleteCandidate('${c.id}', '${electionId}')">✕</button>
            </div>
        `).join('');
    } catch (err) {
        container.innerHTML = `<p class="text-danger">${err.message}</p>`;
    }
}

async function handleAddCandidate(e) {
    e.preventDefault();
    const electionId = new URLSearchParams(window.location.search).get('id');
    const name = document.getElementById('candidate-name').value.trim();
    const desc = document.getElementById('candidate-desc').value.trim();

    if (!name) { showToast('Candidate name is required', 'warning'); return; }

    try {
        await api.addCandidate(electionId, name, desc);
        showToast('Candidate added!', 'success');
        document.getElementById('candidate-name').value = '';
        document.getElementById('candidate-desc').value = '';
        loadCandidatesList(electionId);
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function deleteCandidate(candidateId, electionId) {
    if (!confirm('Remove this candidate?')) return;
    try {
        await api.deleteCandidate(candidateId);
        showToast('Candidate removed', 'success');
        loadCandidatesList(electionId);
    } catch (err) {
        showToast(err.message, 'error');
    }
}

// Voters are no longer managed per-election; all registered users may vote.
// related APIs and UI have been removed.

function openManageElection(id) {
    window.location.href = `/static/manage-election.html?id=${id}`;
}

// --- Org loader for dropdowns ---
async function loadOrgDropdown() {
    const select = document.getElementById('election-org');
    if (!select) return;
    try {
        const orgs = await api.listOrganizations();
        if (!orgs.length) {
            select.innerHTML = '<option value="">No organizations — create one first</option>';
            // Show helper message
            const hint = document.getElementById('org-hint');
            if (hint) hint.style.display = 'block';
        } else {
            select.innerHTML = '<option value="">Select Organization</option>' +
                orgs.map(o => `<option value="${o.id}">${escapeHtml(o.name)}</option>`).join('');
        }
    } catch (err) {
        showToast('Failed to load organizations', 'error');
    }
}

// --- Escape HTML ---
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text || '';
    return div.innerHTML;
}
