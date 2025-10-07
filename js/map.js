function initImpactMap() { // <--- ESTE É O NOVO BLOCO QUE VOCÊ DEVE COLAR
    const projectsData = [
        { coordinates: [-23.58, -46.68], title: 'Projeto Raízes da Cantareira', description: '<strong>Ação:</strong> Reflorestamento<br><strong>Mudas Plantadas:</strong> 1.200<br><strong>Impacto:</strong> Recuperação de área degradada na Serra da Cantareira.', category: 'reflorestamento' },
        { coordinates: [-7.11, -37.28], title: 'Escolas Solares do Sertão', description: '<strong>Ação:</strong> Educação e Energia Limpa<br><strong>Alunos Impactados:</strong> 850<br><strong>Impacto:</strong> Workshops sobre sustentabilidade e instalação de painéis solares.', category: 'educacao' },
        { coordinates: [-23.86, -46.42], title: 'Estação de Monitoramento Ar Puro', description: '<strong>Ação:</strong> Monitoramento Climático<br><strong>Dados Coletados:</strong> Emissões de CO₂ e MP2.5<br><strong>Impacto:</strong> Relatórios públicos para pressionar por políticas ambientais.', category: 'monitoramento' },
        { coordinates: [-3.10, -60.02], title: 'Guardiões das Águas Amazônicas', description: '<strong>Ação:</strong> Proteção de Nascentes<br><strong>Comunidades Apoiadas:</strong> 15<br><strong>Impacto:</strong> Proteção de nascentes do Rio Negro e apoio a comunidades ribeirinhas.', category: 'protecao' },
        { coordinates: [-12.97, -38.50], title: 'Comunidade Energia Limpa', description: '<strong>Ação:</strong> Energia Renovável<br><strong>Famílias Atendidas:</strong> 50<br><strong>Impacto:</strong> Instalação de um microgerador de energia solar para uma comunidade local.', category: 'energia' }
    ];

    const map = L.map('map').setView([-15.0, -49.0], 4);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    const markersLayer = L.layerGroup().addTo(map); // Criamos uma camada para todos os marcadores

    // Função para criar os marcadores
    function createMarkers(filterCategory) {
        markersLayer.clearLayers(); // Limpa os marcadores existentes

        const filteredProjects = (filterCategory === 'all')
            ? projectsData
            : projectsData.filter(p => p.category === filterCategory);

        filteredProjects.forEach(project => {
            let iconHtml = '';
            switch (project.category) {
                case 'reflorestamento': iconHtml = '<i class="fas fa-leaf"></i>'; break;
                case 'educacao': iconHtml = '<i class="fas fa-book-open"></i>'; break;
                case 'monitoramento': iconHtml = '<i class="fas fa-chart-line"></i>'; break;
                case 'protecao': iconHtml = '<i class="fas fa-shield-alt"></i>'; break;
                case 'energia': iconHtml = '<i class="fas fa-solar-panel"></i>'; break;
                default: iconHtml = '<i class="fas fa-map-marker-alt"></i>';
            }

            const customIcon = L.divIcon({
                html: `<div class="marker-icon-container marker-icon-${project.category}">${iconHtml}</div>`,
                className: 'leaflet-div-icon',
                iconSize: [32, 32], iconAnchor: [16, 16], popupAnchor: [0, -16]
            });

            L.marker(project.coordinates, { icon: customIcon })
                .bindPopup(`<h3>${project.title}</h3><p>${project.description}</p>`)
                .addTo(markersLayer);
        });
    }

    // Lógica para os botões de filtro
    const filterButtons = document.querySelectorAll('.map-filter-btn');
    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            filterButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            const category = button.dataset.category;
            createMarkers(category);
        });
    });

    // Criar os marcadores iniciais (todos)
    createMarkers('all');
} // <--- A NOVA FUNÇÃO TERMINA AQUI

// A chamada da função continua a mesma
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('map')) {
        initImpactMap();
    }
});

// Chamada da função para inicializar o mapa quando a página carregar
document.addEventListener('DOMContentLoaded', () => {
    // Esta verificação garante que a função só rode se o elemento do mapa existir na página.
    if (document.getElementById('map')) {
        initImpactMap();
    }
});