# URAC — Unité de Recherche en Anatomie Clinique

Site web de l'Unité de Recherche en Anatomie Clinique (URAC), Faculté de Médecine, de Pharmacie et d'Odonto-Stomatologie (FMPOS), Université de Nouakchott Al Aasriya, Mauritanie.

- **Bilingue** : français / anglais (sélecteur 🌐 dans la barre de navigation, ou `?lang=en` dans l'URL)
- **Responsive** : mobile, tablette, ordinateur
- **Mode clair / sombre**
- **Statique** : HTML, CSS et JavaScript, sans dépendance ni étape de build

## Pages

Le site tient dans une seule page, `index.html`. Les boutons du menu affichent une vue sans recharger la page (adresse `index.html#vue`) :

| Vue | Contenu |
| --- | --- |
| `#home` | Accueil |
| `#about` | À propos (mission, objectifs, axes de recherche) |
| `#team` | Équipe |
| `#research` | Recherches et projets |
| `#partners` | Partenariats et collaborations |
| `#contact` | Contact (coordonnées) |

## Modifier le contenu

- **Textes (FR et EN)** : `assets/js/i18n.js` — chaque texte existe en `fr` et en `en`.
- **Coordonnées, réseaux sociaux, membres de l'équipe** : `assets/js/config.js`.
  Les champs laissés vides s'affichent « À compléter » (ou sont masqués).
- **Styles / couleurs** : `assets/css/style.css` (variables en haut du fichier).
- **Logo** : `assets/img/logo.svg`.

## Aperçu en local

```bash
python3 -m http.server 8000
# puis ouvrir http://localhost:8000
```

## Déploiement sur GitHub Pages

Le workflow `.github/workflows/pages.yml` publie le site à chaque push sur `main`.

1. Dans le dépôt GitHub : **Settings → Pages → Build and deployment → Source : GitHub Actions**.
2. Fusionner les changements dans `main` : le site est publié sur `https://<utilisateur>.github.io/<dépôt>/`.
