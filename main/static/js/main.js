// LetsPlay - Django JavaScript

document.addEventListener('DOMContentLoaded', function() {
  
  // ==================== Mobile Menu Toggle ====================
  const mobileMenuBtn = document.getElementById('mobileMenuBtn');
  const mobileMenu = document.getElementById('mobileMenu');
  const menuIcon = mobileMenuBtn?.querySelector('.menu-icon');
  const closeIcon = mobileMenuBtn?.querySelector('.close-icon');

  if (mobileMenuBtn && mobileMenu) {
    mobileMenuBtn.addEventListener('click', function() {
      mobileMenu.classList.toggle('active');
      menuIcon?.classList.toggle('hidden');
      closeIcon?.classList.toggle('hidden');
    });

    // Close mobile menu when clicking on a link
    const mobileNavLinks = mobileMenu.querySelectorAll('.nav-link');
    mobileNavLinks.forEach(link => {
      link.addEventListener('click', function() {
        mobileMenu.classList.remove('active');
        menuIcon?.classList.remove('hidden');
        closeIcon?.classList.add('hidden');
      });
    });
  }

  // ==================== Console Selector (Home Page) ====================
  const consoleBtns = document.querySelectorAll('.console-btn');
  
  consoleBtns.forEach(btn => {
    btn.addEventListener('click', function() {
      // Remove active class from all buttons
      consoleBtns.forEach(b => b.classList.remove('active'));
      // Add active class to clicked button
      this.classList.add('active');
    });
  });

  // ==================== Smooth Scroll for Anchor Links ====================
  const anchorLinks = document.querySelectorAll('a[href^="#"]');
  
  anchorLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      const href = this.getAttribute('href');
      
      // Only prevent default if it's not just '#'
      if (href && href !== '#') {
        const target = document.querySelector(href);
        
        if (target) {
          e.preventDefault();
          const headerHeight = document.querySelector('.header')?.offsetHeight || 0;
          const targetPosition = target.offsetTop - headerHeight - 20;
          
          window.scrollTo({
            top: targetPosition,
            behavior: 'smooth'
          });
        }
      }
    });
  });

  // ==================== Scroll-Based Header Shadow ====================
  const header = document.querySelector('.header');
  
  if (header) {
    window.addEventListener('scroll', function() {
      if (window.scrollY > 50) {
        header.style.boxShadow = '0 10px 15px -3px rgba(0, 0, 0, 0.3)';
      } else {
        header.style.boxShadow = 'none';
      }
    });
  }

  // ==================== Intersection Observer for Fade-in Animations ====================
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };

  const observerCallback = (entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
        observer.unobserve(entry.target);
      }
    });
  };

  const observer = new IntersectionObserver(observerCallback, observerOptions);

  // Observe cards and sections
  const animatedElements = document.querySelectorAll(
    '.stat-card, .feature-card, .product-card, .review-card, .advantage-card, .team-card'
  );

  animatedElements.forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(el);
  });

  // ==================== Category Filter (Catalog Page) ====================
  const categoryFilters = document.getElementById('categoryFilters');
  
  if (categoryFilters) {
    const filterBtns = categoryFilters.querySelectorAll('.filter-btn');
    const products = document.querySelectorAll('.product-card');

    filterBtns.forEach(btn => {
      btn.addEventListener('click', function() {
        const category = this.dataset.category;
        
        // Update active button
        filterBtns.forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        
        // Filter products with fade animation
        products.forEach(product => {
          const productCategory = product.dataset.category;
          
          if (category === 'all' || productCategory === category) {
            product.style.display = 'block';
            setTimeout(() => {
              product.style.opacity = '1';
              product.style.transform = 'translateY(0)';
            }, 10);
          } else {
            product.style.opacity = '0';
            product.style.transform = 'translateY(30px)';
            setTimeout(() => {
              product.style.display = 'none';
            }, 300);
          }
        });
      });
    });
  }

  // ==================== Review Actions (Reviews Page) ====================
  const reviewActions = document.querySelectorAll('.review-action');
  
  reviewActions.forEach(action => {
    action.addEventListener('click', function() {
      // Add ripple effect
      this.style.transform = 'scale(0.95)';
      setTimeout(() => {
        this.style.transform = 'scale(1)';
      }, 100);
    });
  });

  // ==================== Form Validation (if you add forms later) ====================
  const forms = document.querySelectorAll('form');
  
  forms.forEach(form => {
    form.addEventListener('submit', function(e) {
      const requiredFields = form.querySelectorAll('[required]');
      let isValid = true;
      
      requiredFields.forEach(field => {
        if (!field.value.trim()) {
          isValid = false;
          field.style.borderColor = '#d4183d';
          
          // Reset border color after 2 seconds
          setTimeout(() => {
            field.style.borderColor = '';
          }, 2000);
        }
      });
      
      if (!isValid) {
        e.preventDefault();
        alert('Пожалуйста, заполните все обязательные поля');
      }
    });
  });

  // ==================== Load More Button (optional) ====================
  const loadMoreBtns = document.querySelectorAll('.btn-secondary');
  
  loadMoreBtns.forEach(btn => {
    if (btn.textContent.includes('Показать')) {
      btn.addEventListener('click', function() {
        // This is a placeholder - implement your load more logic here
        this.textContent = 'Загрузка...';
        this.disabled = true;
        
        setTimeout(() => {
          this.textContent = 'Показать ещё';
          this.disabled = false;
        }, 1000);
      });
    }
  });

  // ==================== Add to Cart (placeholder for future implementation) ====================
  window.addToCart = function(productId) {
    console.log('Adding product to cart:', productId);
    // Implement your cart logic here
    alert('Товар добавлен в корзину!');
  };

  // ==================== Console Log for Development ====================
  console.log('LetsPlay JavaScript loaded successfully!');
  console.log('Current page:', document.title);
});

// ==================== Utility Functions ====================

// Format price
function formatPrice(price) {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    minimumFractionDigits: 0
  }).format(price);
}

// Debounce function for performance
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Throttle function for scroll events
function throttle(func, limit) {
  let inThrottle;
  return function() {
    const args = arguments;
    const context = this;
    if (!inThrottle) {
      func.apply(context, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}
document.addEventListener('DOMContentLoaded', () => {
  const button = document.getElementById('load-more');
  const container = document.getElementById('product-list');
  let offset = document.querySelectorAll('.product-card').length;

  if (button) {
    button.addEventListener('click', () => {
      fetch(`/catalog/load_more/?offset=${offset}`)
        .then(res => res.json())
        .then(data => {
          if (data.products.length === 0) {
            button.style.display = 'none';
            return;
          }

          data.products.forEach(p => {
            const card = document.createElement('div');
            card.classList.add('product-card');
            card.innerHTML = `
              <img src="${p.image}" alt="${p.name}">
              <h3>${p.name}</h3>
              <p class="price">${p.price} ₽</p>
              <a href="#" class="btn">Подробнее</a>
            `;
            container.appendChild(card);
          });

          offset += data.products.length;
        })
        .catch(err => console.error('Ошибка загрузки:', err));
    });
  }
});