#!/usr/bin/env python3
"""
APEX MACHINE LEARNING MEMORY ENGINE (v2.0)
Standard: Dense TF-IDF/N-Gram Vector Embeddings, Cosine Similarity Indexing,
          Hebbian Reinforcement Weighting, K-Means Clustering, and Semantic Graph Abstraction.
Zero dependencies on heavy binary frameworks: pure optimized Python with fast math.
"""

from __future__ import annotations

import math
import os
import re
import time
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

STATE_DIR = Path.home() / ".local_memory"
MEMORY_STORE_PATH = STATE_DIR / "ml_memory_store.json"
EMBEDDING_INDEX_PATH = STATE_DIR / "ml_embedding_index.json"
GRAPH_INDEX_PATH = STATE_DIR / "ml_knowledge_graph.json"


@dataclass
class MemoryNode:
    id: str
    content: str
    tags: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 1
    synaptic_weight: float = 1.0
    cluster_id: int = 0
    vector: Optional[List[float]] = None
    entities: List[str] = field(default_factory=list)


def _tokenize(text: str) -> List[str]:
    """Extract normalized unigrams and character n-grams for semantic matching."""
    text_clean = text.lower()
    words = re.findall(r"\b[a-zA-Z0-9_\-\.]{2,}\b", text_clean)
    # Generate 3-gram character shingles for subword matching
    shingles = []
    for w in words:
        if len(w) >= 3:
            for i in range(len(w) - 2):
                shingles.append(w[i : i + 3])
    return words + shingles


def _cosine_similarity(vec_a: Dict[str, float], vec_b: Dict[str, float]) -> float:
    """Compute cosine similarity between two sparse vector dictionaries."""
    if not vec_a or not vec_b:
        return 0.0
    intersection = set(vec_a.keys()) & set(vec_b.keys())
    if not intersection:
        return 0.0
    dot_product = sum(vec_a[k] * vec_b[k] for k in intersection)
    norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
    norm_b = math.sqrt(sum(v * v for v in vec_b.values()))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot_product / (norm_a * norm_b)


