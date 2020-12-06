#!/usr/bin/env python3

""" This class contains all the messages used in the bot """

from os import environ

BOT_NAME = environ["BOT_NAME"]

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
    "Durante la gestione di un update si è verificato questo errore:"
    "\n\n<code>%s</code>\n\nRisolviamo al più presto 😡"
)

USER_ERROR = (
    "Hey, durante la gestione del tuo messaggio si sono verificati degli errori."
    " I nostri sviluppatori sono stati informati:"
    " verranno risolti il prima possibile."
)

NOT_ALLOWED_IN_GROUP = (
    'Ciao <a href="tg://user?id=%s">%s</a>, per piacere continuiamo in chat privata!'
)

START_COMMAND = (
    'Ciao <a href="tg://user?id=%s">%s</a>, benvenuto su <b>#ultimiacquisti</b>!\n\n'
    "Sono un <b>bot di gestione della spesa personale</b>,"
    " e puoi usarmi per registrare i tuoi acquisti recenti"
    " e passati e tracciarli nel tempo."
    "%s<b>Buon utilizzo!</b>"
)

START_GROUP_GROUP_APPEND = (
    "\n\n🏁  Per iniziare, <b>invia</b> o <b>modifica</b> un messaggio di qualunque"
    ' tipo aggiungendo l\'hashtag "<code>#ultimiacquisti</code>"...\n\n'
    "ℹ️  Per maggiori informazioni sul mio utilizzo, <b>vai alla chat privata</b>!\n\n\n"
)

PLEASE_NOTE_APPEND = (
    "\n<b>N.B.:</b> Le funzioni di <b>aggiunta</b>, <b>modifica</b> e <b>rimozione</b>"
    " degli acquisti sono utilizzabili <u>solo all'interno dei"
    " gruppi di <b>VGs NETWORK</b></u> (@VGsGROUPS).\n\n"
)

START_COMMANDS_LIST = (
    "\n\n\n<u><b>LISTA COMANDI</b></u>\n\n\n"
    f'<a href="https://t.me/share/url?text=/howto@{BOT_NAME}">/howto</a>\n\n'
    "<i>Mostra una breve guida all'utilizzo del bot</i>\n\n\n"
    f'<a href="https://t.me/share/url?text=/ultimoacquisto@{BOT_NAME}">/ultimoacquisto</a>\n\n'
    "<i>Ritrova il tuo ultimo acquisto</i>\n\n\n"
    f'<a href="https://t.me/share/url?text=/spesamensile@{BOT_NAME}">/spesamensile</a>\n\n'
    "<i>Mostra la tua spesa totale per questo mese</i>\n\n\n"
    f'<a href="https://t.me/share/url?text=/reportmensile@{BOT_NAME}">/reportmensile</a>\n\n'
    "<i>Mostra un report dettagliato della tua spesa totale per questo mese</i>\n\n\n"
    f'<a href="https://t.me/share/url?text=/comparamese@{BOT_NAME}">/comparamese</a>\n'
    f'<a href="https://t.me/share/url?text=/comparamese@{BOT_NAME}%20%3CMM/YYYY%3E">/'
    "comparamese &lt;MM/YYYY&gt;</a>\n\n"
    "<i>Metti a confronto la tua spesa mensile con quella di un altro utente,"
    " specificando opzionalmente un mese e un anno diversi da quelli correnti"
    " (funziona solo nei <b>gruppi</b> e richiede di <b>quotare un utente</b>)</i>\n\n\n"
    f'<a href="https://t.me/share/url?text=/spesaannuale@{BOT_NAME}">/spesaannuale</a>\n\n'
    "<i>Mostra la tua spesa totale per questo anno</i>\n\n\n"
    f'<a href="https://t.me/share/url?text=/reportannuale@{BOT_NAME}">/reportannuale</a>\n\n'
    "<i>Mostra un report dettagliato della tua spesa totale per questo anno</i>\n\n\n"
    f'<a href="https://t.me/share/url?text=/comparaanno@{BOT_NAME}">/comparaanno</a>\n'
    f'<a href="https://t.me/share/url?text=/comparaanno@{BOT_NAME}%20%3CYYYY%3E">/'
    "comparaanno &lt;YYYY&gt;</a>\n\n"
    "<i>Metti a confronto la tua spesa annuale con quella di un altro utente,"
    " specificando opzionalmente un anno diverso da quello corrente"
    " (funziona solo nei <b>gruppi</b> e richiede di <b>quotare un utente</b>)</i>\n\n\n"
    f'<a href="https://t.me/share/url?text=/cancellaspesa@{BOT_NAME}">/cancellaspesa</a>\n\n'
    "<i>Rimuovi un acquisto dal tuo storico; cancella anche il"
    " relativo post (funziona solo nei <b>gruppi</b> e"
    " richiede di <b>quotare un tuo acquisto</b>)</i>"
)


PRICE_MESSAGE_NOT_FORMATTED = (
    "Il messaggio non è formattato correttamente, assicurati di mandare un'immagine "
    "con la didascalia\n\n<code>#ultimiacquisti PREZZO</code>"
)

