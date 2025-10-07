/* ==========================================================================
   ARQUIVO DE SCRIPTS PRINCIPAIS - CLIMA AÇÃO
   ==========================================================================
   
   ÍNDICE DE CONTEÚDO:
   1. INICIALIZAÇÃO DE BIBLIOTECAS EXTERNAS (AOS)
   2. ANIMAÇÕES DA PÁGINA (GSAP)
   3. LÓGICA DO MENU MOBILE
   4. LÓGICA DA TIMELINE INTERATIVA (SWIPER)
   5. LÓGICA DO CONTADOR DE NÚMEROS
   6. LÓGICA DE ROLAGEM SUAVE (SMOOTH SCROLL)
   7. EVENT LISTENER PRINCIPAL (WINDOW.LOAD)

========================================================================== */


// 1. INICIALIZAÇÃO DA BIBLIOTECA AOS (ANIMATE ON SCROLL)
// Esta função ativa as animações de "fade" quando os elementos entram na tela.
function initAOS() {
    AOS.init({
      duration: 1000, // Duração da animação em milissegundos
      once: true,     // A animação acontece apenas uma vez
      offset: 100     // Distância em pixels do final da tela para disparar a animação
    });
  }
  
  // 2. ANIMAÇÃO DO TÍTULO PRINCIPAL (HERO) COM GSAP
  // Anima as palavras do título principal para que apareçam uma a uma.
  function animateHeroWords() {
    gsap.to(".word", {
      duration: 0.8,
      opacity: 1,
      y: 0,
      stagger: 0.15, // Atraso entre a animação de cada palavra
      ease: "power2.out"
    });
  }
  
  // 3. LÓGICA DO MENU MOBILE
  // Controla a abertura e o fechamento do menu em telas pequenas.
  function setupMobileMenu() {
    const menuBtn = document.getElementById('menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    const closeMenuBtn = document.getElementById('close-menu');
    const mobileMenuLinks = document.querySelectorAll('.mobile-menu-link');
  
    function toggleMenu() {
      mobileMenu.classList.toggle('hidden');
    }
  
    function closeMenu() {
      mobileMenu.classList.add('hidden');
    }
  
    // Adiciona os eventos aos botões
    menuBtn.addEventListener('click', toggleMenu);
    closeMenuBtn.addEventListener('click', closeMenu);
    
    // Adiciona evento para fechar o menu ao clicar em um link
    mobileMenuLinks.forEach(link => {
      link.addEventListener('click', closeMenu);
    });
  
    // Fecha o menu se o usuário clicar fora da área do menu
    mobileMenu.addEventListener('click', (e) => {
      if (e.target === mobileMenu) {
        closeMenu();
      }
    });
  }
  
  
  // 4. LÓGICA DA TIMELINE INTERATIVA (SWIPER)
  const timelineData = [
    { year: "1896", title: "Descoberta do Efeito Estufa", description: "Svante Arrhenius publica a primeira previsão quantitativa do aquecimento global...", image: "img/timeline/Estufa.jpg" },
    { year: "1958", title: "Medições Sistemáticas de CO₂", description: "Charles Keeling inicia medições contínuas de CO₂ no observatório de Mauna Loa...", image: "img/timeline/CO2.jpg" },
    { year: "1988", title: "Criação do IPCC", description: "O Painel Intergovernamental sobre Mudanças Climáticas é estabelecido pela ONU...", image: "img/timeline/ipcc.jpg" },
    { year: "1992", title: "Convenção do Clima (ECO-92)", description: "A Convenção-Quadro das Nações Unidas sobre Mudanças Climáticas é assinada na Rio-92...", image: "img/timeline/rio1992.jpg" },
    { year: "1997", title: "Protocolo de Kyoto", description: "Primeiro acordo internacional juridicamente vinculante para redução de emissões...", image: "img/timeline/kyoto.webp" },
    { year: "2007", title: "IPCC e Nobel da Paz", description: "O IPCC publica seu 4º Relatório de Avaliação e recebe o Prêmio Nobel da Paz...", image: "img/timeline/nobel2007.jpg" },
    { year: "2015", title: "Acordo de Paris", description: "195 países assinam o Acordo de Paris, comprometendo-se a limitar o aquecimento...", image: "img/timeline/paris2015.jpg" },
    { year: "2018", title: "Relatório 1,5°C do IPCC", description: "O IPCC alerta que temos apenas 12 anos para implementar mudanças...", image: "img/timeline/grafico.jpg" },
    { year: "2019", title: "Movimento Fridays for Future", description: "Greta Thunberg inspira milhões de jovens ao redor do mundo a protestarem...", image: "img/timeline/greta.jpg" },
    { year: "2021", title: "COP26 - Glasgow", description: "A COP26 estabelece o Pacto Climático de Glasgow, com compromissos para reduzir o uso de carvão...", image: "img/timeline/cop26.jpg" },
    { year: "2023", title: "Ano Mais Quente Registrado", description: "2023 se torna o ano mais quente já registrado na história...", image: "img/timeline/mapa2023.png" },
    { year: "AGORA", title: "É Hora de Agir!", description: "Estamos em um momento crítico. Cada ação conta. Junte-se a nós!", image: "img/timeline/agir.jpg" }
  ];
  
  // Função que cria os slides da timeline dinamicamente a partir dos dados acima
  function renderTimelineSlides() {
    const swiperWrapper = document.getElementById('timeline-swiper-wrapper');
    if (!swiperWrapper) return;
    swiperWrapper.innerHTML = '';
  
    timelineData.forEach((item, index) => {
      const slide = document.createElement('div');
      slide.classList.add('swiper-slide');
      if (item.year === 'AGORA') {
        slide.classList.add('special');
      }
  
      slide.innerHTML = `
        <div class="timeline-slide-year">${item.year}</div>
        <div class="timeline-card" data-aos="fade-up" data-aos-delay="${index * 100}">
          <img src="${item.image}" alt="${item.title}" class="timeline-card-image">
          <div class="timeline-card-title">${item.title}</div>
          <div class="timeline-card-description">${item.description}</div>
        </div>
      `;
      swiperWrapper.appendChild(slide);
    });
  }
  
  // Função que inicializa o Swiper com as configurações desejadas
  function initSwiper() {
    renderTimelineSlides(); // Primeiro, cria os slides no HTML
  
    new Swiper('.swiper-container', {
      slidesPerView: 'auto',
      spaceBetween: 30,
      centeredSlides: true,
      grabCursor: true,
      loop: false,
      pagination: {
        el: '.swiper-pagination',
        clickable: true,
      },
      navigation: {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev',
      },
      breakpoints: {
        768: {
          slidesPerView: 3,
          spaceBetween: 40,
          centeredSlides: false,
        },
        1024: {
          slidesPerView: 4,
          spaceBetween: 50,
          centeredSlides: false,
        }
      }
    });
  }
  
  // 5. LÓGICA DO CONTADOR DE NÚMEROS
  // Anima os números da seção "Nosso Impacto" para que contem do zero até o valor final.
  function animateCounters() {
    const counters = document.querySelectorAll('.animate-number');
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const counter = entry.target;
          const target = parseInt(counter.dataset.value);
          const suffix = counter.dataset.suffix || '';
          let current = 0;
          const increment = target / 50;
          
          const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
              current = target;
              clearInterval(timer);
            }
            counter.textContent = Math.floor(current) + suffix;
          }, 40);
          observer.unobserve(counter);
        }
      });
    }, { threshold: 0.5 });
  
    counters.forEach(counter => {
      observer.observe(counter);
    });
  }
  
  // 6. LÓGICA DE ROLAGEM SUAVE (SMOOTH SCROLL)
  // Faz com que os cliques em links internos (ex: #contato) rolem a página suavemente.
  function setupSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
          target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      });
    });
  }
  
  
  // 7. EVENT LISTENER PRINCIPAL (WINDOW.LOAD)
  // Este é o ponto de partida. Ele espera a página inteira carregar (incluindo CSS e imagens)
  // e então chama todas as funções de inicialização na ordem correta.
  window.addEventListener('load', () => {
    initAOS();
    animateHeroWords();
    setupMobileMenu();
    initSwiper();
    animateCounters();
    setupSmoothScroll();
  });