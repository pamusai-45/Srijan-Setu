// Main Application Interactions
document.addEventListener('DOMContentLoaded', () => {
    // 1. Mobile Sidebar Toggle
    const sidebarToggleBtn = document.getElementById('sidebar-toggle-btn');
    const appSidebar = document.querySelector('.app-sidebar');

    if (sidebarToggleBtn && appSidebar) {
        sidebarToggleBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            appSidebar.classList.toggle('show');
        });

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', (e) => {
            if (window.innerWidth < 992 && appSidebar.classList.contains('show')) {
                if (!appSidebar.contains(e.target) && e.target !== sidebarToggleBtn) {
                    appSidebar.classList.remove('show');
                }
            }
        });
    }

    // 2. Auto Dismiss Flash Alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-jig');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 400);
        }, 5000);
    });

    // 3. Interactive File Upload Preview
    const fileInput = document.getElementById('media_files');
    const filePreviewBox = document.getElementById('file-preview-list');
    if (fileInput && filePreviewBox) {
        fileInput.addEventListener('change', () => {
            filePreviewBox.innerHTML = '';
            if (fileInput.files.length > 0) {
                Array.from(fileInput.files).forEach(f => {
                    const pill = document.createElement('span');
                    pill.className = 'badge bg-light text-dark border p-2 me-2 mb-2 d-inline-flex align-items-center gap-1';
                    pill.innerHTML = `<i class="bi bi-file-earmark-arrow-up text-success"></i> ${f.name} <small class="text-muted">(${(f.size/1024).toFixed(1)} KB)</small>`;
                    filePreviewBox.appendChild(pill);
                });
            }
        });
    }

    // 4. Sidebar Grouped Cards Accordion Collapse (Citizen & Government)
    const cardHeaders = document.querySelectorAll('.sidebar-card-header');
    cardHeaders.forEach(header => {
        header.addEventListener('click', (e) => {
            e.preventDefault();
            const parentCard = header.closest('.sidebar-nav-card');
            if (parentCard) {
                const isCollapsed = parentCard.classList.toggle('collapsed');
                header.setAttribute('aria-expanded', !isCollapsed);
            }
        });
    });

    // On mobile (<768px), collapse non-active cards initially for clean view
    if (window.innerWidth < 768) {
        document.querySelectorAll('.sidebar-nav-card').forEach(card => {
            const hasActiveLink = card.querySelector('.card-nav-link.active');
            if (!hasActiveLink) {
                card.classList.add('collapsed');
                const header = card.querySelector('.sidebar-card-header');
                if (header) header.setAttribute('aria-expanded', 'false');
            }
        });
    }
});
