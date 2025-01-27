// Generate current year
const yearSpan = document.getElementById("current_year");
const currentYear = new Date().getFullYear();
yearSpan.textContent = currentYear;

// Use local timezone
function formatDateForUser(dateString) {
    var date = new Date(dateString);
    return date.toLocaleString();
}

// Delete confirmation script
function confirmDelete(event, url) {
    event.preventDefault(); 
    $('#deleteModal').modal('show');
    document.getElementById('confirmDeleteBtn').onclick = function() {
        window.location.href = url;
    }
}