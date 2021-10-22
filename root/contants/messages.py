#!/usr/bin/env python3

""" This class contains all the messages used in the bot """

from datetime import datetime
from os import environ
from root.helper.notification import count_unread_notifications
from root.contants.VERSION import WISHLIST_VERSION
from root.model.user import User
from root.model.user_rating import UserRating
import root.util.logger as logger


def TODAY():
    T = datetime.now()
    return "%s/%s/%s" % ("%02d" % T.day, "%02d" % T.month, T.year)


BOT_NAME = environ["BOT_NAME"]

BOT_ID = environ["BOT_ID"]

VGS_GROUPS_PRIMARY_LINK = "https://t.me/joinchat/T8CJkZHor02rIzVy"

REPO_LINK = "https://github.com/VGsNETWORK/ultimi-acquisti"

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
    "<i><b>Ehi!</b>\nDurante la gestione del tuo messaggio si sono verificati degli errori."
    " I nostri sviluppatori sono stati informati:"
    " verranno risolti il prima possibile.</i>"
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
    "📚  Per maggiori informazioni sul mio utilizzo, <b>vai alla chat privata</b>!\n\n"
)

PLEASE_NOTE_APPEND = (
    "\n    <i><b><u>NOTA BENE</u>:</b>  Le funzioni di <b>aggiunta</b>, <b>modifica</b> e <b>rimozione</b>"
    f' degli acquisti sono fruibili <a href="{VGS_GROUPS_PRIMARY_LINK}"><u>solo all\'interno dei'
    " gruppi di VGs NETWORK</u></a>.</i>\n\n"
)

START_COMMANDS_LIST_HEADER = (
    "<u><b>LISTA DEI COMANDI</b></u>\n\n\n"
    "Questo è un riepilogo di tutti i comandi che supporto.\nTieni presente che alcuni di questi"
    " funzionano <b>solo nei gruppi</b> (👥), mentre altri funzionano anche qui, <b>in chat privata</b> (👤).\n"
    "<i>💡 Per lanciare un comando di gruppo da qui, clicca sul suggerimento ove indicato e seleziona un"
    f' <a href="{VGS_GROUPS_PRIMARY_LINK}"><u>gruppo in cui sono presente</u></a>: inserirò per te il comando nel campo di testo della chat indicata,'
    " così potrai completarlo con gli argomenti necessari e inviarlo in men che non si dica!</i>\n\n\n"
)

START_COMMAND_LIST_WARNING_ARGS = (
    "%0A%0A💡%20Sostituisci%20i%20campi%20in%20coda%20al%20modello%20del%20comando%20con%20i%20valori%20desiderati"
    "%2E%20Ricordati%20di%20togliere%20i%20simboli%20%22%3C%22%20e%20%22%3E%22%20e%20questo%20avviso%21"
)

START_COMMANDS_LIST = [
    (
        "<code>(👤)  </code><b>/howto</b>\n\n"
        "<i>Mostra una breve guida al mio utilizzo</i>\n\n\n"
    ),
    (
        f'<code>(👤)  </code><b>/ultimoacquisto</b>      (👥  <a href="https://t.me/share/url?url=%2Fultimoacquisto%40{BOT_NAME}">Invialo in un gruppo</a>)\n\n'
        f"<i>Ritrova il tuo ultimo acquisto</i>\n\n\n"
    ),
    (
        f'<code>(👤)  </code><b>/spesamensile</b>      (👥  <a href="https://t.me/share/url?url=%2Fspesamensile%40{BOT_NAME}">Invialo in un gruppo</a>)\n\n'
        "<i>Mostra la tua spesa totale per questo mese</i>\n\n\n"
    ),
    (
        f'<code>(👤)  </code><b>/reportmensile</b>      (👥  <a href="https://t.me/share/url?url=%2Freportmensile%40{BOT_NAME}">Invialo in un gruppo</a>)\n\n'
        "<i>Mostra un report dettagliato della tua spesa totale per questo mese</i>\n\n\n"
    ),
    (
        f'<code>(👥)  </code><b><a href="https://t.me/share/url?url=%2Fcomparamese%40{BOT_NAME}">/comparamese</a></b>\n'
        f'<code>      </code><b><a href="https://t.me/share/url?url=%2Fcomparamese%40{BOT_NAME}%20%3Cmese%3E{START_COMMAND_LIST_WARNING_ARGS}">/comparamese &lt;mese&gt;</a></b>\n'
        f'<code>      </code><b><a href="https://t.me/share/url?url=%2Fcomparamese%40{BOT_NAME}%20%3Cmese%3E%20%3Canno%3E{START_COMMAND_LIST_WARNING_ARGS}">/comparamese &lt;mese&gt; &lt;anno&gt;</a></b>\n\n'
        "<i>Metti a confronto la tua spesa mensile per il mese corrente con quella di un altro utente.\n"
        "Specifica opzionalmente un <b>mese</b> o un <b>mese + anno</b> diversi per effettuare l'operazione su periodi precedenti</i>  (richiede di <b>quotare un utente</b>)\n\n\n"
    ),
    (
        f'<code>(👤)  </code><b>/spesaannuale</b>      (👥  <a href="https://t.me/share/url?url=%2Fspesaannuale%40{BOT_NAME}">Invialo in un gruppo</a>)\n\n'
        "<i>Mostra la tua spesa totale per questo anno</i>\n\n\n"
    ),
    (
        f'<code>(👤)  </code><b>/reportannuale</b>      (👥  <a href="https://t.me/share/url?url=%2Freportannuale%40{BOT_NAME}">Invialo in un gruppo</a>)\n\n'
        "<i>Mostra un report dettagliato della tua spesa totale per questo anno</i>\n\n\n"
    ),
    (
        f'<code>(👥)  </code><b><a href="https://t.me/share/url?url=%2Fcomparaanno%40{BOT_NAME}">/comparaanno</a></b>\n'
        f'<code>      </code><b><a href="https://t.me/share/url?url=%2Fcomparaanno%40{BOT_NAME}%20%3Canno%3E{START_COMMAND_LIST_WARNING_ARGS}">/comparaanno &lt;anno&gt;</a></b>\n\n'
        f"<i>Metti a confronto la tua spesa annuale per l'anno corrente con quella di un altro utente.\n"
        "Specifica opzionalmente un <b>anno</b> diverso per effettuare l'operazione su anni precedenti</i>  (richiede di <b>quotare un utente</b>)\n\n\n"
    ),
    (
        f'<code>(👥)  </code><b><a href="https://t.me/share/url?url=%2Fcancellaspesa%40{BOT_NAME}">/cancellaspesa</a></b>\n\n'
        "<i>Rimuovi un acquisto dal tuo storico; <b>cancella anche il relativo post nel gruppo</b></i>  (richiede di <b>quotare un tuo acquisto</b>)\n\n\n"
    ),
    (
        f'<code>(👥)  </code><b><a href="https://t.me/share/url?url=%2Fcancellastorico%40{BOT_NAME}">/cancellastorico</a></b>\n\n'
        f"<i>Cancella il tuo storico degli acquisti per un gruppo</i>\n\n\n"
    ),
    (
        f"<code>(👤)  </code><b>/wishlist</b>\n\n"
        f"<i>Apri la tua lista dei desideri</i>\n\n\n"
    ),
    (
        f"<code>(👤)  </code><b>/impostazioni</b>\n\n"
        f"<i>Apri le impostazioni utente</i>\n\n\n"
    ),
    (
        f"<code>(👤)  </code><b>/info</b>\n\n"
        f"<i>Mostra i crediti e delle informazioni su questo progetto</i>\n\n\n"
    ),
    (f"<code>(👤)  </code><b>/vota</b>\n\n" f"<i>Dammi una valutazione</i>\n\n\n"),
]


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
    "\n💲 Puoi aggiungere un <b>prezzo</b> al tuo acquisto specificandolo nel messaggio."
)

PURCHASE_TITLE_HINT = (
    "\n🔤  Puoi aggiungere un <b>titolo</b> al tuo acquisto includendo"
    f' del testo tra <code>%...%</code>. Potrai visualizzarlo nel <b><a href="t.me/{BOT_NAME}?start=monthly_report">/reportmensile</a></b>.'
)

