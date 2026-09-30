(function () {
    'use strict';

    var I18N = window.URAC_I18N;
    var CONFIG = window.URAC_CONFIG || {};
    var LANGS = [
        { code: 'fr', label: 'Français', short: 'FR' },
        { code: 'en', label: 'English', short: 'EN' },
    ];
    var LANG_KEY = 'urac_lang';
    var THEME_KEY = 'urac_theme';

    // Chaque entrée correspond à une vue de index.html (<div class="view" data-view="...">)
    var NAV = ['home', 'about', 'team', 'research', 'partners', 'contact'];

    var FOOTER = [
        { key: 'unit', links: ['about', 'team', 'partners'] },
        { key: 'activities', links: ['research'] },
        { key: 'connect', links: ['contact'] },
    ];

    var ICONS = {
        chevron: '<path d="m6 9 6 6 6-6"/>',
        arrow: '<path d="M5 12h14M13 6l6 6-6 6"/>',
        sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M2 12h2m16 0h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
        moon: '<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8Z"/>',
        globe: '<circle cx="12" cy="12" r="9"/><path d="M3.6 9h16.8M3.6 15h16.8M12 3c-2.4 2.8-3.8 5.7-3.8 9s1.4 6.2 3.8 9M12 3c2.4 2.8 3.8 5.7 3.8 9s-1.4 6.2-3.8 9"/>',
        menu: '<path d="M4 7h16M4 12h16M4 17h16"/>',
        close: '<path d="m6 6 12 12M18 6 6 18"/>',
        check: '<path d="m5 13 4 4L19 7"/>',
        scalpel: '<path d="M14 4 4 14l3 3L17 7"/><path d="m14 4 6 6-3 1-4-4 1-3Z"/><path d="M7 17 5 21"/>',
        scan: '<path d="M4 8V5a1 1 0 0 1 1-1h3M16 4h3a1 1 0 0 1 1 1v3M20 16v3a1 1 0 0 1-1 1h-3M8 20H5a1 1 0 0 1-1-1v-3"/><circle cx="12" cy="12" r="3.5"/><path d="M12 8.5V7m0 10v-1.5M8.5 12H7m10 0h-1.5"/>',
        cube: '<path d="m12 3 8 4.5v9L12 21l-8-4.5v-9L12 3Z"/><path d="m4 7.5 8 4.5 8-4.5M12 12v9"/>',
        ai: '<rect x="6" y="6" width="12" height="12" rx="2"/><path d="M10 10h4v4h-4zM9 3v3m6-3v3M9 18v3m6-3v3M3 9h3m-3 6h3m12-6h3m-3 6h3"/>',
        microscope: '<path d="M6 21h12M9 17h6M12 17v-3"/><path d="M8 3h4l1 7H9L8 3Z"/><path d="M13 10a5 5 0 0 1 2 9"/>',
        ultrasound: '<path d="M8 3h8l-1 7H9L8 3Z"/><path d="M9 10v2a3 3 0 0 0 6 0v-2"/><path d="M6 17a8 8 0 0 0 12 0M4 20a11 11 0 0 0 16 0"/>',
        book: '<path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2V5Z"/><path d="M4 19a2 2 0 0 1 2-2h13"/>',
        cap: '<path d="M12 4 2 9l10 5 10-5-10-5Z"/><path d="M6 11.5V17c0 1.5 3 3 6 3s6-1.5 6-3v-5.5"/>',
        users: '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><path d="M16 4.6a3.5 3.5 0 0 1 0 6.8M21.5 20a6.5 6.5 0 0 0-4-6"/>',
        language: '<path d="M4 5h9M8.5 3v2M6 5c.5 3 2.5 5.5 5 7M11 5c-.6 3.5-3 6.5-6.5 8"/><path d="m12 21 4.5-10L21 21M13.5 18h6"/>',
        mail: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
        phone: '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2Z"/>',
        pin: '<path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21Z"/><circle cx="12" cy="9.5" r="2.5"/>',
        building: '<path d="M3 21h18M5 21V10l7-5 7 5v11"/><path d="M9 21v-6h6v6M9 11h.01M15 11h.01"/>',
        link: '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
        file: '<path d="M14 3H6a1 1 0 0 0-1 1v16a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V8l-5-5Z"/><path d="M14 3v5h5M8 13h8M8 17h5"/>',
        calendar: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4m8-4v4"/>',
        globe2: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
        handshake: '<path d="m11 17 2 2a1.4 1.4 0 0 0 2-2"/><path d="m14 14 2.5 2.5a1.4 1.4 0 0 0 2-2l-3.9-3.9a2 2 0 0 0-2.8 0l-.9.9a1.4 1.4 0 0 1-2-2l2.8-2.8a3.8 3.8 0 0 1 4.8-.4l.4.3a3 3 0 0 0 2 .5H21"/><path d="M21 4v9h-2M3 4v9h2l6 6"/><path d="M3 4h7"/>',
    };

    function icon(name, extraAttrs) {
        return (
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"' +
            (extraAttrs || '') +
            '>' +
            (ICONS[name] || '') +
            '</svg>'
        );
    }

    function escapeHtml(s) {
        return String(s).replace(/[&<>"']/g, function (c) {
            return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
        });
    }

    function safeGet(key) {
        try {
            return localStorage.getItem(key);
        } catch (e) {
            return null;
        }
    }

    function safeSet(key, value) {
        try {
            localStorage.setItem(key, value);
        } catch (e) {
            /* storage unavailable */
        }
    }

    /* ---------- Language ---------- */

    function detectLang() {
        var param = new URLSearchParams(window.location.search).get('lang');
        if (param && I18N[param]) {
            safeSet(LANG_KEY, param);
            return param;
        }
        var stored = safeGet(LANG_KEY);
        if (stored && I18N[stored]) return stored;
        var nav = (navigator.language || 'fr').toLowerCase();
        return nav.indexOf('en') === 0 ? 'en' : 'fr';
    }

    var lang = detectLang();

    function t(key) {
        var parts = key.split('.');
        var node = I18N[lang];
        for (var i = 0; i < parts.length; i++) {
            if (node == null) break;
            node = node[parts[i]];
        }
        if (node == null) {
            node = I18N.fr;
            for (var j = 0; j < parts.length; j++) {
                if (node == null) break;
                node = node[parts[j]];
            }
        }
        return node == null ? key : node;
    }

    function localized(value) {
        if (value == null) return '';
        if (typeof value === 'string') return value;
        return value[lang] || value.fr || value.en || '';
    }

    function placeholder() {
        return '<span class="placeholder">' + escapeHtml(t('common.toComplete')) + '</span>';
    }

    /* ---------- Header & footer ---------- */

    function currentView() {
        var key = window.location.hash.replace('#', '');
        return NAV.indexOf(key) === -1 ? 'home' : key;
    }

    var page = currentView();

    function navLink(key, cls) {
        var current = key === page ? ' aria-current="page"' : '';
        return '<a class="' + cls + '" href="#' + key + '"' + current + '>' + t('nav.' + key) + '</a>';
    }

    function renderHeader() {
        var items = NAV.map(function (key) {
            return '<li>' + navLink(key, 'nav-link') + '</li>';
        }).join('');

        var langItems = LANGS.map(function (l) {
            return (
                '<li><button type="button" class="menu__item" role="menuitemradio" data-lang="' +
                l.code +
                '" aria-checked="' +
                (l.code === lang) +
                '"><strong>' +
                l.short +
                '</strong><span>' +
                l.label +
                '</span>' +
                icon('check', ' class="menu__check" stroke-width="2.5"') +
                '</button></li>'
            );
        }).join('');

        var current = LANGS.filter(function (l) {
            return l.code === lang;
        })[0];

        return (
            '<a class="skip-link" href="#main">' + t('nav.skip') + '</a>' +
            '<header class="app-navbar"><div class="container app-navbar__inner">' +
            '<a class="brand" href="#home"><img src="assets/img/logo.svg" alt="" width="44" height="44">' +
            '<span class="brand__wordmark"><span>URAC</span><span>' + t('meta.long') + '</span></span></a>' +
            '<nav class="app-navbar__collapse" id="primary-nav" data-open="false" aria-label="Menu"><div>' +
            '<ul class="app-navbar__nav">' + items + '</ul></div></nav>' +
            '<div class="app-navbar__actions">' +
            '<button type="button" class="icon-button theme-toggle" aria-label="' + t('nav.theme') + '">' +
            icon('sun', ' class="icon-sun"') + icon('moon', ' class="icon-moon"') + '</button>' +
            '<div class="dropdown"><button type="button" class="icon-button" data-menu="lang" aria-expanded="false" aria-label="' +
            t('nav.lang') + '">' + icon('globe', ' stroke-width="1.6"') + '<span>' + current.short + '</span></button>' +
            '<ul class="menu" id="menu-lang" role="menu">' + langItems + '</ul></div>' +
            '<button type="button" class="icon-button nav-toggle" aria-controls="primary-nav" aria-expanded="false" aria-label="' +
            t('nav.menu') + '">' + icon('menu', ' stroke-width="2"') + '</button>' +
            '</div></div></header>'
        );
    }

    function renderFooter() {
        var cols = FOOTER.map(function (section) {
            return (
                '<div><h2 class="site-footer__heading">' + t('footer.' + section.key) + '</h2><ul class="site-footer__nav">' +
                section.links
                    .map(function (k) {
                        return '<li><a href="#' + k + '">' + t('nav.' + k) + '</a></li>';
                    })
                    .join('') +
                (section.key === 'connect' && CONFIG.contact && CONFIG.contact.email
                    ? '<li><a href="mailto:' + escapeHtml(CONFIG.contact.email) + '">' + escapeHtml(CONFIG.contact.email) + '</a></li>'
                    : '') +
                '</ul></div>'
            );
        }).join('');

        return (
            '<footer class="site-footer"><div class="container">' +
            '<div class="site-footer__inner"><div>' +
            '<a class="brand" href="#home"><img src="assets/img/logo.svg" alt="" width="48" height="48">' +
            '<span class="brand__wordmark"><span>URAC</span><span>' + t('meta.long') + '</span></span></a>' +
            '<p class="site-footer__tagline">' + t('footer.tagline') + '</p></div>' +
            '<nav aria-label="Footer"><div class="site-footer__columns">' + cols + '</div></nav></div>' +
            '<div class="site-footer__bottom"><p>&copy; ' + new Date().getFullYear() + ' ' + t('footer.rights') + '</p>' +
            '<p>' + t('footer.fmpos') + '</p></div>' +
            '</div></footer>'
        );
    }

    /* ---------- Dynamic lists (from config.js) ---------- */

    function initials(name) {
        return name
            .replace(/^(Dr\.?|Pr\.?|Prof\.?)\s+/i, '')
            .split(/\s+/)
            .slice(0, 2)
            .map(function (w) {
                return w.charAt(0).toUpperCase();
            })
            .join('');
    }

    function renderMembers(list, emptyKey) {
        if (!list || !list.length) {
            return '<p class="callout">' + t(emptyKey) + '</p>';
        }
        return (
            '<div class="grid" style="--col-min: 16rem">' +
            list
                .map(function (m) {
                    var avatar = m.photo
                        ? '<img class="avatar avatar--sm" src="' + escapeHtml(m.photo) + '" alt="" style="object-fit:cover">'
                        : '<span class="avatar avatar--sm" aria-hidden="true">' + escapeHtml(initials(m.name)) + '</span>';
                    return (
                        '<article class="card" style="flex-direction:row;align-items:center">' + avatar +
                        '<div><h3 class="card__title">' + escapeHtml(m.name) + '</h3>' +
                        (m.title ? '<p class="card__meta" style="margin:0">' + escapeHtml(localized(m.title)) + '</p>' : '') +
                        (m.role ? '<p class="card__text" style="font-size:var(--text-sm)">' + escapeHtml(localized(m.role)) + '</p>' : '') +
                        '</div></article>'
                    );
                })
                .join('') +
            '</div>'
        );
    }

    function renderSocial() {
        var s = CONFIG.social || {};
        var names = { linkedin: 'LinkedIn', researchgate: 'ResearchGate', googleScholar: 'Google Scholar', facebook: 'Facebook', x: 'X' };
        var links = Object.keys(names)
            .filter(function (k) {
                return s[k];
            })
            .map(function (k) {
                return '<a class="btn-ghost" href="' + escapeHtml(s[k]) + '" target="_blank" rel="noopener">' + names[k] + '</a>';
            });
        return links.length ? '<div class="cluster">' + links.join('') + '</div>' : placeholder();
    }

    /* ---------- Apply translations ---------- */

    function applyI18n() {
        document.documentElement.lang = lang;

        document.querySelectorAll('[data-i18n]').forEach(function (el) {
            el.innerHTML = t(el.getAttribute('data-i18n'));
        });

        document.querySelectorAll('[data-i18n-attr]').forEach(function (el) {
            el.getAttribute('data-i18n-attr')
                .split(';')
                .forEach(function (pair) {
                    var p = pair.split(':');
                    if (p.length === 2) el.setAttribute(p[0].trim(), t(p[1].trim()));
                });
        });

        document.querySelectorAll('[data-icon]').forEach(function (el) {
            el.innerHTML = icon(el.getAttribute('data-icon'));
        });

        document.querySelectorAll('[data-config]').forEach(function (el) {
            var path = el.getAttribute('data-config').split('.');
            var v = CONFIG;
            path.forEach(function (k) {
                v = v == null ? v : v[k];
            });
            v = localized(v);
            if (!v) {
                el.innerHTML = placeholder();
                return;
            }
            var type = el.getAttribute('data-config-type');
            if (type === 'mailto') el.innerHTML = '<a href="mailto:' + escapeHtml(v) + '">' + escapeHtml(v) + '</a>';
            else if (type === 'tel') el.innerHTML = '<a href="tel:' + escapeHtml(v.replace(/\s+/g, '')) + '">' + escapeHtml(v) + '</a>';
            else el.textContent = v;
        });


        var lists = {
            researchers: function () { return renderMembers(CONFIG.researchers, 'team.researchersEmpty'); },
            students: function () { return renderMembers(CONFIG.students, 'team.studentsEmpty'); },
            social: renderSocial,
        };
        document.querySelectorAll('[data-list]').forEach(function (el) {
            var fn = lists[el.getAttribute('data-list')];
            if (fn) el.innerHTML = fn();
        });

        updateTitle();
    }

    /* ---------- Views (navigation sans rechargement) ---------- */

    function updateTitle() {
        document.title = (page === 'home' ? '' : t(page + '.title') + ' · ') + t('meta.siteName');
    }

    function showView() {
        page = currentView();
        document.querySelectorAll('.view').forEach(function (el) {
            el.hidden = el.getAttribute('data-view') !== page;
        });
        document.querySelectorAll('.nav-link').forEach(function (a) {
            if (a.getAttribute('href') === '#' + page) a.setAttribute('aria-current', 'page');
            else a.removeAttribute('aria-current');
        });
        updateTitle();
    }

    /* ---------- Interactions ---------- */

    function closeMenus(except) {
        document.querySelectorAll('[data-menu]').forEach(function (btn) {
            var id = btn.getAttribute('data-menu');
            if (id === except) return;
            btn.setAttribute('aria-expanded', 'false');
            var menu = document.getElementById('menu-' + id);
            if (menu) menu.setAttribute('data-open', 'false');
        });
    }

    var docBound = false;

    function bindHeader() {
        document.querySelectorAll('[data-menu]').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                var id = btn.getAttribute('data-menu');
                var menu = document.getElementById('menu-' + id);
                var open = btn.getAttribute('aria-expanded') !== 'true';
                closeMenus(id);
                btn.setAttribute('aria-expanded', String(open));
                menu.setAttribute('data-open', String(open));
            });
        });

        if (!docBound) {
            docBound = true;
            document.addEventListener('click', function () {
                closeMenus();
            });
            document.addEventListener('keydown', function (e) {
                if (e.key === 'Escape') {
                    closeMenus();
                    setNav(false);
                }
            });
        }

        document.querySelectorAll('[data-lang]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                lang = btn.getAttribute('data-lang');
                safeSet(LANG_KEY, lang);
                var url = new URL(window.location.href);
                if (url.searchParams.has('lang')) {
                    url.searchParams.set('lang', lang);
                    history.replaceState(null, '', url.toString());
                }
                render();
            });
        });

        var themeBtn = document.querySelector('.theme-toggle');
        themeBtn.setAttribute('aria-pressed', String(document.documentElement.dataset.theme === 'dark'));
        themeBtn.addEventListener('click', function () {
            var next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
            document.documentElement.dataset.theme = next;
            themeBtn.setAttribute('aria-pressed', String(next === 'dark'));
            safeSet(THEME_KEY, next);
        });

        var toggle = document.querySelector('.nav-toggle');
        toggle.addEventListener('click', function (e) {
            e.stopPropagation();
            setNav(toggle.getAttribute('aria-expanded') !== 'true');
        });

        document.getElementById('primary-nav').addEventListener('click', function (e) {
            e.stopPropagation();
            if (e.target.closest('a')) setNav(false);
        });
    }

    function setNav(open) {
        var toggle = document.querySelector('.nav-toggle');
        var nav = document.getElementById('primary-nav');
        if (!toggle || !nav) return;
        toggle.setAttribute('aria-expanded', String(open));
        toggle.innerHTML = icon(open ? 'close' : 'menu', ' stroke-width="2"');
        nav.setAttribute('data-open', String(open));
    }

    function initReveal() {
        var els = document.querySelectorAll('.reveal');
        if (!('IntersectionObserver' in window)) {
            els.forEach(function (el) { el.classList.add('is-visible'); });
            return;
        }
        var io = new IntersectionObserver(
            function (entries) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('is-visible');
                        io.unobserve(entry.target);
                    }
                });
            },
            { rootMargin: '0px 0px -8% 0px' }
        );
        els.forEach(function (el) { io.observe(el); });
    }

    function render() {
        document.getElementById('site-header').innerHTML = renderHeader();
        document.getElementById('site-footer').innerHTML = renderFooter();
        applyI18n();
        bindHeader();
        showView();
    }

    window.addEventListener('hashchange', function () {
        // Ignore les ancres internes (ex. lien d'évitement #main)
        if (NAV.indexOf(window.location.hash.replace('#', '')) === -1) return;
        showView();
        window.scrollTo(0, 0);
    });

    render();
    initReveal();
    document.body.classList.remove('is-loading');
})();
