document.addEventListener('DOMContentLoaded', () => {
    // Add simple animation for cards on load
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 50); // Stagger effect
    });

    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 10) {
            navbar.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)';
        } else {
            navbar.style.boxShadow = 'none';
        }
    });
});

function rateMovie(movieId, score) {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/api/movies/rate/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            movie_id: movieId,
            score: score
        })
    })
        .then(response => {
            if (response.ok) {
                alert('Rating saved! Recommendations will be updated.');
            } else {
                response.json().then(data => {
                    if (data.error === 'Authentication required') {
                        window.location.href = '/accounts/login/';
                    } else {
                        alert('Error: ' + data.error);
                    }
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}
