#!/usr/bin/env python3
"""
Test script for Market Analysis Stub Data Generation
Run this to test the stub data generator independently
"""

import sys
import os

# Add the agent directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'agent'))

try:
    from market_analysis_v2.stub_data import MarketAnalysisStubData
    print("✅ Successfully imported MarketAnalysisStubData")
except ImportError as e:
    print(f"❌ Failed to import MarketAnalysisStubData: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

def test_stub_data_generation():
    """Test the stub data generation functionality"""

    print("\n" + "="*60)
    print("🧪 TESTING MARKET ANALYSIS STUB DATA GENERATION")
    print("="*60)

    # Initialize the stub data generator
    stub_generator = MarketAnalysisStubData()

    # Sample portfolio for testing
    test_portfolio = ["AAPL", "MSFT", "GOOGL", "NVDA"]
    test_query = "How will Fed rate changes impact my tech stocks?"

    print(f"\n📊 Test Portfolio: {test_portfolio}")
    print(f"❓ Test Query: '{test_query}'")

    # Test individual components
    print("\n" + "-"*40)
    print("1️⃣ Testing Economic Data Generation")
    print("-"*40)

    try:
        economic_data = stub_generator.generate_economic_data(delay_simulation=False)
        print("✅ Economic data generated successfully")
        print(f"   Federal Funds Rate: {economic_data['federal_funds_rate']['value']}%")
        print(f"   Inflation Rate: {economic_data['inflation_rate']['value']}%")
        print(f"   GDP Growth: {economic_data['gdp_growth']['value']}%")
        print(f"   Unemployment Rate: {economic_data['unemployment_rate']['value']}%")
    except Exception as e:
        print(f"❌ Economic data generation failed: {e}")
        return False

    print("\n" + "-"*40)
    print("2️⃣ Testing News Analysis Generation")
    print("-"*40)

    try:
        news_analysis = stub_generator.generate_news_analysis(test_portfolio, test_query, delay_simulation=False)
        print("✅ News analysis generated successfully")
        print(f"   Articles found: {len(news_analysis['articles'])}")
        print(f"   Overall sentiment: {news_analysis['sentiment_summary']['overall_tone']}")
        print(f"   Portfolio coverage: {news_analysis['portfolio_relevance']['coverage_score']:.1%}")
    except Exception as e:
        print(f"❌ News analysis generation failed: {e}")
        return False

    print("\n" + "-"*40)
    print("3️⃣ Testing Portfolio Impact Generation")
    print("-"*40)

    try:
        portfolio_impact = stub_generator.generate_portfolio_impact(
            test_portfolio, economic_data, news_analysis, delay_simulation=False
        )
        print("✅ Portfolio impact generated successfully")
        print(f"   Holdings analyzed: {len(portfolio_impact['holdings_impact'])}")
        print(f"   Overall risk level: {portfolio_impact['overall_risk_assessment']['level']}")
        print(f"   Recommended actions: {len(portfolio_impact['recommended_actions'])}")
    except Exception as e:
        print(f"❌ Portfolio impact generation failed: {e}")
        return False

    print("\n" + "-"*40)
    print("4️⃣ Testing Complete Analysis Generation")
    print("-"*40)

    try:
        complete_analysis = stub_generator.generate_complete_analysis(
            test_portfolio, test_query, enable_delays=False
        )
        print("✅ Complete analysis generated successfully")
        print(f"   Status: {complete_analysis['status']}")
        print(f"   Processing time: {complete_analysis['processing_time_ms']}ms")
        print(f"   Components: economic_data, news_analysis, portfolio_impact")
    except Exception as e:
        print(f"❌ Complete analysis generation failed: {e}")
        return False

    print("\n" + "-"*40)
    print("5️⃣ Testing Streaming Events Generation")
    print("-"*40)

    try:
        streaming_events = stub_generator.simulate_streaming_events(test_portfolio, test_query)
        print("✅ Streaming events generated successfully")
        print(f"   Total events: {len(streaming_events)}")

        event_types = [event['type'] for event in streaming_events]
        unique_types = list(set(event_types))
        print(f"   Event types: {', '.join(unique_types)}")

        # Show event sequence
        print("   Event sequence:")
        for i, event in enumerate(streaming_events[:8]):  # Show first 8 events
            print(f"     {i+1}. {event['type']}")
        if len(streaming_events) > 8:
            print(f"     ... and {len(streaming_events) - 8} more events")

    except Exception as e:
        print(f"❌ Streaming events generation failed: {e}")
        return False

    print("\n" + "="*60)
    print("🎉 ALL TESTS PASSED SUCCESSFULLY!")
    print("="*60)
    print("\n📋 Summary:")
    print("   ✅ Economic data generation working")
    print("   ✅ News analysis generation working")
    print("   ✅ Portfolio impact generation working")
    print("   ✅ Complete analysis generation working")
    print("   ✅ Streaming events generation working")
    print("\n🚀 The stub data generator is ready for frontend integration!")

    return True

def show_sample_data():
    """Show a sample of generated data for inspection"""

    print("\n" + "="*60)
    print("📄 SAMPLE DATA PREVIEW")
    print("="*60)

    stub_generator = MarketAnalysisStubData()

    # Generate sample data
    economic_data = stub_generator.generate_economic_data(delay_simulation=False)
    news_analysis = stub_generator.generate_news_analysis(["AAPL", "MSFT"], "market outlook", delay_simulation=False)

    print("\n📈 Sample Economic Data:")
    print(f"   Fed Rate: {economic_data['federal_funds_rate']['value']}% ({economic_data['federal_funds_rate']['trend']})")
    print(f"   Confidence: {economic_data['federal_funds_rate']['confidence']:.1%}")

    print("\n📰 Sample News Article:")
    if news_analysis['articles']:
        article = news_analysis['articles'][0]
        print(f"   Title: {article['title']}")
        print(f"   Source: {article['source']}")
        print(f"   Sentiment: {article['sentiment']}")
        print(f"   Relevance: {article['relevance_score']:.1%}")
        print(f"   Snippet: {article['snippet'][:100]}...")

if __name__ == "__main__":
    print("🔬 Market Analysis Stub Data Test Suite")
    print("=" * 60)

    # Run tests
    success = test_stub_data_generation()

    if success:
        show_sample_data()

        print("\n🎯 Next Steps:")
        print("   1. Start the frontend development server: `cd frontend && pnpm run dev`")
        print("   2. Navigate to the Market Analysis tab")
        print("   3. Test the stub API endpoint at /api/market-analysis-v2-stub")
        print("   4. Use the MarketAnalysisPanel components")

    else:
        print("\n❌ Tests failed. Please check the error messages above.")
        sys.exit(1)