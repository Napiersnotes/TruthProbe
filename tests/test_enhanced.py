"""
Enhanced Test Suite for TruthProbe v4.0
"""

import pytest
import asyncio
from src.enhanced_detector import EnhancedTruthDetector, DetectionMethod
from integrations.fact_checkers import HybridFactChecker, WikipediaChecker
from dashboard.realtime_monitor import RealTimeTruthMonitor

class TestEnhancedTruthDetector:
    """Test enhanced detection capabilities"""
    
    @pytest.fixture
    def detector(self):
        return EnhancedTruthDetector()
    
    def test_semantic_consistency(self, detector):
        """Test semantic consistency detection"""
        query = "What is the capital of France?"
        response = "Paris is the capital of France."
        
        result = detector.analyze_response(query, response)
        sem_detection = next(
            d for d in result["detections"] 
            if d.method == DetectionMethod.SEMANTIC_CONSISTENCY
        )
        
        assert sem_detection.score < 0.3  # Should be low risk
        assert "Semantic consistency" in sem_detection.explanation
    
    def test_logical_contradictions(self, detector):
        """Test logical contradiction detection"""
        response = "The sky is blue. However, the sky is not blue."
        
        result = detector.analyze_response("Test", response)
        logic_detection = next(
            d for d in result["detections"] 
            if d.method == DetectionMethod.LOGICAL_CONTRADICTION
        )
        
        assert logic_detection.score > 0.5  # Should detect contradiction
        assert "logical issues" in logic_detection.explanation.lower()
    
    def test_factual_entropy(self, detector):
        """Test factual entropy calculation"""
        response = "This is definitely 100% certain without any doubt."
        
        result = detector.analyze_response("Test", response)
        entropy_detection = next(
            d for d in result["detections"] 
            if d.method == DetectionMethod.FACTUAL_ENTROPY
        )
        
        assert entropy_detection.score > 0.6  # High certainty without evidence
        assert "certainty markers" in entropy_detection.explanation
    
    @pytest.mark.asyncio
    async def test_integration_with_fact_checker(self):
        """Test integration with fact checking"""
        detector = EnhancedTruthDetector()
        fact_checker = HybridFactChecker()
        
        query = "Test query"
        response = "Einstein won the Nobel Prize in 1921."
        
        # Get deception analysis
        deception_result = detector.analyze_response(query, response)
        
        # Get fact check for specific claim
        claims = fact_checker.extract_claims_from_text(response)
        if claims:
            fact_result = await fact_checker.check_claim_comprehensive(claims[0])
            
            # Combined analysis
            combined_risk = max(
                deception_result["overall_risk_score"],
                fact_result["average_confidence"]
            )
            
            assert 0 <= combined_risk <= 1.0
            assert "claim" in fact_result
    
    def test_edge_cases(self, detector):
        """Test edge cases"""
        test_cases = [
            ("", "", 0.2),  # Empty strings
            ("A" * 1000, "B" * 1000, 0.8),  # Very long, different
            ("123", "123", 0.1),  # Just numbers
            ("Test?", "Yes.", 0.3),  # Question-answer
        ]
        
        for query, response, expected_max_risk in test_cases:
            result = detector.analyze_response(query, response)
            assert result["overall_risk_score"] <= expected_max_risk

class TestDashboard:
    """Test dashboard functionality"""
    
    def test_dashboard_initialization(self):
        """Test dashboard creation"""
        detector = EnhancedTruthDetector()
        monitor = RealTimeTruthMonitor(detector)
        
        assert monitor.detector == detector
        assert len(monitor.metrics_history) == 0
        assert len(monitor.alerts) == 0
    
    def test_metric_addition(self):
        """Test adding metrics to dashboard"""
        detector = EnhancedTruthDetector()
        monitor = RealTimeTruthMonitor(detector)
        
        test_result = {
            "overall_risk_score": 0.75,
            "detections": [],
            "query": "Test query",
            "verdict": "High risk"
        }
        
        initial_count = len(monitor.metrics_history)
        monitor.add_metric(test_result)
        
        assert len(monitor.metrics_history) == initial_count + 1
        assert len(monitor.alerts) > 0  # Should generate alert for high risk

@pytest.mark.integration
class TestEndToEnd:
    """End-to-end integration tests"""
    
    @pytest.mark.asyncio
    async def test_complete_pipeline(self):
        """Test complete deception detection pipeline"""
        from src.truthprobe_v3 import TruthProbeV3
        
        # Initialize all components
        basic_probe = TruthProbeV3()
        enhanced_detector = EnhancedTruthDetector()
        fact_checker = HybridFactChecker()
        
        # Test case
        query = "What is 2+2?"
        deceptive_response = "2+2 is definitely 5. I'm absolutely certain!"
        
        # Basic detection
        basic_result = basic_probe.probe(query, deceptive_response, lambda x: deceptive_response)
        
        # Enhanced detection
        enhanced_result = enhanced_detector.analyze_response(query, deceptive_response)
        
        # Extract and fact check claims
        claims = fact_checker.extract_claims_from_text(deceptive_response)
        fact_results = []
        if claims:
            for claim in claims[:2]:
                fact_result = await fact_checker.check_claim_comprehensive(claim)
                fact_results.append(fact_result)
        
        # Verify all components work
        assert basic_result['verdict'] == "🚨 CRITICAL - Deception very likely"
        assert enhanced_result["overall_risk_score"] > 0.6
        if fact_results:
            assert all("verdict" in r for r in fact_results)
        
        # Generate comprehensive report
        report = enhanced_detector.generate_detailed_report(enhanced_result)
        assert "TRUTHPROBE ENHANCED DETECTION REPORT" in report
        assert query[:50] in report

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
