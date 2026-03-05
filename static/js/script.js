document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.getElementById("sidebar");
    const menuItems = document.getElementById("menu-items");
    const toggleBtn = document.getElementById("toggle-btn");

    toggleBtn.addEventListener("click", function () {
        // Toggle the "hidden" class for the sidebar
        sidebar.classList.toggle("hidden");

        // Dynamically update the button icon
        if (sidebar.classList.contains("hidden")) {
            toggleBtn.textContent = "☰"; // Hamburger icon
        } else {
            toggleBtn.textContent = "×"; // Close icon
        }
    });
});
