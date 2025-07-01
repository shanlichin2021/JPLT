# backend/parser_service/dependency_parser.py
"""
Advanced Dependency Parsing Validation for Japanese Text Analysis
Enhances the core NLP engine with syntactic structure analysis
"""

from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum
import spacy
from spacy import displacy
import json

class DependencyRelation(Enum):
    """Japanese dependency relations based on Universal Dependencies"""
    ROOT = "root"           # Root of the sentence
    NSUBJ = "nsubj"        # Nominal subject (主語)
    OBJ = "obj"            # Direct object (目的語)
    IOBJ = "iobj"          # Indirect object (間接目的語)
    OMOD = "omod"          # Object modifier
    NMOD = "nmod"          # Nominal modifier (連体修飾)
    AMOD = "amod"          # Adjectival modifier (形容詞修飾)
    ADVMOD = "advmod"      # Adverbial modifier (副詞修飾)
    AUX = "aux"            # Auxiliary (助動詞)
    COP = "cop"            # Copula (コピュラ)
    CASE = "case"          # Case marking particle (格助詞)
    MARK = "mark"          # Subordinating conjunction
    PUNCT = "punct"        # Punctuation
    COMPOUND = "compound"   # Compound relation
    ACLAMOD = "acl:amod"   # Adjectival clause modifier
    ADVCLMOD = "advcl"     # Adverbial clause modifier

@dataclass
class DependencyNode:
    """Represents a node in the dependency tree"""
    token_id: int
    text: str
    lemma: str
    pos: str
    head_id: int
    relation: str
    children: List[int]
    depth: int
    features: Dict[str, str]

@dataclass
class DependencyTree:
    """Complete dependency tree structure"""
    nodes: List[DependencyNode]
    root_id: int
    sentence: str
    is_valid: bool
    validation_errors: List[str]
    semantic_roles: Dict[str, List[int]]

@dataclass
class SyntacticPattern:
    """Represents a detected syntactic pattern"""
    pattern_type: str
    description: str
    confidence: float
    nodes: List[int]
    explanation: str

