/**
 * XPilot Application Frontend JavaScript
 */

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash-message');
    if (flashMessages.length > 0) {
        setTimeout(function() {
            flashMessages.forEach(message => {
                message.style.opacity = '0';
                message.style.transition = 'opacity 0.5s ease';
                setTimeout(() => {
                    message.remove();
                }, 500);
            });
        }, 5000);
    }

    // Character counter for post composition
    const postTextArea = document.getElementById('post-content');
    const charCounter = document.getElementById('char-counter');
    if (postTextArea && charCounter) {
        const maxLength = 280;

        postTextArea.addEventListener('input', function() {
            const remaining = maxLength - this.value.length;
            charCounter.textContent = remaining;

            if (remaining < 0) {
                charCounter.classList.add('text-danger');
                document.getElementById('post-submit').disabled = true;
            } else {
                charCounter.classList.remove('text-danger');
                document.getElementById('post-submit').disabled = false;
            }
        });
    }

    // Toggle mobile navigation
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    const navLinks = document.querySelector('.nav-links');

    if (mobileMenuToggle && navLinks) {
        mobileMenuToggle.addEventListener('click', function() {
            navLinks.classList.toggle('active');
        });
    }

    // Mobile navigation toggle
    setupMobileNavigation();

    // Add animation to feature cards
    animateFeatureCards();

    // Auto-dismiss flash messages
    setupFlashMessagesDismissal();

    // Add smooth scrolling for anchor links
    setupSmoothScrolling();

    // Add dark mode toggle (if needed)
    // setupDarkModeToggle();
});

/**
 * Setup mobile navigation toggle functionality
 */
function setupMobileNavigation() {
    const navToggle = document.createElement('button');
    navToggle.className = 'nav-toggle';
    navToggle.setAttribute('aria-label', 'Toggle navigation menu');
    navToggle.innerHTML = '<span></span><span></span><span></span>';

    const nav = document.querySelector('nav');
    const navLinks = document.querySelector('.nav-links');

    if (nav && navLinks) {
        nav.insertBefore(navToggle, navLinks);

        navToggle.addEventListener('click', function() {
            navLinks.classList.toggle('active');
            navToggle.classList.toggle('active');

            const expanded = navToggle.getAttribute('aria-expanded') === 'true' || false;
            navToggle.setAttribute('aria-expanded', !expanded);
        });

        // Close mobile nav when clicking outside
        document.addEventListener('click', function(event) {
            const isClickInside = nav.contains(event.target);

            if (!isClickInside && navLinks.classList.contains('active')) {
                navLinks.classList.remove('active');
                navToggle.classList.remove('active');
                navToggle.setAttribute('aria-expanded', 'false');
            }
        });
    }
}

/**
 * Animate feature cards on scroll
 */
function animateFeatureCards() {
    const featureCards = document.querySelectorAll('.feature-card');

    if (featureCards.length) {
        // Add initial invisible class
        featureCards.forEach(card => {
            card.classList.add('feature-card-hidden');
        });

        // Create intersection observer
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('feature-card-visible');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.2
        });

        // Observe each card
        featureCards.forEach(card => {
            observer.observe(card);
        });
    }
}

/**
 * Setup flash messages auto-dismissal
 */
function setupFlashMessagesDismissal() {
    const flashMessages = document.querySelectorAll('.flash-message');

    flashMessages.forEach(message => {
        // Add close button
        const closeBtn = document.createElement('button');
        closeBtn.innerHTML = '&times;';
        closeBtn.className = 'flash-close';
        closeBtn.setAttribute('aria-label', 'Close message');
        message.appendChild(closeBtn);

        // Add click event
        closeBtn.addEventListener('click', () => {
            message.classList.add('flash-dismissing');
            setTimeout(() => {
                message.remove();
            }, 300);
        });

        // Auto dismiss after 5 seconds
        setTimeout(() => {
            if (document.body.contains(message)) {
                message.classList.add('flash-dismissing');
                setTimeout(() => {
                    if (document.body.contains(message)) {
                        message.remove();
                    }
                }, 300);
            }
        }, 5000);
    });
}

/**
 * Setup smooth scrolling for anchor links
 */
function setupSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');

            if (targetId !== '#') {
                e.preventDefault();

                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    // Get header height for offset
                    const headerHeight = document.querySelector('header')?.offsetHeight || 0;

                    window.scrollTo({
                        top: targetElement.offsetTop - headerHeight - 20,
                        behavior: 'smooth'
                    });

                    // Update URL but without scrolling
                    history.pushState(null, null, targetId);
                }
            }
        });
    });
}
