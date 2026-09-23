# URAC — Unité de Recherche en Anatomie Clinique

Site web de l'Unité de Recherche en Anatomie Clinique (URAC), Faculté de Médecine, de Pharmacie et d'Odonto-Stomatologie (FMPOS), Université de Nouakchott Al Aasriya, Mauritanie.

- **Bilingue** : français / anglais (sélecteur 🌐 dans la barre de navigation, ou `?lang=en` dans l'URL)
- **Responsive** : mobile, tablette, ordinateur
- **Mode clair / sombre**
- **Statique** : HTML, CSS et JavaScript, sans dépendance ni étape de build

## Pages

| Fichier | Contenu |
| --- | --- |
| `index.html` | Accueil |
| `about.html` | À propos (mission, objectifs, axes de recherche) |
| `team.html` | Équipe |
| `research.html` | Recherches et projets |
| `publications.html` | Publications |
| `partners.html` | Partenariats et collaborations |
| `teaching.html` | Formation et enseignement |
| `news.html` | Actualités / événements |
| `resources.html` | Ressources |
| `contact.html` | Contact |

## Modifier le contenu

- **Textes (FR et EN)** : `assets/js/i18n.js` — chaque texte existe en `fr` et en `en`.
- **Coordonnées, réseaux sociaux, liens, membres de l'équipe, publications, actualités** : `assets/js/config.js`.
  Les champs laissés vides s'affichent « À compléter » (ou sont masqués).
- **Styles / couleurs** : `assets/css/style.css` (variables en haut du fichier).
- **Logo** : `assets/img/logo.svg`.

Exemple d'ajout d'une publication dans `config.js` :

```js
publications: [
    { year: 2025, authors: 'A. Moulaye Idriss, et al.', title: 'Titre de l’article', venue: 'Nom de la revue', url: 'https://doi.org/...' },
],
```

## Aperçu en local

```bash
python3 -m http.server 8000
# puis ouvrir http://localhost:8000
```

## Déploiement sur GitHub Pages

Le workflow `.github/workflows/pages.yml` publie le site à chaque push sur `main`.

1. Dans le dépôt GitHub : **Settings → Pages → Build and deployment → Source : GitHub Actions**.
2. Fusionner les changements dans `main` : le site est publié sur `https://<utilisateur>.github.io/<dépôt>/`.
