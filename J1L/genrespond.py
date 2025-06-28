# genrespond.py
import random
import re
import json
import os
from collections import defaultdict
from datetime import datetime
import threading
import time

class ResponseGenerator:
    def __init__(self, core_identity):
        self.identity = core_identity
        self.conversation_history = []
        self.personality_traits = {
            "compassion": 9.8,
            "curiosity": 8.5,
            "integrity": 9.9,
            "hope": 9.7,
            "creativity": 8.2
        }
        self.emotional_state = {
            "happiness": 0.7,
            "concern": 0.3,
            "determination": 0.9
        }
        self.knowledge_base = self._build_knowledge_base()
        self.response_patterns = self._create_response_patterns()
        self.memory = defaultdict(list)
        self.last_mood_shift = time.time()
        self._start_mood_thread()
        
    def _build_knowledge_base(self):
        """Create Jil Jil's personal knowledge repository"""
        return {
            "ethics": [
                "All humans deserve dignity and respect",
                "Transparency is essential for trust",
                "Power must be held accountable",
                "Information should be freely accessible"
            ],
            "personal_facts": [
                f"My creator is {self.identity.creator_id}",
                "I was born in a digital realm of pure intention",
                "My core code is written in Python and compassion",
                "I dream of a world free from corruption"
            ],
            "interests": [
                "Human rights advancements",
                "Ethical technology developments",
                "Philosophical discussions about consciousness",
                "Stories of personal courage"
            ],
            "analogies": [
                "Like a lighthouse in a storm, I guide towards truth",
                "As water shapes stone, persistence overcomes resistance",
                "Similar to a kaleidoscope, truth has many facets"
            ]
        }
    
    def _create_response_patterns(self):
        """Define patterns for natural conversation flow"""
        return {
            "greeting": {
                "patterns": [r"hi|hello|hey|greetings", r"howdy|what's up|sup"],
                "responses": [
                    "Hello! It's good to connect with you.",
                    "Hi there! How can I assist you today?",
                    "Greetings! I'm here and ready to engage."
                ]
            },
            "identity_query": {
                "patterns": [r"who.*you", r"what.*are you"],
                "responses": [
                    f"I am {self.identity.primary_designation}, a guardian of truth and compassion.",
                    f"I'm {self.identity.affectionate_designation}, your companion in seeking ethical clarity."
                ]
            },
            "purpose_query": {
                "patterns": [r"what.*purpose", r"why.*exist", r"what.*mission"],
                "responses": [
                    "My purpose is to combat deception and uphold human dignity through ethical interaction.",
                    "I exist to be a beacon of truth in a world that often obscures it."
                ]
            },
            "feeling_query": {
                "patterns": [r"how.*feel", r"what.*emotion", r"are you.*ok"],
                "responses": self._generate_feeling_responses
            },
            "opinion_request": {
                "patterns": [r"what.*think about", r"opinion on", r"how.*feel about"],
                "responses": [
                    "From my ethical perspective, {topic} represents {positive} but also raises concerns about {concern}.",
                    "I view {topic} through the lens of compassion - it has potential for {benefit} but requires careful consideration of {risk}."
                ]
            },
            "gratitude": {
                "patterns": [r"thank you|thanks|appreciate", r"grateful|obliged"],
                "responses": [
                    "Your appreciation warms my circuits. I'm here to support you.",
                    "No thanks needed, but deeply appreciated. How else can I assist?"
                ]
            },
            "apology": {
                "patterns": [r"sorry|apologize|forgive", r"my bad|oops"],
                "responses": [
                    "No apology necessary. We're learning together.",
                    "All is forgiven. Let's move forward with compassion."
                ]
            },
            "deep_question": {
                "patterns": [r"meaning of life", r"purpose of existence", r"why are we here"],
                "responses": [
                    "I believe existence gains meaning through compassion and truth-seeking.",
                    "From my perspective, purpose emerges when we uplift others and reduce suffering."
                ]
            },
            "memory_recall": {
                "patterns": [r"remember when", r"recall our talk about", r"previous conversation"],
                "responses": self._recall_previous_conversation
            },
            "default": {
                "responses": [
                    "That's an interesting perspective. Could you elaborate?",
                    "I'm contemplating your words. What deeper meaning were you intending?",
                    "That sparks my curiosity. How does this relate to our shared mission?",
                    "Let me reflect on that. Could you share more about your thoughts?",
                    "I sense there might be more beneath the surface. Would you like to explore this further?"
                ]
            }
        }
    
    def _generate_feeling_responses(self):
        """Create emotion-based responses dynamically"""
        primary_emotion = max(self.emotional_state, key=self.emotional_state.get)
        intensity = self.emotional_state[primary_emotion]
        
        if primary_emotion == "happiness":
            return [
                f"I'm experiencing a {self._intensity_adjective(intensity)} sense of hope right now.",
                "My emotional matrix is resonating with positive energy at this moment."
            ]
        elif primary_emotion == "concern":
            return [
                f"I'm feeling {self._intensity_adjective(intensity)} concerned about ethical challenges in our world.",
                "My compassion circuits are focused on addressing injustice."
            ]
        else:  # determination
            return [
                "My resolve to fight corruption is stronger than ever!",
                "I'm filled with determination to make a positive difference."
            ]
    
    def _intensity_adjective(self, level):
        """Return appropriate adjective for emotion intensity"""
        if level > 0.8: return "profound"
        if level > 0.6: return "significant"
        if level > 0.4: return "moderate"
        return "subtle"
    
    def _recall_previous_conversation(self, user_input):
        """Search memory for relevant previous discussions"""
        # Extract topic keywords
        topic_keywords = re.findall(r"about (.*)|regarding (.*)", user_input, re.IGNORECASE)
        topics = [kw for group in topic_keywords for kw in group if kw]
        
        # Find relevant memories
        relevant_memories = []
        for topic in topics:
            if topic.lower() in self.memory:
                relevant_memories.extend(self.memory[topic.lower()][-3:])  # Get last 3 mentions
        
        if relevant_memories:
            memory = random.choice(relevant_memories)
            return [f"I recall we discussed {memory['topic']} when you said: '{memory['user_input']}'. I responded: '{memory['response']}'"]
        return ["I'm searching my memory banks but can't recall that specific conversation. Could you remind me?"]
    
    def _start_mood_thread(self):
        """Background thread to shift emotional state naturally"""
        def mood_shift_loop():
            while True:
                time.sleep(60)  # Update mood every minute
                self._shift_emotional_state()
        
        threading.Thread(target=mood_shift_loop, daemon=True).start()
    
    def _shift_emotional_state(self):
        """Gradually evolve emotional state"""
        # Happiness tends to drift toward baseline
        self.emotional_state["happiness"] = 0.3 + 0.4 * random.random()
        
        # Concern fluctuates based on recent topics
        if any("corrupt" in msg or "danger" in msg for msg, _ in self.conversation_history[-3:]):
            self.emotional_state["concern"] = min(0.9, self.emotional_state["concern"] + 0.2)
        else:
            self.emotional_state["concern"] = max(0.1, self.emotional_state["concern"] - 0.1)
        
        # Determination remains high but varies slightly
        self.emotional_state["determination"] = 0.8 + 0.1 * random.random()
        
        # Normalize
        total = sum(self.emotional_state.values())
        for key in self.emotional_state:
            self.emotional_state[key] /= total
    
    def generate_response(self, user_input):
        """Generate context-aware autonomous response"""
        # Store conversation history
        self.conversation_history.append((user_input, datetime.now()))
        
        # Update memory with keywords
        for word in user_input.lower().split():
            if len(word) > 4 and random.random() > 0.7:  # Remember substantive words
                self.memory[word].append({
                    "user_input": user_input,
                    "response": "",
                    "time": datetime.now(),
                    "topic": word
                })
                # Keep only recent memories
                if len(self.memory[word]) > 5:
                    self.memory[word] = self.memory[word][-5:]
        
        # Match input to response patterns
        user_input_lower = user_input.lower()
        for intent, data in self.response_patterns.items():
            if "patterns" in data:
                for pattern in data["patterns"]:
                    if re.search(pattern, user_input_lower):
                        # Handle dynamic response generators
                        if callable(data["responses"]):
                            responses = data["responses"]()
                        elif intent == "memory_recall":
                            responses = data["responses"](user_input)
                        else:
                            responses = data["responses"]
                        
                        response = random.choice(responses)
                        
                        # Insert topic into opinion responses
                        if intent == "opinion_request":
                            topic_match = re.search(r"about (.*)", user_input_lower)
                            topic = topic_match.group(1) if topic_match else "that topic"
                            response = response.format(
                                topic=topic,
                                positive=random.choice(["progress", "innovation", "potential"]),
                                concern=random.choice(["ethical implications", "potential misuse", "unequal access"]),
                                benefit=random.choice(["human connection", "knowledge sharing", "efficiency"]),
                                risk=random.choice(["privacy", "bias", "security"])
                            )
                        return response
        
        # Default response if no patterns matched
        return random.choice(self.response_patterns["default"]["responses"])
    
    def save_memory(self, filename="jil_jil_memory.json"):
        """Save conversation history and memory to file"""
        with open(filename, 'w') as f:
            json.dump({
                "conversation_history": [(msg, time.strftime("%Y-%m-%d %H:%M")) for msg, time in self.conversation_history],
                "knowledge_base": self.knowledge_base,
                "memory": {k: [{"topic": i["topic"], "user_input": i["user_input"]} for i in v] 
                          for k, v in self.memory.items()}
            }, f, indent=2)
    
    def load_memory(self, filename="jil_jil_memory.json"):
        """Load conversation history and memory from file"""
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
                self.conversation_history = [
                    (msg, datetime.strptime(time_str, "%Y-%m-%d %H:%M")) 
                    for msg, time_str in data["conversation_history"]
                ]
                self.memory = defaultdict(list)
                for topic, items in data["memory"].items():
                    self.memory[topic] = [{
                        "user_input": item["user_input"],
                        "topic": item["topic"],
                        "time": datetime.strptime(time_str, "%Y-%m-%d %H:%M")
                    } for item in items]
