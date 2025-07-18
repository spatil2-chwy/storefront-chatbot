#!/usr/bin/env python3
"""
Single script to run all data loading processes
"""
import subprocess
import sys
from pathlib import Path

def run_script(script_name, description, cwd=None):
    print(f"\n🚀 {description}")
    print("=" * 50)
    
    try:
        result = subprocess.run([sys.executable, script_name], check=True, cwd=cwd)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        return False

def main():
    print("🎯 Running all data loading scripts...")
    
    # Get the scripts directory
    scripts_dir = Path(__file__).parent
    
    # Define scripts to run in order with their working directories
    scripts = [
        ("customer_persona_enhancer.py", "Enhancing customer data with personas", "."),
        ("../server/src/load_data.py", "Loading customer and pet data to SQLite", "../server"),
        ("articledbbuilder.py", "Building article database", "."),
        ("review_synthesis_dbbuilder.py", "Building review synthesis database", "."),
    ]
    
    success_count = 0
    
    for script, description, cwd in scripts:
        script_path = scripts_dir / script
        if script_path.exists():
            if run_script(str(script_path), description, cwd):
                success_count += 1
        else:
            print(f"⚠️  Script not found: {script_path}")
    
    print(f"\n📊 Summary: {success_count}/{len(scripts)} scripts completed successfully")
    
    if success_count == len(scripts):
        print("🎉 All data loaded successfully!")
    else:
        print("⚠️  Some scripts failed. Check the output above.")

if __name__ == "__main__":
    main() 