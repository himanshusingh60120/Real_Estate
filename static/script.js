document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    const propertyList = document.getElementById('property-list');
    const dashboardSection = document.getElementById('dashboard-section');

    let currentUserId = null;
    let currentUserType = null;

    // --- User Authentication ---

    // Handle Login Form Submission
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;

        const response = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const result = await response.json();
        
        if (response.ok) {
            alert(result.message);
            currentUserId = result.user_id;
            currentUserType = result.user_type;
            updateUI();
        } else {
            alert(result.error);
        }
    });

    // Handle Signup Form Submission
    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('signup-email').value;
        const password = document.getElementById('signup-password').value;
        const userType = document.getElementById('user-type').value;

        const response = await fetch('/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, user_type: userType })
        });
        const result = await response.json();
        alert(result.message || result.error);
    });

    // --- Property Interaction ---

    // Function to fetch and display properties
    const fetchProperties = async () => {
        const response = await fetch('/properties');
        const properties = await response.json();
        
        propertyList.innerHTML = '';
        if (properties.length === 0) {
            propertyList.innerHTML = '<p>No available properties at the moment.</p>';
            return;
        }

        properties.forEach(property => {
            const propertyDiv = document.createElement('div');
            propertyDiv.className = 'property-card';
            propertyDiv.innerHTML = `
                <h3>${property.title}</h3>
                <p><strong>City:</strong> ${property.city}</p>
                <p><strong>Price:</strong> ₹${property.price}</p>
                ${currentUserType === 'tenant' ? 
                    `<button class="like-button" data-property-id="${property.property_id}">Like</button>` : ''
                }
            `;
            propertyList.appendChild(propertyDiv);
        });
    };

    // Event listener for the "Like" button
    propertyList.addEventListener('click', async (e) => {
        if (e.target.classList.contains('like-button')) {
            const propertyId = e.target.getAttribute('data-property-id');
            const response = await fetch('/like_property', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ property_id: propertyId, tenant_user_id: currentUserId })
            });
            const result = await response.json();
            alert(result.message || result.error);
        }
    });

    // --- Dashboard Views ---

    const updateUI = () => {
        if (currentUserId && currentUserType === 'owner') {
            fetchOwnerDashboard();
        } else if (currentUserId && currentUserType === 'tenant') {
            fetchTenantDashboard();
            fetchProperties(); // Show properties as well
        } else {
            // User is logged out, show default view
            fetchProperties();
        }
    };

    const fetchOwnerDashboard = async () => {
        const response = await fetch(`/owner_dashboard/${currentUserId}`);
        const data = await response.json();
        dashboardSection.innerHTML = '<h2>Owner Dashboard</h2>';
        if (response.ok) {
            data.forEach(property => {
                dashboardSection.innerHTML += `
                    <div class="dashboard-card">
                        <h4>${property.property_title}</h4>
                        <p><strong>Rental Yield:</strong> ${property.rental_yield_percent}%</p>
                        <p><strong>Payback Period:</strong> ${property.years_to_cover_price} years</p>
                    </div>
                `;
            });
        } else {
            dashboardSection.innerHTML += `<p>${data.message}</p>`;
        }
    };

    const fetchTenantDashboard = async () => {
        const response = await fetch(`/tenant_dashboard/${currentUserId}`);
        const data = await response.json();
        dashboardSection.innerHTML = '<h2>My Liked Properties</h2>';
        if (response.ok) {
            data.forEach(property => {
                let interestedTenantsHtml = property.interested_tenants.map(tenant => `
                    <li>Name: ${tenant.name} | Phone: ${tenant.phone} | Email: ${tenant.email}</li>
                `).join('');
                
                dashboardSection.innerHTML += `
                    <div class="dashboard-card">
                        <h4>${property.title}</h4>
                        <p><strong>Total Interested:</strong> ${property.total_likes} people</p>
                        <ul>${interestedTenantsHtml}</ul>
                    </div>
                `;
            });
        } else {
            dashboardSection.innerHTML += `<p>${data.message}</p>`;
        }
    };

    // Initial load
    updateUI();
});