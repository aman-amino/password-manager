document.querySelectorAll(".nav-link").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".nav-link").forEach((btn) => btn.classList.remove("active"));
    button.classList.add("active");
  });
});

// Admin URL rotation logic
const adminBtn = document.querySelector('.sidebar-footer .btn');
if (adminBtn) {
  adminBtn.addEventListener('click', async () => {
    try {
      const response = await fetch('/rotate-admin/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
        }
      });
      const data = await response.json();
      if (data.admin_url) {
        window.open(data.admin_url, '_blank');
      } else {
        alert('Failed to rotate admin URL: ' + (data.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error rotating admin URL:', error);
      alert('Error rotating admin URL. See console for details.');
    }
  });
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
