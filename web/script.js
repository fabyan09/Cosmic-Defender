// Cosmic Defender Leaderboard JavaScript - Modern Version

class CosmicLeaderboard {
    constructor() {
        this.scores = [];
        this.filteredScores = [];
        this.currentFilter = 'all';
        this.searchTerm = '';
        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.loadScores();
        this.updateStats();
        this.renderLeaderboard();
    }

    setupEventListeners() {
        // Filter buttons
        const filterButtons = document.querySelectorAll('.filter-btn');
        filterButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const mode = e.target.dataset.mode;
                this.setFilter(mode);

                // Update active state with modern styling
                filterButtons.forEach(b => {
                    b.classList.remove('bg-gradient-to-r', 'from-cyan-500', 'to-blue-600',
                                      'shadow-cyan-500/50', 'text-white', 'active');
                    b.classList.add('glass-effect', 'text-gray-300');
                });

                e.target.classList.remove('glass-effect', 'text-gray-300');
                e.target.classList.add('bg-gradient-to-r', 'from-cyan-500', 'to-blue-600',
                                      'shadow-cyan-500/50', 'text-white', 'active');
            });
        });

        // Search functionality
        const searchInput = document.getElementById('search-input');
        const clearBtn = document.getElementById('clear-search');

        searchInput.addEventListener('input', (e) => {
            this.searchTerm = e.target.value.toLowerCase();
            this.updateClearButton();
            this.renderLeaderboard();
        });

        clearBtn.addEventListener('click', () => {
            searchInput.value = '';
            this.searchTerm = '';
            this.updateClearButton();
            this.renderLeaderboard();
        });
    }

    async loadScores() {
        const loadingElement = document.getElementById('loading');
        const errorElement = document.getElementById('error');

        try {
            loadingElement.classList.remove('hidden');
            errorElement.classList.add('hidden');

            // Try to load from GitHub Pages first, then fallback to local file
            let response;
            try {
                // GitHub raw file URL for real-time updates
                response = await fetch('https://raw.githubusercontent.com/fabyan09/cosmic-defender-leaderboard/main/cosmic_defender_leaderboard.json');
            } catch (githubError) {
                try {
                    // Fallback to GitHub Pages
                    response = await fetch('https://fabyan09.github.io/cosmic-defender-leaderboard/cosmic_defender_leaderboard.json');
                } catch (pagesError) {
                    // Fallback to local file for testing
                    response = await fetch('./cosmic_defender_leaderboard.json');
                }
            }

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.scores = data.scores || [];

            // Update last updated time
            const lastUpdated = new Date(data.last_updated).toLocaleString('fr-FR');
            document.getElementById('last-updated').textContent = lastUpdated;

            loadingElement.classList.add('hidden');
        } catch (error) {
            console.error('Error loading scores:', error);
            loadingElement.classList.add('hidden');
            errorElement.classList.remove('hidden');

            // Load demo data for demonstration
            this.loadDemoData();
        }
    }

    loadDemoData() {
        // Demo data for testing
        this.scores = [
            { name: "COSMIC_ACE", score: 15420, wave: 25, mode: "infinite", date: "2024-01-15 14:30" },
            { name: "STAR_WARRIOR", score: 12890, wave: 10, mode: "normal", date: "2024-01-15 13:45" },
            { name: "GALACTIC_HERO", score: 11750, wave: 22, mode: "infinite", date: "2024-01-15 12:20" },
            { name: "SPACE_COMMANDER", score: 9340, wave: 10, mode: "normal", date: "2024-01-14 19:15" },
            { name: "NEBULA_FIGHTER", score: 8760, wave: 18, mode: "infinite", date: "2024-01-14 16:45" }
        ];

        // Update stats and render with demo data
        this.updateStats();
        this.renderLeaderboard();
    }

    setFilter(mode) {
        this.currentFilter = mode;
        this.applyFilters();
        this.renderLeaderboard();
    }

    applyFilters() {
        let filtered = [...this.scores];

        // Apply mode filter
        if (this.currentFilter !== 'all') {
            filtered = filtered.filter(score => score.mode === this.currentFilter);
        }

        // Apply search filter
        if (this.searchTerm) {
            filtered = filtered.filter(score =>
                score.name.toLowerCase().includes(this.searchTerm)
            );
        }

        this.filteredScores = filtered;
    }

    updateClearButton() {
        const clearBtn = document.getElementById('clear-search');
        if (this.searchTerm) {
            clearBtn.classList.remove('hidden');
            clearBtn.classList.add('flex');
        } else {
            clearBtn.classList.add('hidden');
            clearBtn.classList.remove('flex');
        }
    }

    updateStats() {
        const uniquePlayers = new Set(this.scores.map(score => score.name)).size;
        const highestScore = Math.max(...this.scores.map(score => score.score), 0);
        const highestWave = Math.max(...this.scores.map(score => score.wave), 0);

        // Animate numbers
        this.animateNumber('total-players', uniquePlayers);
        this.animateNumber('highest-score', highestScore);
        this.animateNumber('highest-wave', highestWave);
    }

    animateNumber(elementId, targetValue) {
        const element = document.getElementById(elementId);
        const duration = 2000; // 2 seconds
        const startTime = Date.now();
        const startValue = 0;

        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);

            // Easing function
            const easeOutCubic = 1 - Math.pow(1 - progress, 3);
            const currentValue = Math.floor(startValue + (targetValue - startValue) * easeOutCubic);

            element.textContent = currentValue.toLocaleString('fr-FR');

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        animate();
    }

    renderLeaderboard() {
        const tbody = document.getElementById('leaderboard-body');
        tbody.innerHTML = '';

        // Apply filters before rendering
        this.applyFilters();
        const scoresToShow = this.filteredScores;

        if (scoresToShow.length === 0) {
            const row = document.createElement('tr');
            let message = 'Aucun score trouvé';
            if (this.searchTerm) {
                message += ` pour "${this.searchTerm}"`;
            }
            if (this.currentFilter !== 'all') {
                message += ` en mode ${this.currentFilter.toUpperCase()}`;
            }

            row.innerHTML = `
                <td colspan="6" class="text-center py-12 text-gray-400">
                    <div class="text-4xl mb-2">🔍</div>
                    ${message}
                </td>
            `;
            tbody.appendChild(row);
            return;
        }

        scoresToShow.forEach((score, index) => {
            const row = document.createElement('tr');
            row.className = 'hover:bg-white/5 transition-colors duration-200';

            // Special styling for top 3
            let rankDisplay = index + 1;
            let rankClass = 'text-gray-400';
            if (index === 0) {
                rankDisplay = '🥇';
                row.className += ' bg-gradient-to-r from-yellow-500/10 to-transparent';
            } else if (index === 1) {
                rankDisplay = '🥈';
                row.className += ' bg-gradient-to-r from-gray-400/10 to-transparent';
            } else if (index === 2) {
                rankDisplay = '🥉';
                row.className += ' bg-gradient-to-r from-orange-600/10 to-transparent';
            }

            // Mode badge styling
            let modeBadge = '';
            if (score.mode === 'normal') {
                modeBadge = `<span class="inline-block px-3 py-1 rounded-full text-xs font-semibold bg-yellow-500/20 text-yellow-300">CAMPAGNE</span>`;
            } else {
                modeBadge = `<span class="inline-block px-3 py-1 rounded-full text-xs font-semibold bg-purple-500/20 text-purple-300">INFINI</span>`;
            }

            row.innerHTML = `
                <td class="px-6 py-4 text-center text-2xl">${rankDisplay}</td>
                <td class="px-6 py-4 text-left font-bold text-cyan-400">${this.escapeHtml(score.name)}</td>
                <td class="px-6 py-4 text-center font-bold text-green-400">${score.score.toLocaleString('fr-FR')}</td>
                <td class="px-6 py-4 text-center text-blue-300">${score.wave}</td>
                <td class="px-6 py-4 text-center">${modeBadge}</td>
                <td class="px-6 py-4 text-center text-gray-400 text-sm">${this.formatDate(score.date)}</td>
            `;

            tbody.appendChild(row);

            // Animate row appearance
            setTimeout(() => {
                row.style.opacity = '0';
                row.style.transform = 'translateY(20px)';
                row.style.transition = 'opacity 0.5s ease, transform 0.5s ease';

                requestAnimationFrame(() => {
                    row.style.opacity = '1';
                    row.style.transform = 'translateY(0)';
                });
            }, index * 50);
        });
    }

    formatDate(dateString) {
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString('fr-FR', {
                day: '2-digit',
                month: '2-digit',
                year: '2-digit'
            });
        } catch (error) {
            return dateString.split(' ')[0] || dateString;
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    new CosmicLeaderboard();
});