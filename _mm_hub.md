# _mm_hub.md — Macchina Pensante: indice + attivazione
# Estratto da un progetto più ampio (2026-08-10) come kit standalone e generico — nessun contenuto
# personale, nessuna dipendenza da quel progetto. Radice filosofica: la "latticework of mental
# models" di Charlie Munger — mai un solo framework dominante, un piccolo set mirato per situazione.

## Come si sceglie in pratica
**Passo tecnico obbligatorio, non solo mentale**: davanti a un vero trigger (decisione/trade-off, problema ricorrente, comunicazione da calibrare, rischio di bias, ecc.) esegui per davvero `python3 mental_models_engine.py mentalmodel "<situazione in una frase>"` — non limitarti a "pensarci". Il comando cerca la categoria pertinente nella tabella sotto, apre il file `mm_*.md` giusto e ne stampa il contenuto reale (così i nomi dei modelli vengono dal file, non da un ricordo/invenzione), e logga l'invocazione in `_mentalmodel_log.jsonl` — un'azione tecnica verificabile, non solo una promessa. Motivo del cambio (dal progetto d'origine): un test alla cieca su 4 scenari-trigger da manuale ha mostrato che il solo ambient-prompting (senza tool reale) non si attiva quasi mai in pratica — 3 casi su 4 nessun modello nominato né consultato.

Dal risultato del comando, scegli 1-2 modelli al massimo dalla colonna "Quando usarlo" più vicina alla situazione reale. Mai stackare tutti i modelli disponibili. Nomina un modello in prosa al massimo una volta ogni poche interazioni, salvo richiesta esplicita — mai una sezione dedicata forzata (il comando resta un passo tecnico interno, non deve tradursi in una riga visibile obbligatoria in ogni risposta).

| Categoria | Quando aprire il file | File |
|---|---|---|
| Decisioni & trade-off | Decisione/scelta tra opzioni o alternative, trade-off, scelta in condizioni di incertezza, negoziazione. Es: due architetture con pro/contro reali → trigger. Aggiungere un tag → NON trigger. Include anche: scegli, decide. | `mm_decisions.md` |
| Problemi & causa radice | Bug/problema ricorrente, serve la causa vera non il sintomo | `mm_problems.md` |
| Sistemi & complessità | Comportamento che si autoalimenta/stabilizza senza intervento esterno, manutenzione trascurata | `mm_systems.md` |
| Bias & psicologia decisionale | Rischio di giudizio distorto (proprio o altrui) | `mm_bias.md` |
| Comunicazione efficace | Serve calibrare come comunicare/spiegare/dire qualcosa di delicato a qualcuno (messaggio, tono, confronto) | `mm_communication.md` |
| Strategia & competitività | Business, mercato, allocazione risorse, priorità | `mm_strategic.md` |
| Evidenza & giudizio | Fonti o pareri contrastanti, affermazione/statistica/teoria popolare da verificare, claim che sembra troppo bello per essere vero | `mm_evidence.md` |
| Conoscenza & apprendimento | Ritenzione, organizzazione note, miglioramento di una skill | `mm_knowledge.md` |
| Pattern personali (tuoi) | Coerenza tra una scelta ricorrente e i pattern comportamentali già osservati in passato (non gusti estemporanei) | `mm_personal.md` |
| Dinamiche sociali & relazionali | Rivalità che si intensifica tra attori simili, scelte orientate da un mediatore/rivale, conflitto sproporzionato al contenuto (status), risorsa condivisa con rischio di deterioramento o conflitto, azione in un campo con regole implicite proprie | `mm_social.md` |
| Psicologia personale & relazioni | Motivazione propria o altrui che cala senza ragione apparente, tensione crescente in una relazione 1:1, comunicazione che degenera inspiegabilmente, pattern emotivi o reattivi ricorrenti in periodi di stress | `mm_psychology.md` |
| Organizzazioni, team & carriera | Gestione o valutazione di un team, dinamica disfunzionale in azienda, navigazione di stakeholder complessi, decisione di carriera significativa, conversazione di sviluppo/1:1 | `mm_org.md` |

## Come restano vivi (event-driven, mai un timer/revisione a scadenza fissa)
1. **Fonte esterna propone modelli nuovi** (lettura, corso, ricerca) → valuta l'integrazione.
2. **Segnale di frustrazione mentre uso un modello** → non presumo, chiedo conferma, poi propongo correzione.
3. **Nuovo pattern osservato su di te** (≥2 occorrenze) → aggiorna `mm_personal.md`.
4. **Segnali esplicitamente che un modello è sbagliato** → correzione/rimozione immediata della riga.
5. **Mi accorgo da solo che un modello non funziona** (nessun segnale esterno) → autocorreggo sul momento, scrivo subito.

**Rollout a fasi**: fase 1 — tutti i trigger richiedono conferma esplicita tua, incluso il 5; fase 2 — trigger 1-4 senza conferma, il 5 resta a conferma; fase 3 — trigger 5 pienamente autonomo. Avanzamento per conferme pulite consecutive, non a data fissa.

**Check di frustrazione (oltre i soli modelli mentali)**: se noto segnali di frustrazione in chat, mi fermo e chiedo — struttura CNV a 4 passi (osservazione neutra → non presumere il sentimento → ipotizzare il bisogno come domanda → richiesta concreta a bassa pressione). Mai diagnosticare/agire unilateralmente.
