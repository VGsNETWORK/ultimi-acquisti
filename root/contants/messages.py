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
    " degli acquisti sono fruibili <u>solo all'interno dei"
    " gruppi di <b>VGs NETWORK</b></u> (@VGsGROUPS).\n\n"
)


START_COMMANDS_LIST = (
    "\n\n<u><b>LISTA COMANDI</b></u>\n\n"
    "Tieni presente che alcuni comandi funzionano <b>solo nei gruppi</b> (👥), mentre per altri rispondo sia nei gruppi, sia qui (👤).\n"
    "Per lanciare un comando di gruppo da qui, clicca sul suggerimento ove indicato e seleziona un <u>gruppo in cui sono presente</u>: inserirò per te il comando nel campo di testo della chat indicata, così potrai inviarlo in men che non si dica!\n\n\n"
    "(👤)   /howto\n\n"
    "<i>Mostra una breve guida all'utilizzo del bot</i>\n\n\n"
    f'(👤)   /ultimoacquisto      (<a href="https://t.me/share/url?text=%2Fultimoacquisto%40{BOT_NAME}">Invialo in un gruppo</a> 👥)\n\n'
    "<i>Ritrova il tuo ultimo acquisto</i>\n\n\n"
    f'(👤)   /spesamensile      (<a href="https://t.me/share/url?text=%2Fspesamensile%40{BOT_NAME}">Invialo in un gruppo</a> 👥)\n\n'
    "<i>Mostra la tua spesa totale per questo mese</i>\n\n\n"
    f'(👤)   /reportmensile      (<a href="https://t.me/share/url?text=%2Freportmensile%40{BOT_NAME}">Invialo in un gruppo</a> 👥)\n\n'
    "<i>Mostra un report dettagliato della tua spesa totale per questo mese</i>\n\n\n"
    f'(👥)   <a href="https://t.me/share/url?text=%2Fcomparamese%40{BOT_NAME}">/comparamese</a>\n'
    f'(👥)   <a href="https://t.me/share/url?text=%2Fcomparamese%40{BOT_NAME}%20%3CMM%2FYYYY%3E">/comparamese &lt;MM/YYYY&gt;</a>\n\n'
    "<i>Metti a confronto la tua spesa mensile con quella di un altro utente, specificando opzionalmente un mese e un anno diversi da quelli correnti (funziona solo nei <b>gruppi</b> e richiede di <b>quotare un utente</b>)</i>\n\n\n"
    f'(👤)   /spesaannuale      (<a href="https://t.me/share/url?text=%2Fspesaannuale%40{BOT_NAME}">Invialo in un gruppo</a> 👥)\n\n'
    "<i>Mostra la tua spesa totale per questo anno</i>\n\n\n"
    f'(👤)   /reportannuale      (<a href="https://t.me/share/url?text=%2Freportannuale%40{BOT_NAME}">Invialo in un gruppo</a> 👥)\n\n'
    "<i>Mostra un report dettagliato della tua spesa totale per questo anno</i>\n\n\n"
    f'(👥)   <a href="https://t.me/share/url?text=%2Fcomparaanno%40{BOT_NAME}">/comparaanno</a>\n'
    f'(👥)   <a href="https://t.me/share/url?text=%2Fcomparaanno%40{BOT_NAME}%20%3CYYYY%3E">/comparaanno &lt;YYYY&gt;</a>\n\n'
    "<i>Metti a confronto la tua spesa annuale con quella di un altro utente, specificando opzionalmente un anno diverso da quello corrente (funziona solo nei <b>gruppi</b> e richiede di <b>quotare un utente</b>)</i>\n\n\n"
    f'(👥)   <a href="https://t.me/share/url?text=%2Fcancellaspesa%40{BOT_NAME}">/cancellaspesa</a>\n\n'
    "<i>Rimuovi un acquisto dal tuo storico; cancella anche il relativo post (funziona solo nei <b>gruppi</b> e richiede di <b>quotare un tuo acquisto</b>)</i>"
)