PURCHASE_EMPTY_TITLE_HINT = (
    "\n⚠🔤  <b>Volevi inserire un titolo, ma non sei sicuro su come procedere?</b>"
    " Ti basta racchiudere del testo tra <code>%...%</code>, ad esempio: <code>%Il mio titolo%</code>."
)

PURCHASE_DATE_HINT = (
    "\n📅  Puoi collocare il tuo acquisto nel passato"
    " specificando una <b>data</b> anteriore ad oggi nel formato <code>DD/MM/YY(YY)</code>."
)

PURCHASE_HINT_NO_HINT = "\n\n<i>Il tuo acquisto è completo. Niente male!</i>  😉"

PURCHASE_ADDED = "✅  <i>Acquisto aggiunto con successo!</i>"

PURCHASE_MODIFIED = "✅  <i>Acquisto modificato con successo!</i>"


def PURCHASE_RECAP_APPEND(
    price, title, date, dprice: bool = False, dtitle: bool = False, ddate: bool = False
):
    message = ""
    if price or title or date:
        message = "\n"
        if price:
            message += "\n💲 <b>Prezzo:</b>  <code>%s €</code>" % price
            message += "  (default)" if dprice else ""
        if date:
            message += "\n📅  <b>Data:</b>  <code>%s</code>" % date.strftime("%d/%m/%Y")
            message += "  (default)" if ddate else ""
        if title:
            message += '\n🔤  <b>Titolo:</b>  "<code>%s</code>"' % title
            message += "  (default)" if dtitle else ""
    return message


ONLY_PRIVATE = (
    "❌  La funzione  <code>%s</code>  è disponibile solo in <b>chat privata</b>!"
)


ONLY_GROUP = (
    "❌  La funzione  <code>%s</code>  è disponibile solo all'interno di un <b>gruppo</b>.\n\n"
    f'Assicurati di selezionarne <a href="{VGS_GROUPS_PRIMARY_LINK}"><b><u>uno in cui sono presente</u></b></a> e di'
    " <b>quotare prima il messaggio di un utente</b>!"
)

ONLY_GROUP_NO_QUOTE = (
    "❌  La funzione  <code>%s</code>  è disponibile solo all'interno di un <b>gruppo</b>.\n\n"
    f'Assicurati di selezionarne <a href="{VGS_GROUPS_PRIMARY_LINK}"><b><u>uno in cui sono presente</u></b></a>!'
)

