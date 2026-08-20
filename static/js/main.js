document.addEventListener("DOMContentLoaded", function () {
    if (window.lucide) {
        window.lucide.createIcons();
    }

    var header = document.querySelector(".site-header");
    var menuToggle = document.querySelector(".menu-toggle");

    if (header && menuToggle) {
        menuToggle.addEventListener("click", function () {
            var isOpen = header.classList.toggle("is-menu-open");
            menuToggle.setAttribute("aria-expanded", String(isOpen));
        });
    }

    var filterModal = document.querySelector("[data-filter-modal]");
    var filterOpen = document.querySelector("[data-filter-open]");
    var filterCloseButtons = document.querySelectorAll("[data-filter-close]");
    var lastFocusedElement = null;

    var closeFilters = function () {
        if (!filterModal || !filterOpen) {
            return;
        }

        filterModal.classList.remove("is-open");
        filterModal.setAttribute("aria-hidden", "true");
        filterOpen.setAttribute("aria-expanded", "false");
        document.body.classList.remove("is-filter-open");

        if (lastFocusedElement) {
            lastFocusedElement.focus();
        }
    };

    var openFilters = function () {
        if (!filterModal || !filterOpen) {
            return;
        }

        lastFocusedElement = document.activeElement;
        filterModal.classList.add("is-open");
        filterModal.setAttribute("aria-hidden", "false");
        filterOpen.setAttribute("aria-expanded", "true");
        document.body.classList.add("is-filter-open");

        var firstField = filterModal.querySelector("input, select, button, a");
        if (firstField) {
            firstField.focus();
        }
    };

    if (filterModal && filterOpen) {
        filterOpen.addEventListener("click", openFilters);

        filterCloseButtons.forEach(function (button) {
            button.addEventListener("click", closeFilters);
        });

        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape" && filterModal.classList.contains("is-open")) {
                closeFilters();
            }
        });
    }

    var filterForm = document.querySelector("[data-auto-filter-form]");

    if (filterForm) {
        var submitFilters = function () {
            filterForm.submit();
        };

        var searchInput = filterForm.querySelector("[data-auto-search]");
        var searchTimeout;

        if (searchInput) {
            searchInput.addEventListener("input", function () {
                window.clearTimeout(searchTimeout);

                searchTimeout = window.setTimeout(function () {
                    var value = searchInput.value.trim();

                    if (value.length === 0 || value.length >= 2) {
                        submitFilters();
                    }
                }, 500);
            });
        }
    }

    document.querySelectorAll(".favorite-button").forEach(function (button) {
        button.addEventListener("click", function () {
            var isPressed = button.getAttribute("aria-pressed") === "true";
            button.setAttribute("aria-pressed", String(!isPressed));
        });
    });

    var featuredTrack = document.querySelector("[data-featured-carousel]");
    var featuredPrev = document.querySelector("[data-featured-prev]");
    var featuredNext = document.querySelector("[data-featured-next]");

    if (featuredTrack && featuredNext) {
        var featuredIndex = 0;
        var featuredCards = Array.prototype.slice.call(featuredTrack.querySelectorAll(".vehicle-card"));

        var getFeaturedVisibleCount = function () {
            var value = window.getComputedStyle(featuredTrack).getPropertyValue("--featured-visible");
            return Number.parseInt(value, 10) || 4;
        };

        var updateFeaturedCarousel = function () {
            var card = featuredTrack.querySelector(".vehicle-card");
            var gap = Number.parseFloat(window.getComputedStyle(featuredTrack).columnGap) || 18;
            var visibleCount = getFeaturedVisibleCount();
            var maxIndex = Math.max(0, featuredCards.length - visibleCount);

            featuredIndex = Math.min(featuredIndex, maxIndex);

            if (card) {
                var offset = featuredIndex * (card.getBoundingClientRect().width + gap);
                featuredTrack.style.transform = "translateX(-" + offset + "px)";
            }

            if (featuredPrev) {
                featuredPrev.disabled = featuredIndex === 0;
            }

            if (featuredNext) {
                featuredNext.disabled = featuredIndex >= maxIndex;
            }
        };

        if (featuredPrev) {
            featuredPrev.addEventListener("click", function () {
                featuredIndex = Math.max(0, featuredIndex - 1);
                updateFeaturedCarousel();
            });
        }

        featuredNext.addEventListener("click", function () {
            featuredIndex += 1;
            updateFeaturedCarousel();
        });

        window.addEventListener("resize", updateFeaturedCarousel);
        updateFeaturedCarousel();
    }
});
