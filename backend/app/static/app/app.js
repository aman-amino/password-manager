document.querySelectorAll(".nav-link").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".nav-link").forEach((btn) => btn.classList.remove("active"));
    button.classList.add("active");
  });
});

async function rotateAdminUrl() {
  const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  try {
    const response = await fetch('/rotate-admin/', {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken,
        'Content-Type': 'application/json'
      }
    });
    if (response.ok) {
      const data = await response.json();
      alert('Admin URL rotated: ' + data.admin_url);
      console.log('New Admin URL:', data.admin_url);
    } else {
      alert('Failed to rotate Admin URL');
    }
  } catch (error) {
    console.error('Error rotating Admin URL:', error);
  }
}

const adminBtn = document.querySelector('.sidebar-footer .btn');
if (adminBtn) {
  adminBtn.textContent = 'Rotate Admin URL';
  adminBtn.addEventListener('click', (e) => {
    e.preventDefault();
    rotateAdminUrl();
  });
}
