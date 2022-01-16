## Question 1
Dans la fonction step de la classe Villager , j'ai ajouté une boucle sur tous les autres villageois
qui se trouvent dans model.schedule.agent_buffer() et J'ai filtré ceux avec une distance inférieure à 40 . Ceci est bien conforme à la définition actuelle de l'agent de vue car
le loup-garou évolue et est capable de percevoir l'environnement (distance <=40) et agit sur les autres villageois.

## Question 2
Le système converge vers la présence de quelques villageois et chasseurs et apothicaires et de quelques loups-garous très éloignés des chasseurs.
Le rôle des apothicaires n'est pas vraiment intéressant car les loups-garous se transforment vite et du coup ça n'a aucun effet .Par contre , la présence de chasseurs influence grandement la convergence car ils éliminent les loups-garous transformés et donc réduisent le nombre de villageois transformés en loups-garous.

## Question 3
Il n'y a plus de villageois dans l'environnement et c'est parce que les loups-garous se transforment rapidement et nous devons donc augmenter le nombre de chasseurs ou diminuer le nombre de loups-garous pour avoir un village d'oies en bonne santé à la fin.

## Question 4

En comparant les résultats, nous constatons que même si nous diminuons le nombre de groupes de loups à 2, le résultat est le même qu'avec 5 loups-garous. Mais en faisant passer le nombre de chasseurs de 2 à 5 on constate une amélioration du résultat, il reste encore beaucoup de villageois à la fin.

## Question 5
Comme je l'ai déjà dit dans les questions précédentes. Le nombre de chaussures est le plus important dans la simulation.

## Question 6

Mon hypothèse est que si le nombre d'apothicaires est très important, on peut trouver un peu d'amélioration, mais sinon cela n'aura pas beaucoup d'influence à cause du taux de transformation des loups-garous.

## Question 7
Dans les 5 runs on constate qu'il n'y a plus d'humain à la fin et le nombre de loups garous transformés et en moyenne 36. On en conclut donc que le nombre d'apothicaires n'a pas un gros effet sur la simulation.

## Question bonus

