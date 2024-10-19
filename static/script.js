function fetchNews() {
    fetch('/news')
        .then(response => response.json())
        .then(data => {
            const newsContainer = document.getElementById('news-container');
            newsContainer.innerHTML = '';
            data.forEach(article => {
                const newsItem = document.createElement('div');
                newsItem.className = 'news-item';
                newsItem.innerHTML = `
                    <h3>
                        <a href="${article.link}" target="_blank">${article.title}</a>
                    </h3>
                    <p>${article.summary}</p>
                    <button onclick="showMetaDescription('${article.title}', \`${article.description}\`)">Show Description</button>
                    <div class="category-buttons">
                        <button class="category-btn">${article.category}</button>
                        <button class="subcategory-btn">${article.subcategory}</button>
                    </div>
                `;
                newsContainer.appendChild(newsItem);

                // Show notification for new headlines
                showNotification(article.title);
            });
        });
}

function showMetaDescription(title, description) {
    alert(`Title: ${title}\n\nDescription:\n${description}`);
}

function showNotification(title) {
    const notification = document.getElementById('notification');
    notification.innerText = title;
    notification.classList.remove('hidden');
    setTimeout(() => {
        notification.classList.add('hidden');
    }, 5000);
}
function filterNews(subcategory) {
    fetch(`/news?subcategory=${subcategory}`)
        .then(response => response.json())
        .then(data => {
            const newsContainer = document.getElementById('news-container');
            newsContainer.innerHTML = ''; // Clear current news

            data.forEach(article => {
                const newsItem = document.createElement('div');
                newsItem.className = 'news-item';
                newsItem.innerHTML = `
                    <h3>
                        <a href="${article.link}" target="_blank">${article.title}</a>
                    </h3>
                    <p>${article.summary}</p>
                    <button onclick="showMetaDescription('${article.title}', \`${article.description}\`)">Show Description</button>
                    <div class="category-buttons">
                        <button class="category-btn">${article.category}</button>
                        <button class="subcategory-btn" onclick="filterNews('${article.subcategory}')">${article.subcategory}</button>
                    </div>
                `;
                newsContainer.appendChild(newsItem);
            });
        });
}


// Fetch news every 5 seconds
setInterval(fetchNews, 5000);
fetchNews();
