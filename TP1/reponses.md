## Question 1
Dans la fonction step du classe Villager , j'ai ajouté une boucle sur tous les autres villagers
qui se trouvent dans model.schedule.agent_buffer() et j'ai filitré ceux qui ont une distance
inférieure à 40. Cela est bien conforme avec la définition d'agent vue en cours car 
le loup garou évolue et il est capable de percevoir l'environnement (distance <=40)  et 
agit sur les autres villagers.

## Question 2
Le système converge vers la présence de quelques villageois et les chasseurs et les apothicaires et quelques loup garou qui sont très loin des chasseurs.
Le role des apothicaires n'est pas vraiment intéréssant car les loup garou se transforme
rapidement et par suite il n'a pas d'effet.Par contre , la présence des chasseurs influe 
beacoup sur le convergence car il permet d'éliminer les loup garou transformé et par suite
diminue le nombre de villageois transformés en loup garou.

## Question 3
Il reste aucun villageois dans l'environnement et c'est parce que les loup garou transforment
rapidement et donc on doit augmenter le nombre de chasseurs ou diminuer le nombre de loup garou
pour avoir de villageoie sain à la fin.

## Question 4

En comparant les résultats on trouve que même si on diminuant le nombre de loup group à
2 le résultat est la même qu'avec 5 loup garou. Mais en augmentant le nombre de chasseur de 
2 à 5 on remarque une grande amélioration du résultat , il reste beaucoup de villageois à la fin. 

## Question 5
Comme j'ai déja dit dans les questions précédentes. Le nombre de chausseur est le plus 
important dans la simulation.

## Question 6

L'hpothèse je pose c'est que si le nombre d’apothicaires est très grand on peut trouver
un peut d'amélioration mais sinon ça ne va pas influencer beaucoup à cause du taux de transformation
des loup graou.

## Question 7
Dans les 5 runs on trouve qu'il n'y a plus d'humain à la fin et le nombre de loup garou
transofmré et au moyenne de 36. Donc on conclue que le nombre d’apothicaires  n'a pas de grande effet sur la simulation.


## Question bonus

