#!/usr/bin/env python3
"""
Alkaid Self-Optimization System v2 — QMD Dedup
Uses local QMD vector search for semantic deduplication.
Replaces v1 OpenAI Embedding + cosine similarity.
"""
import asyncio
import re
from typing import List, Tuple


class QMDDedup:
    """Semantic deduplication using QMD local vector search."""

    def __init__(self, qmd_binary: str = "/usr/bin/qmd",
                 collection: str = "alkaid",
                 threshold: float = 0.85):
        self.qmd_binary = qmd_binary
        self.collection = collection
        self.threshold = threshold

    async def is_known(self, description: str) -> Tuple[bool, str]:
        """
        Check if an error/learning is already known in QMD index.

        Args:
            description: Error description or learning text

        Returns:
            (is_known, matching_content)
            - is_known: True if a similar entry exists with score > threshold
            - matching_content: The matching entry text (if known)
        """
        # Sanitize query
        query = description[:200].replace('"', '\\"')

        try:
            proc = await asyncio.create_subprocess_exec(
                self.qmd_binary, "search", query,
                "-c", self.collection,
                "--limit", "3",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=20)
            output = stdout.decode("utf-8", errors="replace")

            results = self._parse_results(output)
            for score, content in results:
                if score >= self.threshold:
                    return True, content

            return False, ""

        except asyncio.TimeoutError:
            return False, ""  # On timeout, assume not known
        except Exception:
            return False, ""

    async def update_index(self) -> bool:
        """Run qmd embed to update the alkaid collection index."""
        try:
            proc = await asyncio.create_subprocess_exec(
                self.qmd_binary, "embed",
                "-c", self.collection,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _, _ = await asyncio.wait_for(proc.communicate(), timeout=60)
            return proc.returncode == 0
        except Exception:
            return False

    def _parse_results(self, output: str) -> List[Tuple[float, str]]:
        """Parse QMD search output into (score, content) tuples."""
        results = []
        # QMD output format varies; try to extract score and content
        lines = output.strip().split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Try to extract score pattern like "[0.92]" or "score: 0.92"
            score_match = re.search(r"[\[\(]?(0\.\d+)[\]\)]?", line)
            if score_match:
                score = float(score_match.group(1))
                content = re.sub(r"[\[\(]?0\.\d+[\]\)]?\s*", "", line).strip()
                results.append((score, content))
        return results
