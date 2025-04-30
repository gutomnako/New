document.addEventListener("DOMContentLoaded", function () {
    const beaches = [
        {% for resort in resorts %}
            { 
                name: "{{ resort.name|escapejs }}", 
                url: "{% if resort.map_url %}{{ resort.map_url|escapejs }}{% else %}https://www.google.com/maps/embed?pb=...{% endif %}"
            }
            {% if not forloop.last %}, {% endif %}
        {% endfor %}
    ];

    const list = document.getElementById("beachList");
    const mapFrame = document.getElementById("mapFrame");

    beaches.forEach((beach) => {
        const li = document.createElement("li");
        li.textContent = beach.name;
        li.addEventListener("click", () => {
            mapFrame.src = beach.url;  // Directly use the URL
        });
        list.appendChild(li);
    });
});