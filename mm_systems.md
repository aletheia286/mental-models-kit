# mm_systems.md — Sistemi & complessità
# Categoria del kit. Letto solo se `_mm_hub.md` indirizza qui.
# Formato colonna 2: "usa quando X · no se Y".

| Modello | Quando usarlo / evitarlo | Passi | DoD (come sai che ha funzionato) |
|---|---|---|---|
| Feedback Loops | Un comportamento si amplifica/stabilizza da solo · no per eventi isolati | Identifica se il loop è positivo (amplifica) o negativo (stabilizza) | Prevedi correttamente la direzione del prossimo ciclo |
| Goodhart's Law | Una metrica guida decisioni importanti · no per metriche puramente descrittive | Chiediti se il target è ancora un buon proxy o è stato "giocato" | La metrica correla ancora con l'obiettivo reale |
| Second-Order Thinking | Decisione con conseguenze a catena · no per scelte senza seguito | Chiediti "e poi cosa succede?" almeno due volte | La conseguenza di secondo livello è stata anticipata |
| Thermodynamics & Entropy | Sistema/progetto trascurato tende al disordine · no per sistemi già presidiati | Pianifica manutenzione continua, non solo interventi puntuali | Il debito di manutenzione non è cresciuto tra un intervento e l'altro |
| Resilience vs Robustness vs Antifragility | Progettare per gli shock · no se non c'è variabilità reale attesa | Scegli: assorbire, resistere, o migliorare sotto stress | Il sistema si comporta come progettato al primo shock reale |
| Critical Mass | Iniziativa che fatica a decollare · no se già auto-sostenuta | Trova la soglia minima di scala oltre cui diventa auto-sostenuta | Oltre la soglia, l'iniziativa prosegue senza spinta esterna |
| Signal-to-Noise Ratio | Troppa informazione, poca azionabile · no con dati già puliti | Separa dati rilevanti da distrazione di fondo prima di decidere | La decisione non cambia rimuovendo altro rumore |
| Regola dell'uno-ogni-60 | Micro-derive che sembrano trascurabili · no per deviazioni già grandi e visibili | Stima l'effetto cumulato su una scala temporale lunga, non solo oggi | La correzione fatta ora ha evitato uno scarto grande dopo |

**Applicabilità concreta**: manutenzione di immobili/impianti, debito tecnico di un progetto software, coerenza-decisionale (vedi `mm_personal.md`).
**Trigger di auto-correzione**: vedi `_mm_hub.md`. Ultima potatura: 2026-08-04.
