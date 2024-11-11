// schedule.js

// Fetch and render schedules
function renderSchedules() {
    fetch('/api/schedules')
        .then(response => response.json())
        .then(data => {
            const scheduleContainer = document.getElementById('schedule-container');
            scheduleContainer.innerHTML = ''; // Clear existing content

            data.schedules.forEach(schedule => {
                const imageSrc = schedule.image
                    ? `data:image/png;base64,${schedule.image}`
                    : 'https://via.placeholder.com/150';

                const cardHTML = `
                    <div class="col">
                        <div class="card shadow-sm schedule-card" data-id="${schedule.id}">
                            <img src="${imageSrc}" class="bd-placeholder-img card-img-top" width="100%" height="225" alt="Schedule Image">
                            <div class="card-body text-center">
                                <p class="card-text">${schedule.title}</p>
                            </div>
                        </div>
                    </div>
                `;

                scheduleContainer.insertAdjacentHTML('beforeend', cardHTML);
            });

            // Add click event to each card
            document.querySelectorAll('.schedule-card').forEach(card => {
                card.addEventListener('click', () => {
                    const scheduleId = card.getAttribute('data-id');
                    window.location.href = `/schedule/detail?id=${scheduleId}`;
                });
            });
        })
        .catch(error => console.error('Error fetching schedules:', error));
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    renderSchedules();
});
