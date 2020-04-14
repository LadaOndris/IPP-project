Implementační dokumentace k 2. úloze do IPP 2019/2020  
Jméno a příjmení: Ladislav Ondris  
Login: xondri07

## Společné pro interpret a test

### Struktura kódu

Byl především kladen důraz na objektový návrh.

Hlavním prostředkem k dosažení dobrého návrhu bylo **Dependency Injection** (DI). V tomto případě bylo použito klasického **Pure DI** bez kontejnerů. Kontejner není potřebný pro projekt takto malého rozsahu. **OOP** je pro DI samozřejmostí.

Vstupním bodem DI je na konci souboru `test.php`. V případě interpretu je to v souboru `interpret.py`.  Nejprve se vytvoří všechny objekty, s kterými se bude pracovat - vytvoří se takzvaný Object Graph. Poté se s tímto grafem začne pracovat.

### Systém řešení chybových stavů

V obou skriptech je vracení chybových kódů řešeno pomocí **výjimek**. Vyhodí se výjimka obsahující zprávu a chybový kód. Na nejvyšší úrovni programu je konstrukce try catch, která odchytává výjimky. Pokud nastane výjimka, tak se odchytí, vypíše se zpráva výjimky a ukončí se program s návratovým kódem z výjimky. V `parser.php` je pro jednoduchost použita obecná výjimka typu Exception a v `interpret.py` je použit vlastní typ výjimky `InterpretException` dědící z `Exception`. 

## test

Celé řešení je rozděleno do souboru `test.php` a dalších souborů ve složce `test`. Většina tříd je umístěna v samostatném souboru. Pro interní reprezentaci testů a složek testů se používají instance tříd `TestCase` a `TestSuite`. Výsledky těchto testů, respektive sady testů, nesou instance třídy `TestCaseResult` a `TestSuiteResult`. Implementace spouštění testů je umístěno v třídách `InterpretRunner` a `ParseRunner`. Pro ověření výstupů slouží `DiffRunner` a `XmlDiffRunner`.

Načtení `TestSuite` a jeho předzpracování je řešeno návrhovým vzorem **Decorator**. `DirectoryTestSuiteReader` načítá `TestSuite` ze složky a `PreprocessTestSuiteReader` přichystá `TestSuite` k testování. 

## interpret

Celé řešení je rozděleno do souboru `interpret.py` a souborů ve složce `interpret`. Většina tříd má svůj soubor kromě tříd instrukcí a procesoru.

Vykonávání instrukcí je řešeno návrhovým vzorem **Command**, pričemž každá třída instrukce reprezentuje jeden `Command` a je vykonána třídou `Processor`.

Čtení vstupního xml souboru je odděleno od vykonávání instrukcí a je provedeno ihned po spuštění interpretu.

### Implementační detaily

Rámce jsou implementovány datovými strukturami slovník. Práce s rámcem je obalena třídou `Frame`. Lokální rámce jsou uloženy v poli instancí třídy `Frame`. Všechny rámce spravuje třída `FrameModel`. 
 
Zásobník volání je implementován obyčejným polem, s kterým je pracováno jako se zásobníkem.
Ukazatel na aktuální instrukci je ve tříde `InstructionCounter` spolu se zásobníkem volání.
Seznam instrukcí je vnitřně reprezentován polem, se kterým pracuje `InstructionCounter`.

K vytváření instancí tříd instrukcí je použita funkce jazyka python `exec`.
Každé instanci instrukce jsou předány operandy, které jsou nejprve vytvořeny třídou `OperandFactory`, která zpracuje hodnoty operandů ze vstupního xml a vytvoří odpovídající instance tříd operandů, například `ConstantOperand`, `SymbolOperand`, `LabelOperand`.






