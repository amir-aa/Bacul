// custom.js - Main JavaScript file for Bacula Dashboard

document.addEventListener('DOMContentLoaded', function() {
    // Sidebar Toggle
    const sidebarToggle = document.getElementById('sidebarToggle');
    if (sidebarToggle) {
        // Initialize sidebar state from localStorage
        const sidebarState = localStorage.getItem('sidebarToggled');
        if (sidebarState === 'true') {
            document.body.classList.add('sidebar-toggled');
            document.querySelector('.sidebar').classList.add('toggled');
        }

        // Toggle sidebar on click
        sidebarToggle.addEventListener('click', function(e) {
            e.preventDefault();
            document.body.classList.toggle('sidebar-toggled');
            const sidebar = document.querySelector('.sidebar');
            sidebar.classList.toggle('toggled');
            
            // Save state to localStorage
            localStorage.setItem('sidebarToggled', sidebar.classList.contains('toggled'));
        });
    }

    // Close sidebar on small screens when clicking outside
    const screenWidth = window.innerWidth;
    if (screenWidth < 768) {
        document.addEventListener('click', function(e) {
            const sidebar = document.querySelector('.sidebar');
            const sidebarToggle = document.getElementById('sidebarToggle');
            
            // Check if sidebar is open and click is outside sidebar and toggle button
            if (sidebar && !sidebar.contains(e.target) && 
                sidebarToggle && !sidebarToggle.contains(e.target) && 
                !document.body.classList.contains('sidebar-toggled')) {
                document.body.classList.add('sidebar-toggled');
                sidebar.classList.add('toggled');
                localStorage.setItem('sidebarToggled', 'true');
            }
        });
    }

    // Handle dropdown menus in sidebar
    const dropdownToggles = document.querySelectorAll('.sidebar .nav-item .dropdown-toggle');
    dropdownToggles.forEach(function(toggle) {
        // Set initial state based on active children
        const dropdownContent = toggle.nextElementSibling;
        const hasActiveChild = dropdownContent && dropdownContent.querySelector('.active');
        
        if (hasActiveChild) {
            toggle.classList.add('show');
            if (dropdownContent) {
                dropdownContent.classList.add('show');
            }
        }
        
        // Toggle dropdown on click
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            this.classList.toggle('show');
            const dropdownContent = this.nextElementSibling;
            if (dropdownContent) {
                dropdownContent.classList.toggle('show');
            }
        });
    });

    // Set active menu item based on current URL
    function setActiveMenuItem() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.sidebar .nav-link');
        
        navLinks.forEach(function(link) {
            // Remove active class from all links
            link.classList.remove('active');
            
            // Check if link href matches current path
            const linkPath = link.getAttribute('href');
            if (linkPath && currentPath.startsWith(linkPath) && linkPath !== '/') {
                // Set link as active
                link.classList.add('active');
                
                // Expand parent dropdown if in one
                const parentItem = link.closest('.nav-item');
                if (parentItem) {
                    const parentDropdown = parentItem.closest('.collapse');
                    if (parentDropdown) {
                        parentDropdown.classList.add('show');
                        const parentToggle = parentDropdown.previousElementSibling;
                        if (parentToggle) {
                            parentToggle.classList.add('show');
                        }
                    }
                }
            } else if (linkPath === '/' && currentPath === '/') {
                // Special case for home page
                link.classList.add('active');
            }
        });
    }
    
    // Call function to set active menu item
    setActiveMenuItem();

    // Initialize all tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (typeof bootstrap !== 'undefined') {
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    }

    // Initialize all popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    if (typeof bootstrap !== 'undefined') {
        const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
    }

    // Handle alert dismissals
    const alertCloseButtons = document.querySelectorAll('.alert .btn-close');
    alertCloseButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const alert = this.closest('.alert');
            if (alert) {
                alert.classList.add('fade');
                setTimeout(function() {
                    alert.style.display = 'none';
                }, 150);
            }
        });
    });

    // Auto-hide alerts after 5 seconds
    const autoHideAlerts = document.querySelectorAll('.alert-auto-dismiss');
    autoHideAlerts.forEach(function(alert) {
        setTimeout(function() {
            if (alert) {
                alert.classList.add('fade');
                setTimeout(function() {
                    alert.style.display = 'none';
                }, 150);
            }
        }, 5000);
    });

    // Scroll to top button
    const scrollTopBtn = document.getElementById('scrollTopBtn');
    if (scrollTopBtn) {
        // Show/hide button based on scroll position
        window.addEventListener('scroll', function() {
            if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
                scrollTopBtn.style.display = 'block';
            } else {
                scrollTopBtn.style.display = 'none';
            }
        });

        // Scroll to top when button is clicked
        scrollTopBtn.addEventListener('click', function() {
            document.body.scrollTop = 0; // For Safari
            document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
        });
    }

    // Handle card collapsing
    const cardCollapseButtons = document.querySelectorAll('.card-header .btn-collapse');
    cardCollapseButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const card = this.closest('.card');
            const cardBody = card.querySelector('.card-body');
            
            if (cardBody) {
                if (cardBody.style.display === 'none') {
                    cardBody.style.display = '';
                    this.querySelector('i').classList.remove('fa-plus');
                    this.querySelector('i').classList.add('fa-minus');
                } else {
                    cardBody.style.display = 'none';
                    this.querySelector('i').classList.remove('fa-minus');
                    this.querySelector('i').classList.add('fa-plus');
                }
            }
        });
    });

    // Handle DataTables initialization if jQuery and DataTables are available
    if (typeof $ !== 'undefined' && typeof $.fn.DataTable !== 'undefined') {
        $('.datatable').each(function() {
            $(this).DataTable({
                responsive: true,
                pageLength: 25,
                language: {
                    search: "<i class='fas fa-search'></i>",
                    searchPlaceholder: "Search records"
                }
            });
        });
    }

    // Handle form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Handle confirmation dialogs
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm') || 'Are you sure you want to perform this action?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Handle ajax loading indicators
    document.addEventListener('ajax:before', function() {
        document.getElementById('ajax-loader').style.display = 'block';
    });
    
    document.addEventListener('ajax:complete', function() {
        document.getElementById('ajax-loader').style.display = 'none';
    });

    // Toggle password visibility
    const passwordToggles = document.querySelectorAll('.password-toggle');
    passwordToggles.forEach(function(toggle) {
        toggle.addEventListener('click', function() {
            const passwordField = document.getElementById(this.getAttribute('data-target'));
            if (passwordField) {
                if (passwordField.type === 'password') {
                    passwordField.type = 'text';
                    this.querySelector('i').classList.remove('fa-eye');
                    this.querySelector('i').classList.add('fa-eye-slash');
                } else {
                    passwordField.type = 'password';
                    this.querySelector('i').classList.remove('fa-eye-slash');
                    this.querySelector('i').classList.add('fa-eye');
                }
            }
        });
    });

    // Handle refresh button clicks
    const refreshButtons = document.querySelectorAll('.btn-refresh');
    refreshButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            location.reload();
        });
    });

    // Initialize datetime pickers if flatpickr is available
    if (typeof flatpickr !== 'undefined') {
        flatpickr('.datetime-picker', {
            enableTime: true,
            dateFormat: "Y-m-d H:i:S",
            time_24hr: true
        });
        
        flatpickr('.date-picker', {
            dateFormat: "Y-m-d"
        });
    }

    // Handle theme switching
    const themeSwitch = document.getElementById('themeSwitch');
    if (themeSwitch) {
        // Set initial state based on localStorage or system preference
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            document.documentElement.setAttribute('data-bs-theme', 'dark');
            themeSwitch.checked = true;
        } else if (savedTheme === 'light') {
            document.documentElement.setAttribute('data-bs-theme', 'light');
            themeSwitch.checked = false;
        } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            document.documentElement.setAttribute('data-bs-theme', 'dark');
            themeSwitch.checked = true;
        }

        // Toggle theme on switch change
        themeSwitch.addEventListener('change', function() {
            if (this.checked) {
                document.documentElement.setAttribute('data-bs-theme', 'dark');
                localStorage.setItem('theme', 'dark');
            } else {
                document.documentElement.setAttribute('data-bs-theme', 'light');
                localStorage.setItem('theme', 'light');
            }
        });
    }
});