const toggleButton = document.getElementById("burger")
const navbar = document.getElementById("menu")

toggleButton.addEventListener("click", () => {
    navbar.classList.toggle("active")
})