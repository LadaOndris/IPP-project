Implementační dokumentace k 1. úloze do IPP 2019/2020  
Jméno a příjmení: Ladislav Ondris  
Login: xondri07

## Řešení
Celé řešení je obsaženo v souboru parse.php. Při řešení bylo třeba řešit strukturu kódu a implementační detaily. 

### Struktura kódu
Obecně byl kladen důraz na celkový návrh jako celku a jeho jednoduchou modifikovatelnost a rozšiřitelnost. Byl tedy kladen důraz na dobrý návrh tříd, malých funkcí a obecně clean code.

Hlavním prostředkem k dosažení dobrého návrhu bylo Dependency Injection. V tomto případě jsem použil klasické Pure DI bez kontejnerů. Kontejner není potřebný pro projekt takto malého rozsahu.

Vstupním bodem DI je v souboru parse.php úplně dole. Nejprve se vytvoří všechny objekty, s kterými se bude pracovat - vytvoří se takzvaný Object Graph. Poté se s tímto grafem začne pracovat.

Veškeré třídy s chováním jsou implementacemi definovaných rozhraní.

Proces parseru při spuštění je následující:   
Nejprve se zpracují argumenty programu a zkontrolují se jejich správnost. Pokud je vše v pořádku, zavolá se funkce parse() na IProgramParser, který načte celý program a vrátí ho. Poté se zavolá funkce serialize na IProgramSerializer, která program serializuje. A úplně nakonec se vytvoří statistiky.

Implementace IProgramParser, ProgramParser, používá ke své práci IInstructionParser a IInputReader. IInstructionParser vrací instrukce a IInputReader vrací text ze vstupu. Implementace IInstructionParser, InstructionParser, používá ke své práci IArgParser, který zpracuje operandy instrukce.

Na následujícím diagramu je znázorněna výše popsaná struktura programu. Nejsou v něm však obsaženy detaily, pouze důležité části.
![Class Diagram znázorňující celkovou sturukturu parseru](/images/parse_class_diagram.png)

### Implementační detaily
Řešení chybových stavů je řešeno pomocí výjimek. Vyhodí se výjimka se zprávou obsahující detaily a chybovým kódem. Na nejvyšší úrovni programu je konstrukce try catch, která odchytává výjimky. Pokud nastane výjimka, ta se odchytí, vypíše se zpráva výjimky a ukončí se program s návratovým kódem z výjimky.  
Tento způsob řešení vracení chybových stavů zpřehledňuje celý kód. V tomto případě se vrací výjimka typu Exception, tedy obecná výjimka. V produkčním řešení o větším rozsahu by stálo za zvážení použití vytvoření konkrétních typů výjimek, které budou dědit z Exception. U většího projektu to zvýší udržovatelnost.

Každá instrukce očekává sadu operandů. Jaké operandy každá instrukce potřebuje je uloženo v asociativním poli, kde ke každému operačnímu kódu instrukce je přiřazeno pole očekávaných typů operandů. Ke každému typu operandu existuje regex, který musí splňovat.


