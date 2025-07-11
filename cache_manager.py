#!/usr/bin/env python3
"""Cache management utility for Starlight."""

import sys
import argparse
sys.path.insert(0, 'src')

from starlight.cache import cache_info, clear_cache, cache_size


def main():
    """Main cache management interface."""
    parser = argparse.ArgumentParser(description='Manage Starlight cache')
    parser.add_argument('action', choices=['info', 'clear', 'size'], 
                       help='Action to perform')
    parser.add_argument('--type', choices=['ephemeris', 'geocoding', 'general'],
                       help='Cache type to operate on (default: all)')
    
    args = parser.parse_args()
    
    if args.action == 'info':
        info = cache_info()
        print("🗂️  Starlight Cache Information")
        print("=" * 40)
        print(f"Cache Directory: {info['cache_directory']}")
        print(f"Max Age: {info['max_age_seconds']} seconds ({info['max_age_seconds']/3600:.1f} hours)")
        print(f"Total Files: {info['total_cached_files']}")
        print(f"Total Size: {info['cache_size_mb']} MB")
        print()
        print("By Type:")
        for cache_type, count in info['by_type'].items():
            print(f"  {cache_type}: {count} files")
    
    elif args.action == 'size':
        sizes = cache_size(args.type)
        print("📊 Cache Size Information")
        print("=" * 30)
        for cache_type, count in sizes.items():
            print(f"{cache_type}: {count} files")
    
    elif args.action == 'clear':
        if args.type:
            removed = clear_cache(args.type)
            print(f"🗑️  Cleared {removed} files from {args.type} cache")
        else:
            removed = clear_cache()
            print(f"🗑️  Cleared {removed} files from all caches")
    
    print()


if __name__ == "__main__":
    main()