async function adminLogin(email, password) {
    const response = await fetch('/admin/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`,
        credentials: "include"  // Critical for cookies
    });
    
    const data = await response.json();
    if (response.ok) {
        localStorage.setItem('admin_token', data.access_token);
        return true;
    }
    return false;
}

document.addEventListener('DOMContentLoaded', function() {
// Check login state via cookie (no direct access to HTTP-only cookie)
    fetch('/admin/verify-token', {
        credentials: 'include'  // Required to send cookies
    })
    .then(response => {
        if (response.ok) {
            // User is authenticated (cookie is valid)
            document.getElementById('loginForm').style.display = 'none';
            loadPendingUsers();
        } else {
            // Not logged in or token expired
            showLoginForm();
        }
    })
    .catch(() => showLoginForm());

    document.getElementById('adminLoginForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        const email = document.getElementById('adminEmail').value;
        const password = document.getElementById('adminPassword').value;
        
        if (await adminLogin(email, password)) {
            location.reload(); // Refresh to show admin panel
        } else {
            alert('Login failed');
        }
    });
});

async function loadPendingUsers() {
    try {
        const response = await fetch('/admin/pending-users', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('admin_token')}`
            }
        });
        
        const users = await response.json();
        const table = document.querySelector('#pendingUsers tbody');
        table.innerHTML = users.map(user => `
            <tr>
                <td>${user.id}</td>
                <td>${user.email}</td>
                <td>${user.name}</td>
                <td>${user.family_name}</td>
                <td>
                    <button class="btn btn-sm btn-success" onclick="approveUser(${user.id})">
                        Approve
                    </button>
                    <button class="btn btn-sm btn-success" onclick="rejectUser(${user.id})">
                        Reject
                    </button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

async function approveUser(userId) {
    try {
        await fetch(`/admin/users/${userId}/approve`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('admin_token')}`
            }
        });
        loadPendingUsers(); // Refresh the list
    } catch (error) {
        console.error('Approval failed:', error);
    }
}

async function rejectUser(userId) {
    try {
        await fetch(`/admin/users/${userId}/reject`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('admin_token')}`
            }
        });
        loadPendingUsers(); // Refresh the list
    } catch (error) {
        console.error('Rejection failed:', error);
    }
}
