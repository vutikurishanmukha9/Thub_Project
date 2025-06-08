// Enhanced JavaScript with API integration

document.addEventListener('DOMContentLoaded', () => {
    // Initialize the application
    initializeApp();
    
    // Check authentication status
    checkAuthStatus();
    
    // Start real-time clock
    updateClock();
    setInterval(updateClock, 1000);
});

// Global variables
let currentUser = null;
let filteredData = [];

// Initialize application
function initializeApp() {
    setupEventListeners();
    setDefaultDates();
}

// Setup all event listeners
function setupEventListeners() {
    // Login form
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Logout button
    const logoutButton = document.getElementById('logoutButton');
    if (logoutButton) {
        logoutButton.addEventListener('click', handleLogout);
    }
    
    // Filter and download buttons
    const showButton = document.getElementById('showButton');
    if (showButton) {
        showButton.addEventListener('click', handleFilterData);
    }
    
    const downloadButton = document.getElementById('downloadButton');
    if (downloadButton) {
        downloadButton.addEventListener('click', handleDownloadReport);
    }
}

// Set default date range (last 7 days)
function setDefaultDates() {
    const today = new Date();
    const weekAgo = new Date(today);
    weekAgo.setDate(today.getDate() - 7);
    
    const dateFromInput = document.getElementById('date-from');
    const dateToInput = document.getElementById('date-to');
    
    if (dateFromInput) {
        dateFromInput.value = weekAgo.toISOString().split('T')[0];
    }
    
    if (dateToInput) {
        dateToInput.value = today.toISOString().split('T')[0];
    }
}

// Check authentication status
function checkAuthStatus() {
    // Check if user data exists in sessionStorage
    const userData = sessionStorage.getItem('userData');
    
    if (userData) {
        try {
            currentUser = JSON.parse(userData);
            showDashboard();
            loadDashboardData();
        } catch (error) {
            console.error('Error parsing user data:', error);
            showLogin();
        }
    } else {
        showLogin();
    }
}

// Handle login form submission
async function handleLogin(event) {
    event.preventDefault();
    
    const loginBtn = document.getElementById('login-btn');
    const loginSpinner = document.getElementById('login-spinner');
    const loginError = document.getElementById('login-error');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    
    // Show loading state
    loginBtn.disabled = true;
    loginSpinner.style.display = 'inline-block';
    loginError.style.display = 'none';
    
    try {
        const formData = new FormData();
        formData.append('username', usernameInput.value);
        formData.append('password', passwordInput.value);
        
        const response = await fetch('/login', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Store user data
            currentUser = {
                username: usernameInput.value,
                loginTime: new Date().toISOString()
            };
            sessionStorage.setItem('userData', JSON.stringify(currentUser));
            
            // Show dashboard
            showDashboard();
            loadDashboardData();
        } else {
            showError(loginError, result.message || 'Login failed');
        }
    } catch (error) {
        console.error('Login error:', error);
        showError(loginError, 'Network error. Please try again.');
    } finally {
        // Reset loading state
        loginBtn.disabled = false;
        loginSpinner.style.display = 'none';
    }
}

// Handle logout
async function handleLogout() {
    try {
        const response = await fetch('/logout', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Clear user data
            currentUser = null;
            sessionStorage.removeItem('userData');
            
            // Show login page
            showLogin();
        }
    } catch (error) {
        console.error('Logout error:', error);
        // Force logout on error
        currentUser = null;
        sessionStorage.removeItem('userData');
        showLogin();
    }
}

// Show login page
function showLogin() {
    document.getElementById('login-page').style.display = 'block';
    document.getElementById('data-page').style.display = 'none';
}

// Show dashboard
function showDashboard() {
    document.getElementById('login-page').style.display = 'none';
    document.getElementById('data-page').style.display = 'block';
    
    // Update welcome text
    const welcomeText = document.getElementById('welcome-text');
    if (welcomeText && currentUser) {
        welcomeText.textContent = `Welcome, ${currentUser.username}`;
    }
}

