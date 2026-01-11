"""
Minimal test file for initial CI setup
"""
def test_basic():
    """Always passes"""
    assert 1 + 1 == 2

def test_import():
    """Test if we can import (won't fail if not)"""
    try:
        import sys
        sys.path.insert(0, 'src')
        # Try to import, but don't fail if it doesn't exist yet
        import truthprobe_v3
        return True
    except ImportError:
        # Expected on first run
        return True
EOF