ONLY_GROUP_QUOTE_SELF_PURCHASE = (
    "❌  La funzione  <code>%s</code>  è disponibile solo all'interno di un <b>gruppo</b>.\n\n"
    f'Assicurati di selezionarne <a href="{VGS_GROUPS_PRIMARY_LINK}"><b><u>uno in cui sono presente</u></b></a> e di'
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
PURCHASES_DELETED_APPEND = "<i>\n        – %s %s</i>"

# fmt: off
PURCHASE_DELETED = (
    '✅  <i><a href="tg://user?id=%s">%s</a>,</i>' 
    " %s <i>%s cancellato con successo!</i>"
)
# fmt: on

GROUP_NOT_ALLOWED = (
    "❌  <i>Questo gruppo non è abilitato al mio utilizzo.\n"
    "Puoi creare il tuo bot personale con il codice al seguente link:</i>\n\n"
    "https://github.com/VGsNETWORK/ultimi-acquisti"
)

NO_PURCHASE = (
    '⚠  <a href="tg://user?id=%s">%s</a>, '
    "<b>non hai ancora registrato alcun acquisto</b> su questo bot.\n\n"
    "Per aggiungerne uno, clicca il pulsante sottostante e seleziona un"
    f' <a href="{VGS_GROUPS_PRIMARY_LINK}"><b><u>gruppo in cui sono presente</u></b></a>: inserirò per te un <i>modello di acquisto</i> nel campo di testo della chat indicata,'
    " così potrai completarlo con i dati necessari e inviarlo in men che non si dica!"
)

NO_GROUP_PURCHASE = (
    '⚠  <a href="tg://user?id=%s">%s</a>, '
    "non hai registrato alcun acquisto in questo gruppo."
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
    "in data <b>%s alle %s</b>.%s\n\n"
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
    "<code>%s</code><code>%s €</code>             %s     (%s acquist%s)"
)

PURCHASE_REPORT_TEMPLATE = (
    '<code>%s</code><code>%s €</code>             <a href="https://t.me/c/%s/%s">%s</a>'
)

NEW_PURCHASE_LINK = "https://t.me/share/url?url=%23ultimiacquisti%20%3Cprezzo%3E%20{}%2F{}%2F{}%0A%0A%25%3Ctitolo%3E%25"

PURCHASE_REPORT_ADD_NEW_PURCHASE = '<code>%s</code>%s► <a href="%s">%s</a>'

REPORT_PURCHASE_TOTAL = "<code>%s</code><code>%s €</code>             <b>TOTALE</b>"

PURCHASE_DATE_ERROR = (
    '⚠️  <a href="tg://user?id=%s">%s</a>, l\'acquisto che stai tentando di registrare presenta una data futura o errata.'
    " Dal momento che non è possibile collocare un acquisto al futuro, questo"
    f" sarà aggiunto alla data di oggi, <b>{TODAY()}</b>.\n\n"
    "Vuoi continuare o annullare questo inserimento?"
)

PURCHASE_MODIFIED_DATE_ERROR = (
    '⚠️  <a href="tg://user?id=%s">%s</a>, l\'acquisto che stai modificando presenta una data futura o errata.'
    " Dal momento che non è possibile collocare un acquisto al futuro, questo"
    f" sarà spostato alla data di oggi, <b>{TODAY()}</b>.\n\n"
    "Accetti queste condizioni o preferisci eliminare l'acquisto?"
)

PURCHASE_DISCARDED = "✅  <i>Acquisto eliminato con successo.</i>"

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

NOT_MESSAGE_OWNER = "❌  Non puoi interagire con questo messaggio: la richiesta è stata fatta da un altro utente!"

SESSION_ENDED = (
    "❗️ SESSIONE DEL MESSAGGIO SCADUTA\nIl bot è stato aggiornato o riavviato per motivi tecnici."
    '\n\nPer continuare, digita "/" nella chat e seleziona un comando dalla lista.'
)

MESSAGE_TOO_OLD = (
    "❗️ SESSIONE DEL MESSAGGIO SCADUTA\n\nPer continuare, digita "
    '"/" nella chat e seleziona un comando dalla lista.'
)

HOW_TO_DEEP_LINK = (
    '<a href="tg://user?id=%s">%s</a>, per visualizzare la <b>guida all\'utilizzo</b> del bot...'
    ' <a href="t.me/%s?start=how_to"><b>clicca qui</b></a>!'
)

DEEP_LINK = '<a href="t.me/%s?start=%s">clicca qui</a>!'

HOW_TO_INTRODUCTION = (
    "<b><u>GUIDA</u>    ➔    INTRODUZIONE</b>\n\n\n"
    "Per far sì che io possa riconoscere un tuo acquisto"
    " è necessario che invii nel gruppo un messaggio di"
    ' qualsiasi tipo contenente l\'<b><u>hashtag</u></b> "<code>#ultimiacquisti</code>".\n'
    "Se il messaggio non è di tipo testuale, ma consiste in una (o più) <i>foto</i> o altro "
    "tipo di <i><b>medium</b></i> (<i>immagine non compressa</i>, <i>audio</i>, <i>file</i>, etc.), "
    "dovrai aggiungere il tag in <b>didascalia</b> ai suddetti media per renderli un acquisto legittimo."
)

HOW_TO_PRICE = (
    "<b><u>GUIDA</u>    ➔   💲 GESTIONE DEL PREZZO</b>\n\n\n"
    'Se oltre al tag "<code>#ultimiacquisti</code>" indicherai'
    " una cifra numerica assegnerò quell'importo come <b><u>prezzo</u></b>"
    " dell'<i>acquisto</i>. Nel caso in cui il testo – o la didascalia,"
    " in caso di media – presentasse più di una cifra, ricorda che prenderò"
    " in considerazione <u>soltanto la prima</u> trovata a partire dall'alto.\n"
    "Puoi inserire l'importo in molteplici formati; ecco alcuni di quelli riconosciuti:\n\n"
    "   •  <code>22</code>\n"
    "   •  <code>22,50 €</code>\n"
    "   •  <code>22.50</code>\n"
    "   •  <code>2250,10</code>\n"
    "   •  <code>€ 2,250.10</code>\n"
    "   •  <code>2.250,10€</code>\n"
    "   •  <code>2'250.10</code>\n\n"
    "Se invece ometti l'importo, salverò il tuo <i>acquisto</i> con un importo <i>di default</i>"
    " di  <code>0,00 €</code>; questo è utile per i regali, o se non vuoi rivelare il prezzo di un"
    " certo acquisto – tieni presente che in questo secondo caso la scelta si rifletterà"
    " sui totali mensili e annuali.\n\n"
    "<i>Tutto il testo in chiaro che aggiungerai al di fuori di prezzo, data e titolo verrà ignorato,"
    " quindi sentiti pure libero di inserire una qualsiasi descrizione riguardante il tuo acquisto.</i>"
)

HOW_TO_DATE = (
    "<b><u>GUIDA</u>    ➔    📅  ACQUISTI RETRODATATI</b>\n\n\n"
    'Se assieme al tag "<code>#ultimiacquisti</code>" espliciti una <b><u>data</u></b>'
    " anteriore ad oggi collocherò temporalmente l'<i>acquisto</i> a quel giorno. Tieni presente che:\n\n"
    "   •  i formati accettati per la data sono  <code>DD/MM/YYYY</code>"
    '  (<i>esempio:</i>  "<code>20/04/2021</code>") e  <code>DD/MM/YY</code>  (<i>esempio:</i>  "<code>20/04/21</code>")'
    " – altri formati saranno ignorati o potrebbero generare risultati indesiderati;\n"
    "   •  in caso di date multiple inserite correttamente, prenderò in considerazione <u>soltanto la prima</u> trovata a partire dall'alto.\n\n"
    "Se ometti la data, o ne inserisci una futura, il tuo <i>acquisto</i> sarà collocato"
    " <i>di default</i> alla data di oggi.\n\n"
    "<i>Tutto il testo in chiaro che aggiungerai al di fuori di prezzo, data e titolo verrà"
    " ignorato, quindi sentiti pure libero di inserire una qualsiasi descrizione riguardante il tuo acquisto.</i>"
)

HOW_TO_TITLE = (
    "<b><u>GUIDA</u>    ➔    🔤  DARE UN NOME ALL'ACQUISTO</b>\n\n\n"
    "Per facilitare il riconoscimento degli <i>acquisti</i> all'interno del <b>report mensile</b>"
    " ti è data facoltà di assegnare loro un breve <b><u>titolo</u></b> personalizzato; questo sarà"
    " mostrato alla destra dell'importo, al posto della stringa di default con data e ora di registrazione dell'acquisto.\n"
    'Per assegnare un titolo al tuo <i>acquisto</i>, tutto ciò che devi fare è inserire del testo racchiuso tra "<code>%...%</code>"'
    '  (<i>esempio:</i>  "<code>%Il mio acquisto%</code>").\n\n'
    "<i>Tutto il testo in chiaro che aggiungerai al di fuori di prezzo, data e titolo verrà ignorato, quindi sentiti pure libero di"
    " inserire una qualsiasi descrizione riguardante il tuo acquisto.</i>"
)

HOW_TO_MODIFY_A_PURCHASE = (
    "<b><u>GUIDA</u>    ➔    ✍🏻  MODIFICA DI UN ACQUISTO</b>\n\n\n"
    "Tieni presente che puoi <b>cambiare</b>, <b>aggiungere</b> o <b>rimuovere</b>"
    " le info di un <i>acquisto</i> in qualsiasi momento; per farlo ti basterà:\n\n"
    "   •  cercare il post relativo al tuo acquisto  (a tale scopo la <i>funzione di ricerca interna alla chat</i> di Telegram può tornarti utile);\n"
    "   •  cliccarci sopra  (tasto destro del mouse se sei su <code>Telegram Desktop</code>);\n"
    "   •  selezionare <b>Modifica</b>;\n"
    "   •  dopo aver apportato le modifiche desiderate al messaggio, confermare.\n\n"
    "💡 Puoi persino convertire un post normale in un <i>acquisto</i> in maniera retroattiva,"
    ' sempre con la stessa procedura: ti basterà taggare il post con "<code>#ultimiacquisti</code>" in fase di modifica del messaggio e,'
    " salvo diversamente specificato, provvederò ad aggiungere un acquisto alla data originale del post."
)

RATING_HEADER_MENU = "<b><u>VALUTAZIONE</u></b>\n\n\n"

USER_HAS_NO_VOTE = (
    "<i>Qui potrai dare un feedback approfondito su vari aspetti del bot, aggiungendo"
    " opzionalmente un commento per ogni area di competenza.\n"
    "💡 Tieni presente che un voto provvisto di commento avrà <b>più peso</b> nella <u>media pubblica</u>"
    "  (consultabile nella sezione  <b>[Menu principale]  &gt;  [Info]</b>) !</i>\n\n\n"
    "<b><i>Lo Staff si riserva il diritto di valutare e rimuovere eventuali"
    ' commenti non idonei al <a href="telegra.ph/Regolamento-del-gruppo-VGs-LOVE-07-03">'
    "regolamento</a>.</i></b>"
)

USER_ALREADY_VOTED = (
    "🗳  Hai %s%s%s.\n<i>%s</i>\n\n\n"
    "<b><i>Lo Staff si riserva il diritto di valutare e rimuovere eventuali commenti non idonei al"
    ' <a href="telegra.ph/Regolamento-del-gruppo-VGs-LOVE-07-03">regolamento</a>.</i></b>'
)

USER_ALREADY_VOTED_BOTH = (
    "Se effettui un'ulteriore votazione, la tua attuale recensione"
    " pendente verrà sostituita; inoltre, se la nuova recensione"
    " viene approvata, quest'ultima sostituirà quella attualmente pubblicata."
)

USER_ALREADY_VOTED_APPROVED = (
    "Se aggiorni la tua recensione, questa verrà sottoposta nuovamente a controllo da parte"
    " dello Staff; se questa viene poi approvata, la tua attuale recensione pubblicata "
    "verrà sostituita."
)

USER_MESSAGE_REVIEW_APPROVED_FROM_STAFF = (
    "👍🏻  La tua recensione <b>è stata approvata</b> dallo Staff. Grande!"
)

USER_MESSAGE_REVIEW_NOT_APPROVED_FROM_STAFF = (
    "👎🏻  La tua recensione <b>non è stata approvata</b> dallo Staff, pertanto <b>solo i voti</b>"
    " che hai assegnato sono stati mantenuti.\n\n"
    "💡 <i>Ricorda che le recensioni senza commenti hanno meno incidenza sulla <b>media pubblica</b>.</i>"
)

USER_ALREADY_VOTED_TO_APPROVE = "Se effettui un'altra votazione, la tua attuale recensione pendente verrà sostituita."

HOW_TO_INTRODUCTION = {
    "button_text": "Introduzione",
    "description": HOW_TO_INTRODUCTION,
}

HOW_TO_PRICE = {"button_text": "💲 Prezzo", "description": HOW_TO_PRICE}

HOW_TO_TITLE = {"button_text": "🔤  Titolo", "description": HOW_TO_TITLE}

HOW_TO_DATE = {"button_text": "📅  Data", "description": HOW_TO_DATE}

HOW_TO_MODIFY_A_PURCHASE = {
    "button_text": "✍🏻  Modifica di un acquisto",
    "description": HOW_TO_MODIFY_A_PURCHASE,
}

HOW_TO_PAGES = [
    HOW_TO_INTRODUCTION,
    HOW_TO_PRICE,
    HOW_TO_DATE,
    HOW_TO_TITLE,
    HOW_TO_MODIFY_A_PURCHASE,
]

FEEDBACK_SEND_MESSAGE = (
    "<b><u>SUPPORTO</u>    ➔    INVIA UN FEEDBACK</b>\n\n\n"
    "Digita il testo che vuoi inviare, "
    "<b>assicurandoti di inserire il tutto in un unico messaggio</b>, poi premi <i>Invio</i>:"
)

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


RATING_VALUES = [
    "Facilità di utilizzo",
    "Funzionalità",
    "Interfaccia utente",
    "Esperienza generale",
]

RATING_PLACEHOLDER = "<b>Dai un voto a...</b>"


def build_show_rating_message(rating: UserRating):
    ux_comment = (
        "<b>Non presente</b>" if not rating.ux_comment else f'"{rating.ux_comment}"'
    )
    ui_comment = (
        "<b>Non presente</b>" if not rating.ui_comment else f'"{rating.ui_comment}"'
    )
    functionality_comment = (
        "<b>Non presente</b>"
        if not rating.functionality_comment
        else f'"{rating.functionality_comment}"'
    )
    overall_comment = (
        "<b>Non presente</b>"
        if not rating.overall_comment
        else f'"{rating.overall_comment}"'
    )
    warning = (
        USER_ALREADY_VOTED_APPROVED
        if rating.approved
        else USER_ALREADY_VOTED_TO_APPROVE
    )
    header = "%s\n\n\n" % (
        "✅  <b><u>RECENSIONE PUBBLICATA</u></b>"
        if rating.approved
        else "⚖️  <b><u>RECENSIONE PENDENTE</u></b>"
    )

    return (
        f"{header}"
        "<b>Facilità di utilizzo</b>\n"
        f"– Voto:  {'⭐️' * rating.ux_vote}{'🕳' * (5 - rating.ux_vote)}\n"
        f"– Commento:  <i>{ux_comment}</i>\n\n"
        "<b>Funzionalità</b>\n"
        f"– Voto:  {'⭐️' * rating.functionality_vote}{'🕳' * (5 - rating.functionality_vote)}\n"
        f"– Commento:  <i>{functionality_comment}</i>\n\n"
        "<b>Interfaccia utente</b>\n"
        f"– Voto:  {'⭐️' * rating.ui_vote}{'🕳' * (5 - rating.ui_vote)}\n"
        f"– Commento:  <i>{ui_comment}</i>\n\n"
        "<b>Esperienza generale</b>\n"
        f"– Voto:  {'⭐️' * rating.overall_vote}{'🕳' * (5 - rating.overall_vote)}\n"
        f"– Commento:  <i>{overall_comment}</i>\n\n\n"
        f"<i>{warning}</i>\n\n"
        "<b><i>Lo Staff si riserva il diritto di valutare e rimuovere eventuali commenti non idonei al"
        ' <a href="telegra.ph/Regolamento-del-gruppo-VGs-LOVE-07-03">regolamento</a>.</i></b>'
    )


def build_approve_rating_message(rating: UserRating, user: User):
    user_id = user.user_id if isinstance(user, User) else user.id
    ux_comment = (
        "<b>Non presente</b>" if not rating.ux_comment else f'"{rating.ux_comment}"'
    )
    ui_comment = (
        "<b>Non presente</b>" if not rating.ui_comment else f'"{rating.ui_comment}"'
    )
    functionality_comment = (
        "<b>Non presente</b>"
        if not rating.functionality_comment
        else f'"{rating.functionality_comment}"'
    )
    overall_comment = (
        "<b>Non presente</b>"
        if not rating.overall_comment
        else f'"{rating.overall_comment}"'
    )

    return (
        f'L\'utente <a href="tg://user?id={user_id}">{user.first_name}</a>'
        " ha recensito il bot dando i seguenti voti:\n\n"
        "<b>Facilità di utilizzo</b>\n"
        f"– Voto:  {'⭐️' * rating.ux_vote}{'🕳' * (5 - rating.ux_vote)}\n"
        f"– Commento:  <i>{ux_comment}</i>\n\n"
        "<b>Funzionalità</b>\n"
        f"– Voto:  {'⭐️' * rating.functionality_vote}{'🕳' * (5 - rating.functionality_vote)}\n"
        f"– Commento:  <i>{functionality_comment}</i>\n\n"
        "<b>Interfaccia utente</b>\n"
        f"– Voto:  {'⭐️' * rating.ui_vote}{'🕳' * (5 - rating.ui_vote)}\n"
        f"– Commento:  <i>{ui_comment}</i>\n\n"
        "<b>Esperienza generale</b>\n"
        f"– Voto:  {'⭐️' * rating.overall_vote}{'🕳' * (5 - rating.overall_vote)}\n"
        f"– Commento:  <i>{overall_comment}</i>\n\n\n"
        "Vuoi approvarlo?"
    )


BULK_DELETE_MESSAGE_SINGLE_PURCHASE = (
    "Sei <b>davvero</b> sicuro di voler procedere?\n"
    "Se vai avanti, <b>cancellerai il tuo acquisto"
    " che hai registrato in questo gruppo</b> tramite @UltimiAcquistiBot."
    " Una volta confermata l'eliminazione, non potrai tornare alla situazione"
    " immediatamente precedente.\n\n<i>Vuoi <b>davvero</b> continuare?</i>\n\n<b>VITE RIMASTE:</b>  ❤️❤️💔"
)

BULK_DELETE_MESSAGE = [
    (
        "Hai deciso di <b>cancellare l'intero storico dei tuoi acquisti</b>.\n"
        "Questo <b>eliminerà dal tuo profilo tutti gli acquisti che hai salvato finora nel gruppo %s</b>."
        " <i>I post degli acquisti saranno invece mantenuti come parte della conversazione del gruppo</i> — potrai sempre"
        " decidere di cancellarli manualmente, se vorrai.\n\n"
        "Sei sicuro di voler procedere? <b>Questa azione è irreversibile.</b>\n\n"
        "<b>VITE RIMASTE:</b>  ❤️❤️❤️"
    ),
    (
        "Sei <b>davvero</b> sicuro di voler procedere?\n"
        "Se vai avanti, <b>cancellerai tutti %s %s"
        " acquisti che hai registrato in questo gruppo</b> tramite @UltimiAcquistiBot."
        " Una volta confermata l'eliminazione, non potrai tornare alla situazione"
        " immediatamente precedente.\n\n<i>Vuoi <b>davvero</b> continuare?</i>\n\n<b>VITE RIMASTE:</b>  ❤️❤️💔"
    ),
    (
        "<b>Ultima occasione</b> per ripensarci...\n\n"
        "<u><b><i>Se confermi ancora 1 volta, non potrai più tornare indietro.</i></b></u>\n\n"
        "<b>VITE RIMASTE:</b>  ❤️💔💔"
    ),
    "<b>*PUFF*</b>, tutti i tuoi acquisti sono spariti!!!",
]

BULK_DELETE_NO_PURCHASE = '<a href="tg://user?id=%s">%s</a>, non hai alcun acquisto da cancellare per questo gruppo.'

BULK_DELETE_CANCELLED = "✅  Cancellazione degli acquisti annullata."

WISHLIST_DESCRIPTION_TOO_LONG = "🚫  <b>Limite di 128 caratteri superato!</b>"

WISHLIST_TITLE_TOO_LONG = "🚫  <b>Limite di %s caratteri superato!</b>\n\n"

NO_ELEMENT_IN_WISHLIST = (
    "<i>In questa sezione potrai aggiungere dei promemoria relativi ad articoli che intendi acquistare in un secondo momento.</i>"
    "\n\n☹️  La tua lista dei desideri è vuota..."
)

NO_OTHER_WISHLISTS = "☹️  La tua lista dei desideri è vuota..."


WISHLIST_STEP_ONE = (
    "<b>Step 1:</b>\n<i><b><u>Testo e Foto</u></b>  ⟶  Link  ⟶  Categoria</i>\n\n"
)
WISHLIST_STEP_TWO = (
    "<b>Step 2:</b>\n<i>Testo e Foto  ⟶  <b><u>Link</u></b>  ⟶  Categoria</i>\n\n"
)
WISHLIST_STEP_THREE = (
    "<b>Step 3:</b>\n<i>Testo e Foto  ⟶  Link  ⟶  <b><u>Categoria</u></b></i>\n\n"
)

WISHLIST_EDIT_STEP_ONE = (
    "<b>Step 1:</b>\n<i><b><u>Testo</u></b>  ⟶  Link  ⟶  Categoria</i>\n\n"
)

WISHLIST_EDIT_STEP_ONE = "<b>Step 1:</b>\n<i><b><u>Testo</u></b>  ⟶  Categoria</i>\n\n"

WISHLIST_EDIT_STEP_TWO = (
    "<b>Step 2:</b>\n<i>Testo  ⟶  <b><u>Link</u></b>  ⟶  Categoria</i>\n\n"
)
WISHLIST_EDIT_STEP_THREE = (
    "<b>Step 3:</b>\n<i>Testo  ⟶  Link  ⟶  <b><u>Categoria</u></b></i>\n\n"
)

WISHLIST_EDIT_STEP_THREE = (
    "<b>Step 2:</b>\n<i>Testo  ⟶  <b><u>Categoria</u></b></i>\n\n"
)

ADD_TO_WISHLIST_PROMPT = (
    "Inserisci l'elemento da aggiungere alla lista dei"
    " desideri:\n"
    "   •  sono supportati sia del testo che altre <b>%s</b> foto;\n"
    "   •  se hai delle foto da aggiungere, assicurati di inserirle tutte prima del testo;\n"
    "   •  testo di massimo <b>128 caratteri</b>;\n"
    '   •  puoi indicare un  🎯 <b>prezzo target</b>  aggiungendo un numero tra "<code>%%...%%</code>";\n'
    "   •  testo su più righe non supportato.\n"
    "<b>Se l'elemento che vuoi aggiungere è un <u>link</u>, aspetta a inserirlo!</b>\n\n%s"
)

ADD_TO_WISHLIST_START_PROMPT = (
    "Inserisci l'elemento da aggiungere alla lista dei"
    " desideri:\n"
    "   •  sono supportati sia del testo che un massimo di <b>10 foto</b>;\n"
    "   •  se hai delle foto da aggiungere, assicurati di inserirle tutte prima del testo;\n"
    "   •  testo di massimo <b>128 caratteri</b>;\n"
    '   •  puoi indicare un  🎯 <b>prezzo target</b>  aggiungendo un numero tra "<code>%%...%%</code>";\n'
    "   •  testo su più righe non supportato.\n"
    "<b>Se l'elemento che vuoi aggiungere è un <u>link</u>, aspetta a inserirlo!</b>\n\n%s"
)

ADD_TO_WISHLIST_MAX_PHOTOS_PROMPT = (
    "Inserisci l'elemento da aggiungere alla lista dei"
    " desideri:\n"
    "   •  sono supportati <s>sia</s> del testo <s>che un massimo di 10 foto</s>;\n"
    "   •  testo di massimo <b>128 caratteri</b>;\n"
    '   •  puoi indicare un  🎯 <b>prezzo target</b>  aggiungendo un numero tra "<code>%%...%%</code>";\n'
    "   •  testo su più righe non supportato.\n"
    "<b>Se l'elemento che vuoi aggiungere è un <u>link</u>, aspetta a inserirlo!</b>\n\n%s"
)

ADD_TO_WISHLIST_ACTIVATE_CYCLE_INSERT_APPEND = "💡 <i>Attiva l'<b>inserimento ciclico</b> per inserire più elementi in sequenza!</i>"

ADD_TO_WISHLIST_DEACTIVATE_CYCLE_INSERT_APPEND = (
    "💡 <i>Disattiva l'<b>inserimento ciclico</b> se questo è l'ultimo elemento!</i>"
)

EDIT_WISHLIST_PROMPT = (
    "Inserisci il nuovo testo dell'elemento:\n"
    "   •  solo testo;\n"
    "   •  minimo <b>1 carattere</b> e massimo <b>128</b>;\n"
    "%s"
    "   •  testo su più righe non supportato.\n"
    "<b>Se il nuovo elemento che vuoi aggiungere è un <u>link</u>, aspetta a inserirlo!</b>"
)

EDIT_WISHLIST_PROMPT = (
    "Inserisci il nuovo testo dell'elemento:\n"
    "   •  solo testo;\n"
    "   •  minimo <b>1 carattere</b> e massimo <b>128</b>;\n"
    "%s"
    "   •  testo su più righe non supportato.\n"
    '<b>Se il nuovo elemento che vuoi aggiungere è un <i>link</i>, sfrutta la nuova <u>sezione link</u>  ("🔗")  dell\'elemento!</b>'
)

EDIT_WISHLIST_PROMPT_TARGET_PRICE = '   •  puoi indicare un nuovo  🎯 <b>prezzo target</b>  aggiungendo un numero tra "<code>%...%</code>"; se non specifichi niente, verrà mantenuto quello corrente;\n'

EDIT_WISHLIST_PROMPT_NO_TARGET_PRICE = '   •  puoi indicare un  🎯 <b>prezzo target</b>  aggiungendo un numero tra "<code>%...%</code>";\n'

EDIT_WISHLIST_TARGET_PRICE_PROMPT = "\n\n\n<b>LEGENDA</b>\n🎯  =  Prezzo target"

CYCLE_INSERT_ENABLED_APPEND = "\n\n🔄  <i><b>Inserimento ciclico</b> attivo!</i>"


ADDED_TO_WISHLIST = "\n✅  <i>Elemento aggiunto con successo!</i>"

WISHLIST_CHANGED = "✅  <i><b>%s</b> spostato nella lista <b>%s</b>!</i>"


USER_SETTINGS_HEADER = "<b><u>IMPOSTAZIONI</u></b>\n\n\n"

USER_SETTINGS_MESSAGE = (
    f"{USER_SETTINGS_HEADER}<i>In questa sezione potrai "
    "modificare il modo in cui mi comporterò in alcune situazioni.</i>\n\n"
    "<b>Suggerimenti di acquisto</b>\nIn fase di aggiunta di un acquisto,"
    " mostra dei consigli relativi a dettagli che non hai inserito e che servono"
    " a integrare il tuo acquisto."
)

EDIT_LINK_TO_WISHLIST_ITEM_MESSAGE = (
    "Se vuoi che il tuo elemento riporti a una pagina web diversa da quella precedente, puoi inserirne ora il link:\n"
    "   •  sono ammessi solamente link;\n"
    "   •  in caso di link multipli immessi, prenderò in considerazione soltanto il primo%s."
)

EDIT_WISHLIST_LINK_EXISTING_PHOTOS = (
    ";\n   •  se l'URL inserito fa parte di quelli supportati per il <i>download "
    "automatico delle foto</i>, <u><b>tutte le foto attualmente salvate per questo elemento"
    " verranno sostituite da quelle nuove</b></u>"
)

EDIT_WISHLIST_LINK_NO_PHOTOS = (
    ";\n   •  se l'URL inserito fa parte di quelli supportati per il <i>download automatico delle "
    "foto</i>, sarà aggiunto un numero di foto compatibile al numero di slot liberi nell'album.\n\n"
    "🆕  <b>Da oggi, aggiungendo un prodotto da uno dei seguenti <i>siti supportati</i> potrai avere"
    ' il <i>download automatico delle sue foto</i> nell\'<u>album</u>  ("🖼")'
    '  e il <i>tracking del prezzo</i> e della sua disponibilità nella <u>sezione link</u>  ("🔗"):</b>'
    "\n   •  gamestop.it;\n   •  multiplayer.com;\n   •  store.playstation.com."
)

SUPPORTED_LINKS_MESSAGE = (
    "🆕  Da oggi i seguenti siti supportano il download automatico delle foto:\n\n"
    "  •  GameStop.it ;\n\n"
    "Aggiungi ora un link al prodotto e lascia che sia io a occuparmi delle scartoffie!"
)

EDIT_CATEGORY_TO_WISHLIST_ITEM_MESSAGE = "Seleziona una nuova categoria per il tuo elemento, conferma quella attuale oppure creane una personalizzata:"

ADD_LINK_TO_WISHLIST_ITEM_MESSAGE = (
    "Se vuoi che il tuo elemento riporti a una pagina web, puoi inserirne qui il link:\n"
    "   •  sono ammessi solamente link;\n"
    "   •  sono supportati un massimo di <b>10</b> link;\n"
    "   •  in caso di link multipli immessi nello stesso messaggio, prenderò in considerazione soltanto il primo%s"
)

ADD_CATEGORY_TO_WISHLIST_ITEM_MESSAGE = (
    "Seleziona una categoria per il tuo elemento, oppure creane una nuova:"
)

MONTHLY_REPORT_POPUP_MESSAGE = (
    "Il report mensile ti dà un resoconto degli"
    " acquisti effettuati nel mese corrente,"
    " con la possibilità di spostarti avanti"
    " e indietro di un mese, 12 mesi o di un"
    " intervallo prefissato di anni."
)


YEARLY_REPORT_POPUP_MESSAGE = (
    "Il report annuale ti dà un resoconto"
    " degli acquisti effettuati nell'anno"
    " corrente, con la possibilità di spostarti"
    " avanti e indietro di un singolo anno o di"
    " un intervallo prefissato di anni."
)


VIEW_WISHLIST_PHOTO_MESSAGE = "Hai aggiunto  <code>%s</code>  foto per <b>%s</b>."

VIEW_NO_WISHLIST_PHOTO_MESSAGE = "Qui puoi aggiungere delle foto per <b>%s</b>."

REQUEST_WISHLIST_PHOTO = "Invia adesso <u><b>come foto</b></u> (non come <i>file</i>) le immagini che vuoi aggiungere per <b>%s</b>:"

WISHLIST_PHOTO_LIMIT_REACHED = "\n\n<i><b>Limite massimo di foto raggiunto!</b>\nSe vuoi aggiungerne di nuove, devi prima eliminarne qualcuna.</i>"

SINGLE_WISHLIST_PHOTO_ADDED = "\n\n✅  <i><b>%s foto</b> aggiunta con successo!</i>"

ASK_FOR_PHOTOS_PREPEND = "<i>Foto inviate finora:</i>  <code>%s</code> / 10"


ASK_FOR_CONVERT_WISHLIST = (
    "<b>Vuoi continuare?</b>\n"
    "<i>Questa azione è irreversibile, "
    "e <b><u>cancellerà sia l'elemento che le sue "
    "foto</u></b> dalla lista dei desideri.</i>\n"
    "⚠️  <i>Dal momento che il template di acquisto che "
    "verrà creato se procedi <b><u>non può ereditare delle "
    "foto</u></b>, ti ho inviato qui sopra tutte quelle che hai "
    "aggiunto per questo elemento per darti la possibilità "
    "di salvarle e allegarle al futuro post di acquisto.</i>"
)

WISHLIST_HEADER = f"<b><u>%sLISTA DEI DESIDERI</u></b>     (Versione:  <code>{WISHLIST_VERSION}</code>)\n\n\n"


# TODO: create query to retrieve all number of all wishlist_element items and all photos
DELETE_ALL_WISHLIST_ITEMS_MESSAGE = (
    f"{WISHLIST_HEADER}<b>%s element%s, %s foto</b>\n🚮  "
    "<i>Stai per cancellare <b>tutti gli elementi</b> e <b>tutte le foto</b> della lista dei desideri"
    "</i>\n\n<b>Vuoi confermare?</b>"
)

DELETE_ALL_WISHLIST_ITEMS_NO_PHOTO_MESSAGE = (
    f"{WISHLIST_HEADER}<b>%s element%s</b>\n🚮  "
    "<i>Stai per cancellare <b>tutti gli elementi</b> della lista dei desideri"
    "</i>\n\n<b>Vuoi confermare?</b>"
)

DELETE_ALL_WISHLIST_ITEMS_AND_LIST_MESSAGE = (
    f"{WISHLIST_HEADER}<b>%s%s%s</b>\n🚮  "
    "<i>Stai per cancellare questa lista dei desideri%s"
    "</i>\n\n<b>Vuoi confermare?</b>"
)

DELETE_WISHLIST_ITEMS_AND_PHOTOS_APPEND = (
    " e <b>tutti gli elementi e le foto</b> al suo interno"
)

DELETE_WISHLIST_ITEMS_APPEND = " e <b>tutti gli elementi</b> al suo interno"

DELETE_ALL_WISHLIST_ITEMS_PHOTOS = (
    "<b>%s foto</b>\n"
    "🚮  <i>Stai per cancellare <b>tutte le foto</b> aggiunte per <b>%s</b>.</i>\n\n"
    "<b>Vuoi confermare?</b>"
)

AD_MESSAGE_ONE = (
    "Sapevi che puoi <b>registrare e tracciare i tuoi acquisti</b> in questo gruppo?\n"
    "Per farlo ti basta inviare un messaggio di qualsiasi tipo (testo, foto compressa o "
    'non, file, etc.) contenente l\'<b>hashtag</b> "<code>#ultimiacquisti</code>"!\n\n\n'
    "💡 <i>Per maggiori informazioni sul mio funzionamento, "
    f'<a href="t.me/{BOT_NAME}?start=how_to">clicca qui</a> e poi su "<b>AVVIA</b>".</i>'
)

AD_MESSAGE_TWO = (
    "Ehi tu... sì, proprio tu col portafogli bucato... "
    "scommetto che ti farebbe comodo un modo per <b>annotare gli articoli che ti interessano</b> "
    "senza il timore di perderli... beh, non disperare: da oggi puoi farlo!\n"
    f'<a href="t.me/{BOT_NAME}?start=wishlist"><b>Clicca qui</b></a> (e poi su "<b>AVVIA</b>") '
    "per imbrigliare il tuo prossimo affare!\n\n\n"
    "💡 <i>Per maggiori informazioni sul mio funzionamento, invece, "
    f'<a href="t.me/{BOT_NAME}?start=how_to">clicca qui</a> e poi su "<b>AVVIA</b>".</i>'
)

AD_MESSAGE_THREE = (
    "Come dici? La voce interiore della tua coscienza si sta chiedendo se questo mese ce la farai a pagare le bollette?\n"
    "Riafferra ORA il <b>controllo delle tue finanze</b> con il comando <code>/spesamensile</code>!\n\n\n"
    "💡 <i>Per maggiori informazioni sull'utilizzo di questo comando, "
    f'<a href="t.me/{BOT_NAME}?start=command_list_3">clicca qui</a> e poi su "<b>AVVIA</b>".</i>\n\n'
    "💡 <i>Per maggiori informazioni sul mio funzionamento, invece, "
    f'<a href="t.me/{BOT_NAME}?start=how_to">clicca qui</a> e poi su "<b>AVVIA</b>".</i>'
)

AD_MESSAGE_FOUR = (
    "Quest'anno avresti tanto voluto fare quella cosa... "
    "sai bene a cosa mi riferisco... quella cosa lì che tieni in pausa da anni!\n"
    "Lancia subito il comando <code>/spesaannuale</code> per fare il punto"
    " della situazione e vedere se ci riuscirai! Tifo per te 🤞🏻!\n\n\n"
    "💡 <i>Per maggiori informazioni sull'utilizzo di questo comando, "
    f'<a href="t.me/{BOT_NAME}?start=command_list_6">clicca qui</a> e poi su "<b>AVVIA</b>".</i>\n\n'
    "💡 <i>Per maggiori informazioni sul mio funzionamento, invece, "
    f'<a href="t.me/{BOT_NAME}?start=how_to">clicca qui</a> e poi su "<b>AVVIA</b>".</i>'
)

ADS_MESSAGES = [AD_MESSAGE_ONE, AD_MESSAGE_TWO, AD_MESSAGE_THREE, AD_MESSAGE_FOUR]


MALFORMED_VALID_LINK_APPEND = (
    "\n\n\n%s\n\n⚠️  <i>Il dominio web inserito SUPPORTA il <b>download automatico delle foto</b>,"
    " ma la pagina indicata è inesistente oppure non conforme al pattern richiesto.</i>"
)

NOT_SUPPORTED_LINK_APPEND = "\n\n\n%s\n\n⚠️  <i>Il dominio web inserito NON SUPPORTA il <b>download automatico delle foto</b>.</i>"

NOT_SUPPORTED_LINKS_APPEND = "\n\n\n⚠️  <i>NESSUNO dei domini web inseriti supporta il <b>download automatico delle foto</b>.</i>"

ADD_WISHLIST_TITLE_PROMPT = (
    "Inserisci il nome della nuova lista dei desideri:\n"
    "   •  solo testo;\n"
    "   •  massimo <b>%s caratteri</b>;\n"
    "   •  testo su più righe non supportato.\n"
)

EDIT_WISHLIST_TITLE_PROMPT = (
    "<code>%s</code>\n✏️  <i>Stai rinominando questa lista</i>\n\n"
    "Inserisci il nuovo nome della lista dei desideri:\n"
    "   •  solo testo;\n"
    "   •  massimo <b>%s caratteri</b>;\n"
    "   •  testo su più righe non supportato.\n"
)


WISHLIST_LIST_MESSAGE = (
    "Questo è il menu di <i>gestione delle liste dei desideri</i>. Puoi avere fino a "
    "<b>10</b> liste dei desideri in contemporanea.\n"
    "Di seguito trovi elencate quelle che possiedi al momento: <i>clicca</i> "
    "sul nome di una lista per <b>aprirla</b>, oppure premi i pulsanti sottostanti "
    "per eseguire varie azioni contestuali.\n\n\n"
    "<b>LEGENDA</b>"
    "%s"
    "\n✏️  =  <b>Rinomina la lista</b>"
    "%s"
    "\n\n"
    "<i>ALTRO</i>\n"
    "📌  =  Lista predefinita\n"
    "✅  =  Lista selezionata"
    "%s"
)

WISHLIST_LIST_LEGEND_REMOVE_ALL = "\n🗑  =  <b>Elimina la lista</b> (previa conferma)"

WISHLIST_LIST_LEGEND_HAS_ELEMENTS = "\n🗂  =  Elementi nella lista"

WISHLIST_LIST_LEGEND_HAS_PHOTOS = "\n🖼  =  Foto nella lista"

WISHLIST_LIST_LEGEND_REORDER_UP = "\n🔺  =  <b>Sposta su</b> la lista"

WISHLIST_LIST_LEGEND_REORDER_DOWN = "\n🔻  =  <b>Sposta giù</b> la lista"

WISHLIST_LIST_LEGEND_REMOVE_ONLY_ITEMS = (
    "\n🌬  =  <b>Svuota la lista</b> (previa conferma)"
)

WISHLIST_LEGEND_APPEND_LEGEND = "\n\n\n<b>LEGENDA</b>\n"

WISHLIST_LEGEND_APPEND_FIRST_PAGE = (
    "<code>🤍 🔄 🛍</code>  =  <b>Converti l'elemento in un acquisto</b> (previa conferma)\n"
    "<code>   🗑   </code>  =  <b>Elimina l'elemento</b> da questa lista (previa conferma)\n"
)


WISHLIST_LEGEND_APPEND_SECOND_PAGE = (
    "<code>   🖼   </code>  =  <b>Gestisci le foto</b> per l'elemento\n"
    "<code>   🔗   </code>  =  <b>Gestisci i link</b> per l'elemento\n"
)

WISHLIST_LEGEND_APPEND_THIRD_PAGE = (
    "<code>   ✏️   </code>  =  <b>Modifica l'elemento</b>\n"
    "<code>   🔀   </code>  =  <b>Sposta l'elemento</b> in un'altra lista"
)

WISHLIST_LEGEND_APPEND_SECOND_PAGE_ONLY = (
    "🖼  =  <b>Gestisci le foto</b> per l'elemento\n"
    "🔗  =  <b>Gestisci i link</b> per l'elemento\n"
)

WISHLIST_LEGEND_APPEND_THIRD_PAGE_ONLY = (
    "✏️  =  <b>Modifica l'elemento</b>\n"
    "🔀  =  <b>Sposta l'elemento</b> in un'altra lista"
)

CHANGE_ELEMENT_WISHLIST_MESSAGE = (
    f"{WISHLIST_HEADER}"
    "<b>%s</b>  <b>%s</b>     %s\n"
    "🔀  <i>Stai per spostare questo elemento in un'altra lista</i>\n\n"
    "Seleziona la lista dei desideri di destinazione:"
)


ADD_NEW_LINK_MESSAGE = (
    f"{WISHLIST_HEADER}%sInvia adesso i link che vuoi aggiungere per <b>%s</b>:\n\n"
    "🆕  <b>Da oggi, aggiungendo un prodotto da uno dei seguenti <i>siti supportati</i> potrai avere"
    ' il <i>download automatico delle sue foto</i> nell\'<u>album</u>  ("🖼")'
    "  e il <i>tracking del prezzo</i> e della sua disponibilità:</b>"
    "\n   •  gamestop.it;\n   •  multiplayer.com;\n   •  store.playstation.com."
)


ADD_NEW_LINK_MESSAGE_NUMBER_OF_NEW_LINK = (
    "<i>Link inviati finora:</i>  <code>%s</code> / %s\n"
)

ADD_NEW_LINK_MESSAGE_NUMBER_OF_NEW_PHOTOS = "\n\n\n✅  <i><b>%s</b> foto scaricat%s!</i>"


WISHLIST_LINK_LIMIT_REACHED = "\n\n\n<i><b>Limite massimo di link raggiunto!</b>\nSe vuoi aggiungerne di nuovi, devi prima eliminarne qualcuno.</i>"

WISHLIST_LINK_LEGEND_APPEND = (
    "\n\n\n<b>LEGENDA</b>\n" "💹  =  <b>Tracking del prezzo abilitato</b>\n"
)
WISHLIST_LINK_LEGEND_APPEND_VARIATION = (
    "📈  =  <b>Prezzo salito</b> rispetto all'<i>offerta migliore di sempre</i><b>*</b>\n"
    "➖  =  <b>Prezzo invariato</b> rispetto all'<i>offerta migliore di sempre</i><b>*</b>\n"
    "📉  =  <b>Prezzo sceso</b> rispetto all'<i>offerta migliore di sempre</i><b>*</b>\n\n"
    "<b>*</b> <i>il prezzo più basso raggiunto dal prodotto da quando hai iniziato a tracciarlo</i>"
)


DEAL_MESSAGE_FORMAT = (
    '💥  <b><a href="%s">%s</a></b> è appena sceso di <code>%s €</code>,'
    " e adesso puoi trovarlo a <code>%s €</code>."
)

DEAL_MESSAGE_FORMAT = (
    '💥  <b><a href="%s">%s</a></b> '
    "è stato appena scontato a  <code>%s €</code>  (<b>–%s €</b>)!"
)

DEAL_MESSAGE_FORMAT = (
    '💥  <b><a href="%s">%s</a></b> '
    "è stato appena scontato del %s% e puoi trovarlo a %s  €"
)

DEAL_MESSAGE_FORMAT = (
    '💥  <b><a href="%s">%s</a></b> è stato '
    "appena scontato del <b>%s%%</b> (<i>–%s €</i>), "
    "e ora puoi trovarlo a  <code>%s €</code>!%s"
)


DEAL_MESSAGE_FORMAT_APPEND = " <b>Non fartelo scappare!</b>"

PRICE_MESSAGE_POPUP = (
    ": :   %s   : :\n\n"
    "PREZZO ATTUALE:\n      %s   (%s)*\n"
    "%s"
    "\n\n* Offerta migliore di sempre prec.te:\n      %s"
)

PRICE_MESSAGE_POPUP_NO_VARIATION = ": :   %s   : :\n\n" "PREZZO ATTUALE:\n      %s%s"

WISHLIST_ELEMENT_PRICE_OUTDATED_WARNING = (
    "\n\n<b>* <i><u>NOTA BENE</u>:</i></b>  <i>Il prezzo o le info visualizzati "
    'per il prodotto potrebbero non essere aggiornati. Apri la <b>sezione link</b>  ("🔗")  '
    "del relativo elemento per aggiornarli.</i>"
)


TRACKED_LINK_EXPLANATION = (
    "<i>Dato che hai dei <b>link compatibili con il <u>tracking del prezzo</u></b> per questo elemento, "
    "in calce al messaggio trovi allegate le <b>offerte migliori del momento</b>!\n"
    "In più, <b>cliccando sul prezzo</b> potrai avere le informazioni aggiornate sulla disponibilità del prodotto in oggetto!</i>\n"
)

USER_INFO_RECAP_LEGEND = (
    "<b>LEGENDA</b>\n"
    "🗃  =  Liste dei desideri\n"
    "🗂  =  Elementi\n"
    "🖼  =  Foto\n"
    "🔗  =  Link\n"
    "💹  =  Link tracciati\n"
)


NEW_CATEGORY_MESSAGE = (
    "✍🏻  <i>Stai inserendo una nuova categoria</i>\n\n"
    "Inserisci il nome della nuova categoria personalizzata:\n"
    "   •  solo testo;\n"
    "   •  minimo <b>1 carattere testuale</b> e massimo <b>%s</b>;\n"
    "   •  è necessario inserire un'<b>emoji</b> in testa al nome;\n"
    "   •  testo su più righe non supportato.\n"
)

TOO_LONG_NEW_CATEGORY_MESSAGE = (
    "Inserisci il nome della nuova categoria personalizzata:\n"
    "   •  solo testo;\n"
    "   •  minimo <b>1 carattere testuale</b> e massimo <b>%s</b>;\n"
    "   •  è necessario inserire un'<b>emoji</b> in testa al nome;\n"
    "   •  testo su più righe non supportato.\n"
)

CATEGORY_NAME_TOO_LONG = "🚫  <b>Limite di %s caratteri superato!</b>"

NO_EMOJI_FOUND = "☑️  <b>Emoji in testa</b> \n✅  Almeno 1 carattere testuale"

NO_CATEGORY_NAME_FOUND = "✅  Emoji in testa \n☑️  <b>Almeno 1 carattere testuale</b>"

CATEGORY_NAME_TOO_LONG_WITH_EMOJI = (
    "✅  Emoji in testa \n🚫  <b>Limite di %s caratteri superato!</b>"
)

CATEGORY_NAME_TOO_LONG_WITHOUT_EMOJI = (
    "☑️  <b>Emoji in testa</b> \n🚫  <b>Limite di %s caratteri superato!</b>"
)

YOU_ARE_CREATING_A_NEW_CATEGORY = "✍🏻  <i>Stai inserendo una nuova categoria</i>"

YOU_ARE_MODIFYING_THIS_ELEMENT = "✏️  <i>Stai modificando questo elemento</i>"

PRODUCT_TYPE = {True: "formato digitale", False: "formato fisico"}

PRODUCT_DEAL = "<code>    </code><b>Scontato del %s%% fino alle %s del %s</b>  •  "

NOTIFICATION_CREATED_ITEM_MESSAGE = (
    'Elemento "<i>%s</i>" (%s)%screato nella lista dei desideri "<i>%s</i>".'
)

NOTIFICATION_CREATED_ITEM_LINK_APPEND = "➕  %s link:"

NOTIFICATION_CREATED_ITEM_PHOTOS_APPEND = "➕  %s foto"

NOTIFICATION_MODIFIED_ITEM_MESSAGE = (
    'Elemento "<i>%s</i>" (%s)%sdella lista dei desideri "<i>%s</i>" modificato:%s'
)

NOTIFICATION_MODIFIED_TITLE = '    ✏️  nome cambiato in "<i>%s</i>"'

NOTIFICATION_MODIFIED_CATEGORY = '    ✏️  categoria cambiata in "<i>%s</i>"'

NOTIFICATION_MODIFIED_ITEM_LINK_APPEND = "▪️ %s link:"

NOTIFICATION_MODIFIED_ITEM_PHOTOS_APPEND = "▪️ %s foto"

NOTIFICATION_WIPED_WISHLIST_ELEMENTS = (
    'Lista dei desideri "<i>%s</i>" (%s element%s%s) svuotata.'
)

NOTIFICATION_DELETED_WISHLIST = 'Lista dei desideri "<i>%s</i>" (%s element%s%s) eliminata.\nIl numero di liste residuo è %s.'

NOTIFICATION_DELETED_WISHLIST_NO_ELEMENTS = (
    'Lista dei desideri "<i>%s</i>" eliminata.\nIl numero di liste residuo è %s.'
)

NOTIFICATION_NEW_WISHLIST = (
    'Lista dei desideri "<i>%s</i>" creata.\nIl nuovo numero di liste è %s.'
)

NOTIFICATION_REORDER_WISHLIST_UP = 'Lista dei desideri "<i>%s</i>" spostata sopra "<i>%s</i>".\nIl nuovo ordine delle liste è:\n%s'

NOTIFICATION_REORDER_WISHLIST_DOWN = 'Lista dei desideri "<i>%s</i>" spostata sotto "<i>%s</i>".\nIl nuovo ordine delle liste è:\n%s'


NOTIFICATION_WISHLIST_NAME_CHANGED = (
    'Lista dei desideri "<i>%s</i>" rinominata in "<i>%s</i>".'
)


NOTIFICATION_WISHLIST_ELEMENT_MOVED = (
    'Elemento "<i>%s</i>" spostato dalla lista "<i>%s</i>" alla lista "<i>%s</i>".'
)

NOTIFICATION_ELEMENT_CONVERTED = (
    'Elemento "<i>%s</i>" della lista dei desideri "<i>%s</i>"'
    ' convertito in un acquisto; <a href="%s">questo è il link</a> per registrarlo.'
)

NOTIFICATION_ELEMENT_DELETED = (
    'Elemento "<i>%s</i>" della lista dei desideri "<i>%s</i>" cancellato.'
)

NOTIFICATION_MULTIPLE_ELEMENTS_REMOVED = (
    'Elementi:\n%s\ndella lista dei desideri "<i>%s</i>" cancellati.'
)


def build_show_notification_button(user: User):
    unread = count_unread_notifications(user.id)
    if unread:
        if unread == 1:
            text = f"📬  {unread} nuova notifica"
        else:
            text = f"📬  {unread} nuove notifiche"
    else:
        text = "📭  Nessuna notifica da leggere"
    return text


NOTIFICATION_WISHLIST_CHANGED = (
    'La lista dei desideri attiva è stata cambiata da "<i>%s</i>" a "<i>%s</i>".'
)

BOT_ADDED_WELCOME_MESSAGE = (
    "Ciao <b>%s</b>, grazie per avermi aggiunto!"
    "\n\nSono <b>#ultimiacquisti</b>, un <b>bot di gestione"
    " della spesa personale</b>, e potete usarmi per registrare i vostri acquisti recenti"
    " e passati e tracciarli nel tempo."
    "%s<b>Buon utilizzo!</b>"
)

BOT_ADDED_WELCOME_APPEND = (
    "\n\n🏁  Per iniziare, <b>inviate</b> o <b>modificate</b> un messaggio di qualunque"
    ' tipo aggiungendo l\'hashtag "<code>#ultimiacquisti</code>"...\n\n'
    "📚  Per maggiori informazioni sul mio utilizzo, <b>andate alla chat privata</b>!\n\n"
)

PREMIUM_DEALS_MESSAGES = {
    "Playstation Store": {
        "PLUS": (
            "<code>    </code><b>GRATIS per gli utenti"
            ' <a href="https://www.playstation.com/it-it/ps-plus/">PS Plus</a> fino alle %s del %s</b>  •  '
        ),
        "NOW": (
            "<code>    </code><b>GRATIS per gli utenti"
            ' <a href="https://www.playstation.com/it-it/ps-now/">PS Now</a> fino alle %s del %s</b>  •  '
        ),
    }
}

PREMIUM_HOME_DEALS_MESSAGES = {
    "Playstation Store": {
        "PLUS": (
            "\n<b>GRATIS per gli utenti"
            ' <a href="https://www.playstation.com/it-it/ps-plus/">PS Plus</a></b>'
        ),
        "NOW": (
            "\n<b>GRATIS per gli utenti"
            ' <a href="https://www.playstation.com/it-it/ps-now/">PS Now</a></b>'
        ),
    }
}
