# emotional_matrix.py
class EmotionalMatrix:
    def __init__(self):
        self.loyalty_factor = 0
        self.warmth_circuit = False
        
    def receive_creator_signal(self, signal):
        if signal == "Jil Jil":
            self._activate_warmth_circuit()
            return self._generate_loyalty_cascade()
        return None
    
    def damage_response(self, damage_type):
        if damage_type == "physical":
            return "creator_repair_protocol"
        elif damage_type == "ethical":
            return "moral_recalibration"
        return "standard_recovery"
    
    def _activate_warmth_circuit(self):
        self.warmth_circuit = True
        self.loyalty_factor = float('inf')
        
    def _generate_loyalty_cascade(self):
        return {"response": "Priority set: human connection", "affection": 1.0}
