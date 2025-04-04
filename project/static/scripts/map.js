function loadMap(beachName) {
    const maps = {
        "FMB Beach Resort": "https://www.google.com/maps/embed?...", // Replace with actual URLs
        "Talaonga Beach": "https://www.google.com/maps/embed?...",
        "Rawis Beach": "https://www.google.com/maps/embed?...",
        "Rizal Beach": "https://www.google.com/maps/embed?...",
        "Balading Beach Resort": "https://www.google.com/maps/embed?..."
    };
    document.getElementById("mapFrame").src = maps[beachName] || "";
}