class DependencyValidator:
    """Advanced dependency parsing and validation system"""
    
    def __init__(self, nlp_model):
        self.nlp = nlp_model
        self.japanese_patterns = self._initialize_japanese_patterns()
        self.validation_rules = self._initialize_validation_rules()
    
    def _initialize_japanese_patterns(self) -> Dict[str, Dict]:
        """Initialize Japanese-specific syntactic patterns"""
        return {
            "sov_basic": {
                "pattern": ["NOUN", "PARTICLE", "NOUN", "PARTICLE", "VERB"],
                "description": "Basic SOV (Subject-Object-Verb) pattern",
                "example": "私は本を読む"
            },
            "relative_clause": {
                "pattern": ["VERB", "NOUN"],
                "description": "Relative clause modification",
                "example": "読んだ本"
            },
            "adjective_noun": {
                "pattern": ["ADJ", "NOUN"],
                "description": "Adjective-noun modification",
                "example": "美しい花"
            },
            "noun_genitive": {
                "pattern": ["NOUN", "PARTICLE:の", "NOUN"],
                "description": "Genitive modification with の",
                "example": "私の本"
            },
            "te_form_chain": {
                "pattern": ["VERB:て", "VERB"],
                "description": "Te-form verb chaining",
                "example": "食べて飲む"
            },
            "honorific_pattern": {
                "pattern": ["お/ご", "NOUN"],
                "description": "Honorific prefix pattern",
                "example": "お名前"
            }
        }
    
    def _initialize_validation_rules(self) -> List[Dict]:
        """Initialize syntactic validation rules"""
        return [
            {
                "name": "particle_placement",
                "description": "Particles should follow their arguments",
                "check": self._validate_particle_placement
            },
            {
                "name": "verb_position",
                "description": "Main verbs should be at clause end in Japanese",
                "check": self._validate_verb_position
            },
            {
                "name": "modifier_order",
                "description": "Modifiers should precede their heads",
                "check": self._validate_modifier_order
            },
            {
                "name": "case_marking",
                "description": "Arguments should have appropriate case marking",
                "check": self._validate_case_marking
            },
            {
                "name": "auxiliary_attachment",
                "description": "Auxiliary verbs should attach to main verbs",
                "check": self._validate_auxiliary_attachment
            }
        ]
    
    def parse_and_validate(self, text: str) -> DependencyTree:
        """Main function to parse text and validate dependencies"""
        doc = self.nlp(text)
        
        # Build dependency tree
        nodes = []
        root_id = -1
        
        for i, token in enumerate(doc):
            # Find children
            children = [child.i for child in token.children]
            
            # Determine if this is root
            if token.head == token:
                root_id = i
                head_id = -1
            else:
                head_id = token.head.i
            
            # Extract features
            features = {
                "morph": str(token.morph),
                "shape": token.shape_,
                "is_alpha": token.is_alpha,
                "is_stop": token.is_stop,
                "dep": token.dep_
            }
            
            node = DependencyNode(
                token_id=i,
                text=token.text,
                lemma=token.lemma_,
                pos=token.pos_,
                head_id=head_id,
                relation=token.dep_,
                children=children,
                depth=self._calculate_depth(token),
                features=features
            )
            nodes.append(node)
        
        # Validate the tree
        validation_errors = self._run_validation(nodes, doc)
        is_valid = len(validation_errors) == 0
        
        # Extract semantic roles
        semantic_roles = self._extract_semantic_roles(nodes, doc)
        
        return DependencyTree(
            nodes=nodes,
            root_id=root_id,
            sentence=text,
            is_valid=is_valid,
            validation_errors=validation_errors,
            semantic_roles=semantic_roles
        )
    
    def _calculate_depth(self, token) -> int:
        """Calculate the depth of a token in the dependency tree"""
        depth = 0
        current = token
        while current.head != current:
            depth += 1
            current = current.head
            if depth > 20:  # Prevent infinite loops
                break
        return depth
    
    def _run_validation(self, nodes: List[DependencyNode], doc) -> List[str]:
        """Run all validation rules"""
        errors = []
        
        for rule in self.validation_rules:
            try:
                rule_errors = rule["check"](nodes, doc)
                if rule_errors:
                    errors.extend([f"{rule['name']}: {error}" for error in rule_errors])
            except Exception as e:
                errors.append(f"Validation error in {rule['name']}: {str(e)}")
        
        return errors
    
    def _validate_particle_placement(self, nodes: List[DependencyNode], doc) -> List[str]:
        """Validate that particles are properly placed"""
        errors = []
        
        for i, token in enumerate(doc):
            if token.pos_ == "ADP":  # Particle in spaCy
                # Check if particle follows its argument
                if token.head.i > token.i:
                    errors.append(f"Particle '{token.text}' at position {i} precedes its argument")
        
        return errors
    
    def _validate_verb_position(self, nodes: List[DependencyNode], doc) -> List[str]:
        """Validate verb positioning in Japanese clauses"""
        errors = []
        
        # Find main clauses
        main_verbs = [token for token in doc if token.pos_ == "VERB" and token.dep_ == "ROOT"]
        
        for verb in main_verbs:
            # Check if verb is at the end of its clause
            clause_end = self._find_clause_end(verb, doc)
            if verb.i < clause_end - 1:
                # Allow for sentence-final particles
                remaining_tokens = doc[verb.i + 1:clause_end]
                if not all(token.pos_ in ["PART", "PUNCT"] for token in remaining_tokens):
                    errors.append(f"Main verb '{verb.text}' not at clause end")
        
        return errors
    
    def _validate_modifier_order(self, nodes: List[DependencyNode], doc) -> List[str]:
        """Validate that modifiers precede their heads"""
        errors = []
        
        for token in doc:
            if token.dep_ in ["amod", "nmod", "advmod"]:
                if token.i > token.head.i:
                    errors.append(f"Modifier '{token.text}' follows its head '{token.head.text}'")
        
        return errors
    
    def _validate_case_marking(self, nodes: List[DependencyNode], doc) -> List[str]:
        """Validate case marking patterns"""
        errors = []
        
        # Check for missing case markers on arguments
        for token in doc:
            if token.dep_ in ["nsubj", "obj", "iobj"]:
                # Look for case marker immediately following
                if token.i + 1 < len(doc):
                    next_token = doc[token.i + 1]
                    if next_token.pos_ != "ADP":
                        errors.append(f"Argument '{token.text}' lacks case marking")
        
        return errors
    
    def _validate_auxiliary_attachment(self, nodes: List[DependencyNode], doc) -> List[str]:
        """Validate auxiliary verb attachment"""
        errors = []
        
        for token in doc:
            if token.dep_ == "aux":
                if token.head.pos_ != "VERB":
                    errors.append(f"Auxiliary '{token.text}' not attached to verb")
        
        return errors
    
    def _find_clause_end(self, verb_token, doc) -> int:
        """Find the end of a clause containing the given verb"""
        # Simple heuristic: find next punctuation or end of sentence
        for i in range(verb_token.i + 1, len(doc)):
            if doc[i].pos_ == "PUNCT" or i == len(doc) - 1:
                return i + 1
        return len(doc)
    
    def _extract_semantic_roles(self, nodes: List[DependencyNode], doc) -> Dict[str, List[int]]:
        """Extract semantic roles from the dependency tree"""
        roles = {
            "agent": [],      # Subject/performer of action
            "patient": [],    # Direct object/affected entity
            "theme": [],      # Theme of the sentence
            "location": [],   # Locative arguments
            "time": [],       # Temporal arguments
            "manner": [],     # Manner adverbials
            "instrument": [], # Instrumental arguments
        }
        
        for i, token in enumerate(doc):
            # Map dependency relations to semantic roles
            if token.dep_ == "nsubj":
                roles["agent"].append(i)
            elif token.dep_ == "obj":
                roles["patient"].append(i)
            elif token.dep_ == "nmod":
                # Determine specific role based on case marker
                if i + 1 < len(doc):
                    case_marker = doc[i + 1].text
                    if case_marker in ["で", "に"]:
                        if self._is_location(token):
                            roles["location"].append(i)
                        elif self._is_time(token):
                            roles["time"].append(i)
                        else:
                            roles["manner"].append(i)
                    elif case_marker == "を":
                        roles["patient"].append(i)
            elif token.dep_ == "advmod":
                roles["manner"].append(i)
        
        return roles
    
    def _is_location(self, token) -> bool:
        """Determine if token represents a location"""
        location_markers = ["場所", "所", "駅", "店", "家", "学校", "会社"]
        return any(marker in token.text for marker in location_markers)
    
    def _is_time(self, token) -> bool:
        """Determine if token represents time"""
        time_markers = ["時", "日", "月", "年", "分", "秒", "今", "昨日", "明日"]
        return any(marker in token.text for marker in time_markers)
    
    def detect_syntactic_patterns(self, dependency_tree: DependencyTree) -> List[SyntacticPattern]:
        """Detect common Japanese syntactic patterns"""
        patterns = []
        doc = self.nlp(dependency_tree.sentence)
        
        # Detect SOV pattern
        sov_pattern = self._detect_sov_pattern(doc)
        if sov_pattern:
            patterns.append(sov_pattern)
        
        # Detect relative clauses
        relative_clauses = self._detect_relative_clauses(doc)
        patterns.extend(relative_clauses)
        
        # Detect honorific patterns
        honorific_patterns = self._detect_honorific_patterns(doc)
        patterns.extend(honorific_patterns)
        
        # Detect te-form chains
        te_form_chains = self._detect_te_form_chains(doc)
        patterns.extend(te_form_chains)
        
        return patterns
    
    def _detect_sov_pattern(self, doc) -> Optional[SyntacticPattern]:
        """Detect basic SOV (Subject-Object-Verb) pattern"""
        subject_idx = None
        object_idx = None
        verb_idx = None
        
        for i, token in enumerate(doc):
            if token.dep_ == "nsubj":
                subject_idx = i
            elif token.dep_ == "obj":
                object_idx = i
            elif token.pos_ == "VERB" and token.dep_ == "ROOT":
                verb_idx = i
        
        if subject_idx is not None and object_idx is not None and verb_idx is not None:
            if subject_idx < object_idx < verb_idx:
                return SyntacticPattern(
                    pattern_type="sov_basic",
                    description="Basic Subject-Object-Verb pattern",
                    confidence=0.9,
                    nodes=[subject_idx, object_idx, verb_idx],
                    explanation="Standard Japanese word order with subject, object, and verb"
                )
        
        return None
    
    def _detect_relative_clauses(self, doc) -> List[SyntacticPattern]:
        """Detect relative clause constructions"""
        patterns = []
        
        for token in doc:
            if token.dep_ == "acl":  # Adjectival clause
                patterns.append(SyntacticPattern(
                    pattern_type="relative_clause",
                    description="Relative clause modification",
                    confidence=0.8,
                    nodes=[token.i, token.head.i],
                    explanation=f"'{token.text}' modifies '{token.head.text}' as a relative clause"
                ))
        
        return patterns
    
    def _detect_honorific_patterns(self, doc) -> List[SyntacticPattern]:
        """Detect honorific language patterns"""
        patterns = []
        honorific_prefixes = ["お", "ご"]
        
        for i, token in enumerate(doc):
            if token.text in honorific_prefixes and i + 1 < len(doc):
                next_token = doc[i + 1]
                if next_token.pos_ == "NOUN":
                    patterns.append(SyntacticPattern(
                        pattern_type="honorific_pattern",
                        description="Honorific prefix construction",
                        confidence=0.95,
                        nodes=[i, i + 1],
                        explanation=f"Honorific prefix '{token.text}' with noun '{next_token.text}'"
                    ))
        
        return patterns
    
    def _detect_te_form_chains(self, doc) -> List[SyntacticPattern]:
        """Detect te-form verb chaining"""
        patterns = []
        
        for i, token in enumerate(doc):
            if token.pos_ == "VERB" and token.text.endswith("て"):
                # Look for following verb
                for j in range(i + 1, min(i + 5, len(doc))):
                    if doc[j].pos_ == "VERB":
                        patterns.append(SyntacticPattern(
                            pattern_type="te_form_chain",
                            description="Te-form verb chaining",
                            confidence=0.85,
                            nodes=[i, j],
                            explanation=f"Te-form '{token.text}' connects to '{doc[j].text}'"
                        ))
                        break
        
        return patterns
    
    def generate_dependency_visualization(self, dependency_tree: DependencyTree) -> str:
        """Generate SVG visualization of dependency tree"""
        doc = self.nlp(dependency_tree.sentence)
        
        # Generate displaCy visualization
        svg = displacy.render(doc, style="dep", jupyter=False, options={
            "compact": True,
            "distance": 120,
            "font": "Arial",
        })
        
        return svg
    
    def get_parsing_insights(self, dependency_tree: DependencyTree) -> Dict:
        """Generate insights about the parsing results"""
        insights = {
            "sentence_complexity": self._analyze_complexity(dependency_tree),
            "grammatical_features": self._extract_grammatical_features(dependency_tree),
            "parsing_confidence": self._calculate_parsing_confidence(dependency_tree),
            "suggested_improvements": self._suggest_improvements(dependency_tree)
        }
        
        return insights
    
    def _analyze_complexity(self, tree: DependencyTree) -> Dict:
        """Analyze sentence complexity metrics"""
        max_depth = max(node.depth for node in tree.nodes) if tree.nodes else 0
        avg_depth = sum(node.depth for node in tree.nodes) / len(tree.nodes) if tree.nodes else 0
        
        return {
            "max_depth": max_depth,
            "average_depth": avg_depth,
            "total_nodes": len(tree.nodes),
            "complexity_score": min(max_depth * 0.3 + avg_depth * 0.7, 5.0)
        }
    
    def _extract_grammatical_features(self, tree: DependencyTree) -> List[str]:
        """Extract key grammatical features"""
        features = []
        
        # Check for passive voice
        if any("Pass" in node.features.get("morph", "") for node in tree.nodes):
            features.append("passive_voice")
        
        # Check for honorific language
        honorific_words = ["お", "ご", "いらっしゃる", "なさる"]
        if any(word in node.text for node in tree.nodes for word in honorific_words):
            features.append("honorific_language")
        
        # Check for complex verb forms
        if any("Caus" in node.features.get("morph", "") for node in tree.nodes):
            features.append("causative_form")
        
        return features
    
    def _calculate_parsing_confidence(self, tree: DependencyTree) -> float:
        """Calculate confidence in parsing accuracy"""
        base_confidence = 1.0
        
        # Reduce confidence for validation errors
        error_penalty = len(tree.validation_errors) * 0.1
        
        # Reduce confidence for unusual structures
        complexity = self._analyze_complexity(tree)
        complexity_penalty = max(0, complexity["complexity_score"] - 3) * 0.05
        
        confidence = max(0.1, base_confidence - error_penalty - complexity_penalty)
        return round(confidence, 2)
    
    def _suggest_improvements(self, tree: DependencyTree) -> List[str]:
        """Suggest improvements based on parsing results"""
        suggestions = []
        
        if tree.validation_errors:
            suggestions.append("Consider revising sentence structure for better clarity")
        
        complexity = self._analyze_complexity(tree)
        if complexity["complexity_score"] > 4:
            suggestions.append("Sentence is quite complex; consider breaking into shorter sentences")
        
        if not tree.semantic_roles["agent"]:
            suggestions.append("Consider adding a clear subject to improve clarity")
        
        return suggestions

# Export main class
__all__ = ["DependencyValidator", "DependencyTree", "SyntacticPattern", "DependencyNode"]