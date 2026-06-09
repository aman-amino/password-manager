import * as crypto from './crypto_helpers.js';

document.addEventListener('DOMContentLoaded', async () => {
    // Elements
    const authOverlay = document.getElementById('authOverlay');
    const authForm = document.getElementById('authForm');
    const authUsername = document.getElementById('authUsername');
    const authEmail = document.getElementById('authEmail');
    const authPassword = document.getElementById('authPassword');
    const emailGroup = document.getElementById('emailGroup');
    const loginTab = document.getElementById('loginTab');
    const registerTab = document.getElementById('registerTab');
    const authSubmit = document.getElementById('authSubmit');
    const authError = document.getElementById('authError');
    const currentUserEl = document.getElementById('currentUser');
    const userRoleEl = document.getElementById('userRole');

    const navLinks = document.querySelectorAll('.nav-link');
    const viewPanes = document.querySelectorAll('.view-pane');
    const viewTitle = document.getElementById('viewTitle');
    const vaultGrid = document.getElementById('vaultGrid');
    const detailPane = document.getElementById('detailPane');
    const closePaneBtn = document.getElementById('closePaneBtn');
    const rotateAdminBtn = document.getElementById('rotateAdminBtn');
    const vaultControls = document.getElementById('vaultControls');

    // State
    let currentUser = null;
    let masterKey = null;
    let secrets = [];
    let isRegister = false;

    // --- Auth Logic ---

    async function checkAuth() {
        try {
            const res = await fetch('/api/me/');
            if (res.ok) {
                const user = await res.json();
                onAuthenticated(user);
            } else {
                showAuth();
            }
        } catch (e) {
            showAuth();
        }
    }

    function showAuth() {
        authOverlay.classList.remove('d-none');
    }

    function onAuthenticated(user) {
        currentUser = user;
        authOverlay.classList.add('d-none');
        currentUserEl.textContent = user.username;
        userRoleEl.textContent = user.role.charAt(0).toUpperCase() + user.role.slice(1);
        loadVault();
    }

    loginTab.addEventListener('click', () => {
        isRegister = false;
        loginTab.classList.add('active');
        registerTab.classList.remove('active');
        emailGroup.classList.add('d-none');
        authSubmit.textContent = 'Sign In';
        authError.classList.add('d-none');
    });

    registerTab.addEventListener('click', () => {
        isRegister = true;
        registerTab.classList.add('active');
        loginTab.classList.remove('active');
        emailGroup.classList.remove('d-none');
        authSubmit.textContent = 'Create Account';
        authError.classList.add('d-none');
    });

    authForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        authError.classList.add('d-none');
        authSubmit.disabled = true;

        const username = authUsername.value;
        const password = authPassword.value;
        const email = authEmail.value;

        try {
            if (isRegister) {
                const salt = crypto.randomBytes(16);
                const iterations = 100000;
                const passwordKey = await crypto.importPassword(password);
                const rootKey = await crypto.deriveRootKey(passwordKey, salt, iterations);

                const authKeyStr = await crypto.deriveAuthKey(rootKey);
                const userMasterKey = await crypto.deriveMasterKey(rootKey);

                const dummyNonce = crypto.randomBytes(12);
                const rawMasterKey = await crypto.exportKeyRaw(userMasterKey);
                const encryptedMasterKey = await crypto.encryptAesGcm(userMasterKey, new Uint8Array(rawMasterKey), dummyNonce);

                const res = await fetch('/api/register/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
                    body: JSON.stringify({
                        username,
                        email,
                        password: authKeyStr,
                        salt: crypto.toBase64(salt),
                        iterations,
                        encrypted_user_key: crypto.toBase64(dummyNonce) + "." + crypto.toBase64(encryptedMasterKey)
                    })
                });

                if (res.ok) {
                    alert('Registration successful! Please login.');
                    loginTab.click();
                } else {
                    const data = await res.json();
                    authError.textContent = data.error || 'Registration failed';
                    authError.classList.remove('d-none');
                }
            } else {
                const paramsRes = await fetch(`/api/login-params/?username=${username}`);
                if (!paramsRes.ok) throw new Error('User not found');
                const params = await paramsRes.json();

                const salt = crypto.fromBase64(params.salt);
                const iterations = params.iterations;
                const passwordKey = await crypto.importPassword(password);
                const rootKey = await crypto.deriveRootKey(passwordKey, salt, iterations);
                const authKeyStr = await crypto.deriveAuthKey(rootKey);

                const loginRes = await fetch('/api/login/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
                    body: JSON.stringify({ username, password: authKeyStr })
                });

                if (loginRes.ok) {
                    const user = await loginRes.json();
                    masterKey = await crypto.deriveMasterKey(rootKey);
                    onAuthenticated(user);
                } else {
                    authError.textContent = 'Invalid credentials';
                    authError.classList.remove('d-none');
                }
            }
        } catch (err) {
            console.error(err);
            authError.textContent = err.message;
            authError.classList.remove('d-none');
        } finally {
            authSubmit.disabled = false;
        }
    });

    function getCsrfToken() {
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfInput ? csrfInput.value : '';
    }

    // --- Navigation ---

    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            const view = link.dataset.view;
            navLinks.forEach(l => {
                l.classList.remove('active');
                l.removeAttribute('aria-current');
            });
            link.classList.add('active');
            link.setAttribute('aria-current', 'page');

            viewPanes.forEach(p => p.classList.add('d-none'));
            const targetView = document.getElementById(view + 'View');
            if (targetView) targetView.classList.remove('d-none');

            viewTitle.textContent = view.charAt(0).toUpperCase() + view.slice(1);
            if (view === 'vault') vaultControls.classList.remove('d-none');
            else vaultControls.classList.add('d-none');

            // Trigger view-specific loads
            if (view === 'shared') loadRequests();
            if (view === 'audit') loadAuditLogs();
            if (view === 'people') loadPeople();
        });
    });

    // --- Vault Logic ---

    async function loadVault() {
        try {
            const res = await fetch('/api/vault-items/');
            if (res.ok) {
                secrets = await res.json();
                renderVault();
            }
        } catch (e) {
            console.error('Failed to load vault', e);
        }
    }

    function renderVault() {
        const query = searchInput.value.toLowerCase();
        const activeFilter = document.querySelector('.filter-chip.active').textContent.toLowerCase();

        // Clear existing content efficiently
        vaultGrid.innerHTML = '';
        const filtered = secrets.filter(item => {
            const matchesSearch = item.title.toLowerCase().includes(query);
            const matchesFilter = activeFilter === 'all' || item.scope === activeFilter;
            return matchesSearch && matchesFilter;
        });

        if (filtered.length === 0) {
            vaultGrid.innerHTML = `
                <div class="col-12 text-center py-5">
                    <div class="text-muted mb-3">
                        <span class="material-icons" style="font-size: 48px;">inventory_2</span>
                    </div>
                    <h5 class="text-muted">No secrets found</h5>
                    <p class="text-muted small">Try adjusting your search or filter</p>
                </div>
            `;
            document.getElementById('itemCount').textContent = `0 Secrets`;
            return;
        }

        // Optimization: Use DocumentFragment to batch DOM updates and reduce reflows
        const fragment = document.createDocumentFragment();

        if (filtered.length === 0) {
            // Palette UX improvement: show a user-friendly empty state when no secrets match filters/search
            const emptyState = document.createElement('div');
            emptyState.className = 'col-12 text-center py-5 opacity-75';
            emptyState.innerHTML = `
                <div class="mb-3">
                    <span class="material-icons" style="font-size: 48px; color: var(--text-muted);">inventory_2</span>
                </div>
                <h5 class="text-muted">No secrets found</h5>
                <p class="small text-muted">Try adjusting your filters or search terms.</p>
            `;
            fragment.appendChild(emptyState);
        } else {
            filtered.forEach(item => {
                const card = document.createElement('div');
                card.className = 'vault-card';
                card.innerHTML = `
                    <div class="card-header">
                        <div class="card-title-group">
                            <h3 class="h6 mb-0">${item.title}</h3>
                            <div class="text-muted small">Updated ${new Date(item.updated_at).toLocaleDateString()}</div>
                        </div>
                    </div>
                    <div class="card-tags">
                        <span class="tag">${item.scope}</span>
                    </div>
                    <div class="card-footer">
                        <div class="password-mask">••••••••••••</div>
                    </div>
                `;
                card.addEventListener('click', () => showDetail(item));
                fragment.appendChild(card);
            });
        }
        vaultGrid.appendChild(fragment);
        document.getElementById('itemCount').textContent = `${filtered.length} Secrets`;
    }

    function showDetail(item) {
        document.getElementById('detailOwner').textContent = item.owner;
        document.getElementById('detailScope').textContent = item.scope;
        document.getElementById('detailType').textContent = item.item_type;
        detailPane.classList.add('active');
        detailPane.dataset.itemId = item.id;
        loadItemAuditLogs(item.id);
    }

    closePaneBtn.addEventListener('click', () => {
        detailPane.classList.remove('active');
    });

    // --- New Secret ---
    const newSecretBtn = document.getElementById('newSecretBtn');
    const newSecretModalEl = document.getElementById('newSecretModal');
    let newSecretModal = null;
    if (newSecretModalEl) newSecretModal = new bootstrap.Modal(newSecretModalEl);
    const newSecretForm = document.getElementById('newSecretForm');

    if (newSecretBtn) {
        newSecretBtn.addEventListener('click', () => {
            newSecretModal.show();
        });
    }

    if (newSecretForm) {
        newSecretForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const saveBtn = document.getElementById('saveSecretBtn');
            saveBtn.disabled = true;

            const title = document.getElementById('secretTitle').value;
            const plaintext = document.getElementById('secretValue').value;
            const type = document.getElementById('secretType').value;
            const scope = document.getElementById('secretScope').value;

            try {
                if (!masterKey) throw new Error('Master key not found. Please re-login.');

                const nonce = crypto.randomBytes(12);
                const plaintextBytes = crypto.utf8Encode(plaintext);
                const ciphertext = await crypto.encryptAesGcm(masterKey, plaintextBytes, nonce);

                const res = await fetch('/api/vault-items/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
                    body: JSON.stringify({
                        title,
                        item_type: type,
                        scope,
                        encrypted_blob: crypto.toBase64(ciphertext),
                        nonce: crypto.toBase64(nonce)
                    })
                });

                if (res.ok) {
                    newSecretModal.hide();
                    newSecretForm.reset();
                    loadVault();
                } else {
                    const data = await res.json();
                    alert('Failed to save: ' + (data.error || JSON.stringify(data)));
                }
            } catch (err) {
                console.error(err);
                alert(err.message);
            } finally {
                saveBtn.disabled = false;
            }
        });
    }

    // --- Decrypt & Show ---
    const decryptBtn = document.querySelector('.detail-actions .btn-primary');

    if (decryptBtn) {
        decryptBtn.addEventListener('click', async () => {
            const itemId = detailPane.dataset.itemId;
            if (!itemId) return;

            const item = secrets.find(s => s.id == itemId);
            if (!item) return;

            try {
                if (!masterKey) throw new Error('Master key not found. Please re-login.');

                const ciphertext = crypto.fromBase64(item.encrypted_blob);
                const nonce = crypto.fromBase64(item.nonce);
                const decryptedBytes = await crypto.decryptAesGcm(masterKey, ciphertext, nonce);
                const plaintext = crypto.utf8Decode(decryptedBytes);

                alert('Decrypted Value: ' + plaintext);
            } catch (err) {
                console.error(err);
                alert('Decryption failed: ' + err.message);
            }
        });
    }

    // --- Search & Filter ---
    const searchInput = document.getElementById('vault-search');
    const filterChips = document.querySelectorAll('.filter-chip');

    // Palette UX Improvement: Debounce search input to avoid excessive DOM re-renders while typing.
    function debounce(func, wait) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }

    if (searchInput) {
        searchInput.addEventListener('input', debounce(() => {
            renderVault();
        }, 250));
    }

    filterChips.forEach(chip => {
        chip.addEventListener('click', () => {
            filterChips.forEach(c => {
                c.classList.remove('active');
                c.setAttribute('aria-pressed', 'false');
            });
            chip.classList.add('active');
            chip.setAttribute('aria-pressed', 'true');
            renderVault();
        });
    });

    // --- Admin ---
    if (rotateAdminBtn) {
        rotateAdminBtn.addEventListener('click', async () => {
            try {
                const response = await fetch('/rotate-admin/', {
                    method: 'POST',
                    headers: { 'X-CSRFToken': getCsrfToken() }
                });
                if (response.ok) {
                    const data = await response.json();
                    alert('Admin URL rotated: ' + data.admin_url);
                } else {
                    alert('Failed to rotate Admin URL (Superadmin only)');
                }
            } catch (error) {
                console.error('Error:', error);
            }
        });
    }

    // --- Sharing Logic ---
    const shareBtn = document.querySelector('.detail-actions .btn-outline-secondary');
    const shareSecretModalEl = document.getElementById('shareSecretModal');
    let shareSecretModal = null;
    if (shareSecretModalEl) shareSecretModal = new bootstrap.Modal(shareSecretModalEl);
    const shareSecretForm = document.getElementById('shareSecretForm');

    if (shareBtn) {
        shareBtn.addEventListener('click', () => {
            shareSecretModal.show();
        });
    }

    if (shareSecretForm) {
        shareSecretForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const itemId = detailPane.dataset.itemId;
            const recipient = document.getElementById('shareRecipient').value;
            const expiry = document.getElementById('shareExpiry').value;

            try {
                const res = await fetch('/api/access-grants/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
                    body: JSON.stringify({
                        vault_item: itemId,
                        grantee_username: recipient,
                        expires_at: expiry || null
                    })
                });

                if (res.ok) {
                    alert('Access shared successfully!');
                    shareSecretModal.hide();
                    shareSecretForm.reset();
                } else {
                    const data = await res.json();
                    alert('Sharing failed: ' + JSON.stringify(data));
                }
            } catch (err) {
                console.error(err);
                alert(err.message);
            }
        });
    }

    // --- Shared View Requests ---
    async function loadRequests() {
        const requestList = document.getElementById('requestList');
        if (!requestList) return;

        try {
            const res = await fetch('/api/access-grants/');
            if (res.ok) {
                const grants = await res.json();
                const received = grants.filter(g => g.grantee === currentUser.username);
                requestList.innerHTML = '';
                received.forEach(g => {
                    const card = document.createElement('div');
                    card.className = 'request-card';
                    card.innerHTML = `
                        <div class="request-info">
                            <div class="fw-medium">Shared by: ${g.granted_by}</div>
                            <div class="text-muted small">Vault Item ID: ${g.vault_item}</div>
                        </div>
                        <div class="request-actions">
                            <button class="btn btn-sm btn-outline-success" onclick="alert('Access already active. Check your vault.')">View</button>
                        </div>
                    `;
                    requestList.appendChild(card);
                });
            }
        } catch (e) {
            console.error('Failed to load requests', e);
        }
    }

    // --- Audit Logs View ---
    async function loadAuditLogs() {
        const auditLogBody = document.getElementById('auditLogBody');
        if (!auditLogBody) return;

        try {
            const res = await fetch('/api/audit-events/');
            if (res.ok) {
                const logs = await res.json();
                auditLogBody.innerHTML = '';
                logs.forEach(log => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${new Date(log.created_at).toLocaleString()}</td>
                        <td>${log.actor}</td>
                        <td><span class="badge bg-secondary">${log.action.toUpperCase()}</span></td>
                        <td>${log.target_type}: ${log.target_id}</td>
                        <td>${log.ip_address || '-'}</td>
                    `;
                    auditLogBody.appendChild(row);
                });
            }
        } catch (e) {
            console.error('Failed to load audit logs', e);
        }
    }

    // --- Detail Pane Access Logs ---
    async function loadItemAuditLogs(itemId) {
        const detailAccessLogs = document.getElementById('detailAccessLogs');
        if (!detailAccessLogs) return;

        try {
            const res = await fetch(`/api/audit-events/?target_id=${itemId}&target_type=vault_item`);
            if (res.ok) {
                const logs = await res.json();
                detailAccessLogs.innerHTML = '';
                logs.slice(0, 5).forEach(log => {
                    const li = document.createElement('li');
                    li.className = 'small text-muted mb-1';
                    li.textContent = `${new Date(log.created_at).toLocaleDateString()} - ${log.actor} (${log.action})`;
                    detailAccessLogs.appendChild(li);
                });
            }
        } catch (e) {
            console.error('Failed to load item audit logs', e);
        }
    }

    // --- People View ---
    async function loadPeople() {
        const peopleList = document.getElementById('peopleList');
        if (!peopleList) return;

        try {
            const res = await fetch('/api/users/');
            if (res.ok) {
                const users = await res.json();
                peopleList.innerHTML = '';
                users.forEach(u => {
                    const col = document.createElement('div');
                    col.className = 'col-md-4 mb-3';
                    col.innerHTML = `
                        <div class="card bg-dark border-secondary h-100">
                            <div class="card-body">
                                <h6 class="mb-1">${u.username}</h6>
                                <div class="small text-muted mb-2">${u.email || 'No email'}</div>
                                <span class="badge bg-secondary">${u.role}</span>
                                <div class="mt-2 small text-muted">
                                    ${u.organization || 'No Organization'} / ${u.department || 'No Dept'}
                                </div>
                            </div>
                        </div>
                    `;
                    peopleList.appendChild(col);
                });
            }
        } catch (e) {
            console.error('Failed to load people', e);
        }
    }

    // --- Logout ---
    const logoutBtn = document.createElement('button');
    logoutBtn.className = 'btn btn-outline-danger btn-sm w-100 mt-2';
    logoutBtn.textContent = 'Logout';
    logoutBtn.onclick = async () => {
        const res = await fetch('/api/logout/', { method: 'POST', headers: { 'X-CSRFToken': getCsrfToken() } });
        if (res.ok) window.location.reload();
    };
    document.querySelector('.sidebar-footer').appendChild(logoutBtn);

    // --- Init ---
    checkAuth();
});
