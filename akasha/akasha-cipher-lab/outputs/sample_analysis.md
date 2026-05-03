# Akasha Cipher Lab Report

Input file: `data/voynich/sample.txt`

## Structural Overview

- Length: 68
- Entropy: 3.5468
- Token count: 12
- Repeated trigrams: 12
- Repeated tetragrams: 11

## Section Analysis

Mode: **lines**
Sections analyzed: **3**

### section_001

Preview: `QOKEEDYQOKEDYDALQOKALDAIIN`

- Length: 26
- Entropy: 3.2476
- Tokens: 5
- Repeated trigrams: 3

### section_002

Preview: `SHEDYQOKAINOLCHEDYQOKEDY`

- Length: 24
- Entropy: 3.5425
- Tokens: 4
- Repeated trigrams: 5

### section_003

Preview: `QOKAIINDAIINQOTEDY`

- Length: 18
- Entropy: 3.1699
- Tokens: 3
- Repeated trigrams: 2

## Top Candidates

### branch_003

Transform: `columnar`
Parameters: `{'width': 3}`
Score: **3.88**
Score delta vs identity: 1.0

Preview:
```
QEYKYLKDIHYKNCDODOIDIODOEQEDQAANEQAOHYKYKIANTYKDODAOLISDOILEQEQANIQE
```

### branch_001

Transform: `identity`
Parameters: `{}`
Score: **2.88**
Score delta vs identity: 0.0

Preview:
```
QOKEEDYQOKEDYDALQOKALDAIINSHEDYQOKAINOLCHEDYQOKEDYQOKAIINDAIINQOTEDY
```

### branch_002

Transform: `reverse`
Parameters: `{}`
Score: **0.88**
Score delta vs identity: -2.0

Preview:
```
YDETOQNIIADNIIAKOQYDEKOQYDEHCLONIAKOQYDEHSNIIADLAKOQLADYDEKOQYDEEKOQ
```

### branch_004

Transform: `columnar`
Parameters: `{'width': 4}`
Score: **0.88**
Score delta vs identity: -2.0

Preview:
```
QEOYQLIEONHQDKNITODKDODNDKOEOYADNEKYEAKASYALDKQIAQDEQDLAIHQICYEOIIOY
```

## Substitution Lenses

### Frequency Remap Preview
```
ATNOOESATNOESEHDATNHDEHIIRCLOESATNHIRTDULOESATNOESATNHIIREHIIRATMOES
```

### Rare Symbol Collapse
```
QOKEEDYQOKEDYDALQOKALDAIIN?HEDYQOKAINOL?HEDYQOKEDYQOKAIINDAIINQO?EDY
```

### Pattern Signature
```
0.1.2.3.3.4.5.0.1.2.3.4.5.4.6.7.0.1.2.6.7.4.6.8.8.9.10.11.3.4.5.0.1.2.6.8.9.1.7.12.11.3.4.5.0.1.2.3.4.5.0.1.2.6.8.8.9.4.6.8.8.9.0.1.13.3.4.5
```
