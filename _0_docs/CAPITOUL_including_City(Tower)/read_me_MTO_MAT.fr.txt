
                    CAPITOUL 2004-2005
     Donn�es moyennes du M�t de Toulouse-Alsace
     ------------------------------------------

Site : Toulouse-Alsace - abr�viation = Ta
----

Fichiers :
--------

  Nommage : TaAAAAMM_MAT_%60.asc pour le fichier de donn�es 
            TaAAAAMM_MAT_%60.txt pour le fichier de description
            AAAA = ann�e
            MM = mois
            %60 pour 60 secondes
       Ex : Ta200407_MAT_%60.asc et Ta200407_MAT_%60.txt

  Contenu des fichiers de donn�es :
  -------------------------------

   p�riode mensuelle

   pas d'�chantillonage : minute

   17 colonnes, s�par�es par des espaces.
   
   colonne 1  : la date au format JJ/MM/AAAA
   colonne 2  : l'heure au format HHMMSS.SSS
   colonne 3  : Pression air (hPa), capteur Vaisala PTB200.
   colonne 4  : Temp�rature (degr�s Celsius), capteur HMP233 VAISALA.
   colonne 5  : Humidit� relative (pourcent), capteur HMP233 VAISALA.
   colonne 6  : Rayonnement Global Descendant (watts/m2), capteur CM3 du CNR1 Kipp et Zonen.
   colonne 7  : Rayonnement Global Montant (watts/m2), capteur CM3 du CNR1 Kipp et Zonen.
   colonne 8  : Rayonnement Infra-Rouge Descendant (watts/m2), capteur CG1 du CNR1 Kipp et Zonen.
   colonne 9  : Rayonnement Infra-Rouge Montant (watts/m2), capteur CG1 du CNR1 Kipp et Zonen.
   colonne 10 : Intensit� Pr�cipitations mesur�e par l'ORG (mm/h)
   colonne 11 : Intensit� Pr�cipitations d�riv�e du pluviom�tre � auget (mm/h)
   colonne 12 : Direction du Vent calcul�e du GILL Haut (degr�)
   colonne 13 : Vitesse du Vent calcul�e du GILL Haut (m/s)
   colonne 14 : Direction du Vent calcul�e du GILL Bas (degr�)
   colonne 15 : Vitesse du Vent calcul�e du GILL Bas (m/s)
   colonne 16 : Concentration de CO2 du LICOR 7500 (g/m3)
   colonne 17 : Position du Mat  1 = lev�
                                 2 = demi-�rig�
                                 3 = baiss�
  
  Donn�es manquantes : +9999

  Fr�quence : Les donn�es sont moyenn�es � la minute � partir de donn�es �chantillonn�es � 10 secondes, hormis le vent (GILL � 50 Hz) et le co2 (LICOR � 20 Hz).

  Contenu des fichiers de description :
  -----------------------------------

   13 lignes/fichier de donn�es fournissant des information sur :

      - la constitution des fichiers
      - les param�tres
      - les unit�s 
