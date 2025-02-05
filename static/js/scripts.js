// Theme selection
document.addEventListener("DOMContentLoaded", () => {
    const themeToggle = document.getElementById("theme-toggle");
    const themeIcon = document.getElementById("theme-icon");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const savedTheme = localStorage.getItem("theme");

    // Determine prefered user theme
    const isDarkMode = savedTheme ? savedTheme === "dark" : prefersDark;
    document.body.classList.toggle("dark-mode", isDarkMode);
    updateIcon(isDarkMode);

    // Save theme in localStorage
    function saveTheme(isDark) {
        localStorage.setItem("theme", isDark ? "dark" : "light");
    }

    // Update sun/moon icon
    function updateIcon(isDark) {
        themeIcon.classList.remove("fas", "far");
        themeIcon.classList.add(isDark ? "far" : "fas");
    }

    // Change theme manually
    themeToggle.addEventListener("click", (event) => {
        event.preventDefault();
        const isDark = document.body.classList.toggle("dark-mode");
        saveTheme(isDark);
        updateIcon(isDark);
    });

    // Review system preferences
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (e) => {
        if (!localStorage.getItem("theme")) { // Change if user didn't change it manually
            const newPreference = e.matches;
            document.body.classList.toggle("dark-mode", newPreference);
            updateIcon(newPreference);
        }
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