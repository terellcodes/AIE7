import numpy as np
from collections import defaultdict
from typing import List, Tuple, Callable
from aimakerspace.openai_utils.embedding import EmbeddingModel
import asyncio
from aimakerspace.openai_utils.chatmodel import ChatOpenAI
import json


def cosine_similarity(vector_a: np.array, vector_b: np.array) -> float:
    """Computes the cosine similarity between two vectors."""
    dot_product = np.dot(vector_a, vector_b)
    norm_a = np.linalg.norm(vector_a)
    norm_b = np.linalg.norm(vector_b)
    return dot_product / (norm_a * norm_b)

class VectorDatabase:
    def __init__(self, embedding_model: EmbeddingModel = None):
        self.vectors = defaultdict(np.array)
        self.embedding_model = embedding_model or EmbeddingModel()

    def insert(self, key: str, vector: np.array) -> None:
        self.vectors[key] = vector

    def search(
        self,
        query_vector: np.array,
        k: int,
        distance_measure: Callable = cosine_similarity,
    ) -> List[Tuple[str, float]]:
        scores = [
            (key, distance_measure(query_vector, vector))
            for key, vector in self.vectors.items()
        ]
        return sorted(scores, key=lambda x: x[1], reverse=True)[:k]

    def search_by_text(
        self,
        query_text: str,
        k: int,
        distance_measure: Callable = cosine_similarity,
        return_as_text: bool = False,
    ) -> List[Tuple[str, float]]:
        query_vector = self.embedding_model.get_embedding(query_text)
        results = self.search(query_vector, k, distance_measure)
        return [result[0] for result in results] if return_as_text else results

    def retrieve_from_key(self, key: str) -> np.array:
        return self.vectors.get(key, None)

    async def abuild_from_list(self, list_of_text: List[str]) -> "VectorDatabase":
        embeddings = await self.embedding_model.async_get_embeddings(list_of_text)
        for text, embedding in zip(list_of_text, embeddings):
            self.insert(text, np.array(embedding))
        return self
    
class Chunk:
    def __init__(self, text: str, metadata: dict = None):
        self.text = text
        self.metadata = metadata or {}

