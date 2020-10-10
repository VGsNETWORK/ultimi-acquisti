WORK_IN_PROGRESS_MESSAGE = "⚠️ Work In Progress... ⚠️"

DB_CONNECTION_ERROR = "Impossibile stabilire un collegamento con il database, alcune funzionalità non funzioneranno come dovrebbero."

DB_CONNECTION_SUCCESS = "Connesso al database..."

DB_GENERIC_ERROR = "Errore sconosciuto durante il collegamento al database, controlla i file di log per risolvere il problema."

TELEGRAM_ERROR = "Durante la gestione di un update è successo questo errore:\n\n<code>%s</code>\n\nRisolviamo al più presto 😡"

USER_ERROR = "Hey, durante la gestione del tuo messaggio si sono verificati degli errori. I nostri sviluppatori sono stati informati " \
             "e verranno risolti il prima possibile."

PRICE_MESSAGE_NOT_FORMATTED = "Il messaggio non è formattato correttamente, assicurati di mandare un'immagine " \
                              "con la didascalia\n\n<code>#ultimiacquisti PREZZO</code>"

MONTH_PURCHASES = "<a href=\"tg://user?id=%s\">%s</a>, a %s hai speso un totale di <code>%s €</code>."

YEAR_PURCHASES = "<a href=\"tg://user?id=%s\">%s</a>, nel %s hai speso un totale di <code>%s €</code>."

PURCHASE_ADDED = "Acquisto aggiunto con successo!"

PURCHASE_MODIFIED = "Acquisto modificato con successo!"

ONLY_GROUP = "Questa funzionalità è disponibile solo all'interno di un gruppo."

CANCEL_PURCHASE_ERROR = "<a href=\"tg://user?id=%s\">%s</a>, per annullare un tuo acquisto devi quotarlo!"

PURCHASE_NOT_FOUND = "<a href=\"tg://user?id=%s\">%s</a>, non riesco a trovare l'acquisto che hai fatto."

PURCHASE_DELETED = "Acquisto cancellato con successo!"

GROUP_NOT_ALLOWED = "Questo gruppo non è abilitato all'utilizzo di questo bot.\n" \
                    "Puoi creare il tuo bot personale con il codice al seguente link:\n\n"\
                    "https://gitlab.com/nautilor/ultimi-acquisti"

NO_PURCHASE = "<a href=\"tg://user?id=%s\">%s</a>, non hai ancora registrato alcun acquisto su questo bot."

NO_MONTH_PURCHASE = "<a href=\"tg://user?id=%s\">%s</a>, nel mese di <b>%s</b> non hai registrato alcun acquisto."

LAST_PURCHASE = '<a href=\"tg://user?id=%s\">%s</a>, il tuo ultimo acquisto è stato effettuato in data %s alle %s, puoi trovarlo <a href="https://t.me/c/%s/%s">qui</a>'

MONTH_PURCHASE_REPORT = "<a href=\"tg://user?id=%s\">%s</a>, nel mese di <b>%s</b> hai avuto le seguenti spese:\n"

PURCHASE_REPORT_TEMPLATE = '• <a href="https://t.me/c/%s/%s">%s</a><code>    %s €</code>'

MONTH_PURCHASE_TOTAL = "per un totale di <code>%s €</code>."