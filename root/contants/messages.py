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
    "ℹ️  Per maggiori informazioni sul mio utilizzo, <b>vai alla chat privata</b>!\n\n"
)

PLEASE_NOTE_APPEND = (
    "\n<b>N.B.:</b> Le funzioni di <b>aggiunta</b>, <b>modifica</b> e <b>rimozione</b>"
    " degli acquisti sono fruibili <u>solo all'interno dei"
    " gruppi di <b>VGs NETWORK</b></u> (@VGsGROUPS).\n\n"
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
    f'<code>(👤)  </code>/ultimoacquisto      (<a href="https://t.me/share/url?url=%2Fultimoacquisto%40{BOT_NAME}">Invialo in un gruppo</a> 👥)\n\n'
    f"<i>Ritrova il tuo ultimo acquisto</i>\n\n\n"
    f'<code>(👤)  </code>/spesamensile      (<a href="https://t.me/share/url?url=%2Fspesamensile%40{BOT_NAME}">Invialo in un gruppo</a> 👥)\n\n'
    "<i>Mostra la tua spesa totale per questo mese</i>\n\n\n"
    f'<code>(👤)  </code>/reportmensile      (<a href="https://t.me/share/url?url=%2Freportmensile%40{BOT_NAME}">Invialo in un gruppo</a> 👥)\n\n'
    "<i>Mostra un report dettagliato della tua spesa totale per questo mese</i>\n\n\n"
    f'<code>(👥)  </code><a href="https://t.me/share/url?url=%2Fcomparamese%40{BOT_NAME}">/comparamese</a>\n'
    f'<code>      </code><a href="https://t.me/share/url?url=%2Fcomparamese%40{BOT_NAME}%20%3Cmese%3E">/comparamese &lt;mese&gt;</a>\n'
    f'<code>      </code><a href="https://t.me/share/url?url=%2Fcomparamese%40{BOT_NAME}%20%3Cmese%3E%20%3Canno%3E">/comparamese &lt;mese&gt; &lt;anno&gt;</a>\n\n'
    "<i>Metti a confronto la tua spesa mensile per il mese corrente con quella di un altro utente.\n"
    "Specifica opzionalmente un <b>mese</b> o un <b>mese + anno</b> diversi per effettuare l'operazione su periodi precedenti</i> (richiede di <b>quotare un utente</b>)\n\n\n"
    f'<code>(👤)  </code>/spesaannuale      (<a href="https://t.me/share/url?url=%2Fspesaannuale%40{BOT_NAME}">Invialo in un gruppo</a> 👥)\n\n'
    "<i>Mostra la tua spesa totale per questo anno</i>\n\n\n"
    f'<code>(👤)  </code>/reportannuale      (<a href="https://t.me/share/url?url=%2Freportannuale%40{BOT_NAME}">Invialo in un gruppo</a> 👥)\n\n'
    "<i>Mostra un report dettagliato della tua spesa totale per questo anno</i>\n\n\n"
    f'<code>(👥)  </code><a href="https://t.me/share/url?url=%2Fcomparaanno%40{BOT_NAME}">/comparaanno</a>\n'
    f'<code>      </code><a href="https://t.me/share/url?url=%2Fcomparaanno%40{BOT_NAME}%20%3Canno%3E">/comparaanno &lt;anno&gt;</a>\n\n'
    f"<i>Metti a confronto la tua spesa annuale per l'anno corrente con quella di un altro utente.\n"
    "Specifica opzionalmente un <b>anno</b> diverso per effettuare l'operazione su anni precedenti</i> (richiede di <b>quotare un utente</b>)\n\n\n"
    f'<code>(👥)  </code><a href="https://t.me/share/url?url=%2Fcancellaspesa%40{BOT_NAME}">/cancellaspesa</a>\n\n'
    "<i>Rimuovi un acquisto dal tuo storico; cancella anche il relativo post</i> (richiede di <b>quotare un tuo acquisto</b>)"
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

PURCHASE_PRICE_HINT = "\n💲  Puoi aggiungere un <b>prezzo</b> al tuo acquisto specificandolo nel messaggio."

PURCHASE_TITLE_HINT = (
    "\n🔠  Puoi aggiungere un <b>titolo</b> al tuo acquisto includendo"
    f' del testo tra <code>%...%</code>. Potrai visualizzarlo nel <b><a href="t.me/{BOT_NAME}?start=monthly_report">/reportmensile</a></b>.'
)

PURCHASE_EMPTY_TITLE_HINT = (
    "\n⚠🔠  <b>Volevi inserire un titolo, ma non sei sicuro su come procedere?</b>"
    " Ti basta racchiudere del testo tra <code>%...%</code>, ad esempio: <code>%Il mio titolo%</code>."
)

PURCHASE_DATE_HINT = (
    "\n📅  Puoi collocare retroattivamente il tuo acquisto"
    " specificando una <b>data</b> antecedente ad oggi nel formato <code>DD/MM/YYYY</code>."
)

PURCHASE_HINT_NO_HINT = "\n\n\n😉  Il tuo acquisto è completo. Niente male!"

PURCHASE_ADDED = "✅  <i>Acquisto aggiunto con successo!</i>"

PURCHASE_MODIFIED = "✅  <i>Acquisto modificato con successo!</i>"

ONLY_GROUP = (
    "❌  La funzione <code>%s</code> è disponibile solo all'interno di un <b>gruppo</b>.\n\n"
    "Assicurati di selezionarne uno <u><b>in cui sono presente</b></u> e di"
    " <b>quotare prima il messaggio di un utente</b>!"
)

ONLY_GROUP_NO_QUOTE = (
    "❌  La funzione <code>%s</code> è disponibile solo all'interno di un <b>gruppo</b>.\n\n"
    "Assicurati di selezionarne uno <u><b>in cui sono presente</b></u>!"
)

ONLY_GROUP_QUOTE_SELF_PURCHASE = (
    "❌  La funzione <code>%s</code> è disponibile solo all'interno di un <b>gruppo</b>.\n\n"
    "Assicurati di selezionarne uno <u><b>in cui sono presente</b></u> e di"
    " <b>quotare prima un tuo <u>acquisto</u></b>!"
)

CANCEL_PURCHASE_ERROR = (
    '❌  <a href="tg://user?id=%s">%s</a>,'
    " per cancellare un tuo acquisto devi <b>quotarlo</b>!"
)

NOT_A_PURCHASE = (
    '❌  <a href="tg://user?id=%s">%s</a>,'
    " il messaggio che hai quotato non è un acquisto valido!\n\n"
    "Per essere riconosciuto, un <i>acquisto</i> deve contenere"
    ' l\'hashtag "<code>#ultimiacquisti</code>".'
)

PURCHASE_NOT_FOUND = (
    '❌  <a href="tg://user?id=%s">%s</a>, non riesco a'
    " trovare l'acquisto che hai fatto..."
)

PURCHASES_DELETED = (
    '✅  <i><a href="tg://user?id=%s">%s</a>,'
    " hai cancellato %s acquisti con successo!</i>"
)
PURCHASES_DELETED_APPEND = "<i>\n        - <b>%s</b> del <b>%s</b></i>"

PURCHASE_DELETED = (
    '✅  <i><a href="tg://user?id=%s">%s</a>,'
    " <b>%s</b> del <b>%s</b> cancellato con successo!</i>"
)

GROUP_NOT_ALLOWED = (
    "❌  Questo gruppo non è abilitato all'utilizzo di questo bot.\n"
    "Puoi creare il tuo bot personale con il codice al seguente link:\n\n"
    "https://gitlab.com/nautilor/ultimi-acquisti"
)

NO_PURCHASE = (
    '⚠  <a href="tg://user?id=%s">%s</a>, '
    "non hai ancora registrato alcun acquisto su questo bot."
)

NOT_YOUR_PURCHASE = (
    '❌  <a href="tg://user?id=%s">%s</a>, '
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

YEAR_PURCHASE_TEMPLATE = (
    "<code>%s</code><code>%s €</code>             %s   (%s acquist%s)"
)

PURCHASE_REPORT_TEMPLATE = (
    '<code>%s</code><code>%s €</code>             <a href="https://t.me/c/%s/%s">%s</a>'
)

REPORT_PURCHASE_TOTAL = "<code>%s</code><code>%s €</code>             <b>TOTALE</b>"

PURCHASE_DATE_ERROR = (
    '✅  <a href="tg://user?id=%s">%s</a>, il tuo acquisto è stato aggiunto con successo.\n\n\n'
    "❗️ Tuttavia, la data che hai indicato presenta una delle seguenti anomalie:\n\n"
    "   –  non rispetta il formato <code>DD/MM/YYYY</code>;\n"
    "   –  è una data futura,\n\n"
    "per questo motivo ho collocato l'acquisto alla data di oggi."
)

MONTH_COMPARE_PRICE = (
    "Nel mese di <b>%s</b>...\n\n"
    '- <a href="tg://user?id=%s">%s</a>, hai speso  <code>%s €</code>\n'
    "- <i>%s</i> ha speso  <code>%s €</code>\n\n"
)

YEAR_COMPARE_PRICE = (
    "Nel <b>%s</b>...\n\n"
    '- <a href="tg://user?id=%s">%s</a>, hai speso  <code>%s €</code>\n'
    "- <i>%s</i> ha speso  <code>%s €</code>\n\n"
)

COMPARE_YOU_WON = "🥳  Hai <b>VINTO</b> di  <code>%s €</code>!"

COMPARE_HE_WON = "😞  Hai <b>perso</b> di  <code>%s €</code>..."

COMPARE_TIE = "💸  I vostri portafogli sono ugualmente leggeri..."

COMPARE_NO_PURCHASE = "Nessuno dei due ha effettuato acquisti finora... 😡"

COMPARE_WRONG_YEAR = (
    '❌  <a href="tg://user?id=%s">%s</a>,'
    " l'anno indicato per la funzione <code>%s</code> (<b>%s</b>) supera quello corrente!\n\n"
    "💡 <i>Per maggiori informazioni sull'utilizzo di questo comando,"
    f' <a href="t.me/{BOT_NAME}?start=command_list">clicca qui</a>.</i>'
)

COMPARE_WRONG_MONTH = (
    '❌  <a href="tg://user?id=%s">%s</a>,'
    " il mese indicato per la funzione <code>%s</code> (<b>%s</b>) supera quello corrente!\n\n"
    "💡 <i>Per maggiori informazioni sull'utilizzo di questo comando,"
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
    '❌  <a href="tg://user?id=%s">%s</a>, hai inserito troppi argomenti per la funzione <code>%s</code>.\n\n'
    "💡 <i>Per maggiori informazioni sull'utilizzo di questo comando,"
    f' <a href="t.me/{BOT_NAME}?start=command_list">clicca qui</a>.</i>'
)

COMMAND_FORMAT_ERROR = (
    '❌  <a href="tg://user?id=%s">%s</a>, "<b>%s</b>"'
    " non rispetta il formato corretto per la funzione <code>%s</code>.\n\n"
    "💡 <i>Per maggiori informazioni sull'utilizzo di questo comando,"
    f' <a href="t.me/{BOT_NAME}?start=command_list">clicca qui</a>.</i>'
)

NO_QUOTE_YOURSELF = (
    '❌  <a href="tg://user?id=%s">%s</a>,'
    " non puoi lanciare questo comando <b>quotando un tuo messaggio</b>!"
)

NO_QUOTE_BOT = (
    '❌  <a href="tg://user?id=%s">%s</a>,'
    " non puoi lanciare questo comando <b>quotando un bot</b>!"
)

NO_QUOTE_FOUND = (
    '❌  <a href="tg://user?id=%s">%s</a>,'
    " per lanciare questo comando prova a <b>quotare un utente</b>..."
)

NOT_MESSAGE_OWNER = "❌  Non puoi navigare tra i report di un altro utente!"

SESSION_ENDED = (
    "❗️ Il bot è stato aggiornato o riavviato per motivi tecnici, pertanto la sessione"
    ' di questo messaggio è scaduta.\n\nPer continuare, digita "/" nella chat e seleziona'
    " un comando dalla lista."
)

HOW_TO_DEEP_LINK = (
    '<a href="tg://user?id=%s">%s</a>, per visualizzare la guida all\'utilizzo del bot...'
    ' <a href="t.me/%s?start=how_to">clicca qui</a>!'
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

FEEDBACK_SEND_MESSAGE = "Digita il testo che vuoi inviare, assicurandoti di inserire il tutto in un unico messaggio, poi premi Invia:"

FEEDBACK_FROM_MESSAGE = "Feedback da %s (ID utente: <code>%s</code>):\n\n<i>%s</i>"

MONTH_REPORT_FUNNY_APPEND = (
    "💡 <i>Ricordi cosa hai acquistato il <b>{}</b>? Era{} o era{}?\n"
    "Facciamo un po' di chiarezza aggiungendo dei titoli ai tuoi acquisti,"
    " così avrai il pieno controllo del tuo storico in un batter d'occhio!\n"
    "Per farlo, clicca sulla data di un acquisto e"
    ' modificalo aggiungendo del testo tra "<code>%...%</code>".</i>'
)

RANDOM_ITEM_LIST = [
    "no delle banane",
    " un ratto",
    "no dei maccheroni",
    " la nonna",
    " un casco",
    " del giallo",
    "no delle corde di violino",
    " uno spoiler 👀",
    " del legname",
    " un martello",
    " una gonna",
    " un panino",
    " una baguette",
    "no dei croissant",
    " un uovo",
    " un uovo sodo",
    " dell'uva",
    " una scimmia",
    " una cipolla",
    " un 4",
    " una mucca",
    " un programmatore JavaScript",
    "no delle sneakers",
    " un Alt+Canc",
    " l'ultimo modello di smartphone",
]

CANNOT_MODIFY_OTHERS_SETTINGS = (
    "❌  Non puoi modificare le impostazioni di un altro utente!"
)

MESSAGE_DELETION_FUNNY_APPEND = [
    " Fuggite, sciocchi!",
    " That'll escalate quickly.",
    " Much hurry.",
]

MESSAGE_EDIT_TIMEOUT = "\n\n\n🕒  <i>Verrai reindirizzato/a alla homepage tra %s.</i>"

MESSAGE_DELETION_TIMEOUT = (
    "\n\n\n🕒  <i>Questo messaggio si autodistruggerà tra %s.<b>%s</b></i>"
)
