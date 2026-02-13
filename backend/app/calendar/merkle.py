"""
Merkle Tree Implementation for Festival Provenance

Provides cryptographic verification that festival dates are derived
from a canonical, auditable dataset.
"""

import hashlib
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class MerkleProof:
    """Merkle proof for a single leaf."""
    leaf_hash: str
    proof: List[Tuple[str, str]]  # List of (hash, position) where position is 'left' or 'right'
    root: str
    
    def to_dict(self) -> Dict:
        return {
            "leaf_hash": self.leaf_hash,
            "proof": [{"hash": h, "position": p} for h, p in self.proof],
            "root": self.root,
        }


def sha256_hash(data: str) -> str:
    """Compute SHA-256 hash of string."""
    return hashlib.sha256(data.encode()).hexdigest()


def hash_pair(left: str, right: str) -> str:
    """Hash two hashes together."""
    return sha256_hash(left + right)


class MerkleTree:
    """
    Merkle tree for festival data provenance.
    
    Each leaf represents one (year, festival_id) -> date mapping.
    """
    
    def __init__(self, leaves: List[Dict[str, Any]]):
        """
        Build Merkle tree from leaves.
        
        Args:
            leaves: List of dictionaries, each representing a festival date entry
        """
        # Create leaf hashes
        self.leaves = leaves
        self.leaf_hashes = [
            sha256_hash(json.dumps(leaf, sort_keys=True))
            for leaf in leaves
        ]
        
        # Build tree
        self.layers = self._build_tree(self.leaf_hashes.copy())
        self.root = self.layers[-1][0] if self.layers else ""
    
    def _build_tree(self, hashes: List[str]) -> List[List[str]]:
        """Build tree layers from bottom up."""
        if not hashes:
            return []
        
        layers = [hashes]
        
        while len(layers[-1]) > 1:
            current = layers[-1]
            next_layer = []
            
            for i in range(0, len(current), 2):
                left = current[i]
                # If odd number, duplicate last element
                right = current[i + 1] if i + 1 < len(current) else current[i]
                next_layer.append(hash_pair(left, right))
            
            layers.append(next_layer)
        
        return layers
    
    def get_proof(self, index: int) -> Optional[MerkleProof]:
        """
        Get Merkle proof for leaf at index.
        
        Args:
            index: Index of the leaf
        
        Returns:
            MerkleProof or None if index invalid
        """
        if index < 0 or index >= len(self.leaf_hashes):
            return None
        
        # Save original leaf hash before modifying index
        leaf_hash = self.leaf_hashes[index]
        proof = []
        current_index = index
        
        for layer in self.layers[:-1]:
            # Find sibling
            sibling_index = current_index + 1 if current_index % 2 == 0 else current_index - 1
            
            if sibling_index < len(layer):
                position = "right" if current_index % 2 == 0 else "left"
                proof.append((layer[sibling_index], position))
            else:
                # Odd number of elements, duplicate self
                position = "right"
                proof.append((layer[current_index], position))
            
            # Move to parent
            current_index //= 2
        
        return MerkleProof(
            leaf_hash=leaf_hash,
            proof=proof,
            root=self.root,
        )
    
    @staticmethod
    def verify_proof(leaf_hash: str, proof: List[Tuple[str, str]], root: str) -> bool:
        """
        Verify a Merkle proof.
        
        Args:
            leaf_hash: Hash of the leaf to verify
            proof: List of (sibling_hash, position) tuples
            root: Expected Merkle root
        
        Returns:
            True if proof is valid
        """
        current = leaf_hash
        
        for sibling_hash, position in proof:
            if position == "left":
                current = hash_pair(sibling_hash, current)
            else:
                current = hash_pair(current, sibling_hash)
        
        return current == root


def build_merkle_from_snapshot(snapshot_path: Path) -> MerkleTree:
    """
    Build Merkle tree from snapshot.json.
    
    Args:
        snapshot_path: Path to snapshot.json
    
    Returns:
        MerkleTree instance
    """
    with open(snapshot_path) as f:
        snapshot = json.load(f)
    
    # Flatten to leaves: one per (year, festival_id)
    leaves = []
    for year, festivals in snapshot["data"].items():
        for fid, data in festivals.items():
            leaves.append({
                "year": int(year),
                "festival_id": fid,
                **data,
            })
    
    return MerkleTree(leaves)


def get_festival_proof(
    snapshot_path: Path,
    year: int,
    festival_id: str
) -> Optional[MerkleProof]:
    """
    Get Merkle proof for a specific festival.
    
    Args:
        snapshot_path: Path to snapshot.json
        year: Year
        festival_id: Festival ID
    
    Returns:
        MerkleProof or None if not found
    """
    with open(snapshot_path) as f:
        snapshot = json.load(f)
    
    # Build leaves in deterministic order
    leaves = []
    target_index = None
    index = 0
    
    for y in sorted(snapshot["data"].keys(), key=int):
        for fid in sorted(snapshot["data"][y].keys()):
            data = snapshot["data"][y][fid]
            leaf = {
                "year": int(y),
                "festival_id": fid,
                **data,
            }
            leaves.append(leaf)
            
            if int(y) == year and fid == festival_id:
                target_index = index
            
            index += 1
    
    if target_index is None:
        return None
    
    tree = MerkleTree(leaves)
    return tree.get_proof(target_index)


# Cache for Merkle tree
_merkle_cache: Optional[MerkleTree] = None
_merkle_root_cache: Optional[str] = None


def get_merkle_root(snapshot_path: Optional[Path] = None) -> str:
    """Get cached Merkle root (or compute for a specific snapshot path)."""
    global _merkle_cache, _merkle_root_cache

    # Explicit path requests bypass shared cache because callers may switch snapshot ids.
    if snapshot_path is not None:
        if snapshot_path.exists():
            return build_merkle_from_snapshot(snapshot_path).root
        return ""

    if _merkle_root_cache is None:
        default_path = Path(__file__).parent.parent.parent / "data" / "snapshot.json"
        if default_path.exists():
            _merkle_cache = build_merkle_from_snapshot(default_path)
            _merkle_root_cache = _merkle_cache.root
        else:
            _merkle_root_cache = ""

    return _merkle_root_cache
