#!/usr/bin/env python3
"""
Temple Data Preparation Script
==============================

Processes facilities data to extract religious sites for Project Parva.

Note: The facilities.geojson does not contain temple-specific data,
so this script demonstrates the intended workflow while the actual
temples.json was created manually with curated data.

Usage:
    python scripts/prepare_temple_data.py
"""

import json
from pathlib import Path


def load_facilities(filepath: Path) -> dict:
    """Load GeoJSON facilities data."""
    if not filepath.exists():
        print(f"Warning: {filepath} not found")
        return {"features": []}
    
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def filter_religious_sites(features: list) -> list:
    """
    Filter facilities for religious sites.
    
    Looks for:
    - facility_type: temple, stupa, monastery, shrine
    - name contains: mandir, temple, stupa, gumba, bahal
    """
    religious_types = {"temple", "stupa", "monastery", "shrine", "religious"}
    religious_keywords = ["mandir", "temple", "stupa", "gumba", "bahal", "chaitya", "vihar"]
    
    temples = []
    for feature in features:
        props = feature.get("properties", {})
        
        # Check facility_type
        facility_type = props.get("facility_type", "").lower()
        if facility_type in religious_types:
            temples.append(feature)
            continue
        
        # Check name for religious keywords
        name = props.get("name", "").lower()
        name_ne = props.get("name_ne", "").lower()
        
        for keyword in religious_keywords:
            if keyword in name or keyword in name_ne:
                temples.append(feature)
                break
    
    return temples


def transform_to_temple_format(features: list) -> list:
    """Transform GeoJSON features to temple JSON format."""
    temples = []
    
    for i, feature in enumerate(features):
        props = feature.get("properties", {})
        coords = feature.get("geometry", {}).get("coordinates", [0, 0])
        
        temple = {
            "id": props.get("id", f"temple-{i+1}"),
            "name": props.get("name", "Unknown Temple"),
            "name_ne": props.get("name_ne"),
            "type": props.get("facility_type", "temple"),
            "coordinates": {
                "lat": coords[1] if len(coords) > 1 else 0,
                "lng": coords[0] if len(coords) > 0 else 0
            },
            "festivals": [],  # To be filled manually
            "significance": props.get("description", ""),
        }
        temples.append(temple)
    
    return temples


def main():
    """Main function to process temple data."""
    project_root = Path(__file__).parent.parent
    
    # Input paths
    facilities_path = project_root / "data" / "processed" / "facilities.geojson"
    
    # Output path
    output_path = project_root / "data" / "festivals" / "temples.json"
    
    print("=" * 60)
    print("Temple Data Preparation Script")
    print("=" * 60)
    
    # Check if temples.json already exists (manually curated)
    if output_path.exists():
        with open(output_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
        temple_count = len(existing.get("temples", []))
        print(f"\n✅ temples.json already exists with {temple_count} temples")
        print("   This file was manually curated for accuracy.")
        print("   Re-run with --force to regenerate from facilities.geojson")
        return
    
    # Load and process facilities
    print(f"\n📂 Loading: {facilities_path}")
    data = load_facilities(facilities_path)
    features = data.get("features", [])
    print(f"   Found {len(features)} total facilities")
    
    # Filter religious sites
    print("\n🔍 Filtering religious sites...")
    religious_features = filter_religious_sites(features)
    print(f"   Found {len(religious_features)} religious sites")
    
    if not religious_features:
        print("\n⚠️  No religious sites found in facilities.geojson")
        print("   The dataset primarily contains hospitals, schools, and transport.")
        print("   temples.json should be created manually with curated data.")
        return
    
    # Transform to temple format
    print("\n🔄 Transforming to temple format...")
    temples = transform_to_temple_format(religious_features)
    
    # Save output
    output_data = {
        "version": "1.0.0",
        "source": "facilities.geojson",
        "temples": temples
    }
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4, ensure_ascii=False)
    
    print(f"\n✅ Saved {len(temples)} temples to {output_path}")
    print("\n⚠️  Note: Festival connections need to be added manually")


if __name__ == "__main__":
    main()
