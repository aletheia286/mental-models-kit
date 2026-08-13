# Set di backtest indipendente per _mm_score_situation() — 44 messaggi italiani,
# 3-4 per ciascuna delle 13 categorie di _mm_hub.md + 3 controlli (None = nessun match atteso),
# incluso un blocco dedicato a "Finanza & investimento personale" (categoria aggiunta dopo un
# gap trovato dal vivo: una domanda finanziaria reale non veniva riconosciuta da nessuna
# categoria esistente). Unico set usato sia da `mm-enrich`/`mm-suggest-words`
# (mental_models_engine.py) sia da qualunque riverifica manuale futura, così un numero citato
# in una sessione è sempre riproducibile in un'altra. Trattato come "held-out" — non va
# arricchito con parole prese dalla tabella di `_mm_hub.md` stessa, altrimenti perde valore
# come test indipendente.

CASES = [
    # (expected_category or None for "no match", message)
    ("Decisioni & trade-off", "Devo scegliere tra tenere il vecchio fornitore di energia o passare a uno nuovo, ci sono pro e contro su entrambi, mi aiuti a decidere?"),
    ("Decisioni & trade-off", "Sto valutando se investire nel rifacimento del bagno adesso o aspettare l'anno prossimo, non so quale opzione convenga di più."),
    ("Decisioni & trade-off", "Ho due preventivi per i lavori del condominio, uno più economico ma con tempi lunghi, l'altro il contrario, come scelgo?"),
    ("Decisioni & trade-off", "Sto valutando se conviene comprare ora un altro immobile per affitto o aspettare che i tassi di interesse scendano, non so quale scelta convenga di più nel lungo periodo."),

    ("Problemi & causa radice", "Lo script di ingest continua a fallire ogni tanto con lo stesso errore, voglio capire perché succede davvero e non solo tappare il buco."),
    ("Problemi & causa radice", "Il backup su Drive si blocca sempre a metà da settimane, è la terza volta che lo sistemo temporaneamente ma si ripresenta."),
    ("Problemi & causa radice", "La caldaia condominiale si spegne in modo random da un mese, i tecnici hanno sempre dato una soluzione diversa senza risolvere."),

    ("Sistemi & complessità", "Ho notato che più file accumuliamo in 01_raw senza processarli, più diventa lento tutto il sistema di ricerca, sembra peggiorare da solo col tempo."),
    ("Sistemi & complessità", "Nessuno controlla più i log del cron della sincronizzazione da mesi, temo che si sia accumulato un problema che ora è difficile da districare."),
    ("Sistemi & complessità", "Il numero di eccezioni non gestite nello script cresce ogni release perché nessuno le rivede mai, la manutenzione è stata abbandonata."),

    ("Bias & psicologia decisionale", "Temo di essere troppo ottimista sui tempi di consegna solo perché il fornitore mi sta simpatico, potrei sbagliare la valutazione."),
    ("Bias & psicologia decisionale", "Continuo a difendere questa scelta di design anche se le prove dicono il contrario, forse sto solo cercando conferme a quello che voglio già credere."),
    ("Bias & psicologia decisionale", "Il condomino insiste che l'amministratore sbaglia sempre, ma mi chiedo se è un giudizio obiettivo o solo antipatia personale."),
    ("Bias & psicologia decisionale", "Il mio portafoglio azionario è ai massimi storici da mesi, ho paura che un ribasso sia vicino e non so se conviene alleggerire la posizione adesso."),

    ("Comunicazione efficace", "Devo spiegare a mia figlia perché non può usare il telefono a cena senza sembrare che la sto punendo, come lo dico bene?"),
    ("Comunicazione efficace", "Come faccio a far capire al vicino il problema delle infiltrazioni senza sembrare aggressivo, voglio scegliere le parole giuste."),
    ("Comunicazione efficace", "Devo dare la notizia dell'aumento delle spese condominiali agli altri proprietari, mi serve un modo chiaro e non allarmante di presentarla."),

    ("Strategia & competitività", "Sto pensando a come allocare il budget del prossimo trimestre tra i vari progetti del team, quali priorità hanno senso?"),
    ("Strategia & competitività", "Il mercato dei concorrenti si sta muovendo veloce, dovremmo decidere su cosa concentrare le risorse per restare competitivi."),
    ("Strategia & competitività", "Con budget limitato quest'anno, quale area merita la priorità più alta per il business?"),

    ("Evidenza & giudizio", "Ho letto due articoli che dicono cose opposte sull'efficacia di questo integratore, come faccio a capire di quale fonte fidarmi?"),
    ("Evidenza & giudizio", "Tutti dicono che questo metodo di studio funziona ma non ho visto uno straccio di prova solida, vale la pena verificarlo prima di adottarlo?"),
    ("Evidenza & giudizio", "Il consulente energetico sostiene una cosa, il sito del produttore un'altra completamente diversa, chi ha ragione secondo i dati reali?"),

    ("Conoscenza & apprendimento", "Sto cercando un modo migliore per organizzare le mie note così non le dimentico dopo due settimane."),
    ("Conoscenza & apprendimento", "Vorrei migliorare come strutturo lo studio del nuovo linguaggio di programmazione, sento che non mi resta in testa niente."),
    ("Conoscenza & apprendimento", "Come posso rivedere periodicamente quello che ho imparato sul project management così non lo perdo nel tempo?"),

    ("Pattern personali (tuoi)", "Ultimamente rimando sempre le stesse cose la sera tardi, è compatibile con come lavoro di solito o è un cambiamento?"),
    ("Pattern personali (tuoi)", "Ho notato che tendo sempre a posticipare le decisioni finanziarie importanti, è in linea con quello che ho fatto in passato?"),
    ("Pattern personali (tuoi)", "Sto scegliendo di nuovo la soluzione più complicata invece della più semplice, è un mio schema ricorrente?"),

    ("Dinamiche sociali & relazionali", "Due condomini si fanno la guerra su chi ha ragione sulle spese comuni e ogni riunione peggiora, sembra più una questione di orgoglio che di soldi."),
    ("Dinamiche sociali & relazionali", "L'uso del giardino condiviso sta creando tensioni perché ognuno lo tratta come fosse solo suo, temo che si rovini per colpa di pochi."),
    ("Dinamiche sociali & relazionali", "Due colleghi competono per lo stesso ruolo e la rivalità sta diventando più intensa di quanto il progetto giustifichi."),

    ("Psicologia personale & relazioni", "Mia compagna sembra meno motivata del solito ultimamente senza un motivo chiaro, e non capisco cosa stia succedendo tra noi."),
    ("Psicologia personale & relazioni", "Le nostre conversazioni finiscono sempre in tensione anche partendo da argomenti banali, non capisco perché degenerino così."),
    ("Psicologia personale & relazioni", "Mia figlia reagisce in modo sempre più nervosa quando è stanca, è un pattern che si ripete sotto stress ultimamente."),

    ("Organizzazioni, team & carriera", "Devo valutare le performance di un membro del team questo trimestre e la situazione è delicata, come imposto la conversazione di sviluppo?"),
    ("Organizzazioni, team & carriera", "C'è una dinamica poco sana tra due reparti in azienda che sta rallentando i progetti, come la affronto da manager?"),
    ("Organizzazioni, team & carriera", "Sto pensando se accettare la promozione o restare nel ruolo attuale, è una decisione di carriera importante e ho stakeholder complessi da gestire."),

    ("Finanza & investimento personale", "Sto valutando se vendere le mie azioni perché il mercato è salito troppo, ho paura di perdere i guadagni."),
    ("Finanza & investimento personale", "Ho paura che il mio fondo pensione non basti quando andrò in pensione, dovrei versarci di più ogni mese?"),
    ("Finanza & investimento personale", "Il mio consulente mi ha proposto un nuovo prodotto assicurativo-finanziario, non capisco se conviene rispetto a quello che ho già."),

    (None, "Aggiungi il tag reporting a questo file."),
    (None, "Qual è lo stato del progetto Alpha in questo momento?"),
    (None, "Rinomina il file _index_work.md e sposta la data di oggi nel frontmatter."),
]