MONTH_PURCHASES = (
    '<a href="tg://user?id=%s">%s</a>, a '
    "<b>%s</b> hai speso un totale di <code>%s €</code>.\n\n"
)

MONTH_PURCHASES_NONE = (
    '<a href="tg://user?id=%s">%s</a>, a <b>%s</b> non hai ancora speso niente.\n\n'
)

MONTH_PREVIOUS_PURCHASES_NONE = "📈 A <i>%s</i> non hai registrato alcun acquisto."

MONTH_PREVIOUS_PURCHASES_HIGHER = (
    "📉 A <i>%s</i> hai speso <code>%s €</code>, "
    "<code>%s</code> in più rispetto a questo mese."
)

MONTH_PREVIOUS_PURCHASES_LOWER = (
    "📈 A <i>%s</i> hai speso <code>%s €</code>, "
    "<code>%s</code> in meno rispetto a questo mese."
)

MONTH_USER_PURCHASES = "<i>%s</i> a <b>%s</b> ha speso un totale di <code>%s €</code>."

MONTH_USER_PURCHASES_NONE = "<i>%s</i> a <b>%s</b> non ha registrato alcun acquisto."

YEAR_PURCHASES = (
    '<a href="tg://user?id=%s">%s</a>, nel <b>%s</b> '
    "hai speso un totale di <code>%s €</code>.\n\n"
)

YEAR_PURCHASES_NONE = (
    '<a href="tg://user?id=%s">%s</a>, nel <b>%s</b> non hai ancora speso niente.\n\n'
)

YEAR_PREVIOUS_PURCHASE_NONE = "📈 Nel <i>%s</i> non hai registrato alcun acquisto."

YEAR_PREVIOUS_PURCHASES_HIGHER = (
    "📉 Nel <i>%s</i> hai speso <code>%s €</code>, "
    "<code>%s</code> in più rispetto a quest'anno."
)

YEAR_PREVIOUS_PURCHASES_LOWER = (
    "📈 Nel <i>%s</i> hai speso <code>%s €</code>, "
    "<code>%s</code> in meno rispetto a quest'anno."
)

YEAR_USER_PURCHASES = "<i>%s</i> nel <b>%s</b> ha speso un totale di <code>%s €</code>."

YEAR_USER_PURCHASES_NONE = "<i>%s</i> nel <b>%s</b> non ha registrato alcun acquisto."

PURCHASE_HEADER_HINT = "\n\n\n<b>Lo sapevi che...?</b>"

PURCHASE_PRICE_HINT = (
    "\n💲  Puoi aggiungere un prezzo al tuo acquisto specificandolo nel messaggio."
)

PURCHASE_TITLE_HINT = (
    "\n🔠  Puoi aggiungere un titolo al tuo acquisto includendo"
    " del testo tra <code>%...%</code>. Potrai visualizzarlo nel <b>report mensile</b>."
)

PURCHASE_DATE_HINT = (
    "\n📅  Puoi collocare retroattivamente il tuo acquisto"
    " specificando una data antecedente ad oggi nel formato <code>DD/MM/YYYY</code>."
)

PURCHASE_ADDED = "✅  <i>Acquisto aggiunto con successo!</i>"

PURCHASE_MODIFIED = "✅  <i>Acquisto modificato con successo!</i>"

ONLY_GROUP = "Questa funzionalità è disponibile solo all'interno di un gruppo."

CANCEL_PURCHASE_ERROR = (
    '<a href="tg://user?id=%s">%s</a>,'
    " per cancellare un tuo acquisto devi <b>quotarlo</b>!"
)

NOT_A_PURCHASE = (
    '<a href="tg://user?id=%s">%s</a>,'
    " il messaggio che hai quotato non è un acquisto valido!\n\n"
    "Per essere riconosciuto, un <i>acquisto</i> deve contenere"
    ' l\'hashtag "<code>#ultimiacquisti</code>".'
)

PURCHASE_NOT_FOUND = (
    '<a href="tg://user?id=%s">%s</a>, non riesco a'
    " trovare l'acquisto che hai fatto..."
)

PURCHASE_DELETED = "✅  <i>Acquisto cancellato con successo!</i>"

GROUP_NOT_ALLOWED = (
    "Questo gruppo non è abilitato all'utilizzo di questo bot.\n"
    "Puoi creare il tuo bot personale con il codice al seguente link:\n\n"
    "https://gitlab.com/nautilor/ultimi-acquisti"
)

NO_PURCHASE = (
    '<a href="tg://user?id=%s">%s</a>, '
    "non hai ancora registrato alcun acquisto su questo bot."
)

NOT_YOUR_PURCHASE = (
    '<a href="tg://user?id=%s">%s</a>, '
    "non puoi cancellare l'acquisto di un altro utente!"
)

NO_MONTH_PURCHASE = (
    '<a href="tg://user?id=%s">%s</a>, nel mese di <b>%s</b> '
    "non hai registrato alcun acquisto."
)