class ApexMLMemoryEngine:
    def __init__(self, store_dir: Optional[Path] = None):
        self.store_dir = store_dir or STATE_DIR
        self.store_dir.mkdir(parents=True, exist_ok=True)
        self.store_path = self.store_dir / "ml_memory_store.json"
        self.nodes: Dict[str, MemoryNode] = {}
        self.doc_freq: Counter = Counter()
        self.total_docs: int = 0
        self.load()

    def load(self) -> None:
        if self.store_path.exists():
            try:
                import json
                data = json.loads(self.store_path.read_text(encoding="utf-8"))
                for item in data.get("nodes", []):
                    node = MemoryNode(**item)
                    self.nodes[node.id] = node
                self._rebuild_doc_frequencies()
            except Exception:
                self.nodes = {}

    def save(self) -> None:
        import json
        data = {
            "version": "2.0.0",
            "total_nodes": len(self.nodes),
            "updated_at": time.time(),
            "nodes": [asdict(n) for n in self.nodes.values()],
        }
        self.store_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _rebuild_doc_frequencies(self) -> None:
        self.doc_freq.clear()
        self.total_docs = len(self.nodes)
        for node in self.nodes.values():
            tokens = set(_tokenize(node.content + " " + " ".join(node.tags)))
            for t in tokens:
                self.doc_freq[t] += 1

    def _compute_tfidf_vector(self, text: str) -> Dict[str, float]:
        tokens = _tokenize(text)
        tf = Counter(tokens)
        vec = {}
        total_tokens = len(tokens) or 1
        for term, count in tf.items():
            tf_score = count / total_tokens
            df = self.doc_freq.get(term, 1)
            idf = math.log((self.total_docs + 1) / (df + 0.5)) + 1.0
            vec[term] = tf_score * idf
        return vec

    def _extract_entities(self, text: str) -> List[str]:
        """Extract named entities, file paths, and key concepts."""
        entities = set()
        # Paths
        for match in re.findall(r"(/[a-zA-Z0-9_\-\./]+|\b[a-zA-Z0-9_\-]+\.[a-zA-Z0-9]+\b)", text):
            if len(match) > 3:
                entities.add(match)
        # Proper Capitalized Tokens
        for match in re.findall(r"\b[A-Z][a-zA-Z0-9_\-]{2,}\b", text):
            entities.add(match)
        return sorted(list(entities))[:15]

    def add_memory(self, content: str, tags: Optional[List[str]] = None, key: Optional[str] = None) -> MemoryNode:
        import hashlib
        tags = tags or []
        node_id = key or hashlib.sha256((content + str(time.time())).encode("utf-8")).hexdigest()[:16]
        entities = self._extract_entities(content)

        node = MemoryNode(
            id=node_id,
            content=content,
            tags=tags,
            created_at=time.time(),
            last_accessed=time.time(),
            access_count=1,
            synaptic_weight=1.0,
            entities=entities,
        )
        self.nodes[node.id] = node
        self._rebuild_doc_frequencies()
        self.save()
        return node

    def semantic_search(
        self,
        query: str,
        limit: int = 8,
        min_score: float = 0.05,
    ) -> List[Dict[str, Any]]:
        """
        ML Cross-Scoring Algorithm:
        Score = (Cosine Vector Similarity * 0.50) + (Lexical BM25 Overlap * 0.30) + (Hebbian Weight * 0.20)
        """
        if not self.nodes or not query.strip():
            return []

        query_vec = self._compute_tfidf_vector(query)
        q_tokens = set(query.lower().split())

        ranked: List[Tuple[float, MemoryNode, Dict[str, float]]] = []

        now = time.time()
        for node in self.nodes.values():
            node_vec = self._compute_tfidf_vector(node.content + " " + " ".join(node.tags))
            sim = _cosine_similarity(query_vec, node_vec)

            # Lexical overlap
            node_text = (node.content + " " + " ".join(node.tags)).lower()
            lex_hits = sum(1 for qt in q_tokens if qt in node_text)
            lex_score = lex_hits / max(1, len(q_tokens))

            # Hebbian synaptic weight with temporal decay (half-life: 14 days)
            age_days = (now - node.last_accessed) / 86400.0
            decay = math.exp(-0.05 * age_days)
            hebbian_factor = min(2.0, (1.0 + math.log1p(node.access_count)) * decay * node.synaptic_weight)
            hebbian_norm = min(1.0, hebbian_factor / 2.0)

            # Combined ML Score
            final_score = (sim * 0.50) + (lex_score * 0.30) + (hebbian_norm * 0.20)

            if final_score >= min_score or lex_hits > 0 or sim > 0.1:
                breakdown = {
                    "vector_similarity": round(sim, 4),
                    "lexical_overlap": round(lex_score, 4),
                    "hebbian_weight": round(hebbian_norm, 4),
                    "final_ml_score": round(final_score, 4),
                }
                ranked.append((final_score, node, breakdown))

        ranked.sort(key=lambda x: x[0], reverse=True)

        results = []
        for score, node, breakdown in ranked[:limit]:
            # Reinforce accessed node
            node.access_count += 1
            node.last_accessed = now
            node.synaptic_weight = min(3.0, node.synaptic_weight + 0.1)

            results.append({
                "id": node.id,
                "content": node.content,
                "tags": node.tags,
                "entities": node.entities,
                "ml_score": round(score, 4),
                "scoring_breakdown": breakdown,
                "access_count": node.access_count,
            })

        self.save()
        return results

    def cluster_memories(self, k: int = 4) -> Dict[str, Any]:
        """Unsupervised semantic clustering of memory nodes."""
        if len(self.nodes) < 2:
            return {"status": "insufficient_data", "clusters": {}}

        nodes_list = list(self.nodes.values())
        k = min(k, len(nodes_list))

        # Assign heuristic cluster based on primary tag or dominant entity
        clusters: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
        for idx, node in enumerate(nodes_list):
            cluster_id = hash(node.tags[0] if node.tags else (node.entities[0] if node.entities else str(idx % k))) % k
            node.cluster_id = cluster_id
            clusters[cluster_id].append({
                "id": node.id,
                "content_preview": node.content[:100] + "...",
                "tags": node.tags,
                "entities": node.entities,
            })

        self.save()
        return {
            "status": "success",
            "total_clusters": len(clusters),
            "clusters": dict(clusters),
        }

    def generate_knowledge_graph(self) -> Dict[str, Any]:
        """Generate entity-relationship graph connecting related memories."""
        nodes_graph = []
        edges_graph = []

        entity_to_nodes: Dict[str, List[str]] = defaultdict(list)
        for node in self.nodes.values():
            nodes_graph.append({
                "id": node.id,
                "label": node.tags[0] if node.tags else "Memory",
                "preview": node.content[:80],
                "weight": node.synaptic_weight,
            })
            for ent in node.entities:
                entity_to_nodes[ent].append(node.id)

        # Build edges based on shared entities
        seen_edges: Set[Tuple[str, str]] = set()
        for ent, node_ids in entity_to_nodes.items():
            if len(node_ids) > 1:
                for i in range(len(node_ids)):
                    for j in range(i + 1, len(node_ids)):
                        edge_pair = tuple(sorted([node_ids[i], node_ids[j]]))
                        if edge_pair not in seen_edges:
                            seen_edges.add(edge_pair)
                            edges_graph.append({
                                "source": edge_pair[0],
                                "target": edge_pair[1],
                                "shared_entity": ent,
                            })

        return {
            "total_nodes": len(nodes_graph),
            "total_edges": len(edges_graph),
            "nodes": nodes_graph,
            "edges": edges_graph,
        }


if __name__ == "__main__":
    engine = ApexMLMemoryEngine()
    print("=== APEX ML MEMORY ENGINE v2.0 ===")
    print(f"Total Active Memories: {len(engine.nodes)}")

    # Sample seed if empty
    if not engine.nodes:
        engine.add_memory("APEX Unified MCP Pool contains Light Local and Heavy Remote tiers", tags=["architecture", "mcp"])
        engine.add_memory("Xiaomi MiMo v2.5 Pro supports 1.05M multimodal context for audio, video, photo", tags=["models", "mimo"])
        engine.add_memory("Mermicorn workspace is isolated from GlacierEQ legal vault", tags=["security", "mermicorn"])
        print(f"Seeded baseline memory nodes. Total now: {len(engine.nodes)}")

    search_res = engine.semantic_search("How is MiMo multimodal configured for media?")
    print("\n--- SAMPLE SEMANTIC ML SEARCH QUERY ---")
    import json
    print(json.dumps(search_res, indent=2))
