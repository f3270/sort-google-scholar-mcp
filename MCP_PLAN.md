# SORT GOOGLE SCHOLAR MCP

Original project: https://github.com/WittmannF/sort-google-scholar

El plan de este proyecto es hacer un upgrade del proyecto original para
extender las capacidades del repositorio y habilitarlo como un MCP para ser
consumido por agentes de IA

```mermaid
flowchart LR

U(("User")) --> UQ{{"User Queries"}}
U --> UKW{{"User keywords"}}

subgraph MCP
direction TB
    UKW --> GKW
    UQ --> GKW
    GKW["Generate Search Keywords"]
    GKW --> OKW["Optim GScholar Keywords (KW)"]
    OKW --> SGS
    subgraph SGS["Sort Google Scholar"]
        KW{{KW}} --> Search --> CSV[(CSV)]
    end
    SGS --> F["Filter CSV"]
    F --> CSVD["CSV DOWLOADER"]
    CSVD --> R[(RAG)]
    UQ{{"User Queries"}} --> R
end
R --> O((Output))
```
