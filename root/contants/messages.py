#!/usr/bin/env python3

""" This class contains all the messages used in the bot """

from datetime import datetime
from os import environ
from root.contants.VERSION import WISHLIST_VERSION
from root.model.user import User
from root.model.user_rating import UserRating
import root.util.logger as logger

TODAY = datetime.now()
TODAY = "%s/%s/%s" % ("%02d" % TODAY.day, "%02d" % TODAY.month, TODAY.year)

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

START_COMMANDS_LIST_HEADER = (
    "\n\n\n<u><b>LISTA COMANDI</b></u>\n\n"
    "Questo è un riepilogo di tutti i comandi supportati dal bot.\nTieni presente che alcuni di questi"
    " funzionano <b>solo nei gruppi</b> (👥), mentre altri funzionano anche qui, <b>in chat privata</b> (👤).\n"
    "💡 Per lanciare un comando di gruppo da qui, clicca sul suggerimento ove indicato e seleziona un"
    " <u>gruppo in cui sono presente</u>: inserirò per te il comando nel campo di testo della chat indicata,"
    " così potrai completarlo con gli argomenti necessari e inviarlo in men che non si dica!\n\n\n"
)

START_COMMANDS_LIST = [
    (
        "<code>(👤)  </code>/howto\n\n"
        "<i>Mostra una breve guida all'utilizzo del bot</i>\n\n\n"
    ),
    (
        f'<code>(👤)  </code>/ultimoacquisto      (<a href="https://t.me/share/url?url=%2Fultimoacquisto%40{BOT_NAME}">Invialo in un gruppo</a> 👥)\n\n'
        f"<i>Ritrova il tuo ultimo acquisto</i>\n\n\n"
    ),
    (
        f'<code>(👤)  </code>/spesamensile      (<a href="https://t.me/share/url?url=%2Fspesamensile%40{BOT_NAME}">Invialo in un gruppo</a> 👥)\n\n'
        "<i>Mostra la tua spesa totale per questo mese</i>\n\n\n"
    ),
    (
        f'<code>(👤)  </code>/reportmensile      (<a href="https://t.me/share/url?url=%2Freportmensile%40{BOT_NAME}">Invialo in un gruppo</a> 👥)\n\n'
        "<i>Mostra un report dettagliato della tua spesa totale per questo mese</i>\n\n\n"
    ),
    (
        f'<code>(👥)  </code><a href="https://t.me/share/url?url=%2Fcomparamese%40{BOT_NAME}">/comparamese</a>\n'
        f'<code>      </code><a href="https://t.me/share/url?url=%2Fcomparamese%40{BOT_NAME}%20%3Cmese%3E">/comparamese &lt;mese&gt;</a>\n'
        f'<code>      </code><a href="https://t.me/share/url?url=%2Fcomparamese%40{BOT_NAME}%20%3Cmese%3E%20%3Canno%3E">/comparamese &lt;mese&gt; &lt;anno&gt;</a>\n\n'
        "<i>Metti a confronto la tua spesa mensile per il mese corrente con quella di un altro utente.\n"
        "Specifica opzionalmente un <b>mese</b> o un <b>mese + anno</b> diversi per effettuare l'operazione su periodi precedenti</i> (richiede di <b>quotare un utente</b>)\n\n\n"
    ),
    (
        f'<code>(👤)  </code>/spesaannuale      (<a href="https://t.me/share/url?url=%2Fspesaannuale%40{BOT_NAME}">Invialo in un gruppo</a> 👥)\n\n'
        "<i>Mostra la tua spesa totale per questo anno</i>\n\n\n"
    ),
    (
        f'<code>(👤)  </code>/reportannuale      (<a href="https://t.me/share/url?url=%2Freportannuale%40{BOT_NAME}">Invialo in un gruppo</a> 👥)\n\n'
        "<i>Mostra un report dettagliato della tua spesa totale per questo anno</i>\n\n\n"
    ),
    (
        f'<code>(👥)  </code><a href="https://t.me/share/url?url=%2Fcomparaanno%40{BOT_NAME}">/comparaanno</a>\n'
        f'<code>      </code><a href="https://t.me/share/url?url=%2Fcomparaanno%40{BOT_NAME}%20%3Canno%3E">/comparaanno &lt;anno&gt;</a>\n\n'
        f"<i>Metti a confronto la tua spesa annuale per l'anno corrente con quella di un altro utente.\n"
        "Specifica opzionalmente un <b>anno</b> diverso per effettuare l'operazione su anni precedenti</i> (richiede di <b>quotare un utente</b>)\n\n\n"
    ),
    (
        f'<code>(👥)  </code><a href="https://t.me/share/url?url=%2Fcancellaspesa%40{BOT_NAME}">/cancellaspesa</a>\n\n'
        "<i>Rimuovi un acquisto dal tuo storico; cancella anche il relativo post</i> (richiede di <b>quotare un tuo acquisto</b>)"
    ),
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
PURCHASES_DELETED_APPEND = "<i>\n        – %s %s</i>"

# fmt: off
PURCHASE_DELETED = (
    '✅  <i><a href="tg://user?id=%s">%s</a>,</i>' 
    " %s <i>%s cancellato con successo!</i>"
)
# fmt: on

GROUP_NOT_ALLOWED = (
    "❌  Questo gruppo non è abilitato all'utilizzo di questo bot.\n"
    "Puoi creare il tuo bot personale con il codice al seguente link:\n\n"
    "https://gitlab.com/nautilor/ultimi-acquisti"
)

NO_PURCHASE = (
    '⚠  <a href="tg://user?id=%s">%s</a>, '
    "<b>non hai ancora registrato alcun acquisto</b> su questo bot.\n\n"
    "Per aggiungerne uno, clicca il pulsante sottostante e seleziona un"
    " <b><u>gruppo in cui sono presente</u></b>: inserirò per te un modello di acquisto nel campo di testo della chat indicata,"
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
    f" sarà aggiunto alla data di oggi, <b>{TODAY}</b>.\n\n"
    "Vuoi continuare o annullare questo inserimento?"
)

PURCHASE_MODIFIED_DATE_ERROR = (
    '⚠️  <a href="tg://user?id=%s">%s</a>, l\'acquisto che stai modificando presenta una data futura o errata.'
    " Dal momento che non è possibile collocare un acquisto al futuro, questo"
    f" sarà spostato alla data di oggi, <b>{TODAY}</b>.\n\n"
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

HOW_TO_DEEP_LINK = (
    '<a href="tg://user?id=%s">%s</a>, per visualizzare la guida all\'utilizzo del bot...'
    ' <a href="t.me/%s?start=how_to">clicca qui</a>!'
)

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

USER_HAS_NO_VOTE = (
    "Benvenuto nella sezione di valutazione di <b>#ultimiacquisti</b>!\n\n"
    "Qui potrai dare un feedback approfondito su vari aspetti del bot, aggiungendo"
    " opzionalmente un commento per ogni area di competenza. Tieni presente che un"
    " voto provvisto di commento avrà <b>più peso</b> nella <i>media pubblica</i>"
    "  (consultabile nella sezione <b>[Menu principale] &gt; [Info]</b>) !\n\n\n"
    "<b><i>Lo Staff si riserva il diritto di valutare e rimuovere eventuali"
    ' commenti non idonei al <a href="telegra.ph/Regolamento-del-gruppo-VGs-LOVE-07-03">'
    "regolamento</a>.</i></b>"
)

USER_ALREADY_VOTED = (
    "Benvenuto nella sezione di valutazione di <b>#ultimiacquisti</b>!\n\n"
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

WISHLIST_DESCRIPTION_TOO_LONG = "🚫  <b>Limite di 128 caratteri superato!</b>\n\n"

NO_ELEMENT_IN_WISHLIST = (
    "<i>In questa sezione potrai aggiungere dei promemoria relativi ad articoli che intendi acquistare in un secondo momento.</i>"
    "\n\n☹️  La tua lista dei desideri è vuota..."
)


WISHLIST_STEP_ONE = (
    "<b>Step 1:</b>\n<i><b><u>Testo</u></b>  ⟶  Link  ⟶  Categoria</i>\n\n"
)
WISHLIST_STEP_TWO = (
    "<b>Step 2:</b>\n<i>Testo  ⟶  <b><u>Link</u></b>  ⟶  Categoria</i>\n\n"
)
WISHLIST_STEP_THREE = (
    "<b>Step 3:</b>\n<i>Testo  ⟶  Link  ⟶  <b><u>Categoria</u></b></i>\n\n"
)

ADD_TO_WISHLIST_PROMPT = (
    "Inserisci l'elemento da aggiungere alla lista dei"
    " desideri:\n"
    "   •  solo testo;\n"
    "   •  massimo <b>128 caratteri</b>;\n"
    "   •  testo su più righe non supportato.\n"
    "<b>Se l'elemento che vuoi aggiungere è un <u>link</u>, aspetta a inserirlo!</b>"
)

EDIT_WISHLIST_PROMPT = (
    "Inserisci il nuovo testo dell'elemento:\n"
    "   •  solo testo;\n"
    "   •  massimo <b>128 caratteri</b>;\n"
    "   •  testo su più righe non supportato.\n"
    "<b>Se l'elemento che vuoi aggiungere è un <u>link</u>, aspetta a inserirlo!</b>"
)

ADDED_TO_WISHLIST = "✅  <i>Elemento aggiunto con successo!</i>"


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
    "   •  in caso di link multipli immessi, prenderò in considerazione soltanto il primo."
)

EDIT_CATEGORY_TO_WISHLIST_ITEM_MESSAGE = (
    "Seleziona una nuova categoria per il tuo elemento, oppure conferma quella attuale:"
)

ADD_LINK_TO_WISHLIST_ITEM_MESSAGE = (
    "Se vuoi che il tuo elemento riporti a una pagina web, puoi inserirne qui il link:\n"
    "   •  sono ammessi solamente link;\n"
    "   •  in caso di link multipli immessi, prenderò in considerazione soltanto il primo."
)

ADD_CATEGORY_TO_WISHLIST_ITEM_MESSAGE = "Seleziona una categoria per il tuo elemento:"

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

REQUEST_WISHLIST_PHOTO = "Invia adesso <b>come foto</b> (non come <i>file</i>) le immagini che vuoi aggiungere per <b>%s</b>:"

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

WISHLIST_HEADER = f"<b><u>LISTA DEI DESIDERI</u></b>     (Versione:  <code>{WISHLIST_VERSION}</code>)\n\n\n"


# TODO: create query to retrieve all number of all wishlist items and all photos
DELETE_ALL_WISHLIST_ITEMS_MESSAGE = (
    f"{WISHLIST_HEADER}<b>%s elementi, %s foto</b>\n🚮  "
    "<i>Stai per cancellare <b>tutti gli elementi</b> e <b>tutte le foto</b> della lista dei desideri."
    "</i>\n\n<b>Vuoi confermare?</b>"
)

DELETE_ALL_WISHLIST_ITEMS_NO_PHOTO_MESSAGE = (
    f"{WISHLIST_HEADER}<b>%s elementi</b>\n🚮  "
    "<i>Stai per cancellare <b>tutti gli elementi</b> della lista dei desideri."
    "</i>\n\n<b>Vuoi confermare?</b>"
)

DELETE_ALL_WISHLIST_ITEMS_PHOTOS = (
    "<b>%s foto</b>\n"
    "🚮  <i>Stai per cancellare <b>tutte le foto</b> aggiunte per <b>%s</b>.</i>\n\n"
    "<b>Vuoi confermare?</b>"
)
