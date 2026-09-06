// Split-Screen Login Interactions

document.addEventListener('DOMContentLoaded', () => {
    const roleTabs = document.querySelectorAll('.role-tab-btn');
    const roleInput = document.getElementById('selected-role-input');
    const emailInput = document.getElementById('email-field');
    const passwordInput = document.getElementById('password-field');
    const togglePasswordBtn = document.getElementById('toggle-password-btn');
    const togglePasswordIcon = document.getElementById('toggle-password-icon');

    const roleConfig = {
        citizen: {
            label: 'Email or Mobile Number',
            placeholder: 'Enter email or mobile number'
        },
        government: {
            label: 'Official Email or Employee ID',
            placeholder: 'Enter official email or employee ID'
        },
        university: {
            label: 'Institutional Email or University ID',
            placeholder: 'Enter institutional email or university ID'
        }
    };

    const identifierLabel = document.getElementById('login-identifier-label');

    // 1. Role Tabs Switching
    roleTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const role = tab.getAttribute('data-role');
            selectRole(role);
        });
    });

    function selectRole(role) {
        roleTabs.forEach(tab => {
            if (tab.getAttribute('data-role') === role) {
                tab.classList.add('active');
            } else {
                tab.classList.remove('active');
            }
        });
        if (roleInput) {
            roleInput.value = role;
        }
        if (roleConfig[role]) {
            if (identifierLabel) {
                identifierLabel.textContent = roleConfig[role].label;
            }
            if (emailInput) {
                emailInput.setAttribute('placeholder', roleConfig[role].placeholder);
            }
        }
    }

    // 2. Show/Hide Password Toggle
    if (togglePasswordBtn && passwordInput) {
        togglePasswordBtn.addEventListener('click', () => {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            if (type === 'text') {
                togglePasswordIcon.classList.remove('bi-eye');
                togglePasswordIcon.classList.add('bi-eye-slash');
            } else {
                togglePasswordIcon.classList.remove('bi-eye-slash');
                togglePasswordIcon.classList.add('bi-eye');
            }
        });
    }

    // 3. Demo Credentials 1-Click Fill
    const demoAccounts = {
        citizen: {
            email: 'citizen@demo.com',
            password: 'demo123'
        },
        government: {
            email: 'government@demo.com',
            password: 'demo123'
        },
        university: {
            email: 'university@demo.com',
            password: 'demo123'
        }
    };

    window.fillDemoCredentials = function(role) {
        if (demoAccounts[role]) {
            selectRole(role);
            if (emailInput) emailInput.value = demoAccounts[role].email;
            if (passwordInput) passwordInput.value = demoAccounts[role].password;
        }
    };
});
