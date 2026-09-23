/*
 * ============================================================
 *  CONFIGURATION DU SITE — à modifier facilement
 *  SITE CONFIGURATION — easy to edit
 * ============================================================
 * Remplissez les champs vides ('') avec vos informations.
 * Fill in the empty fields ('') with your information.
 * Tout champ vide s'affiche comme « À compléter » ou est masqué.
 */
window.URAC_CONFIG = {
    contact: {
        email: '', // ex. 'urac@una.mr'
        phone: '', // ex. '+222 00 00 00 00'
        address: {
            fr: '', // ex. 'FMPOS, Nouakchott, Mauritanie'
            en: '',
        },
    },

    // Réseaux sociaux / Social links — laissez '' pour masquer / leave '' to hide
    social: {
        linkedin: '',
        researchgate: '',
        googleScholar: '',
        facebook: '',
        x: '',
    },

    // Liens institutionnels / Institutional links
    links: {
        university: '',
        fmpos: '',
        association: '',
        slicer: 'https://www.slicer.org/',
        openAnatomy: 'https://www.openanatomy.org/',
    },

    /*
     * Membres de l'équipe / Team members
     * { name: 'Dr X', title: { fr: '...', en: '...' }, role: { fr: '...', en: '...' }, photo: 'assets/img/team/x.jpg' }
     */
    researchers: [],
    students: [],

    /*
     * Publications (les plus récentes en premier / most recent first)
     * { year: 2025, authors: 'A. Author, B. Author', title: '...', venue: 'Journal', url: 'https://...' }
     */
    publications: [],

    /*
     * Actualités supplémentaires / Extra news items
     * { date: { fr: 'Mars 2026', en: 'March 2026' }, title: { fr: '...', en: '...' }, text: { fr: '...', en: '...' } }
     */
    news: [],
};