// Load dashboard data
async function loadDashboardData() {
    try {
        await Promise.all([
            loadDashboardStats(),
            loadRecentAttendance()
        ]);
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

// Load dashboard statistics
async function loadDashboardStats() {
    try {
        const response = await fetch('/api/dashboard/stats');
        const result = await response.json();
        
        if (result.success) {
            const stats = result.stats;
            
            document.getElementById('total-students').textContent = stats.total_students;
            document.getElementById('today-attendance').textContent = stats.today_attendance;
            document.getElementById('attendance-percentage').textContent = `${stats.attendance_percentage}%`;
        }
    } catch (error) {
        console.error('Error loading dashboard stats:', error);
    }
}

// Load recent attendance
async function loadRecentAttendance() {
    try {
        const response = await fetch('/api/dashboard/stats');
        const result = await response.json();
        
        if (result.success && result.stats.recent_attendance) {
            const recentContainer = document.getElementById('recent-attendance');
            const recentData = result.stats.recent_attendance;
            
            if (recentData.length === 0) {
                recentContainer.innerHTML = '<p class="text-muted">No recent attendance records.</p>';
                return;
            }
            
            let html = '';
            recentData.forEach(record => {
                html += `
                    <div class="recent-item">
                        <div class="recent-info">
                            <h6>${record.name}</h6>
                            <small>Roll: ${record.roll_number} | Location: ${record.location}</small>
                        </div>
                        <div class="recent-time">${formatDateTime(record.scan_time)}</div>
                    </div>
                `;
            });
            
            recentContainer.innerHTML = html;
        }
    } catch (error) {
        console.error('Error loading recent attendance:', error);
        document.getElementById('recent-attendance').innerHTML = 
            '<p class="text-danger">Error loading recent attendance.</p>';
    }
}

// Handle filter data
async function handleFilterData() {
    const showButton = document.getElementById('showButton');
    const originalText = showButton.innerHTML;
    
    // Show loading state
    showButton.disabled = true;
    showButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
    
    try {
        const filterData = {
            session: document.getElementById('session').value,
            campus: document.getElementById('campus').value,
            course: document.getElementById('course').value,
            date_from: document.getElementById('date-from').value,
            date_to: document.getElementById('date-to').value
        };
        
        const response = await fetch('/api/attendance/filter', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(filterData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            filteredData = result.data;
            displayFilteredData(filteredData);
            updateRecordCount(filteredData.length);
        } else {
            showAlert('danger', result.message || 'Failed to filter data');
        }
    } catch (error) {
        console.error('Filter error:', error);
        showAlert('danger', 'Network error. Please try again.');
    } finally {
        // Reset button state
        showButton.disabled = false;
        showButton.innerHTML = originalText;
    }
}

// Handle download report
async function handleDownloadReport() {
    if (filteredData.length === 0) {
        showAlert('warning', 'No data to download. Please filter some records first.');
        return;
    }
    
    const downloadButton = document.getElementById('downloadButton');
    const originalText = downloadButton.innerHTML;
    
    // Show loading state
    downloadButton.disabled = true;
    downloadButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
    
    try {
        const filterData = {
            session: document.getElementById('session').value,
            campus: document.getElementById('campus').value,
            course: document.getElementById('course').value,
            date_from: document.getElementById('date-from').value,
            date_to: document.getElementById('date-to').value
        };
        
        const response = await fetch('/api/attendance/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(filterData)
        });
        
        if (response.ok) {
            // Create download link
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `attendance_report_${new Date().toISOString().split('T')[0]}.xlsx`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            showAlert('success', 'Report downloaded successfully!');
        } else {
            const result = await response.json();
            showAlert('danger', result.message || 'Failed to download report');
        }
    } catch (error) {
        console.error('Download error:', error);
        showAlert('danger', 'Network error. Please try again.');
    } finally {
        // Reset button state
        downloadButton.disabled = false;
        downloadButton.innerHTML = originalText;
    }
}

// Display filtered data in table
function displayFilteredData(data) {
    const tableBody = document.getElementById('data-table-body');
    
    if (data.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="10" class="text-center text-muted">
                    <i class="fas fa-search"></i> No records found for the selected criteria.
                </td>
            </tr>
        `;
        return;
    }
    
    let html = '';
    data.forEach((record, index) => {
        const statusClass = getStatusClass(record.status);
        html += `
            <tr>
                <td>${index + 1}</td>
                <td>${escapeHtml(record.name)}</td>
                <td>${escapeHtml(record.roll_number)}</td>
                <td>${escapeHtml(record.session)}</td>
                <td>${escapeHtml(record.campus)}</td>
                <td>${escapeHtml(record.course)}</td>
                <td>${formatDate(record.scan_date)}</td>
                <td>${formatTime(record.scan_time)}</td>
                <td>${escapeHtml(record.location)}</td>
                <td><span class="${statusClass}">${escapeHtml(record.status)}</span></td>
            </tr>
        `;
    });
    
    tableBody.innerHTML = html;
}

// Update record count
function updateRecordCount(count) {
    const recordCount = document.getElementById('record-count');
    if (recordCount) {
        recordCount.textContent = `${count} record${count !== 1 ? 's' : ''}`;
    }
}

// Get status CSS class
function getStatusClass(status) {
    switch (status.toLowerCase()) {
        case 'present':
            return 'status-present';
        case 'late':
            return 'status-late';
        case 'absent':
            return 'status-absent';
        default:
            return 'status-present';
    }
}

// Update clock
function updateClock() {
    const clockElement = document.getElementById('current-time');
    if (clockElement) {
        const now = new Date();
        const timeString = now.toLocaleTimeString('en-US', {
            hour12: false,
            hour: '2-digit',
            minute: '2-digit'
        });
        clockElement.textContent = timeString;
    }
}

// Utility functions
function showError(element, message) {
    element.textContent = message;
    element.style.display = 'block';
}

function showAlert(type, message) {
    // Create temporary alert
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatTime(timeString) {
    return timeString.substring(0, 5); // HH:MM format
}

function formatDateTime(dateTimeString) {
    const date = new Date(dateTimeString);
    return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Periodic data refresh (every 30 seconds)
setInterval(() => {
    if (currentUser && document.getElementById('data-page').style.display !== 'none') {
        loadDashboardStats();
        loadRecentAttendance();
    }
}, 30000);
