# mm_personal.md — Pattern tuoi osservati (file vivo)
# Categoria del kit. Letto solo se `_mm_hub.md` indirizza qui. Nuova riga richiede ≥2 occorrenze osservate prima di essere proposta (vedi `_mm_hub.md`, meccanismo 3).
# Formato colonna 3 (come negli altri file): "si applica quando X · no se Y".

| Pattern | Descrizione | Quando si applica / evitarlo | DoD (come sai che ha funzionato) |
|---|---|---|---|
| Fix → Test → Avanti | Un fix alla volta con verifica immediata, mai batch non testati | Ogni modifica a un progetto o al codice · no per esplorazione rapida usa-e-getta | Ogni step ha una verifica propria prima del successivo, non una sola finale |
| No-info-loss | Non eliminare/comprimere contenuti senza una versione equivalente o superiore già presente | Split, archiviazione, riscrittura di qualunque contenuto · no per scratch/temp esplicitamente usa-e-getta | Nulla è stato perso, solo riorganizzato o esplicitamente sostituito |
| Coerenza-decisionale | Una decisione presa in sessione va registrata subito, non solo tenuta a mente | Qualunque scelta di design non banale · no per micro-dettagli reversibili all'istante | Non citi in seguito un approccio diverso da quello già deciso |
| Token-consciousness | Attenzione esplicita al costo in token di ciò che si legge ad ogni sessione | File di contesto letti sempre ad ogni avvio · no per un file aperto una tantum | Il costo fisso per sessione è noto e giustificato, non ignorato |
| Trasparenza-totale | Vuoi sapere cosa sto facendo e perché, non solo il risultato | Scelte non ovvie, trade-off, errori trovati · no per azioni ovvie senza alternative reali | La logica della scelta è stata spiegata prima o insieme al risultato |
| Miglioramento-continuo / Kaizen | Revisione periodica e correzione costante della propria rotta | Fine sessione, revisione settimanale · no a metà di un task ancora aperto | Almeno una correzione concreta emerge dalla revisione, non solo conferma |

**Trigger di auto-correzione**: vedi `_mm_hub.md`. Ultima potatura: 2026-08-04.
