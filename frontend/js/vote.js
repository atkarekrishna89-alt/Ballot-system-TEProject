/**
 * Vote Module — Ballot casting and results display
 */

let selectedCandidateId = null;

// --- Load Ballot ---
async function loadBallot() {
    const electionId = new URLSearchParams(window.location.search).get('id');
    if (!electionId) {
        showToast('No election specified', 'error');
        return;
    }

    const container = document.getElementById('ballot-area');
    if (!container) return;

    // show spinner in candidate list rather than wiping the whole container
    const candidateList = document.getElementById('candidate-list');
    if (candidateList) {
        candidateList.innerHTML = '<div class="text-center"><span class="loading-spinner"></span></div>';
    }

    try {
        // Check vote status first
        const voteStatus = await api.getVoteStatus(electionId);
        if (voteStatus.has_voted) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">✅</div>
                    <h3>You Have Already Voted</h3>
                    <p>Your vote has been recorded anonymously. You cannot vote again in this election.</p>
                    <a href="/static/dashboard.html" class="btn btn-secondary mt-2">← Back to Dashboard</a>
                </div>`;
            return;
        }

        const election = await api.getElection(electionId);

        // Status check
        if (election.status !== 'active') {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">${election.status === 'draft' ? '📝' : '🔴'}</div>
                    <h3>Election is ${election.status === 'draft' ? 'Not Yet Active' : 'Closed'}</h3>
                    <p>${election.status === 'draft' ? 'Voting has not started yet.' : 'Voting has ended.'}</p>
                    <a href="/static/dashboard.html" class="btn btn-secondary mt-2">← Back to Dashboard</a>
                </div>`;
            return;
        }

        // Set header info (elements should still exist)
        const titleEl = document.getElementById('ballot-title');
        const descEl = document.getElementById('ballot-desc');
        const timeEl = document.getElementById('ballot-time');
        if (titleEl) titleEl.textContent = election.title;
        if (descEl) descEl.textContent = election.description || '';
        if (timeEl) timeEl.textContent = `Voting ends: ${formatDate(election.end_time)}`;

        // Render candidates
        const candidates = election.candidates || [];
        if (!candidates.length) {
            container.innerHTML = '<div class="empty-state"><h3>No candidates available</h3></div>';
            return;
        }

        if (candidateList) {
            candidateList.innerHTML = candidates.map(c => `
                <div class="candidate-option animate-in" data-id="${c.id}" onclick="selectCandidate('${c.id}', this)">
                    <div class="candidate-radio"></div>
                    <div class="candidate-info">
                        <h3>${escapeHtml(c.name)}</h3>
                        <p>${escapeHtml(c.description || '')}</p>
                    </div>
                </div>
            `).join('');
        }

    } catch (err) {
        container.innerHTML = `<div class="empty-state"><p class="text-danger">${err.message}</p></div>`;
    }
}

// --- Select Candidate ---
function selectCandidate(candidateId, element) {
    // Deselect all
    document.querySelectorAll('.candidate-option').forEach(el => el.classList.remove('selected'));
    // Select clicked
    element.classList.add('selected');
    selectedCandidateId = candidateId;
    // Enable submit
    const btn = document.getElementById('submit-vote-btn');
    if (btn) btn.disabled = false;
}

// --- Submit Vote ---
async function submitVote() {
    const electionId = new URLSearchParams(window.location.search).get('id');

    if (!selectedCandidateId) {
        showToast('Please select a candidate', 'warning');
        return;
    }

    // Show confirmation modal
    const modal = document.getElementById('confirm-modal');
    if (modal) {
        modal.classList.add('active');
    }
}

async function confirmVote() {
    const electionId = new URLSearchParams(window.location.search).get('id');
    const modal = document.getElementById('confirm-modal');
    const btn = document.getElementById('confirm-vote-btn');

    btn.disabled = true;
    btn.innerHTML = '<span class="loading-spinner"></span> Casting Vote...';

    try {
        await api.castVote(electionId, selectedCandidateId);

        if (modal) modal.classList.remove('active');

        // Show success — redirect to dashboard so vote counts update
        document.getElementById('ballot-area').innerHTML = `
            <div class="empty-state" style="padding:var(--space-2xl) 0;">
                <div class="empty-icon" style="font-size:5rem;margin-bottom:var(--space-lg)">🗳️</div>
                <h3 style="font-size:1.5rem;color:var(--success);margin-bottom:var(--space-md)">Vote Cast Successfully!</h3>
                <p style="max-width:500px;margin:0 auto var(--space-xl)">
                    Your vote has been recorded <strong>anonymously</strong>. No one can trace your choice back to your identity.
                </p>
                <a href="/static/dashboard.html?voted=1" class="btn btn-primary">← Back to Dashboard</a>
            </div>
        `;
        showToast('Vote cast successfully!', 'success');
    } catch (err) {
        showToast(err.message, 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = 'Confirm Vote';
    }
}

function cancelVote() {
    const modal = document.getElementById('confirm-modal');
    if (modal) modal.classList.remove('active');
}

// --- Load Results ---
async function loadResults() {
    const electionId = new URLSearchParams(window.location.search).get('id');
    if (!electionId) return;

    const container = document.getElementById('results-area');
    if (!container) return;

    container.innerHTML = '<div class="text-center"><span class="loading-spinner"></span></div>';

    try {
        const results = await api.getResults(electionId);

        document.getElementById('results-title').textContent = results.title;
        document.getElementById('results-total').textContent = `Total votes: ${results.total_votes}`;

        if (!results.results.length) {
            container.innerHTML = '<div class="empty-state"><h3>No votes recorded</h3></div>';
            return;
        }

        const maxVotes = Math.max(...results.results.map(r => r.vote_count), 1);

        container.innerHTML = results.results.map((r, i) => {
            const percentage = results.total_votes > 0 ? ((r.vote_count / results.total_votes) * 100).toFixed(1) : 0;
            const isWinner = i === 0 && r.vote_count > 0;

            return `
                <div class="result-item animate-in ${isWinner ? 'winner' : ''}">
                    <div class="result-header">
                        <span class="result-name">
                            ${isWinner ? '🏆 ' : ''}${escapeHtml(r.candidate_name)}
                        </span>
                        <span class="result-votes">${r.vote_count} votes (${percentage}%)</span>
                    </div>
                    <div class="result-bar">
                        <div class="result-bar-fill" style="width: ${percentage}%"></div>
                    </div>
                </div>
            `;
        }).join('');

    } catch (err) {
        container.innerHTML = `<div class="empty-state"><p class="text-danger">${err.message}</p></div>`;
    }
}