class VectorDatabaseWithMetadata(VectorDatabase):
    """
    Extension of VectorDatabase to support metadata and advanced indexing.
    """
    gpt_prompt = '''
You are a smart assistant that maps user questions to the **exact chapter and section** in the textbook:

Fundamentals of Python: Data Structures and Algorithms

Use only the Table of Contents below to determine the best match. If unsure, respond with `null` for chapter and section and a confidence under 0.5.

---

Cover (Page 1)  
Title Page (Page 3)  
Copyright Page (Page 4)  
Preface (Page 7)  
Contents (Page 13)  
1 Python Primer (23)  
1.1 Python Overview (24)  
1.1.1 The Python Interpreter (24)  
1.1.2 Preview of a Python Program (25)  
1.2 Objects in Python (26)  
1.2.1 Identifiers, Objects, and the Assignment Statement (26)  
1.2.2 Creating and Using Objects (28)  
1.2.3 Python's Built‑In Classes (29)  
1.3 Expressions, Operators, and Precedence (34)  
1.3.1 Compound Expressions and Operator Precedence (39)  
1.4 Control Flow (40)  
1.4.1 Conditionals (40)  
1.4.2 Loops (42)  
1.5 Functions (45)  
1.5.1 Information Passing (46)  
1.5.2 Python's Built‑In Functions (50)  
1.6 Simple Input and Output (52)  
1.6.1 Console Input and Output (52)  
1.6.2 Files (53)  
1.7 Exception Handling (55)  
1.7.1 Raising an Exception (56)  
1.7.2 Catching an Exception (58)  
1.8 Iterators and Generators (61)  
1.9 Additional Python Conveniences (64)  
1.9.1 Conditional Expressions (64)  
1.9.2 Comprehension Syntax (65)  
1.9.3 Packing and Unpacking of Sequences (66)  
1.10 Scopes and Namespaces (68)  
1.11 Modules and the Import Statement (70)  
1.11.1 Existing Modules (71)  
1.12 Exercises (73)  
2 Object‑Oriented Programming (78)  
2.1 Goals, Principles, and Patterns (79)  
2.1.1 Object‑Oriented Design Goals (79)  
2.1.2 Object‑Oriented Design Principles (80)  
2.1.3 Design Patterns (83)  
2.2 Software Development (84)  
2.2.1 Design (84)  
2.2.2 Pseudo‑Code (86)  
2.2.3 Coding Style and Documentation (86)  
2.2.4 Testing and Debugging (89)  
2.3 Class Definitions (91)  
2.3.1 Example: CreditCard Class (91)  
2.3.2 Operator Overloading and Python's Special Methods (96)  
2.3.3 Example: Multidimensional Vector Class (99)  
2.3.4 Iterators (101)  
2.3.5 Example: Range Class (102)  
2.4 Inheritance (104)  
2.4.1 Extending the CreditCard Class (105)  
2.4.2 Hierarchy of Numeric Progressions (109)  
2.4.3 Abstract Base Classes (115)  
2.5 Namespaces and Object‑Orientation (118)  
2.5.1 Instance and Class Namespaces (118)  
2.5.2 Name Resolution and Dynamic Dispatch (122)  
2.6 Shallow and Deep Copying (123)  
2.7 Exercises (125)  
3 Algorithm Analysis (131)  
3.1 Experimental Studies (133)  
3.1.1 Moving Beyond Experimental Analysis (135)  
3.2 The Seven Functions Used in This Book (137)  
3.2.1 Comparing Growth Rates (144)  
3.3 Asymptotic Analysis (145)  
3.3.1 The "Big‑Oh" Notation (145)  
3.3.2 Comparative Analysis (150)  
3.3.3 Examples of Algorithm Analysis (152)  
3.4 Simple Justification Techniques (159)  
3.4.1 By Example (159)  
3.4.2 The "Contra" Attack (159)  
3.4.3 Induction and Loop Invariants (160)  
3.5 Exercises (163)  
4 Recursion (170)  
4.1 Illustrative Examples (172)  
4.1.1 The Factorial Function (172)  
4.1.2 Drawing an English Ruler (174)  
4.1.3 Binary Search (177)  
4.1.4 File Systems (179)  
4.2 Analyzing Recursive Algorithms (183)  
4.3 Recursion Run Amok (187)  
4.3.1 Maximum Recursive Depth in Python (190)  
4.4 Further Examples of Recursion (191)  
4.4.1 Linear Recursion (191)  
4.4.2 Binary Recursion (196)  
4.4.3 Multiple Recursion (197)  
4.5 Designing Recursive Algorithms (199)  
4.6 Eliminating Tail Recursion (200)  
4.7 Exercises (202)  
5 Array‑Based Sequences (205)  
5.1 Python's Sequence Types (206)  
5.2 Low‑Level Arrays (207)  
5.2.1 Referential Arrays (209)  
5.2.2 Compact Arrays in Python (212)  
5.3 Dynamic Arrays and Amortization (214)  
5.3.1 Implementing a Dynamic Array (217)  
5.3.2 Amortized Analysis of Dynamic Arrays (219)  
5.3.3 Python's List Class (223)  
5.4 Efficiency of Python's Sequence Types (224)  
5.4.1 Python's List and Tuple Classes (224)  
5.4.2 Python's String Class (230)  
5.5 Using Array‑Based Sequences (232)  
5.5.1 Storing High Scores for a Game (232)  
5.5.2 Sorting a Sequence (236)  
5.5.3 Simple Cryptography (238)  
5.6 Multidimensional Data Sets (241)  
5.7 Exercises (246)  
6 Stacks, Queues, and Deques (250)  
6.1 Stacks (251)  
6.1.1 The Stack Abstract Data Type (252)  
6.1.2 Simple Array‑Based Stack Implementation (253)  
6.1.3 Reversing Data Using a Stack (257)  
6.1.4 Matching Parentheses and HTML Tags (258)  
6.2 Queues (261)  
6.2.1 The Queue Abstract Data Type (262)  
6.2.2 Array‑Based Queue Implementation (263)  
6.3 Double‑Ended Queues (269)  
6.3.1 The Deque Abstract Data Type (269)  
6.3.2 Implementing a Deque with a Circular Array (270)  
6.3.3 Deques in the Python Collections Module (271)  
6.4 Exercises (272)  
7 Linked Lists (277)  
7.1 Singly Linked Lists (278)  
7.1.1 Implementing a Stack with a Singly Linked List (283)  
7.1.2 Implementing a Queue with a Singly Linked List (286)  
7.2 Circularly Linked Lists (288)  
7.2.1 Round‑Robin Schedulers (289)  
7.2.2 Implementing a Queue with a Circularly Linked List (290)  
7.3 Doubly Linked Lists (292)  
7.3.1 Basic Implementation of a Doubly Linked List (295)  
7.3.2 Implementing a Deque with a Doubly Linked List (297)  
7.4 The Positional List ADT (299)  
7.4.1 The Positional List Abstract Data Type (301)  
7.4.2 Doubly Linked List Implementation (303)  
7.5 Sorting a Positional List (307)  
7.6 Case Study: Maintaining Access Frequencies (308)  
7.6.1 Using a Sorted List (308)  
7.6.2 Using a List with the Move‑to‑Front Heuristic (311)  
7.7 Link‑Based vs. Array‑Based Sequences (314)  
7.8 Exercises (316)  
8 Trees (321)  
8.1 General Trees (322)  
8.1.1 Tree Definitions and Properties (323)  
8.1.2 The Tree Abstract Data Type (327)  
8.1.3 Computing Depth and Height (330)  
8.2 Binary Trees (333)  
8.2.1 The Binary Tree Abstract Data Type (335)  
8.2.2 Properties of Binary Trees (337)  
8.3 Implementing Trees (339)  
8.3.1 Linked Structure for Binary Trees (339)  
8.3.2 Array‑Based Representation of a Binary Tree (347)  
8.3.3 Linked Structure for General Trees (349)  
8.4 Tree Traversal Algorithms (350)  
8.4.1 Preorder and Postorder Traversals of General Trees (350)  
8.4.2 Breadth‑First Tree Traversal (352)  
8.4.3 Inorder Traversal of a Binary Tree (353)  
8.4.4 Implementing Tree Traversals in Python (355)  
8.4.5 Applications of Tree Traversals (359)  
8.4.6 Euler Tours and the Template Method Pattern (363)  
8.5 Case Study: An Expression Tree (370)  
8.6 Exercises (374)  
9 Priority Queues (384)  
9.1 The Priority Queue Abstract Data Type (385)  
9.1.1 Priorities (385)  
9.1.2 The Priority Queue ADT (386)  
9.2 Implementing a Priority Queue (387)  
9.2.1 The Composition Design Pattern (387)  
9.2.2 Implementation with an Unsorted List (388)  
9.2.3 Implementation with a Sorted List (390)  
9.3 Heaps (392)  
9.3.1 The Heap Data Structure (392)  
9.3.2 Implementing a Priority Queue with a Heap (394)  
9.3.3 Array‑Based Representation of a Complete Binary Tree (398)  
9.4 Sorting with a Priority Queue (407)  
9.4.1 Selection‑Sort and Insertion‑Sort (408)  
9.4.2 Heap‑Sort (410)  
9.5 Adaptable Priority Queues (412)  
9.5.1 Locators (412)  
9.6 Exercises (417)  
10 Maps, Hash Tables, and Skip Lists (423)  
10.1 Maps and Dictionaries (424)  
10.1.1 The Map ADT (425)  
10.1.2 Application: Counting Word Frequencies (427)  
10.1.3 Python's MutableMapping Abstract Base Class (428)  
10.1.4 Our MapBase Class (429)  
10.2 Hash Tables (432)  
10.2.1 Hash Functions (433)  
10.2.2 Collision‑Handling Schemes (439)  
10.2.3 Load Factors, Rehashing, and Efficiency (442)  
10.4 Sorted Maps (449)  
10.4.1 Sorted Search Tables (450)  
10.4.2 Two Applications of Sorted Maps (456)  
10.5 Sets, Multisets, and Multimaps (468)  
10.5.1 The Set ADT (468)  
10.5.2 Python's MutableSet Abstract Base Class (470)  
10.5.3 Implementing Sets, Multisets, and Multimaps (472)  
10.6 Exercises (474)  
11 Search Trees (481)  
11.1 Binary Search Trees (482)  
11.1.1 Navigating a Binary Search Tree (483)  
11.1.2 Searches (485)  
11.1.3 Insertions and Deletions (487)  
11.1.4 Python Implementation (490)  
11.1.5 Performance of a Binary Search Tree (495)  
11.2 Balanced Search Trees (497)  
11.3 AVL Trees (503)  
11.3.1 Update Operations (505)  
11.3.2 Python Implementation (510)  
11.4 Splay Trees (512)  
11.4.1 Splaying (512)  
11.4.2 When to Splay (516)  
11.4.3 Python Implementation (518)  
11.5 (2,4) Trees (524)  
11.5.1 Multiway Search Trees (524)  
11.5.2 (2,4)-Tree Operations (527)  
11.6 Red‑Black Trees (534)  
11.6.1 Red‑Black Tree Operations (536)  
11.6.2 Python Implementation (547)  
11.7 Exercises (550)  
12 Sorting and Selection (558)  
12.1 Why Study Sorting Algorithms? (559)  
12.2 Merge‑Sort (560)  
12.2.1 Divide‑and‑Conquer (560)  
12.2.2 Array‑Based Implementation of Merge‑Sort (565)  
12.2.3 The Running Time of Merge‑Sort (566)  
12.2.4 Alternative Implementations of Merge‑Sort (569)  
12.3 Quick‑Sort (572)  
12.3.1 Randomized Quick‑Sort (579)  
12.4 Studying Sorting through an Algorithmic Lens (584)  
12.5 Comparing Sorting Algorithms (589)  
12.6 Python's Built‑In Sorting Functions (591)  
12.6.1 Sorting According to a Key Function (591)  
12.7 Selection (593)  
12.7.1 Prune‑and‑Search (593)  
12.7.2 Randomized Quick‑Select (594)  
12.7.3 Analyzing Randomized Quick‑Select (595)  
12.8 Exercises (596)  
13 Text Processing (603)  
13.1 Abundance of Digitized Text (604)  
13.1.1 Notations for Strings and the Python str Class (605)  
13.2 Pattern‑Matching Algorithms (606)  
13.2.1 Brute Force (606)  
13.2.2 The Boyer‑Moore Algorithm (608)  
13.3 Dynamic Programming (616)  
13.3.1 Matrix Chain‑Product (616)  
13.3.2 DNA and Text Sequence Alignment (619)  
13.4 Text Compression and the Greedy Method (623)  
13.4.1 The Huffman Coding Algorithm (624)  
13.4.2 The Greedy Method (625)  
13.5 Tries (626)  
13.5.1 Standard Tries (626)  
13.5.2 Compressed Tries (630)  
13.5.3 Suffix Tries (632)  
13.5.4 Search Engine Indexing (634)  
13.6 Exercises (635)  
14 Graph Algorithms (641)  
14.1 Graphs (642)  
14.1.1 The Graph ADT (648)  
14.2 Data Structures for Graphs (649)  
14.2.1 Edge List Structure (650)  
14.2.2 Adjacency List Structure (652)  
14.2.3 Adjacency Map Structure (654)  
14.2.4 Adjacency Matrix Structure (655)  
14.2.5 Python Implementation (656)  
14.3 Graph Traversals (660)  
14.3.1 Depth‑First Search (661)  
14.3.2 DFS Implementation and Extensions (666)  
14.3.3 Breadth‑First Search (670)  
14.4 Transitive Closure (673)  
14.5 Directed Acyclic Graphs (677)  
14.6 Shortest Paths (681)  
14.6.1 Weighted Graphs (681)  
14.6.2 Dijkstra's Algorithm (683)  
14.7 Minimum Spanning Trees (692)  
14.7.1 Prim‑Jarník Algorithm (694)  
14.7.2 Kruskal's Algorithm (698)  
14.7.3 Disjoint Partitions and Union‑Find Structures (703)  
14.8 Exercises (708)  
15 Memory Management and B‑Trees (719)  
15.1 Memory Management (720)  
15.1.1 Memory Allocation (721)  
15.1.2 Garbage Collection (722)  
15.1.3 Additional Memory Used by the Python Interpreter (725)  
15.2 Memory Hierarchies and Caching (727)  
15.3 External Searching and B‑Trees (733)  
15.3.1 (a,b) Trees (734)  
15.3.2 B‑Trees (736)  
15.4 External‑Memory Sorting (737)  
15.5 Exercises (739)  
A Character Strings in Python (743)  
B Useful Mathematical Facts (747)  
Bibliography (754)  
Index (759)

---

**One‑Shot Example**  
User question: "How do list comprehensions differ from conditional expressions?"  
Model output (JSON only):
```json
[
  {
    "chapter": "Python Primer",
    "section": "Additional Python Conveniences",
    "confidence": 0.88
  },
  {
    "chapter": "Python Primer",
    "section": "Comprehension Syntax",
    "confidence": 0.92
  }
]
```

User question: {user_query}
'''

    def __init__(self, embedding_model: EmbeddingModel = None):
        super().__init__(embedding_model=embedding_model)
        self.chunk_index = {  # {('chapter', chapter_name): [keys], ('section', section_name): [keys]}
        }

    def insert(self, chunk: dict, vector: np.array) -> None:
        key = chunk['text']
        self.vectors[key] = {"vector": vector, "metadata": chunk.get('metadata', {})}

    async def abuild_from_list(self, list_of_chunks: List[dict]) -> "VectorDatabase":
        embeddings = await self.embedding_model.async_get_embeddings([chunk['text'] for chunk in list_of_chunks])
        for chunk, embedding in zip(list_of_chunks, embeddings):
            self.insert(chunk, np.array(embedding))
        return self

    def build_chunk_index(self, chunks: list):
        """
        Build an index mapping each chunk to its chapter and section.
        Each chunk should be a dict or object with 'text' and 'metadata' (containing 'chapter' and 'section').
        The index is stored as self.chunk_index.
        """
        self.chunk_index = {}
        for chunk in chunks:
            key = chunk['text'] if isinstance(chunk, dict) else getattr(chunk, 'text', None)
            metadata = chunk['metadata'] if isinstance(chunk, dict) else getattr(chunk, 'metadata', {})
            chapter = metadata.get('chapter')
            section = metadata.get('section')
            # Index by chapter
            if chapter:
                self.chunk_index.setdefault(('chapter', chapter), []).append(key)
            # Index by section
            if section:
                self.chunk_index.setdefault(('section', f"{chapter} - {section}"), []).append(key)

    def gpt_section_chapter_match(self, query_text: str):
        """
        Calls ChatGPT to map the user query to relevant chapter/section(s) using the provided prompt and parses the JSON response.
        """
        chat = ChatOpenAI()
        prompt = self.gpt_prompt.replace('{user_query}', query_text)
        response = chat.run([
            {"role": "user", "content": prompt}
        ])
        # Extract JSON from response
        try:
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            json_str = response[json_start:json_end]
            parsed = json.loads(json_str)
            # Return as list of (('chapter', chapter), ('section', section)) keys
            keys = []
            for item in parsed:
                chapter = item.get('chapter')
                section = item.get('section')
                if chapter:
                    keys.append(("chapter", chapter))
                if section:
                    keys.append(("section", section))
            return keys
        except Exception as e:
            print(f"Error parsing GPT response: {e}\nResponse: {response}")
            return []

    def search_by_text(
        self,
        query_text: str,
        k: int,
        distance_measure: Callable = cosine_similarity,
        return_as_text: bool = False,
    ) -> List[Tuple[str, float]]:
        # Task 3A: Get relevant sections/chapters (placeholder)
        relevant_keys = self.gpt_section_chapter_match(query_text)
        # Task 3B: Use the index to get matching embedding keys
        candidate_keys = set()
        for key in relevant_keys:
            candidate_keys.update(self.chunk_index.get(key, []))
        # If no matches, fall back to all embeddings
        if not candidate_keys:
            candidate_keys = set(self.vectors.keys())
        # Get query vector
        query_vector = self.embedding_model.get_embedding(query_text)
        # Only search over candidate keys
        scores = [
            (key, distance_measure(query_vector, self.vectors[key]["vector"]))
            for key in candidate_keys
        ]
        results = sorted(scores, key=lambda x: x[1], reverse=True)[:k]
        return [result[0] for result in results] if return_as_text else results


if __name__ == "__main__":
    list_of_text = [
        "I like to eat broccoli and bananas.",
        "I ate a banana and spinach smoothie for breakfast.",
        "Chinchillas and kittens are cute.",
        "My sister adopted a kitten yesterday.",
        "Look at this cute hamster munching on a piece of broccoli.",
    ]

    vector_db = VectorDatabase()
    vector_db = asyncio.run(vector_db.abuild_from_list(list_of_text))
    k = 2

    searched_vector = vector_db.search_by_text("I think fruit is awesome!", k=k)
    print(f"Closest {k} vector(s):", searched_vector)

    retrieved_vector = vector_db.retrieve_from_key(
        "I like to eat broccoli and bananas."
    )
    print("Retrieved vector:", retrieved_vector)

    relevant_texts = vector_db.search_by_text(
        "I think fruit is awesome!", k=k, return_as_text=True
    )
    print(f"Closest {k} text(s):", relevant_texts)
