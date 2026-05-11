# AI Code Reviewer — Tələbə Hesabatı

**Tələbə:** Qurban  
**Qrup:** KOM24A  
**Fənn:** Data Structures and Algorithms 2  
**Müəllim:** Şamil Hümbətov  
**Universitet:** Qarabağ Universiteti

---

## 1. Giriş

(Problem statement: kod review niyə bottleneck-dir, niyə avtomatlaşdırma lazımdır)

## 2. Layihənin Məqsədi

(MVP nəyi həll edir, hansı istifadəçilər üçün)

## 3. İstifadə Olunan Data Structures

### 3.1 Tree (Abstract Syntax Tree)
- Python kodunun strukturunu təmsil etmək üçün
- Hər node bir kod elementidir
- Traversal: `ast.walk()` — DFS əsaslı
- Complexity: O(n), n = node sayı

### 3.2 Directed Graph (Dependency Graph)
- Fayllar arası import əlaqələrini təmsil edir
- NetworkX `DiGraph` (adjacency list)
- Cycle detection: Tarjan's algorithm
- Complexity: O(V+E)

### 3.3 Min-Heap (Priority Queue)
- Faylları review prioritetinə görə sıralayır
- Python `heapq` (array-əsaslı binary heap)
- Insert/Pop: O(log n)

### 3.4 Hash Map (Cache)
- Eyni kodu iki dəfə review etməmək üçün
- SHA256 hash → review nəticəsi
- Get/Set: O(1) ortalama

## 4. Alqoritmlər

### 4.1 BFS — Impact Analysis
"Bu fayl dəyişərsə hansı fayllar təsirlənir?" — reverse BFS.

### 4.2 DFS — Cycle Detection
Dairəvi import-ları tapmaq üçün.

### 4.3 Cyclomatic Complexity
McCabe metric: kodun mürəkkəbliyini ədədi şəkildə ölçür.

## 5. Arxitektura

(Diaqram burada — `architecture.png`)

## 6. İmplementasiya Detalları

(Hər modulun qısa təsviri + kod nümunələri)

## 7. Test Nəticələri

(pytest coverage, test sayı, screenshot-lar)

## 8. Performance Analizi

(Neçə PR test edildi, neçə saniyə, neçə token)

## 9. Complexity Analysis Cədvəli

| Əməliyyat | Struktur | Time | Space |
|-----------|----------|------|-------|
| AST traversal | Tree | O(n) | O(n) |
| Impact BFS | Graph | O(V+E) | O(V) |
| Cycle detection | Graph | O(V+E) | O(V) |
| Priority insert | Min-Heap | O(log n) | O(1) |
| Priority pop | Min-Heap | O(log n) | O(1) |
| Cache lookup | Hash Map | O(1) avg | O(n) |
| SHA256 hash | — | O(k), k = code length | O(1) |

## 10. Nəticə və Gələcək İş

(Nə öyrəndim, layihəni necə genişləndirmək olar)

## 11. Mənbələr

- Python documentation: ast module
- NetworkX documentation
- McCabe, T.J. (1976). "A Complexity Measure"
- Tarjan, R. (1972). "Depth-first search and linear graph algorithms"