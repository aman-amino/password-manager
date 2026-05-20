document.addEventListener('DOMContentLoaded', () => {
    const navLinks = document.querySelectorAll('.nav-link');
    const viewPanes = document.querySelectorAll('.view-pane');
    const viewTitle = document.getElementById('viewTitle');
    const vaultGrid = document.getElementById('vaultGrid');
    const detailPane = document.getElementById('detailPane');
    const closePaneBtn = document.getElementById('closePaneBtn');
    const rotateAdminBtn = document.getElementById('rotateAdminBtn');
    const vaultControls = document.getElementById('vaultControls');

    // State
    let secrets = [
        { id: 1, title: 'Prod Admin', owner: 'superadmin@vault', scope: 'Organization', tags: ['critical', 'infra'], type: 'generic', updated: '2h ago' },
        { id: 2, title: 'HR Payroll', owner: 'admin@vault', scope: 'Department', tags: ['dept'], type: 'generic', updated: '1d ago' },
        { id: 3, title: 'Personal MFA', owner: 'superadmin@vault', scope: 'Personal', tags: ['personal'], type: 'generic', updated: '3d ago' }
    ];

    // Navigation
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            const view = link.dataset.view;

            // UI Update
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');

            viewPanes.forEach(p => p.classList.add('d-none'));
            const targetView = document.getElementById(view + 'View');
            if (targetView) targetView.classList.remove('d-none');

            viewTitle.textContent = view.charAt(0).toUpperCase() + view.slice(1);

            // Show/Hide controls
            if (view === 'vault') {
                vaultControls.classList.remove('d-none');
            } else {
                vaultControls.classList.add('d-none');
            }
        });
    });

    // Render Vault
    function renderVault() {
        vaultGrid.innerHTML = '';
        secrets.forEach(item => {
            const card = document.createElement('div');
            card.className = 'vault-card';
            card.innerHTML = `
                <div class="card-header">
                    <div class="card-title-group">
                        <h3 class="h6 mb-0">${item.title}</h3>
                        <div class="text-muted small">Updated ${item.updated}</div>
                    </div>
                </div>
                <div class="card-tags">
                    ${item.tags.map(t => `<span class="tag ${t === 'critical' ? 'tag-critical' : ''}">${t}</span>`).join('')}
                </div>
                <div class="card-footer">
                    <div class="password-mask">••••••••••••</div>
                </div>
            `;
            card.addEventListener('click', () => showDetail(item));
            vaultGrid.appendChild(card);
        });
        document.getElementById('itemCount').textContent = `${secrets.length} Secrets`;
    }

    function showDetail(item) {
        document.getElementById('detailOwner').textContent = item.owner;
        document.getElementById('detailScope').textContent = item.scope;
        document.getElementById('detailType').textContent = item.type;
        detailPane.classList.add('active');
    }

    closePaneBtn.addEventListener('click', () => {
        detailPane.classList.remove('active');
    });

    // Admin Rotation
    rotateAdminBtn.addEventListener('click', async () => {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        try {
            const response = await fetch('/rotate-admin/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json'
                }
            });
            if (response.ok) {
                const data = await response.json();
                alert('Admin URL rotated: ' + data.admin_url);
            } else {
                alert('Failed to rotate Admin URL');
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });

    // Init
    renderVault();
});
