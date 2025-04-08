# AMP Wspinaczka Sportowa Kalkulator wyników
Aplikacja do liczenia wyników klasyfikacji drużynowej na Akademickich Mistrzostwach Polski we wspinaczce sportowej

## Jak tego użyć
Przygotuj 3 pliki `xlsx` z wynikami z poszczególnych konkurencji.

Każdy plik powinien zawierać kolumny:
```
Numer Startowy | Imię i Nazwisko |       Uczelnia            | Typ Uczelni   | Miejsce
----------------------------------------------------------------------------------------
       123      | Piotr Oleszczuk | Uniwersytet Warszawski    |      UNI       |    1 
       456      | Olaf Malinowski |       PL Lublin           |      UTE       |    2 
       789      | Kajetan Kupś    |       AGH Kraków          |      UTE       |    3 
       ...      |     ...         |           ...             |      ...       |   ... 

```
- W pliku moga znaleźć się także inne kolumny, ale istnienie powyższych jest obowiązkowe.
- Zwróć uwagę na nazwy kolumn. Wielkość liter i liczba spacji jest w tym przypadku ważna i uruchomienie z innymi nazwami kolumn spowoduje błąd.
- Osoby niestartujące w konkurencji także mogą pojawić się w tabeli, ale w ich kolumnie "Miejsce" powinnien pojawić się napis "DNS".
- Zwróć uwagę czy we wszystkich plikach nazwy uczelni są takie same. Na przykład jeżeli w tabeli z wynikami boulderingu
krakowski AWF ma nazwę uczelni "AWF Kraków", a w tabeli z wynikami prowadzenia "AWF w Krakowie" to program zinterpretuje je jako dwie rożne uczelnie.

## Uruchomienie programu
- Uruchomienie programu otworzy okno, w którym trzeba wybrać pliki(xlsx) na podstawie, których zostaną policzone wyniki, zgodne ze strukturą podaną wyżej. Po wybraniu ścieżek do plików i kliknięciu przycisku **Analizuj wyniki** wyświetlone zostaną wyniki
- Po kliknięciu **Analizuj wyniki** zostanie wyświetlona klasyfikacja uczelni. Przy każdej uczelni zostanie wyświetlona
liczba punktów przez nią zdobyta, a po kliknięciu w strzałeczkę przy uczelni rozwinie się panel, który umożliwia
umożliwia sprawdzenie wszystkich zawodników punktujących w danej kategorii oraz liczbę punktów, które zdobyli
- Nad okienkiem wyświeli się także informacja o liczbie zawodników startujących w najliczniejszej konkurencji (w ramach sprawdzenia czy wrzuciliśmy dobre excele)
- Jeżeli liczymy wyniki dla kobiet, musi zostać zaznaczona opcja klasyfikacji kobiet, wtedy liczymy dwie najlepsze zawodniczki
- Po obliczeniu wyników możemy sobie filtrować uczelnie o konkretnych typach
- Po obliczeniu wyników możemy wyeksportować je do pliku xlsx

## Dodatkowe informacje
- Dostępne na Windows, Linux oraz MacOS

## Pytania
- DNF liczy się jako osoba startujaca w konkurencji prawda?
- Czy osoby ktore w czasówkach maja wynik DNF mają eqaequo ostatnie miejsce?
- Czy wystartuje i ukończy to znaczy ze na czasówce nie mozna spaśc?
- Napisać, że w wynikach moze być DNS w kolumnie który sie nie liczy