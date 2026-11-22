# Référence UX : More Nutrition (more-nutrition.webflow.io)

Étude du 22/11/2026, faite dans le navigateur (le site refuse la lecture automatique), pour la refonte de l'accueil d'actionsbenefices.com.
Périmètre validé par Nicolas : accueil d'abord, puis extension au reste du site ; on reprend les animations, les couleurs vives et la typographie. On prend l'idée, jamais la marque : ni logo, ni texte, ni image du site d'origine.

## Ce qui fait la qualité du site
- Une seule couleur maîtresse (vert sauge #335C30) déclinée en teintes claires (#E8EFE4, #B6CBA5, #90B96D) : sections pleines aux couleurs franches, texte sombre #333 sur fond clair, blanc sur la couleur.
- Une seule police, grotesque condensée (Founders Grotesk Condensed), en très grand : h1 ≈ 80 px capitales, interlignage serré (0,7), approche négative (−0,03 em). Paragraphes en 21 px, approche négative aussi. Taille de base proportionnelle à la largeur d'écran (`--size-font` = largeur / 90).
- Le produit au centre de tout : il reste épinglé au milieu de l'écran pendant que les arguments défilent autour (sections « More Taste / More Caffeine / More weight loss » qui entrent et sortent pendant qu'il tourne).
- Des annotations manuscrites avec flèches dessinées (« Why people love it », « Free shipping ») : humain, ludique.
- Un grand tracé blanc qui serpente et se dessine au défilement (DrawSVG).
- Des chiffres clés en pastilles rondes (20 g, 95 %, 85 mg) posées sur un arc autour du produit.
- Cartes de vidéos de la communauté inclinées et en éventail, avec bouton son.
- Un bandeau qui défile en boucle (« It's a Match(a) · … »), en arc.
- Tableau comparatif « nous / les autres » avec coches et croix.
- Avis clients en carrousel à flèches ; pied de page avec grand appel à l'action.

## Animations relevées
- Outils : GSAP + ScrollTrigger (animations liées au défilement, éléments épinglés), SplitText (titres qui apparaissent ligne par ligne ou lettre par lettre), DrawSVG (tracés qui se dessinent), CustomEase, InertiaPlugin ; défilement fluide Lenis ; animation Lottie du logo à l'ouverture.
- Ouverture : écran de chargement sauge, logo dessiné trait par trait, puis la page se révèle.
- Entrées des éléments : « ressort » de 0,725 à 0,8 s sur translate et rotate, avec un dépassement d'environ 14 % puis retour (courbe linear() à rebond) ; scale en 0,75 s même courbe ; opacité et flou en 0,15 s ease-out ; décalages de 0,05 / 0,1 / 0,15 s entre éléments voisins.
- Survols : scale 0,3–0,35 s cubic-bezier(0.72, 0.17, 0.17, 1), ombre 0,35 s cubic-bezier(0.32, 0.72, 0, 1).
- Défilement : produit épinglé qui tourne et change d'échelle ; ingrédients qui flottent en parallaxe ; titres qui changent de couleur par ligne.

## Transposition proposée pour Actions Bénéfices (à valider en maquette)
- Couleur maîtresse : notre marine #17375E pour les sections pleines, avec l'or #F5C451 en accent et des teintes claires dérivées (ivoire actuel, sable, bleu très pâle). Sections alternées pleines et claires, plus franches qu'aujourd'hui.
- Typographie : garder Anton pour les titres, plus grands (jusqu'à ≈ 96 px sur grand écran), capitales serrées, interlignage 0,9 ; Inter pour le texte. Taille proportionnelle à l'écran.
- Mister Coin dans le rôle du produit : il reste épinglé au centre pendant que défilent nos piliers (News du vendredi, fiches entreprises, lexique et quiz, calculateurs), il change de pose à chaque pilier.
- Annotations manuscrites façon Mister Coin (« Clique-moi ! », « Nouveau chaque vendredi »), avec flèches dessinées au défilement.
- Pastilles de chiffres autour de Mister Coin (abonnés, vidéos publiées, sujets traités).
- Tracé or qui se dessine au défilement entre les sections.
- Nos vidéos en cartes inclinées en éventail.
- Entrées à ressort (0,75 s, dépassement léger, décalage 0,05–0,15 s), animations seulement sur transform et opacity, déclenchées une fois, désactivées si l'utilisateur a demandé moins d'animations ; le site reste complet sans JavaScript.
- Outil : GSAP est gratuit (y compris ScrollTrigger, SplitText et DrawSVG depuis 2025) ; à défaut, Intersection Observer + CSS pour rester sans dépendance.
