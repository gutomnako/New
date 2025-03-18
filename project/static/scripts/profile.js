document.addEventListener("DOMContentLoaded", function () {
    const uploadInput = document.getElementById("uploadInput");
    const profilePicture = document.getElementById("profilePicture");

    // Load saved image from localStorage
    const savedImage = localStorage.getItem("profileImage");
    if (savedImage) {
        profilePicture.src = savedImage;
    }

    // Upload image and store it
    uploadInput.addEventListener("change", function (event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                const imageData = e.target.result;
                profilePicture.src = imageData;

                // Save image in localStorage
                localStorage.setItem("profileImage", imageData);
            };
            reader.readAsDataURL(file);
        }
    });
});
