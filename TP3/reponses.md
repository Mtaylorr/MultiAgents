## Question 1


## Question 2

Il y a de plusieurs choses à faire donc on fait un ordre qui convient : 
1 - Détruire les mines s'il est possible
2 - Diminuer la vitesse s'il trouve dans un environnement ralentissant pour qu'on puisse calculer sa prochaine position
3 - changement de l'angle aléatoirement
4 - Détecter les mines ( se dirige vers le mine si les conditions de 5 sont valides)
5 - On change l'angle tant qu'il y a une collision

temps moyen de désamorçage de toutes les mines : 152.18

## Question 3

les principes des agents réactifs qui sont  été respectés ici : 
	- éviter collision (robot - bord - obstacles)
	- explorer (se déplacer aléatoirement)
	- manipuler object (détruire les mines)

les principes des agents réactifs qui ne sont pas été respectés ici : 
 	- absence de communication indirecte
	
## Question 4

L'ahout des balises permet au robots de se communiquer entre eux indirectement


## Question 5

1 - Détruire les mines s'il est possible
2 - Ramasser les balises 'il est possible
3 - Diminuer la vitesse s'il trouve dans un environnement ralentissant pour qu'on puisse calculer sa prochaine position
4 - changement de l'angle aléatoirement
5 - Détecter les mines ( se dirige vers le mine si les conditions de 7 sont valides)
6 - Détecter les balises( se dirige vers la balise si les conditions de 7 sont valides)
7 - On change l'angle tant qu'il y a une collision
8 -  ajout des balises s'il est dans une des conditions du problème 

## Question 6

temps moyen de désamorçage de toutes les mines :83.42 
On remarque que le temps a été divisé par 2 donc la communication indirecte a amélioré
la performance des robots.

## Question 7

On remarque que le temps moyen passé dans les sables mouvants a diminué quand on a ajouté les balises de danger.
Ce qui est un autre avantage pour la communication indirecte entre robots.


