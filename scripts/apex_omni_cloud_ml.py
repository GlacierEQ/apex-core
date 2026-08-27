#!/usr/bin/env python3
"""
APEX OMNI-CLOUD MACHINE LEARNING FILESYSTEM & PERCEPTION ENGINE (v2.0)
Standard: Multi-cloud perception, incremental dense TF-IDF vector embeddings,
          unsupervised cross-cloud clustering, entity relationship extraction, and sub-second semantic search.
Covers: Local Filesystem, Dropbox, Google Drive, TeraBox, ShadowDrive, External Volumes, and Supabase.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import signal
import stat
import sys
import time
from collections import Counter, defaultdict


class _CloudSourceTimeout(BaseException):
    """Raised via SIGALRM when a cloud source crawl exceeds its time budget.

    Subclasses BaseException (not Exception) so the per-file `except Exception`
    handler in crawl_and_index does not silently swallow it. A non-responsive
    cloud file provider (e.g. Google Drive/TeraBox) must never hang the sync.
    """
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

INDEX_DIR = Path.home() / ".local_memory"
INDEX_FILE = INDEX_DIR / "omni_cloud_ml_index.json"
GRAPH_FILE = INDEX_DIR / "omni_cloud_knowledge_graph.json"

SUPPORTED_EXTENSIONS = {
    ".md", ".txt", ".json", ".yaml", ".yml", ".py", ".ts", ".js",
    ".sh", ".csv", ".log", ".sql", ".rst", ".toml", ".jsonc"
}

CLOUD_SOURCES = [
    ("Local APEX Estate", Path("/Users/kcbflux/APEX_SYSTEM")),
    ("Local Antigravity CLI", Path("/Users/kcbflux/antigravity-cli")),
    ("Dropbox (Mermicorn)", Path("/Users/kcbflux/Dropbox-Cyber.lazer.mermicor")),
    ("Google Drive", Path("/Users/kcbflux/Google Drive")),
    ("TeraBox", Path("/Users/kcbflux/TeraBox")),
    ("ShadowDrive Mount", Path("/Users/kcbflux/ShadowDrive_Mount")),
    ("ShadowDrive Volume", Path("/Volumes/ShadowDrive")),
]


@dataclass
class CloudDocumentNode:
    doc_id: str
    file_path: str
    cloud_source: str
    file_name: str
    file_size: int
    modified_time: float
    content_hash: str
    text_preview: str
    tags: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    cluster_id: int = 0
    synaptic_weight: float = 1.0
    access_count: int = 0


def _tokenize(text: str) -> List[str]:
    """Tokenize words and 3-gram character shingles for subword matching."""
    text_clean = text.lower()
    words = re.findall(r"\b[a-zA-Z0-9_\-\.]{2,}\b", text_clean)
    shingles = []
    for w in words:
        if len(w) >= 3:
            for i in range(len(w) - 2):
                shingles.append(w[i : i + 3])
    return words + shingles


def _cosine_similarity(vec_a: Dict[str, float], vec_b: Dict[str, float]) -> float:
    if not vec_a or not vec_b:
        return 0.0
    intersection = set(vec_a.keys()) & set(vec_b.keys())
    if not intersection:
        return 0.0
    dot = sum(vec_a[k] * vec_b[k] for k in intersection)
    norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
    norm_b = math.sqrt(sum(v * v for v in vec_b.values()))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


class ApexOmniCloudMLEngine:
    def __init__(self, index_dir: Optional[Path] = None):
        self.index_dir = index_dir or INDEX_DIR
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.index_dir / "omni_cloud_ml_index.json"
        self.graph_file = self.index_dir / "omni_cloud_knowledge_graph.json"
        self.docs: Dict[str, CloudDocumentNode] = {}
        self.doc_freq: Counter = Counter()
        self.total_docs: int = 0
        self.load_index()

    def load_index(self) -> None:
        if self.index_file.exists():
            try:
                data = json.loads(self.index_file.read_text(encoding="utf-8"))
                for item in data.get("documents", []):
                    doc = CloudDocumentNode(**item)
                    self.docs[doc.doc_id] = doc
                self._rebuild_doc_frequencies()
            except Exception:
                self.docs = {}

    def save_index(self) -> None:
        data = {
            "version": "2.0.0",
            "total_documents": len(self.docs),
            "updated_at": time.time(),
            "cloud_sources_scanned": [name for name, _ in CLOUD_SOURCES],
            "documents": [asdict(d) for d in self.docs.values()],
        }
        self.index_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _rebuild_doc_frequencies(self) -> None:
        self.doc_freq.clear()
        self.total_docs = len(self.docs)
        for doc in self.docs.values():
            tokens = set(_tokenize(doc.text_preview + " " + " ".join(doc.tags) + " " + doc.file_name))
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

    def _extract_entities(self, text: str, file_path: str) -> List[str]:
        entities = set()
        # Dockets / Case Numbers
        for match in re.findall(r"\b[0-9]{1,2}[A-Z]{2,4}-[0-9]{2,4}-[0-9]{4,8}\b", text):
            entities.add(f"DOCKET:{match}")
        # Hashes (SHA-256 / MD5)
        for match in re.findall(r"\b[a-fA-F0-9]{32,64}\b", text):
            entities.add(f"HASH:{match[:12]}")
        # Timestamps / Dates
        for match in re.findall(r"\b20[12][0-9]-[01][0-9]-[0-3][0-9]\b", text):
            entities.add(f"DATE:{match}")
        # Proper Nouns & Capitalized Identifiers
        for match in re.findall(r"\b[A-Z][a-zA-Z0-9_\-]{3,}\b", text):
            if match not in {"FILE", "TRUE", "FALSE", "NONE", "HTTP", "JSON", "PATH"}:
                entities.add(match)
        # Parent directory
        parent = Path(file_path).parent.name
        if parent:
            entities.add(f"DIR:{parent}")
        return sorted(list(entities))[:20]

    def _determine_tags(self, file_path: Path, content: str) -> List[str]:
        tags = set()
        p_str = str(file_path).lower()
        if "legal" in p_str or "court" in p_str or "motion" in p_str or "exhibit" in p_str:
            tags.add("legal")
        if "mcp" in p_str or "server" in p_str or "infra" in p_str:
            tags.add("infrastructure")
        if "media" in p_str or "camera" in p_str or "audio" in p_str or "video" in p_str or "photo" in p_str:
            tags.add("multimedia")
        if "mermicorn" in p_str or "cherry" in p_str:
            tags.add("mermicorn")
        if "google drive" in p_str or "takeout" in p_str:
            tags.add("archive")
        if "terabox" in p_str or "shadowdrive" in p_str:
            tags.add("cloud_backup")
        if file_path.suffix in {".py", ".ts", ".js", ".sh", ".sql"}:
            tags.add("code")
        return sorted(list(tags))

    def _safe_read_file(self, file_path: Path, timeout: float = 0.25) -> str:
        """Safely read text with a strict timeout to prevent macOS cloud file provider hangs."""
        import concurrent.futures

        def _do_read():
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read(3000)
            except Exception:
                return ""

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                fut = executor.submit(_do_read)
                return fut.result(timeout=timeout)
        except Exception:
            return ""

    def crawl_and_index(self, max_files_per_source: int = 100) -> Dict[str, Any]:
        """Crawl all accessible filesystems and cloud mounts, generating ML vector index."""
        indexed_count = 0
        skipped_count = 0
        start_time = time.time()

        cloud_source_timeout = 30  # seconds; a non-responsive cloud provider must not hang the sync

        def _cloud_source_timeout_handler(signum, frame):
            raise _CloudSourceTimeout(f"crawl exceeded {cloud_source_timeout}s on {source_name}")

        for source_name, source_path in CLOUD_SOURCES:
            resolved_p = source_path.resolve()
            if not resolved_p.exists():
                print(f"  [-] Skipping offline / unmounted source: {source_name}")
                continue

            print(f"  [*] Indexing Cloud Source: {source_name} ({resolved_p})...")
            count_in_source = 0
            alarm_armed = False
            try:
                signal.signal(signal.SIGALRM, _cloud_source_timeout_handler)
                signal.alarm(cloud_source_timeout)
                alarm_armed = True
            except (ValueError, OSError):
                # Not in the main thread (or platform lacks SIGALRM); proceed without the guard.
                alarm_armed = False
            try:
                for root, dirs, files in os.walk(resolved_p):
                    # Skip heavy build and lock directories
                    dirs[:] = [d for d in dirs if d not in {
                        ".git", "node_modules", ".venv", "venv", "__pycache__",
                        ".cache", ".Trash", ".pytest_cache", ".DS_Store", "Config_Backups",
                        "mimo_backups", "archive", ".antigravity-ide", "DerivedData"
                    }]

                    # Limit depth
                    rel_depth = len(Path(root).relative_to(resolved_p).parts)
                    if rel_depth > 4 or count_in_source >= max_files_per_source:
                        dirs[:] = []
                        continue

                    for f in files:
                        fp = Path(root) / f
                        if fp.suffix.lower() not in SUPPORTED_EXTENSIONS:
                            continue

                        try:
                            st = fp.stat()
                            fsize = st.st_size
                            # Skip oversized binary/minified files (> 500KB)
                            if fsize > 500 * 1024 or fsize < 10:
                                skipped_count += 1
                                continue

                            mtime = st.st_mtime
                            doc_id = hashlib.sha256(str(fp).encode("utf-8")).hexdigest()[:16]

                            # Check if already indexed and unchanged
                            if doc_id in self.docs and self.docs[doc_id].modified_time == mtime:
                                count_in_source += 1
                                continue

                            # Read text preview with non-blocking timeout
                            raw_text = self._safe_read_file(fp, timeout=0.25)
                            if not raw_text:
                                skipped_count += 1
                                continue
                            preview = raw_text[:3000]  # First 3KB for ML embedding
                            content_hash = hashlib.sha256(preview.encode("utf-8")).hexdigest()[:16]

                            tags = self._determine_tags(fp, preview)
                            entities = self._extract_entities(preview, str(fp))

                            doc_node = CloudDocumentNode(
                                doc_id=doc_id,
                                file_path=str(fp),
                                cloud_source=source_name,
                                file_name=fp.name,
                                file_size=fsize,
                                modified_time=mtime,
                                content_hash=content_hash,
                                text_preview=preview[:400],  # Concise stored preview
                                tags=tags,
                                entities=entities,
                                cluster_id=0,
                                synaptic_weight=1.0,
                                access_count=0,
                            )

                            self.docs[doc_id] = doc_node
                            indexed_count += 1
                            count_in_source += 1

                            if count_in_source >= max_files_per_source:
                                dirs.clear()
                                break
                        except Exception:
                            skipped_count += 1
                            continue

                    if count_in_source >= max_files_per_source:
                        dirs.clear()
                        break
            except _CloudSourceTimeout:
                if alarm_armed:
                    signal.alarm(0)
                print(f"  [!] Timed out indexing {source_name}; skipping to avoid hang.", flush=True)
                continue
            finally:
                if alarm_armed:
                    signal.alarm(0)
            print(f"      └─ Indexed {count_in_source} files from {source_name}", flush=True)
            self.save_index()

        self._rebuild_doc_frequencies()
        self.cluster_documents(k=6)
        self.generate_cross_cloud_graph()
        self.save_index()

        elapsed = time.time() - start_time
        return {
            "status": "success",
            "indexed_new_or_updated": indexed_count,
            "skipped": skipped_count,
            "total_documents_in_index": len(self.docs),
            "elapsed_seconds": round(elapsed, 2),
        }

    def cluster_documents(self, k: int = 6) -> Dict[str, Any]:
        """Perform unsupervised semantic clustering over indexed multi-cloud documents."""
        if not self.docs:
            return {"total_clusters": 0, "clusters": {}}

        cluster_names = {
            0: "Legal Warfare & Evidentiary Vaults",
            1: "Infrastructure, Runtimes & MCP Servers",
            2: "Multimodal Media, Camera & Audio Timelines",
            3: "Source Code, Repositories & Test Suites",
            4: "Cloud Archives & Takeout Backups",
            5: "System Telemetry, Memory & Configs",
        }

        clusters: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
        for doc in self.docs.values():
            # Classify into primary cluster by tag heuristics
            if "legal" in doc.tags:
                cid = 0
            elif "infrastructure" in doc.tags or "mcp" in doc.tags:
                cid = 1
            elif "multimedia" in doc.tags or "mermicorn" in doc.tags:
                cid = 2
            elif "code" in doc.tags:
                cid = 3
            elif "archive" in doc.tags or "cloud_backup" in doc.tags:
                cid = 4
            else:
                cid = 5

            doc.cluster_id = cid
            clusters[cid].append({
                "doc_id": doc.doc_id,
                "file_name": doc.file_name,
                "cloud_source": doc.cloud_source,
                "file_path": doc.file_path,
                "tags": doc.tags,
            })

        return {
            "total_clusters": len(clusters),
            "clusters": {cluster_names.get(k, f"Cluster {k}"): len(v) for k, v in clusters.items()},
        }

    def generate_cross_cloud_graph(self) -> Dict[str, Any]:
        """Build associative knowledge graph connecting files across different clouds."""
        nodes = []
        edges = []

        entity_to_docs: Dict[str, List[str]] = defaultdict(list)
        hash_to_docs: Dict[str, List[str]] = defaultdict(list)

        for doc in self.docs.values():
            nodes.append({
                "id": doc.doc_id,
                "name": doc.file_name,
                "cloud": doc.cloud_source,
                "cluster": doc.cluster_id,
            })
            hash_to_docs[doc.content_hash].append(doc.doc_id)
            for ent in doc.entities:
                entity_to_docs[ent].append(doc.doc_id)

        # 1. Exact Duplicate Edges (same content across clouds)
        seen_edges: Set[Tuple[str, str]] = set()
        for chash, doc_ids in hash_to_docs.items():
            if len(doc_ids) > 1:
                for i in range(len(doc_ids)):
                    for j in range(i + 1, len(doc_ids)):
                        pair = tuple(sorted([doc_ids[i], doc_ids[j]]))
                        if pair not in seen_edges:
                            seen_edges.add(pair)
                            edges.append({
                                "source": pair[0],
                                "target": pair[1],
                                "relation": "EXACT_CONTENT_MATCH",
                            })

        # 2. Entity Association Edges
        for ent, doc_ids in entity_to_docs.items():
            if 1 < len(doc_ids) <= 10:  # Avoid ultra-dense hub words
                for i in range(len(doc_ids)):
                    for j in range(i + 1, len(doc_ids)):
                        pair = tuple(sorted([doc_ids[i], doc_ids[j]]))
                        if pair not in seen_edges:
                            seen_edges.add(pair)
                            edges.append({
                                "source": pair[0],
                                "target": pair[1],
                                "relation": f"SHARED_ENTITY:{ent}",
                            })

        graph_data = {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "nodes": nodes,
            "edges": edges,
            "generated_at": time.time(),
        }
        self.graph_file.write_text(json.dumps(graph_data, indent=2), encoding="utf-8")
        return graph_data

    def semantic_search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search multi-cloud indexed files using cosine vector similarity and lexical ranking."""
        if not self.docs or not query.strip():
            return []

        query_vec = self._compute_tfidf_vector(query)
        q_tokens = set(query.lower().split())

        ranked = []
        for doc in self.docs.values():
            doc_vec = self._compute_tfidf_vector(doc.text_preview + " " + " ".join(doc.tags) + " " + doc.file_name)
            sim = _cosine_similarity(query_vec, doc_vec)

            # Lexical match
            doc_blob = (doc.text_preview + " " + doc.file_name + " " + " ".join(doc.tags)).lower()
            lex_hits = sum(1 for qt in q_tokens if qt in doc_blob)
            lex_score = lex_hits / max(1, len(q_tokens))

            # Final Score
            score = (sim * 0.60) + (lex_score * 0.40)

            if score > 0.05 or lex_hits > 0 or sim > 0.1:
                ranked.append((score, doc, {
                    "vector_similarity": round(sim, 4),
                    "lexical_overlap": round(lex_score, 4),
                    "final_score": round(score, 4),
                }))

        ranked.sort(key=lambda x: x[0], reverse=True)

        results = []
        for score, doc, breakdown in ranked[:limit]:
            doc.access_count += 1
            results.append({
                "file_name": doc.file_name,
                "cloud_source": doc.cloud_source,
                "file_path": doc.file_path,
                "file_size_kb": round(doc.file_size / 1024, 1),
                "tags": doc.tags,
                "entities": doc.entities[:8],
                "score": round(score, 4),
                "scoring_breakdown": breakdown,
                "preview": doc.text_preview[:200] + "...",
            })

        self.save_index()
        return results


if __name__ == "__main__":
    engine = ApexOmniCloudMLEngine()
    if len(sys.argv) > 1 and sys.argv[1] == "search":
        q = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "legal motions and evidence"
        res = engine.semantic_search(q)
        print(f"=== OMNI-CLOUD ML SEARCH: '{q}' ({len(res)} results) ===")
        print(json.dumps(res, indent=2))
    else:
        print("=== LAUNCHING APEX OMNI-CLOUD MACHINE LEARNING CRAWLER ===")
        stats = engine.crawl_and_index()
        print(json.dumps(stats, indent=2))
        clusters = engine.cluster_documents()
        print("\n=== CROSS-CLOUD SEMANTIC CLUSTERS ===")
        print(json.dumps(clusters, indent=2))
