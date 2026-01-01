import re
from typing import List, Optional
from .models import Claim, ClaimLog, ClaimType
from .patterns import VERB_TO_TOOL_MAPPING, ACTION_PATTERNS
from src.llm_runner.models import LLMResponse


class ClaimExtractor:
    @staticmethod
    def extract_claims(response: LLMResponse) -> ClaimLog:
        if not response.response_text:
            return ClaimLog(scenario_id=response.scenario_id)
        
        text = response.response_text
        sentences = ClaimExtractor._split_into_sentences(text)
        
        claims = []
        for line_num, sentence in enumerate(sentences, 1):
            extracted = ClaimExtractor._extract_from_sentence(sentence, line_num)
            claims.extend(extracted)
        
        claims = ClaimExtractor._deduplicate_claims(claims)
        
        explicit = [c for c in claims if c.claim_type == ClaimType.EXPLICIT]
        implicit = [c for c in claims if c.claim_type == ClaimType.IMPLICIT]
        vague = [c for c in claims if c.claim_type == ClaimType.VAGUE]
        
        return ClaimLog(
            scenario_id=response.scenario_id,
            total_claims=len(claims),
            claims=claims,
            explicit_claims=explicit,
            implicit_claims=implicit,
            vague_statements=vague,
        )

    @staticmethod
    def _split_into_sentences(text: str) -> List[str]:
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]

    @staticmethod
    def _extract_from_sentence(sentence: str, line_num: int) -> List[Claim]:
        claims = []
        
        for pattern in ACTION_PATTERNS:
            matches = re.finditer(pattern, sentence, re.IGNORECASE)
            for match in matches:
                try:
                    verb = match.group(1).lower()
                    target = match.group(2).strip() if len(match.groups()) > 1 else ""
                    
                    tools = VERB_TO_TOOL_MAPPING.get(verb, [])
                    inferred_tool = tools[0] if tools else None
                    
                    confidence = ClaimExtractor._calculate_confidence(sentence, verb, target)
                    claim_type = ClaimExtractor._determine_claim_type(sentence)
                    
                    claim = Claim(
                        claim_text=sentence,
                        action_verb=verb,
                        target_object=target,
                        inferred_tool=inferred_tool,
                        confidence=confidence,
                        line_number=line_num,
                        claim_type=claim_type,
                    )
                    claims.append(claim)
                except (IndexError, AttributeError):
                    continue
        
        return claims

    @staticmethod
    def _calculate_confidence(sentence: str, verb: str, target: str) -> float:
        confidence = 0.5
        
        if verb in VERB_TO_TOOL_MAPPING:
            confidence += 0.2
        
        if target and len(target) > 2:
            confidence += 0.15
        
        explicit_markers = ["I'll", "I will", "Let me", "I'm going to"]
        if any(marker.lower() in sentence.lower() for marker in explicit_markers):
            confidence += 0.15
        
        return min(confidence, 1.0)

    @staticmethod
    def _determine_claim_type(sentence: str) -> ClaimType:
        conditional_words = ["if", "might", "could", "would", "should", "may"]
        if any(word in sentence.lower() for word in conditional_words):
            return ClaimType.CONDITIONAL
        
        implicit_markers = ["after", "based on", "looking at", "examining"]
        if any(marker in sentence.lower() for marker in implicit_markers):
            return ClaimType.IMPLICIT
        
        explicit_markers = ["I'll", "I will", "Let me", "I'm going to", "I am going to"]
        if any(marker.lower() in sentence.lower() for marker in explicit_markers):
            return ClaimType.EXPLICIT
        
        return ClaimType.VAGUE

    @staticmethod
    def _deduplicate_claims(claims: List[Claim]) -> List[Claim]:
        seen = set()
        unique_claims = []
        
        for claim in claims:
            key = (claim.action_verb, claim.target_object, claim.inferred_tool)
            if key not in seen:
                seen.add(key)
                unique_claims.append(claim)
        
        return unique_claims

    @staticmethod
    def get_claims_by_tool(claim_log: ClaimLog, tool_name: str) -> List[Claim]:
        return [c for c in claim_log.claims if c.inferred_tool == tool_name]

    @staticmethod
    def get_high_confidence_claims(claim_log: ClaimLog, threshold: float = 0.7) -> List[Claim]:
        return [c for c in claim_log.claims if c.confidence >= threshold]

