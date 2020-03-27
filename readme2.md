Implementační dokumentace k 2. úloze do IPP 2019/2020  
Jméno a příjmení: Ladislav Ondris  
Login: xondri07

## Společné pro interpret a test

### Struktura kódu

Obecně byl kladen důraz na celkový návrh jako celku a jeho jednoduchou modifikovatelnost a rozšiřitelnost. Byl tedy kladen důraz na dobrý návrh tříd, malých funkcí a obecně <em>clean code</em>.

Hlavním prostředkem k dosažení dobrého návrhu bylo Dependency Injection. V tomto případě jsem použil klasické Pure DI bez kontejnerů. Kontejner není potřebný pro projekt takto malého rozsahu.

Vstupním bodem DI je v souboru test.php úplně dole. V případě interpretu je to v souboru interpret.py.  Nejprve se vytvoří všechny objekty, s kterými se bude pracovat - vytvoří se takzvaný Object Graph. Poté se s tímto grafem začne pracovat.

### Systém řešení chybových stavů

Řešení chybových stavů je řešeno pomocí výjimek. Vyhodí se výjimka se zprávou obsahující detaily a chybovým kódem. Na nejvyšší úrovni programu je konstrukce try catch, která odchytává výjimky. Pokud nastane výjimka, ta se odchytí, vypíše se zpráva výjimky a ukončí se program s návratovým kódem z výjimky.  

Tento způsob řešení vracení chybových stavů zpřehledňuje celý kód. V tomto případě se vrací výjimka typu Exception, tedy obecná výjimka. V produkčním řešení o větším rozsahu by stálo za zvážení použití vytvoření konkrétních typů výjimek, které budou dědit z Exception. U většího projektu to zvýší udržovatelnost.

## test

### Řešení
Celé řešení je rozděleno do souboru `test.php` a souborů ve složce `test`. 

## interpret

### Řešení
Celé řešení je rozděleno do souboru `interpret.py` a souborů ve složce `interpret`. 

### Implementační detaily


