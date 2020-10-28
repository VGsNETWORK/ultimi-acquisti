#!/usr/bin/env python3

WORK_IN_PROGRESS_MESSAGE = "⚠️ Work In Progress... ⚠️"

DB_CONNECTION_ERROR = (
    "Impossibile stabilire un collegamento con il database,"
    " alcune funzionalità non funzioneranno come dovrebbero."
)

DB_CONNECTION_SUCCESS = "Connesso al database..."

DB_GENERIC_ERROR = (
    "Errore sconosciuto durante il collegamento al database,"
    " controlla i file di log per risolvere il problema."
)

TELEGRAM_ERROR = (
    "Durante la gestione di un update è successo questo errore:"
    "\n\n<code>%s</code>\n\nRisolviamo al più presto 😡"
)

USER_ERROR = (
    "Hey, durante la gestione del tuo messaggio si sono verificati degli errori."
    " I nostri sviluppatori sono stati informati "
    "e verranno risolti il prima possibile."
)

PRICE_MESSAGE_NOT_FORMATTED = (
    "Il messaggio non è formattato correttamente, assicurati di mandare un'immagine "
    "con la didascalia\n\n<code>#ultimiacquisti PREZZO</code>"
)

MONTH_PURCHASES = '<a href="tg://user?id=%s">%s</a>, a <b>%s</b> hai speso un totale di <code>%s €</code>.\n\n'

MONTH_PREVIOUS_PURCHASES_HIGER = "📈 A <b>%s</b> hai speso <code>%s €</code>, <code>%s €</code> in più rispetto a questo mese."

MONTH_PREVIOUS_PURCHASES_LOWER = "📉 A <b>%s</b> hai speso <code>%s €</code>, <code>%s €</code> in meno rispetto a questo mese."

MONTH_USER_PURCHASES = "<i>%s</i> a <b>%s</b> ha speso un totale di <code>%s €</code>."

YEAR_PURCHASES = '<a href="tg://user?id=%s">%s</a>, nel <b>%s</b> hai speso un totale di <code>%s €</code>.\n\n'

YEAR_PREVIOUS_PURCHASES_HIGER = "📈 Nel <b>%s</b> hai speso <code>%s €</code>, <code>%s €</code> in più rispetto a quest'anno."

YEAR_PREVIOUS_PURCHASES_LOWER = "📉 Nel <b>%s</b> hai speso <code>%s €</code>, <code>%s €</code> in meno rispetto a quest'anno."

YEAR_USER_PURCHASES = "<i>%s</i> nel <b>%s</b> ha speso un totale di <code>%s €</code>."

PURCHASE_ADDED = "Acquisto aggiunto con successo!"

PURCHASE_MODIFIED = "Acquisto modificato con successo!"

ONLY_GROUP = "Questa funzionalità è disponibile solo all'interno di un gruppo."

CANCEL_PURCHASE_ERROR = (
    '<a href="tg://user?id=%s">%s</a>, per annullare un tuo acquisto devi quotarlo!'
)

PURCHASE_NOT_FOUND = (
    '<a href="tg://user?id=%s">%s</a>, non riesco a trovare l\'acquisto che hai fatto.'
)

PURCHASE_DELETED = "Acquisto cancellato con successo!"

GROUP_NOT_ALLOWED = (
    "Questo gruppo non è abilitato all'utilizzo di questo bot.\n"
    "Puoi creare il tuo bot personale con il codice al seguente link:\n\n"
    "https://gitlab.com/nautilor/ultimi-acquisti"
)

NO_PURCHASE = (
    '<a href="tg://user?id=%s">%s</a>,'
    " non hai ancora registrato alcun acquisto su questo bot."
)

NO_MONTH_PURCHASE = (
    '<a href="tg://user?id=%s">%s</a>, nel mese di <b>%s</b>'
    " non hai registrato alcun acquisto."
)

NO_YEAR_PURCHASE = (
    '<a href="tg://user?id=%s">%s</a>, durante il <b>%s</b>'
    " non hai registrato alcun acquisto."
)

LAST_PURCHASE = (
    '<a href="tg://user?id=%s">%s</a>, il tuo ultimo acquisto è'
    ' stato effettuato in data <b>%s alle %s</b>, puoi trovarlo <a href="https://t.me/c/%s/%s">qui</a>'
)

MONTH_PURCHASE_REPORT = (
    '<a href="tg://user?id=%s">%s</a>,'
    " nel mese di <b>%s</b> hai avuto le seguenti spese:\n"
)

YEAR_PURCHASE_REPORT = (
    '<a href="tg://user?id=%s">%s</a>, nel <b>%s</b> hai avuto le seguenti spese:\n'
)

YEAR_PURCHASE_TEMPLATE = "•  <code>%s</code>   <code>%s</code><code>%s €</code>"

PURCHASE_REPORT_TEMPLATE = (
    '• <a href="https://t.me/c/%s/%s">%s</a>   <code>%s</code><code>%s €</code>'
)

REPORT_PURCHASE_TOTAL = "per un totale di   <code>%s</code><code>%s €</code>."

PURCHASE_DATE_ERROR = (
    '<a href="tg://user?id=%s">%s</a>, il tuo acquisto è stato aggiunto con successo.\n\n'
    "❗️ Purtroppo la data che mi hai fornito presenta una delle seguenti anomalie:\n"
    "  - non rispetta il formato <code>DD/MM/YYYY</code>\n"
    "  - è una data futura\n"
    "per questo motivo ho collocato l'acquisto alla data di oggi."
)

MONTH_COMPARE_PRICE = (
    "Nel mese di <b>%s</b>...\n"
    '- <a href="tg://user?id=%s">%s</a>, hai speso  <code>%s €</code>\n'
    "- <i>%s</i> ha speso  <code>%s €</code>\n\n"
)

YEAR_COMPARE_PRICE = (
    "Nel <b>%s</b>...\n"
    '- <a href="tg://user?id=%s">%s</a>, hai speso  <code>%s €</code>\n'
    "- <i>%s</i> ha speso  <code>%s €</code>\n\n"
)

COMPARE_YOU_WON = "🥳  Hai <b>vinto</b> di  <code>%s €</code>!"

COMPARE_HE_WON = "😞  Hai <b>perso</b> di  <code>%s €</code>!"

COMPARE_TIE = "💸  I vostri portafogli sono ugualmente leggeri..."

COMPARE_NO_PURCHASE = "Nessuno dei due ha effettuato acquisti finora... 😡"

COMPARE_YOURSELF = "Non puoi lanciare questo comando quotando un tuo messaggio!"

COMPARE_BOT = "Non puoi lanciare questo comando quotando un bot!"