NO_YEAR_PURCHASE = (
    '<a href="tg://user?id=%s">%s</a>, nel <b>%s</b> '
    "non hai registrato alcun acquisto."
)

LAST_PURCHASE = (
    '<a href="tg://user?id=%s">%s</a>, hai effettuato il tuo ultimo acquisto '
    "in data <b>%s alle %s</b>. "
    'Puoi trovarlo <a href="https://t.me/c/%s/%s">qui</a>!'
)

LAST_PURCHASE_USER = (
    "<i>%s</i> ha effettuato il suo ultimo acquisto in data <b>%s alle %s</b>. "
    'Puoi trovarlo <a href="https://t.me/c/%s/%s">qui</a>!'
)

MONTH_PURCHASE_REPORT = (
    '<a href="tg://user?id=%s">%s</a>,'
    " nel mese di <b>%s</b> hai avuto le seguenti spese:\n\n"
)

YEAR_PURCHASE_REPORT = (
    '<a href="tg://user?id=%s">%s</a>, nel <b>%s</b> hai avuto le seguenti spese:\n\n'
)

YEAR_PURCHASE_TEMPLATE = "<code>%s</code><code>%s €</code>             %s"

PURCHASE_REPORT_TEMPLATE = (
    '<code>%s</code><code>%s €</code>             <a href="https://t.me/c/%s/%s">%s</a>'
)

REPORT_PURCHASE_TOTAL = "<code>%s</code><code>%s €</code>             <b>TOTALE</b>"

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

COMPARE_YOU_WON = "🥳 Hai <b>vinto</b> di  <code>%s €</code>!"

COMPARE_HE_WON = "😞 Hai <b>perso</b> di  <code>%s €</code>..."

COMPARE_TIE = "💸 I vostri portafogli sono ugualmente leggeri..."

COMPARE_NO_PURCHASE = "Nessuno dei due ha effettuato acquisti finora... 😡"

NO_QUOTE_YOURSELF = "Non puoi lanciare questo comando quotando un tuo messaggio!"

NO_QUOTE_BOT = "Non puoi lanciare questo comando quotando un bot!"

NO_QUOTE_FOUND = "Per lanciare questo comando prova a quotare un utente..."

NOT_MESSAGE_OWNER = "Non puoi navigare tra i report di un altro utente!"

SESSION_ENDED = (
    "Il bot è stato riavviato per motivi tecnici, la sessione "
    "di questo messaggio è scaduta."
)

HOW_TO_DEEP_LINK = (
    '<a href="tg://user?id=%s">%s</a>, puoi visualizzare la guida all\'utilizzo del bot '
    '<a href="t.me/%s?start=how_to">QUI</a>.'
)


HOW_TO_PAGE_ONE = (
    "Per far sì che io possa riconoscere un tuo <i>acquisto</i> è necessario che tu "
    "invii nel gruppo un messaggio contenente l'hashtag <code>#ultimiacquisti</code>.\n\n"
    "Indicando anche una cifra numerica, registrerò l'<i>acquisto</i> con l'importo indicato. "
    "Nel caso in cui ce ne sia più di una, ricorda che prenderò in considerazione solo la prima.\n"
    "Puoi inserire l'importo in molteplici formati:\n\n"
    "   •  <code>22</code>\n"
    "   •  <code>22,50 €</code>\n"
    "   •  <code>22.50</code>\n"
    "   •  <code>2250,10</code>\n"
    "   •  <code>€ 2,250.10</code>\n"
    "   •  <code>2.250,10€</code>\n"
    "   •  <code>2'250.10</code>\n\n"
    "sono solo alcuni di quelli riconosciuti."
)

HOW_TO_PAGE_TWO = (
    "Se ometti l'importo, il tuo acquisto sarà salvato con un importo di "
    "default di <code>0,00€</code> (utile per i regali o se non vuoi rivelare il "
    "prezzo di un certo acquisto – nel secondo caso, tieni presente che "
    "questo avrà ripercussioni sui totali mensili e annuali).\n\n"
    "Tutto quello che aggiungerai al di fuori dell'importo verrà ignorato, "
    "quindi sentiti pure libero di inserire una qualsiasi "
    "descrizione riguardante il tuo acquisto."
)

HOW_TO_PAGE_THREE = (
    "Tieni presente che puoi cambiare, aggiungere o rimuovere l'importo di "
    "un <i>acquisto</i> in qualsiasi momento; per farlo ti basterà:\n"
    "   • cercare il messaggio relativo al tuo acquisto;\n"
    "   • cliccarci sopra (tasto destro del mouse se sei su <code>Telegram Desktop</code>);\n"
    "   • selezionare <b>Modifica</b>;\n"
    "   • dopo aver apportato le modifiche, confermare.\n\n"
    "Puoi persino convertire un post normale in un <i>acquisto</i> in maniera retroattiva, "
    "sempre con la stessa procedura: ti basterà taggare il post con <code>#ultimiacquisti</code> "
    "in fase di modifica del messaggio e provvederò ad aggiungere un acquisto a quella data."
)
