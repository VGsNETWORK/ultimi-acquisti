#!/usr/bin/env python3

""" This class contains all the messages used in the bot """

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
    "Sono un <b>bot di gestione della spesa personale</b>, e puoi usarmi per registrare"
    " i tuoi acquisti recenti e passati e tracciarli nel tempo.\n"
    "La funzioni di aggiunta, modifica e rimozione degli acquisti sono"
    " utilizzabili solo all'interno dei gruppi di @VGsNETWORK (@VGsGROUPS),"
    " luogo dove puoi anche comparare la tua spesa di un certo periodo con quella"
    " degli altri utenti, nonché vederne i rispettivi acquisti.\n\n"
    "Buon utilizzo!"
)

START_COMMANDS_LIST = (
    "\n\n\n<b>LISTA COMANDI</b>\n\n\n\n"
    '<a href="https://t.me/share/url?text=%2Fhowto@UltimiAcquistiBot">/howto</a>\n\n'
    "Mostra una breve guida all'utilizzo del bot\n\n\n"
    '<a href="https://t.me/share/url?text=%2Fultimoacquisto@UltimiAcquistiBot">'
    "/ultimoacquisto</a>\n\n"
    "Ritrova il tuo ultimo acquisto\n\n\n"
    '<a href="https://t.me/share/url?text=%2Fspesamensile@UltimiAcquistiBot">/spesamensile</a>\n\n'
    "Mostra la tua spesa totale per questo mese\n\n\n"
    '<a href="https://t.me/share/url?text=%2Freportmensile@UltimiAcquistiBot">'
    "/reportmensile</a>\n\n"
    "Mostra un report dettagliato della tua spesa totale per questo mese\n\n\n"
    '<a href="https://t.me/share/url?text=%2Fcomparamese@UltimiAcquistiBot">/comparamese</a>\n\n'
    "Metti a confronto la tua spesa mensile con quella di un altro utente"
    " (funziona solo nei <b>gruppi</b> e richiede di <b>quotare un utente</b>)\n\n\n"
    '<a href="https://t.me/share/url?text=%2Fcomparamese@UltimiAcquistiBot%20%3CMM%2FYYYY%3E">'
    "/comparamese &lt;MM/YYYY&gt;</a>\n\n"
    "Specifica un mese e un anno per cui eseguire <code>comparamese</code>\n\n\n"
    '<a href="https://t.me/share/url?text=%2Fspesaannuale@UltimiAcquistiBot">/spesaannuale</a>\n\n'
    "Mostra la tua spesa totale per questo anno\n\n\n"
    '<a href="https://t.me/share/url?text=%2Freportannuale@UltimiAcquistiBot">'
    "/reportannuale</a>\n\n"
    "Mostra un report dettagliato della tua spesa totale per questo anno\n\n\n"
    '<a href="https://t.me/share/url?text=%2Fcomparaanno@UltimiAcquistiBot">/comparaanno</a>\n\n'
    "Metti a confronto la tua spesa annuale con quella di un altro utente"
    " (funziona solo nei <b>gruppi</b> e richiede di <b>quotare un utente</b>)\n\n\n"
    '<a href="https://t.me/share/url?text=%2Fcomparaanno@UltimiAcquistiBot%20%3CYYYY%3E">'
    "/comparaanno &lt;YYYY&gt;</a>\n\n"
    "Specifica un mese e un anno per cui eseguire <code>comparaanno</code>\n\n\n"
    '<a href="https://t.me/share/url?text=%2Fcancellaspesa@UltimiAcquistiBot">'
    "/cancellaspesa</a>\n\n"
    "Rimuovi un acquisto dal tuo storico; cancella anche il relativo post"
    " (funziona solo nei <b>gruppi</b> e richiede di <b>quotare un tuo acquisto</b>)"
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

PURCHASE_HEADER_HINT = "\n\n\nLo sapevi che...?"

PURCHASE_PRICE_HINT = (
    "\n\n💲  Puoi aggiungere un prezzo al tuo acquisto specificandolo nel messaggio."
)

PURCHASE_TITLE_HINT = (
    "\n\n🔠  Puoi aggiungere un titolo al tuo acquisto includendo"
    " del testo tra <code>%...%</code>."
)

PURCHASE_DATE_HINT = (
    "\n\n📅  Puoi collocare retroattivamente il tuo acquisto"
    " specificando una data antecedente nel formato <code>DD/MM/YYYY</code>."
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
