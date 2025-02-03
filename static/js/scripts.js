// Theme selection
document.addEventListener("DOMContentLoaded", () => {
    const themeToggle = document.getElementById("theme-toggle");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const savedTheme = localStorage.getItem("theme");

    // Set theme on load
    const theme = savedTheme || (prefersDark ? "dark" : "light");
    document.body.classList.toggle("dark-mode", theme === "dark");

    // Save theme to cookies
    document.cookie = `theme=${theme}; path=/; max-age=31536000`;

    themeToggle.addEventListener("click", () => {
        const isDark = document.body.classList.toggle("dark-mode");
        const theme = isDark ? "dark" : "light";
        document.cookie = `theme=${theme}; path=/; max-age=31536000`;
    });
});

// Generate current year
const yearSpan = document.getElementById("current_year");
const currentYear = new Date().getFullYear();
yearSpan.textContent = currentYear;

// Delete confirmation script
function confirmDelete(event, url) {
    event.preventDefault(); 
    $('#deleteModal').modal('show');
    document.getElementById('confirmDeleteBtn').onclick = function() {
        window.location.href = url;
    }
}

// Automatically close the alert message after 5 seconds
setTimeout(function() {
    var alert = document.getElementById('flashedMessage');
    if (alert) {
        alert.classList.remove('show');
        alert.classList.add('fade');
    }
}, 5000);

function showAlert(message) {
    $('#alertMessage').text(message);
    $('#customAlert').show();
    setTimeout(function() {
        $('#customAlert').fadeOut();
    }, 5000);
}