document.addEventListener('DOMContentLoaded', function () {
    // Variables globales
    let figurines = [];
    let allTags = new Set();
    let activeFilters = new Set();

    // Charge les données des figurines
    fetch('data/collection.json')
        .then(response => response.json())
        .then(data => {
            figurines = data.figurines;

            // Collecte tous les tags uniques
            figurines.forEach(figurine => {
                figurine.tags.forEach(tag => allTags.add(tag));
            });

            // Génère les boutons de filtrage par tag
            generateTagButtons();

            // Affiche toutes les figurines
            displayFigurines(figurines);

            // Configure la recherche
            setupSearch();
        });

    // Génère les boutons de tags pour le filtrage
    function generateTagButtons() {
        const tagsContainer = document.getElementById('tags-container');

        allTags.forEach(tag => {
            const button = document.createElement('button');
            button.className = 'tag-btn';
            button.textContent = tag;
            button.addEventListener('click', () => toggleTagFilter(button, tag));
            tagsContainer.appendChild(button);
        });
    }

    // Active/désactive un filtre de tag
    function toggleTagFilter(button, tag) {
        button.classList.toggle('active');

        if (activeFilters.has(tag)) {
            activeFilters.delete(tag);
        } else {
            activeFilters.add(tag);
        }

        applyFilters();
    }

    // Configure la recherche par texte
    function setupSearch() {
        const searchInput = document.getElementById('search-input');

        searchInput.addEventListener('input', applyFilters);
    }

    // Applique tous les filtres actifs
    function applyFilters() {
        const searchText = document.getElementById('search-input').value.toLowerCase();

        const filteredFigurines = figurines.filter(figurine => {
            // Filtre par texte de recherche
            const matchesSearch = figurine.name.toLowerCase().includes(searchText);

            // Si aucun tag actif, n'applique pas de filtre par tag
            if (activeFilters.size === 0) {
                return matchesSearch;
            }

            // Vérifie si la figurine a au moins un des tags actifs
            const hasActiveTag = [...activeFilters].some(tag =>
                figurine.tags.includes(tag)
            );

            return matchesSearch && hasActiveTag;
        });

        displayFigurines(filteredFigurines);
    }

    // Affiche les figurines sur la page
    function displayFigurines(figurinesToDisplay) {
        const container = document.getElementById('figurines-container');
        container.innerHTML = '';

        figurinesToDisplay.forEach(figurine => {
            const card = document.createElement('div');
            card.className = 'figurine-card';

            // Crée le lien vers l'image complète avec lightbox
            const link = document.createElement('a');
            link.href = figurine.fullImage;
            link.setAttribute('data-lightbox', 'figurines');
            link.setAttribute('data-title', figurine.name);

            // Ajoute l'image miniature
            const img = document.createElement('img');
            img.src = figurine.thumbnail;
            img.alt = figurine.name;
            link.appendChild(img);

            // Ajoute les infos de la figurine
            const info = document.createElement('div');
            info.className = 'figurine-info';

            const name = document.createElement('h3');
            name.textContent = figurine.name;
            info.appendChild(name);

            // Ajoute les tags
            const tags = document.createElement('div');
            tags.className = 'figurine-tags';

            figurine.tags.forEach(tag => {
                const tagSpan = document.createElement('span');
                tagSpan.className = 'figurine-tag';
                tagSpan.textContent = tag;
                tags.appendChild(tagSpan);
            });

            info.appendChild(tags);

            // Assemble la carte
            card.appendChild(link);
            card.appendChild(info);
            container.appendChild(card);
        });
    }
});