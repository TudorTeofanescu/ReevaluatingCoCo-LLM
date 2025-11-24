#!/usr/bin/env python3
"""
Get next N unanalyzed extensions and split into groups for parallel analysis.
"""

import sys
from pathlib import Path

def get_unanalyzed_extensions(extensions_dir, analysis_dir, limit=50):
    """
    Find extensions that haven't been analyzed yet.

    Args:
        extensions_dir: Directory containing extension folders
        analysis_dir: Directory containing analysis markdown files
        limit: Maximum number of extensions to return

    Returns:
        List of extension IDs
    """
    ext_path = Path(extensions_dir)
    analysis_path = Path(analysis_dir)

    # Get all extension IDs from directory
    all_extensions = sorted([d.name for d in ext_path.iterdir() if d.is_dir()])

    # Get already analyzed extension IDs
    analyzed = set()
    if analysis_path.exists():
        for md_file in analysis_path.glob("*_analysis.md"):
            ext_id = md_file.stem.replace("_analysis", "")
            analyzed.add(ext_id)

    # Filter to unanalyzed only
    unanalyzed = [ext_id for ext_id in all_extensions if ext_id not in analyzed]

    return unanalyzed[:limit]

def split_into_groups(items, group_size):
    """Split list into groups of specified size."""
    return [items[i:i + group_size] for i in range(0, len(items), group_size)]

def main():
    # Configuration
    num_agents = 10
    extensions_per_agent = 5
    total_extensions = num_agents * extensions_per_agent

    # Paths (relative to DatasetCoCoCategorization root)
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    extensions_dir = str(root_dir / "VulnerableExtensions")
    analysis_dir = str(root_dir / "llm coco analysis")

    print(f"Getting next {total_extensions} unanalyzed extensions...")
    extension_ids = get_unanalyzed_extensions(extensions_dir, analysis_dir, total_extensions)

    if len(extension_ids) == 0:
        print("No unanalyzed extensions found!")
        sys.exit(0)

    if len(extension_ids) < total_extensions:
        print(f"Warning: Only {len(extension_ids)} unanalyzed extensions remaining")
        # Adjust number of agents if needed
        num_agents = (len(extension_ids) + extensions_per_agent - 1) // extensions_per_agent

    # Split into groups
    groups = split_into_groups(extension_ids, extensions_per_agent)

    print(f"\n=== Extension ID Assignment ===")
    print(f"Total agents: {len(groups)}")
    print(f"Extensions per agent: ~{extensions_per_agent}")
    print(f"Total extensions: {len(extension_ids)}\n")

    # Print assignments
    for i, group in enumerate(groups, 1):
        print(f"Agent {i}: {', '.join(group)}")

if __name__ == "__main__":
    main()
