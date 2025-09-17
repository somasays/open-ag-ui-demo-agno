#!/usr/bin/env python3
"""
Verify API credentials are properly configured.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def check_credentials():
    """Check if API credentials are properly set."""
    print("🔍 Checking API Credentials...\n")

    # Check FRED API Key
    fred_key = os.getenv('FRED_API_KEY', '')
    if fred_key and fred_key != 'your_32_character_fred_api_key_here':
        if len(fred_key) == 32:
            print("✅ FRED_API_KEY: Valid format (32 characters)")
        else:
            print(f"⚠️  FRED_API_KEY: Wrong length (got {len(fred_key)}, expected 32)")
    else:
        print("❌ FRED_API_KEY: Not set or still using placeholder")
        print("   → Get your free key at: https://fred.stlouisfed.org/docs/api/api_key.html")

    # Check Exa API Key
    exa_key = os.getenv('EXA_API_KEY', '')
    if exa_key and exa_key != 'your_exa_api_key_here':
        print(f"✅ EXA_API_KEY: Set ({len(exa_key)} characters)")
    else:
        print("❌ EXA_API_KEY: Not set or still using placeholder")
        print("   → Get your key at: https://exa.ai/")

    # Check OpenAI API Key
    openai_key = os.getenv('OPENAI_API_KEY', '')
    if openai_key and openai_key.startswith('sk-'):
        print(f"✅ OPENAI_API_KEY: Set (starts with 'sk-')")
    else:
        print("❌ OPENAI_API_KEY: Not set or invalid format")

    # Check integration test flag
    integration_test = os.getenv('INTEGRATION_TEST', 'false')
    if integration_test.lower() == 'true':
        print("✅ INTEGRATION_TEST: Enabled")
    else:
        print("ℹ️  INTEGRATION_TEST: Disabled (set to 'true' to run real API tests)")

    print("\n" + "="*50)

    # Summary
    if (fred_key and len(fred_key) == 32 and
        exa_key and exa_key != 'your_exa_api_key_here'):
        print("✅ Ready to run real integration tests!")
        print("\nRun: poetry run pytest tests/test_market_analysis_v2/test_integration_real.py -v")
    else:
        print("⚠️  Please add your API keys to .env file first")
        print("\nEdit: /Users/soma/ssa/code/personal/open-ag-ui-demo-agno/agent/.env")

if __name__ == "__main__":
    check_credentials()