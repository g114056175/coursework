// ============================
// Particles Background
// ============================
function createParticles() {
  const container = document.getElementById('particles');
  const count = 40;
  for (let i = 0; i < count; i++) {
    const particle = document.createElement('div');
    particle.classList.add('particle');
    particle.style.left = Math.random() * 100 + '%';
    particle.style.animationDuration = (Math.random() * 15 + 10) + 's';
    particle.style.animationDelay = (Math.random() * 10) + 's';
    particle.style.width = particle.style.height = (Math.random() * 3 + 1) + 'px';
    const colors = ['#7c5cfc', '#00d4aa', '#9070ff', '#00f0c0'];
    particle.style.background = colors[Math.floor(Math.random() * colors.length)];
    container.appendChild(particle);
  }
}

// ============================
// Typewriter Effect
// ============================
function typewriter() {
  const el = document.getElementById('typewriter');
  const phrases = [
    'Creative Developer',
    'Problem Solver',
    'Tech Enthusiast',
    'UI/UX Lover',
    'Lifelong Learner'
  ];
  let phraseIndex = 0;
  let charIndex = 0;
  let isDeleting = false;
  let delay = 100;

  function tick() {
    const current = phrases[phraseIndex];

    if (isDeleting) {
      el.textContent = current.substring(0, charIndex - 1);
      charIndex--;
      delay = 50;
    } else {
      el.textContent = current.substring(0, charIndex + 1);
      charIndex++;
      delay = 100;
    }

    if (!isDeleting && charIndex === current.length) {
      delay = 2000;
      isDeleting = true;
    } else if (isDeleting && charIndex === 0) {
      isDeleting = false;
      phraseIndex = (phraseIndex + 1) % phrases.length;
      delay = 500;
    }

    setTimeout(tick, delay);
  }

  tick();
}

// ============================
// Navbar Scroll Effect
// ============================
function initNavbar() {
  const nav = document.getElementById('nav');
  const navToggle = document.getElementById('navToggle');
  const navLinks = document.querySelector('.nav-links');
  const links = document.querySelectorAll('.nav-link');

  window.addEventListener('scroll', () => {
    nav.classList.toggle('scrolled', window.scrollY > 50);
  });

  // Mobile toggle
  navToggle.addEventListener('click', () => {
    navLinks.classList.toggle('open');
  });

  // Close mobile menu on link click
  links.forEach(link => {
    link.addEventListener('click', () => {
      navLinks.classList.remove('open');
    });
  });

  // Active link on scroll
  const sections = document.querySelectorAll('section[id]');
  window.addEventListener('scroll', () => {
    const scrollY = window.scrollY + 200;
    sections.forEach(section => {
      const top = section.offsetTop;
      const height = section.offsetHeight;
      const id = section.getAttribute('id');
      const link = document.querySelector(`.nav-link[href="#${id}"]`);
      if (link) {
        if (scrollY >= top && scrollY < top + height) {
          links.forEach(l => l.classList.remove('active'));
          link.classList.add('active');
        }
      }
    });
  });
}

// ============================
// Scroll Reveal Animation
// ============================
function initReveal() {
  const revealEls = document.querySelectorAll(
    '.about-grid, .skill-card, .project-card, .contact-wrapper, .card-glass'
  );

  revealEls.forEach(el => el.classList.add('reveal'));

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  }, { threshold: 0.1 });

  revealEls.forEach(el => observer.observe(el));
}

// ============================
// Counter Animation
// ============================
function initCounters() {
  const counters = document.querySelectorAll('.stat-number');

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const target = +entry.target.getAttribute('data-target');
        let current = 0;
        const step = Math.ceil(target / 40);
        const timer = setInterval(() => {
          current += step;
          if (current >= target) {
            current = target;
            clearInterval(timer);
          }
          entry.target.textContent = current;
        }, 40);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });

  counters.forEach(c => observer.observe(c));
}

// ============================
// Contact Form
// ============================
function initContactForm() {
  const form = document.getElementById('contactForm');
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const btn = form.querySelector('.btn-submit span');
    btn.textContent = 'Message Sent! ✓';
    btn.style.color = '#00d4aa';
    setTimeout(() => {
      btn.textContent = 'Send Message';
      btn.style.color = '';
      form.reset();
    }, 3000);
  });
}

// ============================
// Init
// ============================
document.addEventListener('DOMContentLoaded', () => {
  createParticles();
  typewriter();
  initNavbar();
  initReveal();
  initCounters();
  initContactForm();
});
