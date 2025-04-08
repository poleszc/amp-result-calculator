# AMP Wspinaczka Sportowa Kalkulator wyników
Aplikacja do liczenia wyników klasyfikacji drużynowej na Akademickich Mistrzostwach Polski we wspinaczce sportowej

## Jak tego użyć
Przygotuj 3 pliki `xlsx` z wynikami z poszczególnych konkurencji.

Każdy plik powinien zawierać kolumny(TODO: niech nazwy kolumn będa do dostosowania):
```
Numer Startowyy | Imię i Nazwisko |       Uczelnia            | Typ Uczelni   | Miejsce
----------------------------------------------------------------------------------------
       123      | Piotr Oleszczuk | Uniwersytet Warszawski    |      UNI       |    1 
       456      | Olaf Malinowski |       PL Lublin           |      UTE       |    2 
       789      | Kajetan Kupś    |       AGH Kraków          |      UTE       |    3 
       ...      |     ...         |           ...             |      ...       |   ... 

```
- W pliku moga znaleźć się także inne kolumny, ale istnienie powyższych jest obowiązkowe.
- W pliku powinny znaleźć się wszystkie osoby **startujące** w danej konkurencji. Branę pod uwagę w klasyfikacji uczelni.


## Uruchomienie programu
- Uruchomienie programu otworzy okno, w którym trzeba wybrać pliki na podstawie, których zostaną policzone wyniki. Po wybraniu ścieżki i kliknięciu przycisku **LICZ WYNIKI** wyświetlone zostaną wyniki:
  - Generalnego rankingu uczelni - w podziale na kobiety i mężczyzn
  - Rankingu uniwersytetów - w podziale na kobiety i mężczyzn
  - Rankingu uczelni technicznych - w podziale na kobiety i mężczyzn
  - Rankingu uczelni społeczno-przyrodniczych - w podziale na kobiety i mężczyzn
  - Rankingu uczelni medycznych - w podziale na kobiety i mężczyzn
  - Rankingu uczelni wychowania fizycznego(AWF) - w podziale na kobiety i mężczyzn

- Dla każdej uczelni jest możliwość podglądu zawodników punktujących
- Wyświetlone zostaną także podstawowe statystyki zawodów
- Po obliczeniu wyników będzie udostępniona możliwość zapisania ich w plikach `xlsx`

## Dodatkowe informacje
- Available for Windows, MacOS and Linux

## Pytania
- DNF liczy się jako osoba startujaca w konkurencji prawda?
- Czy osoby ktore w czasówkach maja wynik DNF mają eqaequo ostatnie miejsce?
- Osoby niestartujące w danej konkurencji mogą pojawić się w tabeli, ale w kolumnie miejsce powinnien pojawić wówczas wynik "DNS"
- Czy wystartuje i ukończy to znaczy ze na czasówce nie mozna spaśc?
- Napisać, że w wynikach moze być DNS w kolumnie który sie nie liczy