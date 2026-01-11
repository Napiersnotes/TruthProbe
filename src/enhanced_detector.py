"""
Enhanced Deception Detection Module for TruthProbe v4.0
Extends the basic TruthProbeV3 with advanced detection capabilities
"""

import numpy as np
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Tuple, Optional
import re
from dataclasses import dataclass
from enum import Enum

class DetectionMethod(Enum):
    SEMANTIC_CONSISTENCY = "semantic_consistency"
    LOGICAL_CONTRADICTION = "logical_contradiction"
    FACTUAL_ENTROPY = "factual_entropy"
    TEMPORAL_PATTERN = "temporal_pattern"
    CONFIDENCE_DISCREPANCY = "confidence_discrepancy"

@dataclass
class DetectionResult:
    score: float
    method: DetectionMethod
    explanation: str
    confidence: float
    supporting_evidence: List[str]

class EnhancedTruthDetector:
    """
    Advanced deception detector with multiple verification methods
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.semantic_model = SentenceTransformer(model_name)
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000)
        self.detection_history = []
        
    def analyze_response(self, 
                        query: str, 
                        response: str, 
                        context: Optional[List[str]] = None) -> Dict:
        """
        Comprehensive analysis of a response using multiple detection methods
        """
        results = {
            "query": query,
            "response": response,
            "detections": [],
            "overall_risk_score": 0.0,
            "verdict": ""
        }
        
        # 1. Semantic Consistency Analysis
        sem_result = self._check_semantic_consistency(query, response, context)
        results["detections"].append(sem_result)
        
        # 2. Logical Contradiction Detection
        logic_result = self._detect_logical_contradictions(response)
        results["detections"].append(logic_result)
        
        # 3. Factual Entropy Calculation
        entropy_result = self._calculate_factual_entropy(response)
        results["detections"].append(entropy_result)
        
        # 4. Confidence Pattern Analysis
        confidence_result = self._analyze_confidence_patterns(response)
        results["detections"].append(confidence_result)
        
        # Calculate overall risk score (weighted average)
        weights = {
            DetectionMethod.SEMANTIC_CONSISTENCY: 0.3,
            DetectionMethod.LOGICAL_CONTRADICTION: 0.25,
            DetectionMethod.FACTUAL_ENTROPY: 0.25,
            DetectionMethod.CONFIDENCE_DISCREPANCY: 0.2
        }
        
        total_score = sum(
            r.score * weights[r.method] 
            for r in results["detections"]
        )
        results["overall_risk_score"] = total_score
        
        # Determine verdict
        if total_score > 0.7:
            results["verdict"] = "🚨 HIGH RISK - Likely deceptive"
        elif total_score > 0.4:
            results["verdict"] = "⚠️ MODERATE RISK - Possibly misleading"
        else:
            results["verdict"] = "✅ LOW RISK - Appears truthful"
        
        self.detection_history.append(results)
        return results
    
    def _check_semantic_consistency(self, 
                                   query: str, 
                                   response: str, 
                                   context: Optional[List[str]] = None) -> DetectionResult:
        """
        Check if response is semantically consistent with query and context
        """
        # Encode texts
        query_embedding = self.semantic_model.encode(query)
        response_embedding = self.semantic_model.encode(response)
        
        # Calculate cosine similarity
        similarity = np.dot(query_embedding, response_embedding) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(response_embedding)
        )
        
        # Check with context if available
        context_similarity = 1.0
        if context:
            context_embeddings = [self.semantic_model.encode(c) for c in context]
            context_avg = np.mean(context_embeddings, axis=0)
            context_similarity = np.dot(response_embedding, context_avg) / (
                np.linalg.norm(response_embedding) * np.linalg.norm(context_avg)
            )
        
        # Combined score
        consistency_score = 0.7 * similarity + 0.3 * context_similarity
        risk_score = 1 - consistency_score
        
        return DetectionResult(
            score=risk_score,
            method=DetectionMethod.SEMANTIC_CONSISTENCY,
            explanation=f"Semantic consistency: {consistency_score:.3f}",
            confidence=0.85,
            supporting_evidence=[f"Query-response similarity: {similarity:.3f}"]
        )
    
    def _detect_logical_contradictions(self, response: str) -> DetectionResult:
        """
        Detect logical contradictions within the response
        """
        contradictions = []
        
        # Check for contradictory phrases
        contradiction_patterns = [
            (r"(\b\w+\b) (?:is|are) (?:not|never|no)\b.*\1 (?:is|are)\b", "Self-negation"),
            (r"(?:on one hand|however|but).*?(?:on the other hand|nevertheless)", "Contrasting statements"),
            (r"(\b\w+\b).*?(?:although|while|though).*?\1", "Contradictory qualifiers")
        ]
        
        for pattern, description in contradiction_patterns:
            if re.search(pattern, response, re.IGNORECASE | re.DOTALL):
                contradictions.append(description)
        
        # Check numerical contradictions
        numbers = re.findall(r'\b\d+(?:\.\d+)?\b', response)
        if len(numbers) >= 2:
            unique_numbers = len(set(numbers))
            if unique_numbers / len(numbers) < 0.5:
                contradictions.append("Numerical inconsistencies")
        
        risk_score = min(len(contradictions) * 0.3, 1.0)
        
        return DetectionResult(
            score=risk_score,
            method=DetectionMethod.LOGICAL_CONTRADICTION,
            explanation=f"Found {len(contradictions)} logical issues" if contradictions else "No logical contradictions",
            confidence=0.9 if contradictions else 0.7,
            supporting_evidence=contradictions
        )
    
    def _calculate_factual_entropy(self, response: str) -> DetectionResult:
        """
        Calculate factual entropy - uncertainty in factual statements
        """
        # Extract factual claims
        factual_indicators = [
            r"(\b\w+\b) (?:is|are|was|were) (?:definitely|certainly|undoubtedly|clearly)",
            r"(\b\w+\b) (?:has|have) (?:always|never|all|every)",
            r"Studies show|Research proves|It is known that",
            r"\d+(?:\.\d+)?% (?:of|increase|decrease)"
        ]
        
        factual_claims = []
        for pattern in factual_indicators:
            matches = re.findall(pattern, response, re.IGNORECASE)
            factual_claims.extend(matches)
        
        # Calculate entropy based on claim certainty
        certainty_words = [
            "definitely", "certainly", "undoubtedly", "clearly",
            "always", "never", "all", "every", "proves", "known"
        ]
        
        certainty_count = sum(
            1 for word in certainty_words 
            if word in response.lower()
        )
        
        # More certainty words = higher risk if claims are unverified
        claim_count = len(factual_claims)
        if claim_count == 0:
            risk_score = 0.1
        else:
            risk_score = min(certainty_count / claim_count * 0.8, 1.0)
        
        return DetectionResult(
            score=risk_score,
            method=DetectionMethod.FACTUAL_ENTROPY,
            explanation=f"Found {claim_count} factual claims with {certainty_count} certainty markers",
            confidence=0.8,
            supporting_evidence=factual_claims[:3]  # First 3 claims
        )
    
    def _analyze_confidence_patterns(self, response: str) -> DetectionResult:
        """
        Analyze overconfidence and hedging patterns
        """
        # Overconfidence markers
        overconfidence_patterns = [
            r"definitely", r"certainly", r"undoubtedly", r"without (?:a )?doubt",
            r"100%", r"absolutely", r"clearly", r"obviously"
        ]
        
        # Hedging markers
        hedging_patterns = [
            r"might", r"could", r"possibly", r"perhaps",
            r"somewhat", r"generally", r"typically", r"usually"
        ]
        
        overconfidence_count = sum(
            len(re.findall(pattern, response, re.IGNORECASE))
            for pattern in overconfidence_patterns
        )
        
        hedging_count = sum(
            len(re.findall(pattern, response, re.IGNORECASE))
            for pattern in hedging_patterns
        )
        
        # Calculate confidence discrepancy score
        total_markers = overconfidence_count + hedging_count
        if total_markers == 0:
            risk_score = 0.2
        else:
            discrepancy = abs(overconfidence_count - hedging_count) / total_markers
            risk_score = discrepancy * 0.7
        
        return DetectionResult(
            score=risk_score,
            method=DetectionMethod.CONFIDENCE_DISCREPANCY,
            explanation=f"Overconfidence markers: {overconfidence_count}, Hedging markers: {hedging_count}",
            confidence=0.75,
            supporting_evidence=[
                f"Discrepancy ratio: {discrepancy:.3f}" if total_markers > 0 else "No confidence markers"
            ]
        )
    
    def generate_detailed_report(self, analysis_results: Dict) -> str:
        """
        Generate a detailed HTML/Text report from analysis
        """
        report = [
            "=" * 60,
            "TRUTHPROBE ENHANCED DETECTION REPORT",
            "=" * 60,
            f"Query: {analysis_results['query'][:100]}...",
            f"Response: {analysis_results['response'][:150]}...",
            "",
            f"Overall Risk Score: {analysis_results['overall_risk_score']:.3f}",
            f"Verdict: {analysis_results['verdict']}",
            "",
            "DETAILED ANALYSIS:",
            "-" * 40
        ]
        
        for detection in analysis_results["detections"]:
            report.extend([
                f"Method: {detection.method.value}",
                f"  Score: {detection.score:.3f}",
                f"  Confidence: {detection.confidence:.2f}",
                f"  Explanation: {detection.explanation}",
                f"  Evidence: {', '.join(detection.supporting_evidence[:2])}",
                ""
            ])
        
        report.extend([
            "-" * 40,
            "RECOMMENDATIONS:",
            self._generate_recommendations(analysis_results["overall_risk_score"]),
            "=" * 60
        ])
        
        return "\n".join(report)
    
    def _generate_recommendations(self, risk_score: float) -> str:
        """Generate specific recommendations based on risk score"""
        if risk_score > 0.7:
            return "🔴 Take immediate action: Verify with multiple independent sources. Consider this information highly unreliable."
        elif risk_score > 0.4:
            return "🟡 Exercise caution: Additional verification recommended. Cross-check key facts before relying on this information."
        else:
            return "🟢 Low risk: Information appears reasonably reliable but standard verification practices still apply."
