# Akasha Cipher Lab Report

Input file: `data/kryptos/k4.txt`

## Structural Overview

- Length: 97
- Entropy: 4.5548
- Token count: 1
- Repeated trigrams: 0
- Repeated tetragrams: 0

## Section Analysis

Mode: **fixed**
Sections analyzed: **5**

### section_001

Preview: `OBKRUOXOGHULBSOLIFBBWFLR`

- Length: 24
- Entropy: 3.4702
- Tokens: 1
- Repeated trigrams: 0

### section_002

Preview: `VQQPRNGKSSOTWTQSJQSSEKZZ`

- Length: 24
- Entropy: 3.5179
- Tokens: 1
- Repeated trigrams: 0

### section_003

Preview: `WATJKLUDIAWINFBNYPVTTMZF`

- Length: 24
- Entropy: 3.9702
- Tokens: 1
- Repeated trigrams: 0

### section_004

Preview: `PKWGDKZXTJCDIGKUHUAUEKCA`

- Length: 24
- Entropy: 3.7202
- Tokens: 1
- Repeated trigrams: 0

### section_005

Preview: `R`

- Length: 1
- Entropy: 0.0
- Tokens: 1
- Repeated trigrams: 0

## Top Candidates

### branch_006

Transform: `columnar`
Parameters: `{'width': 5}`
Score: **1.8468**
Score delta vs identity: 1.0

Preview:
```
OOULWQGTJKTDNPZGTGAABXLIFQKWQZJIFVFDJKURKOBFLPSTSZKABTPKCUERGSBRRSQSWLWNTKZDHKUHOBVNOSEAUIYMWXIUC
```

### branch_004

Transform: `caesar`
Parameters: `{'shift': 3}`
Score: **1.8365**
Score delta vs identity: 0.9897

Preview:
```
RENUXRARJKXOEVROLIEEZIOUYTTSUQJNVVRWZWTVMTVVHNCCZDWMNOXGLDZLQIEQBSYWWPCISNZJGNCAWMFGLJNXKXDXHNFDU
```

### branch_003

Transform: `caesar`
Parameters: `{'shift': 1}`
Score: **1.8262**
Score delta vs identity: 0.9794

Preview:
```
PCLSVPYPHIVMCTPMJGCCXGMSWRRQSOHLTTPUXURTKRTTFLAAXBUKLMVEJBXJOGCOZQWUUNAGQLXHELAYUKDEJHLVIVBVFLDBS
```

### branch_001

Transform: `identity`
Parameters: `{}`
Score: **0.8468**
Score delta vs identity: 0.0

Preview:
```
OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR
```

### branch_002

Transform: `reverse`
Parameters: `{}`
Score: **0.8468**
Score delta vs identity: 0.0

Preview:
```
RACKEUAUHUKGIDCJTXZKDGWKPFZMTTVPYNBFNIWAIDULKJTAWZZKESSQJSQTWTOSSKGNRPQQVRLFWBBFILOSBLUHGOXOURKBO
```

### branch_007

Transform: `columnar`
Parameters: `{'width': 7}`
Score: **0.8468**
Score delta vs identity: 0.0

Preview:
```
OOOFRTSAINZKIUBGLLNWSTAYFZGEKHIRGTEJWPPXKKRUFVKQKKIVKTUCULBQSSZLNTWJHAOBBQSJZUFTGCURXSWPOQWDBMDDA
```

### branch_005

Transform: `caesar`
Parameters: `{'shift': 13}`
Score: **0.8262**
Score delta vs identity: -0.0206

Preview:
```
BOXEHBKBTUHYOFBYVSOOJSYEIDDCEATXFFBGJGDFWDFFRXMMJNGWXYHQVNJVASOALCIGGZMSCXJTQXMKGWPQVTXHUHNHRXPNE
```

## Substitution Lenses

### Frequency Remap Preview
```
INEHTIBIRVTDNAIDLCNNSCDHKUUFHGREAAIOSOUAYUAAJEMMSWOYEDTPLWSLGCNGQFKOOZMCFESRPEMBOYXPLRETVTWTJEXWH
```

### Rare Symbol Collapse
```
OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBN?PVTT?ZFPKWGDKZXTJCDIGKUHUAUEKCAR
```

### Pattern Signature
```
0.1.2.3.4.0.5.0.6.7.4.8.1.9.0.8.10.11.1.1.12.11.8.3.13.14.14.15.3.16.6.2.9.9.0.17.12.17.14.9.18.14.9.9.19.2.20.20.12.21.17.18.2.8.4.22.10.21.12.10.16.11.1.16.23.15.13.17.17.24.20.11.15.2.12.6.22.2.20.5
```

## Constraint Search Preview

### Frequency Hint Mapping
```
K -> E
U -> T
S -> A
T -> O
O -> I
B -> N
W -> S
R -> H
G -> R
L -> D
I -> L
F -> C
Q -> U
Z -> M
A -> W
P -> F
N -> G
J -> Y
D -> P
X -> B
H -> V
V -> K
E -> J
C -> X
Y -> Q
M -> Z
```

## Dictionary Pattern Attack

Token analyzed: `OBKRUOXOGH`
Pattern signature: `0.1.2.3.4.0.5.0.6.7`

No matching dictionary patterns found.
