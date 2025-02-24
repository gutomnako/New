document.addEventListener('DOMContentLoaded', () => {
    const resortList = document.getElementById('resort-list');
    const addResortForm = document.getElementById('add-resort-form');
    const resortNameInput = document.getElementById('resort-name');
    const reviewList = document.getElementById('review-list');
    const reviewText = document.getElementById('review-text');
    const userCount = document.getElementById('user-count');
    const beachName = document.getElementById('beach-name');

    // Example data
    let resorts = [];
    let reviews = [];
    let loggedInUserCount = 25; // Example monthly user count
    let mostVisitedBeach = 'Sunny Beach'; // Example beach name

    // Display initial analytics
    userCount.textContent = loggedInUserCount;
    beachName.textContent = mostVisitedBeach;

    // Add resort
    addResortForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const resortName = resortNameInput.value.trim();
        if (resortName) {
            resorts.push(resortName);
            renderResorts();
            resortNameInput.value = '';
        }
    });

    // Delete resort
    const renderResorts = () => {
        resortList.innerHTML = '';
        resorts.forEach((resort, index) => {
            const li = document.createElement('li');
            li.textContent = resort;
            const deleteButton = document.createElement('button');
            deleteButton.textContent = 'Delete';
            deleteButton.addEventListener('click', () => {
                resorts.splice(index, 1);
                renderResorts();
            });
            li.appendChild(deleteButton);
            resortList.appendChild(li);
        });
    };

    // Add review
    document.getElementById('submit-review').addEventListener('click', () => {
        const review = reviewText.value.trim();
        if (review) {
            reviews.push(review);
            renderReviews();
            reviewText.value = '';
        }
    });

    // Display reviews
    const renderReviews = () => {
        reviewList.innerHTML = '';
        reviews.forEach((review) => {
            const li = document.createElement('li');
            li.textContent = review;
            reviewList.appendChild(li);
        });
    };
});
