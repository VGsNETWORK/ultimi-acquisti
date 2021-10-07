# #ultimiacquisti

**[UltimiAcquistiBot](https://t.me/UltimiAcquistiBot)** permette di tenere traccia dei propri acquisti in un gruppo Telegram. Il bot è progettato per funzionare solo in alcuni *gruppi whitelistati* appartenenti a ***[VGs NETWORK](https://t.me/VGsNETWORK)***: a meno che l'azione non venga eseguita da un **admin del bot**, quindi, *se questo viene aggiunto in un qualsiasi altro gruppo invia un messaggio di servizio ed esce automaticamente*.

Una volta che il bot è stato aggiunto in un gruppo abilitato al suo utilizzo, è possibile eseguire le seguenti operazioni:

- si può registrare un *acquisto* inviando un messaggio nel seguente formato: `#ultimiacquisti [<prezzo>] [<data>] [%<titolo>%]`;
  1. Gli argomenti tra parentesi quadre sono ***opzionali***, ma il loro uso serve a dettagliare l'*acquisto*:
     - un *acquisto* senza `<prezzo>` verrà salvato con un importo di **0,00 €**;
     - un *acquisto* senza `<data>` verrà collocato alla *data del post di Telegram* (la data corrente nel caso di un nuovo *acquisto*, la data originale del messaggio nel caso di un *acquisto retroattivo*)
	   - se aggiunta, va inserita nel formato `DD/MM/YY(YY)`.
	 - per un *acquisto* senza `%<titolo>%`, nel `/reportmensile` verrà visualizzata l'intestazione di *default* "***DD MMM, HH:MM***";
	   - se aggiunti tra `%...%` come parte del `<titolo>`, **prezzo** e **data** saranno ignorati.
  2. Gli argomenti possono essere inviati in un qualsiasi ordine, *hashtag* incluso;
  3. L'*hashtag* è obbligatorio per permettere al bot di identificare un messaggio come *acquisto*;
  4. Nel caso in cui il messaggio non sia di tipo testuale, ma consista in un ***medium*** (**foto**, **audio**, **video**, **file**, etc.) è necessario inserire l'hashtag e gli argomenti di cui sopra nella sua *didascalia*.

- si possono inviare i *comandi* listati di seguito.



###  ‌‌
## COMANDI
**All'interno di un gruppo**, i comandi provocano una risposta del bot solo se inviati in ***formato esplicito***, ovvero rivolgendosi direttamente a [UltimiAcquistiBot](https://t.me/UltimiAcquistiBot) tramite il formato `/<comando>@UltimiAcquistiBot`. Questo può essere fatto:
- scrivendo l'*username* del bot a mano in coda al comando (**senza spazi in mezzo**), oppure
- cliccando la voce desiderata dalla lista dei comandi che appare digitando il carattere *slash* ("`/`") nella chat.

> 💡 La scelta di far rispondere il bot solo ai comandi in *formato esplicito* risiede nel fatto che bot diversi possono virtualmente avere comandi con lo stesso nome, con il conseguente rischio di falsi positivi qualora si lanci un comando comune a più bot. Interpellando uno specifico bot e ignorando tutti gli altri comandi ricevuti, quindi, ***purché la cosa sia gestita parimenti da tutti gli altri bot presenti nel gruppo*** (🙂), si elimina il rischio di falsi positivi.

In *chat privata* con il bot, invece, i comandi esistenti generano una risposta indipendentemente dal formato in cui vengono inviati (purché preceduti da "`/`").


###  ‌‌
### LEGENDA

`👤` = *Funziona solo in chat privata con il bot*

`👥` = *Funziona solo nei gruppi*

`👤/👥` = *Funziona sia in chat privata con il bot che nei gruppi*

`↩️` = *È necessario quotare il messaggio di un utente*

`↩️🛒` = *È necessario quotare un **proprio acquisto***

###  ‌‌
	/start
`👥` ***Se inviato in un gruppo:*** Visualizza il messaggio iniziale con le istruzioni di base e il redirect alla chat privata.

`👤` ***Se inviato in chat privata:*** Visualizza il menu principale del bot.

###  ‌‌
	/howto
`👤` Visualizza la guida all'utilizzo del bot.

###  ‌‌
	/wishlist
`👤` Apre la *Lista dei desideri* attiva.

###  ‌‌
	/ultimoacquisto
`👤/👥` Visualizza un messaggio con i dettagli dell'ultimo *acquisto* effettuato e il link privato al suddetto post. Se l'ultimo *acquisto* è stato registrato nello stesso gruppo in cui si lancia il comando, il bot quota anche tale messaggio.

###  ‌‌
	/spesamensile
`👤/👥` Visualizza la spesa parziale personale per il mese corrente.

###  ‌‌
	/reportmensile
`👤/👥` Visualizza un report dettagliato della spesa parziale personale per il mese corrente, con la possibilità di navigare i mesi e gli anni precedenti.

###  ‌‌
	/comparamese [<mese> [<anno>]]
`👥`+`↩️` Compara la spesa mensile personale con quella di un altro utente, **quotandolo**.

> 💡 Specificando *opzionalmente* un `<mese>` si può comparare un mese specifico dell'anno corrente. **Esempi di formato:** "*/comparamese **gennaio***", "*/comparamese **gen***".

> 💡 Specificando *opzionalmente* un `<mese>` e un `<anno>` si può comparare un periodo specifico. ***Se si intende specificare un `<anno>`, il `<mese>` è richiesto.*** **Esempi di formato:** "*/comparamese **gennaio 2018***", "*/comparamese **gen 2018***".

###  ‌‌
	/spesaannuale
`👤/👥` Visualizza la spesa parziale personale per l'anno corrente.

###  ‌‌
	/reportannuale
`👤/👥` Visualizza un report dettagliato della spesa parziale personale per l'anno corrente, con la possibilità di navigare gli anni precedenti.

###  ‌‌
	/comparaanno [<anno>]
`👥`+`↩️` Compara la spesa annuale personale con quella di un altro utente, **quotandolo**.

> 💡 Specificando *opzionalmente* un `<anno>` si può comparare un anno specifico. **Esempio di formato:** "*/comparaanno **2018***".

###  ‌‌
	/cancellaspesa
`👥`+`↩️🛒` Cancella un singolo *acquisto* dallo storico personale, **quotandolo**. Elimina anche il relativo post dalla chat.

###  ‌‌
	/cancellastorico
`👥` Cancella l'intero storico personale degli *acquisti* registrati nel gruppo corrente. Mantiene i post degli acquisti nella chat per un'eventuale re-importazione futura.

###  ‌‌
	/impostazioni
`👤` Apre il pannello delle impostazioni utente.

###  ‌‌
	/info
`👤` Visualizza i crediti e delle info sul progetto.

###  ‌‌
	/vota
`👤` Apre la *sezione di valutazione* del bot.



###  ‌‌
## DBMS E VARIABILI D'AMBIENTE

[UltimiAcquistiBot](https://t.me/UltimiAcquistiBot) usa il DBMS `mongodb` per il salvataggio dei dati.

Le seguenti *variabili di ambiente* sono necessarie per la configurazione del bot:
- `DBUSERNAME`: Username per l'accesso al database;
- `DBPASSWORD`: Password per l'accesso al database;
- `DBHOST`: Host dove risiede il database;
- `DBNAME`: Nome del database da utilizzare;
- `CONNECTION`: Lasciare `mongodb://{}:{}@{}/{}`;
- `TELEGRAM_BOT_ADMIN`: `user_id` dell'amministratore del bot;
- `ERROR_CHANNEL`: `chat_id` della chat dove mandare i messaggi di errore;
- `TOKEN`: Il **token** del bot necessario per fare le chiamate alle Bot API di Telegram;
- `GROUP_ID`: Array di stringhe con i `chat_id` dei gruppi abilitati all'utilizzo del bot (**Esempio:** `"['chat_id_0', 'chat_id_1', etc.]"`).



###  ‌‌
## TO DO

- [x] Registrazione di un nuovo acquisto tramite foto (con compressione)
- [x] Registrazione di un nuovo prodotto tramite foto (senza compressione)
- [x] Visualizzazione delle spese mensili
- [x] Visualizzazione della spesa durante l'anno
- [x] Visualizzare la spesa di un messe specifico nell'anno corrente
- [x] Controllare che i messaggi vengano inviati tramite un gruppo
- [x] Controllare che i messaggi vengano inviati da un gruppo specifico
- [x] Cancellare il messaggio se sbagliato
- [x] Cancellare i messaggi dopo un tot di tempo
- [ ] Nel caso di messaggio sbagliato contattare l'utente in privato se ha avviato il bot in chat privata, altrimenti dirgli di farlo.
