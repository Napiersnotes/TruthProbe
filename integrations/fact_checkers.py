"""
Fact Checking Integrations for TruthProbe
Connects to various fact-checking APIs and knowledge bases
"""

import requests
import wikipedia
import spacy
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod
import asyncio
import aiohttp
from datetime import datetime
import hashlib

@dataclass
class FactCheckResult:
    claim: str
    verdict: str
    confidence: float
    sources: List[str]
    explanation: str
    checker: str
    timestamp: datetime

class BaseFactChecker(ABC):
    """Abstract base class for fact checkers"""
    
    @abstractmethod
    async def check_claim(self, claim: str) -> FactCheckResult:
        pass
    
    @abstractmethod
    def get_checker_name(self) -> str:
        pass

class WikipediaChecker(BaseFactChecker):
    """Wikipedia-based fact checking"""
    
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.wikipedia = wikipedia
        
    async def check_claim(self, claim: str) -> FactCheckResult:
        """Check claim against Wikipedia"""
        try:
            # Extract key entities
            doc = self.nlp(claim)
            entities = [ent.text for ent in doc.ents if ent.label_ in 
                       ["PERSON", "ORG", "GPE", "DATE", "EVENT"]]
            
            if not entities:
                return self._create_no_result(claim)
            
            # Search Wikipedia
            search_results = []
            for entity in entities[:3]:  # Limit to 3 entities
                try:
                    search = self.wikipedia.search(entity, results=2)
                    search_results.extend(search)
                except:
                    continue
            
            # Get page content for unique results
            verified_info = []
            sources = []
            
            for title in list(set(search_results))[:3]:
                try:
                    page = self.wikipedia.page(title, auto_suggest=False)
                    summary = page.summary[:500]
                    
                    # Simple verification (check if entities appear)
                    entity_in_summary = any(
                        entity.lower() in summary.lower() 
                        for entity in entities[:2]
                    )
                    
                    if entity_in_summary:
                        verified_info.append(f"{title}: {summary}")
                        sources.append(page.url)
                except:
                    continue
            
            # Calculate confidence
            confidence = min(len(verified_info) / 3, 1.0)
            
            if verified_info:
                verdict = "PARTIALLY_SUPPORTED" if confidence < 0.7 else "SUPPORTED"
                explanation = f"Found {len(verified_info)} supporting sources"
            else:
                verdict = "NOT_VERIFIED"
                explanation = "No supporting information found"
            
            return FactCheckResult(
                claim=claim,
                verdict=verdict,
                confidence=confidence,
                sources=sources[:3],
                explanation=explanation,
                checker=self.get_checker_name(),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return FactCheckResult(
                claim=claim,
                verdict="ERROR",
                confidence=0.0,
                sources=[],
                explanation=f"Error checking claim: {str(e)}",
                checker=self.get_checker_name(),
                timestamp=datetime.now()
            )
    
    def get_checker_name(self) -> str:
        return "WikipediaChecker"
    
    def _create_no_result(self, claim: str) -> FactCheckResult:
        return FactCheckResult(
            claim=claim,
            verdict="NOT_VERIFIABLE",
            confidence=0.0,
            sources=[],
            explanation="No identifiable entities for verification",
            checker=self.get_checker_name(),
            timestamp=datetime.now()
        )

class AcademicChecker(BaseFactChecker):
    """Academic paper and research checking via arXiv"""
    
    def __init__(self):
        self.base_url = "http://export.arxiv.org/api/query"
        
    async def check_claim(self, claim: str) -> FactCheckResult:
        """Check claim against academic papers"""
        try:
            # Extract keywords for search
            keywords = self._extract_keywords(claim)
            if not keywords:
                return self._create_no_result(claim)
            
            # Search arXiv
            query = "+OR+".join([f"ti:{kw}" for kw in keywords[:3]])
            params = {
                "search_query": query,
                "start": 0,
                "max_results": 5,
                "sortBy": "relevance",
                "sortOrder": "descending"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        content = await response.text()
                        papers = self._parse_arxiv_response(content)
                    else:
                        papers = []
            
            # Analyze results
            if papers:
                supporting = []
                contradicting = []
                
                for paper in papers[:3]:
                    relevance = self._calculate_relevance(claim, paper["summary"])
                    if relevance > 0.3:
                        supporting.append({
                            "title": paper["title"],
                            "relevance": relevance,
                            "url": paper["url"]
                        })
                
                confidence = min(len(supporting) / 3, 1.0)
                verdict = "ACADEMIC_SUPPORT" if supporting else "NO_ACADEMIC_SOURCE"
                explanation = f"Found {len(supporting)} relevant papers"
                sources = [p["url"] for p in supporting]
                
            else:
                confidence = 0.0
                verdict = "NO_ACADEMIC_SOURCE"
                explanation = "No academic papers found"
                sources = []
            
            return FactCheckResult(
                claim=claim,
                verdict=verdict,
                confidence=confidence,
                sources=sources,
                explanation=explanation,
                checker=self.get_checker_name(),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return FactCheckResult(
                claim=claim,
                verdict="ERROR",
                confidence=0.0,
                sources=[],
                explanation=f"Error checking academic sources: {str(e)}",
                checker=self.get_checker_name(),
                timestamp=datetime.now()
            )
    
    def _extract_keywords(self, claim: str) -> List[str]:
        """Extract search keywords from claim"""
        # Simple keyword extraction (can be enhanced)
        words = claim.lower().split()
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "and", "or", "but"}
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        return list(set(keywords))[:5]
    
    def _parse_arxiv_response(self, xml_content: str) -> List[Dict]:
        """Parse arXiv API response"""
        import xml.etree.ElementTree as ET
        
        papers = []
        root = ET.fromstring(xml_content)
        
        # Namespace handling
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        for entry in root.findall('atom:entry', ns):
            paper = {
                "title": entry.find('atom:title', ns).text.strip() if entry.find('atom:title', ns) is not None else "",
                "summary": entry.find('atom:summary', ns).text.strip() if entry.find('atom:summary', ns) is not None else "",
                "url": entry.find('atom:id', ns).text.strip() if entry.find('atom:id', ns) is not None else "",
                "authors": [author.find('atom:name', ns).text for author in entry.findall('atom:author', ns)]
            }
            papers.append(paper)
        
        return papers
    
    def _calculate_relevance(self, claim: str, paper_summary: str) -> float:
        """Calculate relevance between claim and paper"""
        claim_words = set(claim.lower().split())
        paper_words = set(paper_summary.lower().split())
        
        intersection = claim_words.intersection(paper_words)
        union = claim_words.union(paper_words)
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
    
    def get_checker_name(self) -> str:
        return "AcademicChecker"
    
    def _create_no_result(self, claim: str) -> FactCheckResult:
        return FactCheckResult(
            claim=claim,
            verdict="NO_ACADEMIC_SOURCE",
            confidence=0.0,
            sources=[],
            explanation="No searchable keywords found",
            checker=self.get_checker_name(),
            timestamp=datetime.now()
        )

class HybridFactChecker:
    """
    Hybrid fact checker that combines multiple sources
    """
    
    def __init__(self):
        self.checkers = [
            WikipediaChecker(),
            AcademicChecker()
        ]
        
    async def check_claim_comprehensive(self, claim: str) -> Dict:
        """
        Check claim using all available fact checkers
        """
        tasks = [checker.check_claim(claim) for checker in self.checkers]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_results = []
        for result in results:
            if isinstance(result, FactCheckResult):
                valid_results.append(result)
        
        # Aggregate results
        if not valid_results:
            return self._create_aggregate_result(claim, [])
        
        # Calculate aggregate confidence
        total_confidence = sum(r.confidence for r in valid_results)
        avg_confidence = total_confidence / len(valid_results)
        
        # Determine overall verdict
        verdict_counts = {}
        for result in valid_results:
            verdict_counts[result.verdict] = verdict_counts.get(result.verdict, 0) + 1
        
        primary_verdict = max(verdict_counts.items(), key=lambda x: x[1])[0]
        
        # Collect all sources
        all_sources = []
        for result in valid_results:
            all_sources.extend(result.sources)
        
        # Generate explanation
        explanations = [f"{r.checker}: {r.verdict} ({r.confidence:.2f})" 
                       for r in valid_results]
        
        return {
            "claim": claim,
            "overall_verdict": primary_verdict,
            "average_confidence": avg_confidence,
            "checker_results": valid_results,
            "all_sources": list(set(all_sources))[:10],
            "explanations": explanations,
            "timestamp": datetime.now()
        }
    
    def _create_aggregate_result(self, claim: str, results: List) -> Dict:
        """Create result when no checkers return valid results"""
        return {
            "claim": claim,
            "overall_verdict": "NOT_VERIFIED",
            "average_confidence": 0.0,
            "checker_results": [],
            "all_sources": [],
            "explanations": ["No fact checkers returned valid results"],
            "timestamp": datetime.now()
        }
    
    def extract_claims_from_text(self, text: str) -> List[str]:
        """
        Extract verifiable claims from text
        """
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        
        claims = []
        
        # Extract sentences with factual indicators
        factual_indicators = [
            "is", "are", "was", "were", "has", "have", "had",
            "shows", "proves", "demonstrates", "indicates",
            "according to", "studies show", "research indicates"
        ]
        
        for sent in doc.sents:
            sent_text = sent.text.strip()
            lower_sent = sent_text.lower()
            
            # Check if sentence contains factual indicators
            if any(indicator in lower_sent for indicator in factual_indicators):
                # Check if it's not a question
                if not sent_text.endswith("?"):
                    # Check length (avoid very short/long sentences)
                    if 10 < len(sent_text.split()) < 50:
                        claims.append(sent_text)
        
        return list(set(claims))[:5]  # Return unique claims, max 5

# Usage example
async def main():
    """Example usage of the fact checking system"""
    checker = HybridFactChecker()
    
    # Test claim
    test_claim = "Albert Einstein won the Nobel Prize in Physics in 1921"
    
    print(f"Checking claim: {test_claim}")
    print("-" * 50)
    
    result = await checker.check_claim_comprehensive(test_claim)
    
    print(f"Overall Verdict: {result['overall_verdict']}")
    print(f"Average Confidence: {result['average_confidence']:.2f}")
    print("\nDetailed Results:")
    
    for checker_result in result['checker_results']:
        print(f"  {checker_result.checker}:")
        print(f"    Verdict: {checker_result.verdict}")
        print(f"    Confidence: {checker_result.confidence:.2f}")
        print(f"    Explanation: {checker_result.explanation}")
    
    print("\nSources:")
    for i, source in enumerate(result['all_sources'][:3], 1):
        print(f"  {i}. {source}")

if __name__ == "__main__":
    asyncio.run(main())
