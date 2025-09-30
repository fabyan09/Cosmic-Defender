// Cosmic Defender Leaderboard JavaScript

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
            loadingElement.style.display = 'block';
            errorElement.style.display = 'none';

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

            loadingElement.style.display = 'none';
        } catch (error) {
            console.error('Error loading scores:', error);
            loadingElement.style.display = 'none';
            errorElement.style.display = 'block';

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
    }

    setFilter(mode) {
        this.currentFilter = mode;

        // Update filter buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-mode="${mode}"]`).classList.add('active');

        // Filter scores
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
            clearBtn.classList.add('visible');
        } else {
            clearBtn.classList.remove('visible');
        }
    }

    updateStats() {
        const uniquePlayers = new Set(this.scores.map(score => score.name)).size;
        const highestScore = Math.max(...this.scores.map(score => score.score), 0);
        const highestWave = Math.max(...this.scores.map(score => score.wave), 0);

        document.getElementById('total-players').textContent = uniquePlayers.toLocaleString();
        document.getElementById('highest-score').textContent = highestScore.toLocaleString();
        document.getElementById('highest-wave').textContent = highestWave;

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

            element.textContent = currentValue.toLocaleString();

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
                <td colspan="6" style="text-align: center; padding: 40px; color: #666;">
                    ${message}
                </td>
            `;
            tbody.appendChild(row);
            return;
        }

        scoresToShow.forEach((score, index) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="rank">${this.getRankDisplay(index + 1)}</td>
                <td class="name">${this.escapeHtml(score.name)}</td>
                <td class="score">${score.score.toLocaleString()}</td>
                <td>${score.wave}</td>
                <td><span class="mode-${score.mode}">${score.mode.toUpperCase()}</span></td>
                <td>${this.formatDate(score.date)}</td>
            `;

            // Add special effects for top 3
            if (index < 3) {
                row.classList.add(`rank-${index + 1}`);
            }

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

    getRankDisplay(rank) {
        const medals = ['🥇', '🥈', '🥉'];
        if (rank <= 3) {
            return medals[rank - 1];
        }
        return rank;
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

// Add some cosmic effects
function createCosmicEffects() {
    // Add twinkling effect to stats
    const statNumbers = document.querySelectorAll('.stat-number');
    statNumbers.forEach(stat => {
        setInterval(() => {
            stat.style.textShadow = `0 0 ${Math.random() * 20 + 10}px #00ffff`;
        }, 2000 + Math.random() * 3000);
    });

    // Add subtle glow effects
    const title = document.querySelector('.title');
    setInterval(() => {
        const intensity = Math.random() * 40 + 20;
        title.style.textShadow = `0 0 ${intensity}px #00ffff, 0 0 ${intensity * 2}px #00ffff`;
    }, 3000);
}

// Start cosmic effects after a short delay
setTimeout(createCosmicEffects, 1000);