document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const showButton = document.getElementById('showButton');
    const logoutButton = document.getElementById('logoutButton');

    // Check if the user is already logged in
    const isLoggedIn = sessionStorage.getItem('isLoggedIn');

    if (isLoggedIn) {
        // If logged in, show the data page
        document.getElementById('login-page').style.display = 'none';
        document.getElementById('data-page').style.display = 'block';
    } else {
        // If not logged in, show the login page
        document.getElementById('login-page').style.display = 'block';
        document.getElementById('data-page').style.display = 'none';
    }

    loginForm.addEventListener('submit', event => {
        event.preventDefault(); // Prevent form submission

        const username = usernameInput.value;
        const password = passwordInput.value;

        // Check if entered username and password match the default credentials
        if (username === 'Shanmukh' && password === '1234') {
            // Set logged in status in sessionStorage
            sessionStorage.setItem('isLoggedIn', true);

            // Hide login page and show data page
            document.getElementById('login-page').style.display = 'none';
            document.getElementById('data-page').style.display = 'block';
        } else {
            // Show an error message or handle invalid credentials
            alert('Invalid username or password. Please try again.');
        }
    });

    showButton.addEventListener('click', () => {
        const sessionSelect = document.getElementById('session');
        const campusSelect = document.getElementById('branch');
        const courseSelect = document.getElementById('course');

        const selectedSession = sessionSelect.value;
        const selectedCampus = campusSelect.value;
        const selectedCourse = courseSelect.value;

        // Filter data based on selected session, campus, and course
        const filteredData = filterStudentData(selectedSession, selectedCampus, selectedCourse);

        // Display filtered data in table format
        displayFilteredData(filteredData);
    });

    logoutButton.addEventListener('click', () => {
        // Remove logged in status from sessionStorage
        sessionStorage.removeItem('isLoggedIn');

        // Show login page and hide data page
        document.getElementById('login-page').style.display = 'block';
        document.getElementById('data-page').style.display = 'none';
    });
}); 

// Sample data representing student records
const studentData = [
    { name: 'John Doe', rollNumber: '001', session: 'AEC', campus: 'AEC', course: 'CE' },
    { name: 'Jane Smith', rollNumber: '002', session: 'AEC', campus: 'AEC', course: 'EEE' },
    { name: 'Alice Johnson', rollNumber: '003', session: 'ACET', campus: 'ACET', course: 'CSE' },
    // Add more sample data as needed
];

// Function to filter student records based on session, campus, and course
function filterStudentData(session, campus, course) {
    return studentData.filter(student => {
        return student.session === session &&
               student.campus === campus &&
               student.course === course;
    });
}

// Function to display filtered data in table format
function displayFilteredData(filteredData) {
    const tableBody = document.getElementById('data-table-body');
    tableBody.innerHTML = ''; // Clear previous data

    filteredData.forEach((student, index) => {
        const row = tableBody.insertRow();
        const serialNumberCell = row.insertCell(0);
        const nameCell = row.insertCell(1); // New cell for Name
        const rollNumberCell = row.insertCell(2);

        serialNumberCell.textContent = index + 1;
        nameCell.textContent = student.name; // Display Name
        rollNumberCell.textContent = student.rollNumber;
    });
}
downloadButton.addEventListener('click', () => {
    downloadDataInExcel(); // Function to initiate download in Excel format
});

// Function to download data in Excel format
function downloadDataInExcel() {
const filteredData = []; // Retrieve your filtered data here

if (filteredData.length === 0) {
    alert('No data to download.'); // Show alert if no data available
    return;
}

// Create a new Excel workbook
const wb = XLSX.utils.book_new();

// Convert data to worksheet
const ws = XLSX.utils.json_to_sheet(filteredData);

// Add the worksheet to the workbook
XLSX.utils.book_append_sheet(wb, ws, 'Sheet1');

// Generate a downloadable file
XLSX.writeFile(wb, 'filtered_data.xlsx');
}