START_COMMANDS_LIST = (
    "\n\n\n<u><b>LISTA COMANDI</b></u>\n\n"
    "Questo è un riepilogo di tutti i comandi supportati dal bot.\nTieni presente che alcuni di questi"
    " funzionano <b>solo nei gruppi</b> (👥), mentre altri funzionano anche qui, <b>in chat privata</b> (👤).\n"
    "💡 Per lanciare un comando di gruppo da qui, clicca sul suggerimento ove indicato e seleziona un"
    " <u>gruppo in cui sono presente</u>: inserirò per te il comando nel campo di testo della chat indicata,"
    " così potrai completarlo con gli argomenti necessari e inviarlo in men che non si dica!\n\n\n"
    "<code>(👤)  </code>/howto\n\n"
    "<i>Mostra una breve guida all'utilizzo del bot</i>\n\n\n"
    f'<code>(👤)  </code>/ultimoacquisto      (<a href="https://t.me/share/url?text=%2Fultimoacquisto%40{BOT_NAME}">Invialo in un gruppo</a> 👥)\n\n'
    f"<i>Ritrova il tuo ultimo acquisto</i>\n\n\n"
    f'<code>(👤)  </code>/spesamensile      (<a href="https://t.me/share/url?text=%2Fspesamensile%40{BOT_NAME}">Invialo in un gruppo</a> 👥)\n\n'
    "<i>Mostra la tua spesa totale per questo mese</i>\n\n\n"
    f'<code>(👤)  </code>/reportmensile      (<a href="https://t.me/share/url?text=%2Freportmensile%40{BOT_NAME}">Invialo in un gruppo</a> 👥)\n\n'
    "<i>Mostra un report dettagliato della tua spesa totale per questo mese</i>\n\n\n"
    f'<code>(👥)  </code><a href="https://t.me/share/url?text=%2Fcomparamese%40{BOT_NAME}">/comparamese</a>\n'
    f'<code>      </code><a href="https://t.me/share/url?text=%2Fcomparamese%40{BOT_NAME}%20%3Cmese%3E">/comparamese &lt;mese&gt;</a>\n'
    f'<code>      </code><a href="https://t.me/share/url?text=%2Fcomparamese%40{BOT_NAME}%20%3Cmese%3E%20%3Canno%3E">/comparamese &lt;mese&gt; &lt;anno&gt;</a>\n\n'
    "<i>Metti a confronto la tua spesa mensile per il mese corrente con quella di un altro utente.\n"
    "Specifica opzionalmente un <b>mese</b> o un <b>mese + anno</b> diversi per effettuare l'operazione su periodi precedenti</i> (richiede di <b>quotare un utente</b>)\n\n\n"
    f'<code>(👤)  </code>/spesaannuale      (<a href="https://t.me/share/url?text=%2Fspesaannuale%40{BOT_NAME}">Invialo in un gruppo</a> 👥)\n\n'
    "<i>Mostra la tua spesa totale per questo anno</i>\n\n\n"
    f'<code>(👤)  </code>/reportannuale      (<a href="https://t.me/share/url?text=%2Freportannuale%40{BOT_NAME}">Invialo in un gruppo</a> 👥)\n\n'
    "<i>Mostra un report dettagliato della tua spesa totale per questo anno</i>\n\n\n"
    f'<code>(👥)  </code><a href="https://t.me/share/url?text=%2Fcomparaanno%40{BOT_NAME}">/comparaanno</a>\n'
    f'<code>      </code><a href="https://t.me/share/url?text=%2Fcomparaanno%40{BOT_NAME}%20%3Canno%3E">/comparaanno &lt;anno&gt;</a>\n\n'
    f"<i>Metti a confronto la tua spesa annuale per l'anno corrente con quella di un altro utente.\n"
    "Specifica opzionalmente un <b>anno</b> diverso per effettuare l'operazione su anni precedenti</i> (richiede di <b>quotare un utente</b>)\n\n\n"
    f'<code>(👥)  </code><a href="https://t.me/share/url?text=%2Fcancellaspesa%40{BOT_NAME}">/cancellaspesa</a>\n\n'
    "<i>Rimuovi un acquisto dal tuo storico; cancella anche il relativo post</i> (richiede di <b>quotare un tuo acquisto</b>)"
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

MONTH_PREVIOUS_PURCHASES_SAME = (
    "➖ Anche a <i>%s</i> hai speso un totale di <code>%s €</code>."
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

YEAR_PREVIOUS_PURCHASES_SAME = (
    "➖ Anche nel <i>%s</i> hai speso un totale di <code>%s €</code>."
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
    " del testo tra <code>%...%</code>. Potrai visualizzarlo nel <b>/reportmensile</b>."
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
    "in data <b>%s alle %s</b>.\n\n"
    'Puoi vederlo <a href="https://t.me/c/%s/%s">cliccando qui</a>!'
)

LAST_PURCHASE_USER = (
    "<i>%s</i> ha effettuato il suo ultimo acquisto in data <b>%s alle %s</b>.\n\n"
    'Puoi vederlo <a href="https://t.me/c/%s/%s">cliccando qui</a>!'
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

COMPARE_WRONG_YEAR = (
    '❌  <a href="tg://user?id=%s">%s</a>,'
    " l'anno indicato per la funzione <code>%s</code> (<b>%s</b>) supera quello corrente!\n\n\n"
    "<i>Per maggiori informazioni sull'utilizzo di questo comando,"
    f' <a href="t.me/{BOT_NAME}?start=command_list">clicca qui</a>.</i>'
)

COMPARE_WRONG_MONTH = (
    '❌  <a href="tg://user?id=%s">%s</a>,'
    " il mese indicato per la funzione <code>%s</code> (<b>%s</b>) supera quello corrente!\n\n\n"
    "<i>Per maggiori informazioni sull'utilizzo di questo comando,"
    f' <a href="t.me/{BOT_NAME}?start=command_list">clicca qui</a>.</i>'
)

COMPARE_MONTH_NOT_VALID = (
    '❌  <a href="tg://user?id=%s">%s</a>,'
    ' "<b>%s</b>" non è un mese valido per la funzione <code>%s</code>!\n\n'
    '<i>💡 Prova con "<b>%s</b>" o "<b>%s</b>".</i>'
)

COMPARE_YEAR_NOT_VALID = (
    '❌  <a href="tg://user?id=%s">%s</a>,'
    ' "<b>%s</b>" non è un anno valido per la funzione <code>%s</code>!'
)

TOO_MANY_ARGUMENTS = (
    '❌  <a href="tg://user?id=%s">%s</a>, hai inserito troppi argomenti per la funzione <code>%s</code>.\n\n\n'
    "<i>Per maggiori informazioni sull'utilizzo di questo comando,"
    f' <a href="t.me/{BOT_NAME}?start=command_list">clicca qui</a>.</i>'
)

COMMAND_FORMAT_ERROR = (
    '❌  <a href="tg://user?id=%s">%s</a>, "<b>%s</b>"'
    " non rispetta il formato corretto per la funzione <code>%s</code>.\n\n\n"
    "<i>Per maggiori informazioni sull'utilizzo di questo comando,"
    f' <a href="t.me/{BOT_NAME}?start=command_list">clicca qui</a>.</i>'
)

NO_QUOTE_YOURSELF = "Non puoi lanciare questo comando quotando un tuo messaggio!"

NO_QUOTE_BOT = "Non puoi lanciare questo comando quotando un bot!"

NO_QUOTE_FOUND = "Per lanciare questo comando prova a quotare un utente..."

NOT_MESSAGE_OWNER = "Non puoi navigare tra i report di un altro utente!"

SESSION_ENDED = (
    "Il bot è stato riavviato per motivi tecnici, la sessione "
    "di questo messaggio è scaduta."
)

HOW_TO_DEEP_LINK = (
    '<a href="tg://user?id=%s">%s</a>, per visualizzare la guida all\'utilizzo del bot '
    '<a href="t.me/%s?start=how_to">clicca qui</a>.'
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

FEEDBACK_SEND_MESSAGE = "Scrivi il messaggio che vuoi inviare, poi premi Invia:"

FEEDBACK_FROM_MESSAGE = "Feedback da %s (ID utente: <code>%s</code>):\n\n<i>%s</i>"
