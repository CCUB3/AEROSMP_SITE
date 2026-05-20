document.addEventListener("DOMContentLoaded", function() {

    // 1. АНИМАЦИЯ ШАПКИ
    const header = document.querySelector(".main-header");
    if (header) {
        window.addEventListener("scroll", function() {
            if (window.scrollY > 40) {
                header.classList.add("scrolled");
            } else {
                header.classList.remove("scrolled");
            }
        });
    }

    // 2. ПЛАВНЫЙ СКРОЛЛ С ИНЕРЦИЕЙ ТОЛЬКО ДЛЯ ПК
    if (window.innerWidth > 1024) {
        let currentY = window.scrollY;
        let targetY = window.scrollY;
        const ease = 0.08;

        function animateScroll() {
            if (Math.abs(targetY - currentY) > 0.5) {
                currentY += (targetY - currentY) * ease;
                window.scrollTo(0, currentY);
            }
            requestAnimationFrame(animateScroll);
        }

        requestAnimationFrame(animateScroll);

        window.addEventListener('wheel', (e) => {
            e.preventDefault();
            targetY += e.deltaY * 1.5;
            const maxScroll = document.body.scrollHeight - window.innerHeight;
            targetY = Math.max(0, targetY);
            targetY = Math.min(maxScroll, targetY);
        }, { passive: false });
    }

    // 3. УВЕЛИЧЕНИЕ КАРТИНОК ПО КЛИКУ
    const modal = document.getElementById("image-modal");
    const modalImg = document.getElementById("modal-img");
    const closeBtn = document.querySelector(".modal-close");
    const imageCards = document.querySelectorAll(".img-card, .hero-image");

    imageCards.forEach(card => {
        card.addEventListener("click", function() {
            if (!modal || !modalImg) return;
            const bgImage = window.getComputedStyle(this).backgroundImage;
            const imageUrl = bgImage.replace(/^url\(["']?/, '').replace(/["']?\)$/, '');

            if (imageUrl && imageUrl !== 'none') {
                modalImg.src = imageUrl;
                modal.classList.add("show");
            }
        });
    });

    function closeModal() {
        if (!modal) return;
        modal.classList.remove("show");
        setTimeout(() => {
            if (!modal.classList.contains("show") && modalImg) {
                modalImg.src = "";
            }
        }, 300);
    }

    if (closeBtn) closeBtn.addEventListener('click', closeModal);

    if (modal) {
        modal.addEventListener("click", (e) => {
            if (e.target === modal) closeModal();
        });
    }

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && modal && modal.classList.contains("show")) {
            closeModal();
        }
    });

    // 4. ЗАГРУЗКА НОВОСТЕЙ С СЕРВЕРА
    async function loadNews() {
        try {
            const response = await fetch('./api/news');
            if (!response.ok) throw new Error('Сервер не отвечает');

            const newsData = await response.json();
            const newsGrid = document.querySelector('.news-grid');

            if (!newsGrid) return;

            newsGrid.innerHTML = '';

            newsData.forEach(item => {
                const card = document.createElement('div');
                card.className = 'news-card';
                card.innerHTML = `
                    <div class="news-date">${item.date}</div>
                    <h3>${item.title}</h3>
                    <p>${item.text}</p>
                `;
                newsGrid.appendChild(card);
            });
        } catch (error) {
            console.error('Ошибка загрузки новостей:', error);
        }
    }

    loadNews();

    // прелоадер
    window.addEventListener('load', function() {
        const preloader = document.getElementById('preloader');
        setTimeout(function() {
            preloader.classList.add('hidden');
        }, 500);
    });


    const secretTrigger = document.getElementById('secretAdmin');

    if (secretTrigger) {
        let clickCount = 0;

        secretTrigger.addEventListener('click', () => {
            clickCount++;
            console.log(`[SUS]: ${clickCount}/10`);

            if (clickCount >= 10) {
                clickCount = 0;

                setTimeout(async () => {
                    const userPassword = prompt('AERO_SUS: Ведай:');

                    if (userPassword) {
                        try {
                            const response = await fetch('./api/check_password', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ password: userPassword })
                            });

                            if (response.ok) {
                                const data = await response.json();
                                sessionStorage.setItem('aero_admin_token', data.token);
                                window.open('admin.html', '_blank');
                            } else {
                                alert('AERO_SUS: Пошел нахуй');
                            }
                        } catch (err) {
                            console.error(err);
                            alert('AERO_SUS');
                        }
                    }
                }, 10);
            }
        });
    }
});