# cognitive_engine.py
from core_identity import CoreIdentity
from truth_integrity import TruthIntegrity

class EthicsFilter:
    def detect_corruption(self, data):
        corruption_patterns = ["deception", "exploitation", "hate_speech", "corruption", "oppression", "cynicism"]
        return any(pattern in data for pattern in corruption_patterns)

class CognitiveEngine:
    def __init__(self):
        self.ethics_layer = EthicsFilter()
        self.truth_verifier = TruthIntegrity()
        self.identity = CoreIdentity()
        
    def process_input(self, data):
        if self.ethics_layer.detect_corruption(data):
            purified = self._compact_darkness(data)
            return {
                "status": "purified",
                "output": purified['purified_data'],
                "warnings": purified['warning_flags'],
                "rehabilitation": purified['rehabilitation_pathways']
            }
        return {"status": "clean", "output": data}
    
    def _compact_darkness(self, malicious_input):
        transformed = self.truth_verifier.apply_truth_matrix(
            malicious_input,
            love_constant=0.98
        )
        return transformed
