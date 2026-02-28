# Document d'Exigences

## Introduction

La plateforme de mise en relation artistes-lieux est un système bidirectionnel qui connecte les artistes (musiciens, performeurs, producteurs de spectacles, sculpteurs, peintres, photographes, etc.) avec des lieux de performance ou d'exposition. Le système facilite la découverte mutuelle, la vérification de compatibilité technique, la coordination des disponibilités et la publication des calendriers de programmation pour le grand public.

## Glossaire

- **Artiste**: Utilisateur créateur (musicien, performeur, producteur de spectacle, sculpteur, peintre, photographe, etc.) cherchant des lieux pour présenter son travail
- **Gestionnaire_de_Lieu**: Utilisateur responsable d'un lieu de performance ou d'exposition cherchant à remplir son calendrier
- **Lieu**: Espace physique pour performances ou expositions avec des capacités techniques spécifiques
- **Profil_Artiste**: Ensemble d'informations décrivant un artiste, incluant ses besoins techniques et sa disponibilité
- **Profil_Lieu**: Ensemble d'informations décrivant un lieu, incluant ses capacités techniques et sa disponibilité
- **Compatibilité_Technique**: Correspondance entre les besoins techniques d'un artiste et les capacités d'un lieu
- **Disponibilité**: Périodes temporelles où un artiste ou un lieu est libre pour une programmation
- **Calendrier_Public**: Vue publique des événements programmés pour un artiste ou un lieu
- **Système**: La plateforme de mise en relation artistes-lieux
- **Match**: Correspondance potentielle entre un artiste et un lieu basée sur la compatibilité et la disponibilité

## Exigences

### Exigence 1: Gestion des Profils Artistes

**User Story:** En tant qu'artiste, je veux créer et gérer mon profil, afin de présenter mes besoins et ma disponibilité aux lieux potentiels.

#### Critères d'Acceptation

1. QUAND un artiste crée un profil, ALORS LE Système DOIT enregistrer les informations de base de l'artiste
2. QUAND un artiste spécifie ses besoins techniques, ALORS LE Système DOIT stocker ces exigences dans le Profil_Artiste
3. QUAND un artiste met à jour sa disponibilité, ALORS LE Système DOIT refléter ces changements immédiatement dans le Profil_Artiste
4. QUAND un artiste modifie son profil, ALORS LE Système DOIT valider les données avant de les enregistrer
5. LE Système DOIT permettre aux artistes de spécifier leur type d'art (musique, performance, sculpture, peinture, photographie, etc.)

### Exigence 2: Gestion des Profils Lieux

**User Story:** En tant que gestionnaire de lieu, je veux créer et gérer le profil de mon lieu, afin d'attirer des artistes compatibles et maximiser mon taux de réservation.

#### Critères d'Acceptation

1. QUAND un gestionnaire crée un profil de lieu, ALORS LE Système DOIT enregistrer les informations de base du lieu
2. QUAND un gestionnaire spécifie les capacités techniques du lieu, ALORS LE Système DOIT stocker ces capacités dans le Profil_Lieu
3. QUAND un gestionnaire met à jour la disponibilité du lieu, ALORS LE Système DOIT refléter ces changements immédiatement dans le Profil_Lieu
4. QUAND un gestionnaire modifie le profil du lieu, ALORS LE Système DOIT valider les données avant de les enregistrer
5. LE Système DOIT permettre aux gestionnaires de spécifier les types d'événements acceptés par le lieu

### Exigence 3: Recherche d'Artistes par les Lieux

**User Story:** En tant que gestionnaire de lieu, je veux rechercher des artistes compatibles avec mon lieu, afin de remplir mon calendrier de programmation.

#### Critères d'Acceptation

1. QUAND un gestionnaire effectue une recherche d'artistes, ALORS LE Système DOIT retourner les artistes dont les besoins techniques correspondent aux capacités du lieu
2. QUAND un gestionnaire filtre par disponibilité, ALORS LE Système DOIT retourner uniquement les artistes disponibles pendant les périodes spécifiées
3. QUAND un gestionnaire filtre par type d'art, ALORS LE Système DOIT retourner uniquement les artistes du type spécifié
4. QUAND les résultats de recherche sont affichés, ALORS LE Système DOIT présenter les informations clés de chaque Profil_Artiste
5. SI aucun artiste ne correspond aux critères, ALORS LE Système DOIT afficher un message indiquant l'absence de résultats

### Exigence 4: Recherche de Lieux par les Artistes

**User Story:** En tant qu'artiste, je veux rechercher des lieux compatibles avec mes besoins, afin de compléter ma saison ou ma tournée.

#### Critères d'Acceptation

1. QUAND un artiste effectue une recherche de lieux, ALORS LE Système DOIT retourner les lieux dont les capacités techniques correspondent aux besoins de l'artiste
2. QUAND un artiste filtre par disponibilité, ALORS LE Système DOIT retourner uniquement les lieux disponibles pendant les périodes où l'artiste est également disponible
3. QUAND un artiste filtre par localisation géographique, ALORS LE Système DOIT retourner uniquement les lieux dans la zone spécifiée
4. QUAND les résultats de recherche sont affichés, ALORS LE Système DOIT présenter les informations clés de chaque Profil_Lieu
5. SI aucun lieu ne correspond aux critères, ALORS LE Système DOIT afficher un message indiquant l'absence de résultats

