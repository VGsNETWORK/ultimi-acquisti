# ULTIMI ACQUISTI

Questo bot permette di tenere traccia dei propri acquisti in un gruppo telegram

Una volta aggiunto il bot nel gruppo è possibile eseguire alcune operazioni

- Mandando una foto e aggiungendo la didascalia  `#ultimiacquisti <prezzo>` sarà possibile registrare il proprio acquisto

- Mandando il comando `/spesamensile` sarà possibile vedere la spesa totale del mese corrente

- Mandando il comando `/spesaannuale` sarà possibile vedere la spesa totale dell'anno corrente

- Mandando il comando `/reportmensile` sarà possible vedere un report del mese corrente e navigare tra i vari mesi/anni


# TODO

- ~~Registrazione di un nuovo acquisto tramite foto (con compressione)~~
- ~~Registrazione di un nuovo prodotto tramite foro (senza compressione)~~
- ~~Visualizzazione delle spese mensili~~ 
- ~~Visualizzazione della spesa durante l'anno~~
- ~~Visualizzare la spesa di un messe specifico nell'anno corrente~~
- ~~Controllare che i messaggi vengano inviati tramite un gruppo~~
- ~~Controllare che i messaggi vengano inviati da un gruppo specifico~~
- Cancellare i messaggi dopo un tot di tempo
- ~~Cancellare il messaggio se sbagliato~~
- Nel caso di messaggio sbagliato contattare l'utente in privato se ha
  fatto lo start del bot in privato, altrimenti dirgli di farlo


# CONSIDERAZIONI

Questo bot utilizza mongodb per il salvataggio dei dati

Questo bot utilizza delle variabili di ambiente per la configurazione del bot

- DBUSERNAME: Username per l'accesso al database
- DBPASSWORD: Password per l'accesso al database
- DBHOST: Host dove risiede il database
- DBNAME: Nome del database da utilizzare
- CONNECTION: Lasciare `mongodb://{}:{}@{}/{}`
- TELEGRAM_BOT_ADMIN: `USER_ID` dell'amministratore del bot
- ERROR_CHANNEL: `ID` della chat dove mandare i messaggi di errore
- TOKEN: Il `TOKEN` del bot di telegram
- GROUP_ID: array di stringhe con gli `ID` dei gruppi abilitati al bot (es: `"['chat_id', 'chat_id']"`)