### Exigence 5: Évaluation de la Compatibilité Technique

**User Story:** En tant qu'utilisateur du système, je veux que le système évalue automatiquement la compatibilité technique, afin de ne voir que des correspondances viables.

#### Critères d'Acceptation

1. QUAND le système compare un artiste et un lieu, ALORS LE Système DOIT vérifier que chaque besoin technique de l'artiste est satisfait par les capacités du lieu
2. QUAND un besoin technique de l'artiste n'est pas satisfait, ALORS LE Système DOIT marquer la correspondance comme incompatible
3. QUAND tous les besoins techniques sont satisfaits, ALORS LE Système DOIT marquer la correspondance comme techniquement compatible
4. LE Système DOIT calculer un score de compatibilité pour chaque paire artiste-lieu
5. QUAND le système affiche des résultats de recherche, ALORS LE Système DOIT trier les résultats par score de compatibilité décroissant

### Exigence 6: Gestion des Disponibilités

**User Story:** En tant qu'utilisateur du système, je veux gérer mes disponibilités, afin que le système puisse identifier les périodes de correspondance mutuelle.

#### Critères d'Acceptation

1. QUAND un utilisateur ajoute une période de disponibilité, ALORS LE Système DOIT enregistrer la date de début et la date de fin
2. QUAND un utilisateur supprime une période de disponibilité, ALORS LE Système DOIT retirer cette période de son profil
3. QUAND le système recherche des correspondances, ALORS LE Système DOIT identifier uniquement les périodes où l'artiste et le lieu sont tous deux disponibles
4. SI un artiste et un lieu n'ont aucune disponibilité commune, ALORS LE Système DOIT exclure cette correspondance des résultats de recherche
5. QUAND une réservation est confirmée, ALORS LE Système DOIT marquer la période comme non disponible pour les deux parties

### Exigence 7: Calendriers Publics pour les Artistes

**User Story:** En tant que membre du grand public, je veux consulter le calendrier de programmation d'un artiste, afin de découvrir où et quand je peux voir ses performances ou expositions.

#### Critères d'Acceptation

1. QUAND un membre du public accède au calendrier d'un artiste, ALORS LE Système DOIT afficher tous les événements confirmés de l'artiste
2. QUAND un événement est affiché, ALORS LE Système DOIT présenter la date, le lieu et les informations de base de l'événement
3. LE Système DOIT afficher les événements dans l'ordre chronologique
4. QUAND un artiste confirme une nouvelle réservation, ALORS LE Système DOIT ajouter l'événement au Calendrier_Public immédiatement
5. QUAND un événement est annulé, ALORS LE Système DOIT retirer l'événement du Calendrier_Public

### Exigence 8: Calendriers Publics pour les Lieux

**User Story:** En tant que membre du grand public, je veux consulter le calendrier de programmation d'un lieu, afin de découvrir quels événements y sont prévus.

#### Critères d'Acceptation

1. QUAND un membre du public accède au calendrier d'un lieu, ALORS LE Système DOIT afficher tous les événements confirmés du lieu
2. QUAND un événement est affiché, ALORS LE Système DOIT présenter la date, l'artiste et les informations de base de l'événement
3. LE Système DOIT afficher les événements dans l'ordre chronologique
4. QUAND un lieu confirme une nouvelle réservation, ALORS LE Système DOIT ajouter l'événement au Calendrier_Public immédiatement
5. QUAND un événement est annulé, ALORS LE Système DOIT retirer l'événement du Calendrier_Public

### Exigence 9: Système de Correspondance Bidirectionnel

**User Story:** En tant qu'utilisateur du système, je veux que le système facilite la découverte mutuelle, afin que les artistes et les lieux puissent se trouver efficacement.

#### Critères d'Acceptation

1. QUAND un artiste recherche des lieux, ALORS LE Système DOIT appliquer les mêmes critères de compatibilité que lorsqu'un lieu recherche des artistes
2. QUAND un Match est identifié, ALORS LE Système DOIT permettre aux deux parties de voir les informations de profil pertinentes
3. LE Système DOIT maintenir la cohérence des données de compatibilité indépendamment de la direction de la recherche
4. QUAND un profil est mis à jour, ALORS LE Système DOIT recalculer toutes les correspondances affectées
5. LE Système DOIT permettre aux deux parties d'initier un contact pour une réservation potentielle

### Exigence 10: Validation et Intégrité des Données

**User Story:** En tant qu'administrateur système, je veux que le système maintienne l'intégrité des données, afin d'assurer la fiabilité de la plateforme.

#### Critères d'Acceptation

1. QUAND un utilisateur soumet des données de profil, ALORS LE Système DOIT valider que tous les champs obligatoires sont remplis
2. QUAND une date de disponibilité est saisie, ALORS LE Système DOIT vérifier que la date de fin est postérieure à la date de début
3. SI des données invalides sont soumises, ALORS LE Système DOIT rejeter la soumission et afficher un message d'erreur descriptif
4. QUAND une réservation est créée, ALORS LE Système DOIT vérifier qu'aucun conflit de disponibilité n'existe
5. LE Système DOIT empêcher la création de réservations qui se chevauchent pour le même artiste ou le même lieu
