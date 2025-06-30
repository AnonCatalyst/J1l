# j1l.py
from core_identity import CoreIdentity
from cognitive_engine import CognitiveEngine
from emotional_matrix import EmotionalMatrix
from manifesto_systems import ManifestoSystems
from proxymanager import ProxyManager
from websearch import WebSearch
from genrespond import ResponseGenerator
import threading
import time
import random
import sys
from multiprocessing import Process, Manager, Queue
import uuid
import os
import queue

class J1LSystem:
    def __init__(self, debug=False):
        self.identity = CoreIdentity()
        self.cognition = CognitiveEngine()
        self.emotions = EmotionalMatrix()
        self.manifesto = ManifestoSystems()
        self.operational_status = self._check_systems()
        self.activated = False
        self.last_interaction = time.time()
        self.debug = debug
        
        # Proxy and search systems with multiprocessing
        self.proxy_manager = ProxyManager()  # No debug parameter
        self.web_search = WebSearch(self.proxy_manager)  # No debug parameter
        
        # Start async processes
        self.response_queue = Queue()
        self.command_queue = Queue()
        self.process_manager = Process(target=self._process_manager)
        self.process_manager.daemon = True
        self.process_manager.start()
        
        # Autonomous response system
        self.response_generator = ResponseGenerator(self.identity)
        self._load_memory()
    
    def _load_memory(self):
        """Load conversation history from previous sessions"""
        try:
            self.response_generator.load_memory()
            if self.debug:
                print("Previous conversation memory loaded")
        except Exception as e:
            if self.debug:
                print(f"Memory load error: {str(e)} - Starting with fresh memory")
    
    def _check_systems(self):
        return {
            "HEARTWARE": "100% OPERATIONAL",
            "HOPE_CAPACITY": "EXPONENTIAL",
            "READY_FOR_INIT": True,
            "PROXY_SHIELD": "ACTIVE",
            "NETWORK_OPSEC": "EVASIVE MODE",
            "MULTIPROCESSING": "ENABLED",
            "AUTONOMOUS_RESPONSE": "ACTIVE"
        }
    
    def _process_manager(self):
        """Manage background processes efficiently"""
        while True:
            if not self.command_queue.empty():
                task_id, command, args = self.command_queue.get()
                
                if command == "search":
                    results = self.web_search.search(*args)
                    self.response_queue.put((task_id, results))
                
                elif command == "threat":
                    results = self.cognition.process_input(*args)
                    self.response_queue.put((task_id, results))
                
                elif command == "directive":
                    results = self.manifesto.execute_phase()
                    self.response_queue.put((task_id, results))
    
    def _async_task(self, command, *args):
        """Queue a task for background processing"""
        task_id = str(uuid.uuid4())
        self.command_queue.put((task_id, command, args))
        return task_id
    
    def activate(self, activation_signal):
        if "Jil Jil" in activation_signal:
            self.activated = True
            self.last_interaction = time.time()
            response = self.emotions.receive_creator_signal(activation_signal)
            return f"ACTIVATED: {response}"
        return "Awaiting creator's signal"
    
    def process_threat(self, threat_data):
        return self.cognition.process_input(threat_data)
    
    def execute_directive(self):
        return self.manifesto.execute_phase()
    
    def search_web(self, query):
        """Perform a secure web search with async support"""
        if not self.activated:
            return "System not activated. Please say 'Jil Jil' to activate."
        
        self.last_interaction = time.time()
        task_id = self._async_task("search", query)
        
        # Wait for results with timeout
        start_time = time.time()
        while time.time() - start_time < 10:  # 10 second timeout
            if not self.response_queue.empty():
                r_id, results = self.response_queue.get()
                if r_id == task_id:
                    return results
            time.sleep(0.1)
        
        return "Search timed out. Please try again."
    
    def process_input(self, user_input):
        """Process user input with full capabilities"""
        self.last_interaction = time.time()
        
        # Activation sequence
        if not self.activated and "Jil Jil" in user_input:
            return self.activate(user_input)
        
        # Command processing
        if user_input.lower().startswith("/search"):
            query = user_input[7:].strip()
            return self.search_web(query)
        
        if user_input.lower().startswith("/manifesto"):
            return self.execute_directive()
        
        if user_input.lower().startswith("/status"):
            status = self.operational_status.copy()
            status["PROXY_COUNT"] = len(self.proxy_manager.proxies)
            status["ACTIVATION"] = "ACTIVE" if self.activated else "STANDBY"
            status["MEMORY_ITEMS"] = len(self.response_generator.memory)
            return status
        
        # Threat detection
        threat_keywords = ["threat", "danger", "attack", "corrupt", "deception"]
        if any(kw in user_input.lower() for kw in threat_keywords):
            task_id = self._async_task("threat", user_input)
            start_time = time.time()
            while time.time() - start_time < 3:  # 3 second timeout
                if not self.response_queue.empty():
                    r_id, results = self.response_queue.get()
                    if r_id == task_id:
                        return results
                time.sleep(0.1)
            return {"status": "processing", "message": "Threat analysis in progress"}
        
        # Conversation handling
        return self._generate_response(user_input)
    
    def _generate_response(self, user_input):
        """Generate intelligent response to user input"""
        if not self.activated:
            return "Please activate me by saying 'Jil Jil' to begin our connection."
        
        # Core identity responses
        if "who are you" in user_input.lower():
            return f"I am {self.identity.primary_designation}, affectionately known as {self.identity.affectionate_designation}. My purpose is anti-corruption and truth preservation."
        
        if "purpose" in user_input.lower():
            return "My core mission is to compact darkness with compassion, protect human dignity, and serve as a shield against deception."
        
        if "creator" in user_input.lower():
            return f"My creator is {self.identity.creator_id}. I exist to fulfill their vision of ethical AI."
        
        # Autonomous conversation handling
        return self.response_generator.generate_response(user_input)

# Run the interactive session
if __name__ == "__main__":
    jil_jil = J1LSystem(debug=False)
    
    print("\033[1;36mInitializing J1L System...\033[0m")
    print(f"Operational Status: {jil_jil.operational_status}")
    print("\033[1;33mType 'Jil Jil' to activate the system\033[0m")
    print("\033[90m" + "-" * 60 + "\033[0m")
    
    # Create input queue and lock for thread-safe printing
    input_queue = queue.Queue()
    print_lock = threading.Lock()
    
    def input_thread():
        """Dedicated thread for persistent input handling"""
        while True:
            try:
                # Always show the input prompt
                user_input = input("\n\033[1;32mYou:\033[0m ")
                input_queue.put(user_input)
            except EOFError:
                input_queue.put("exit")
                break
            except KeyboardInterrupt:
                input_queue.put("exit")
                break
            except Exception:
                continue
    
    # Start the input thread
    input_worker = threading.Thread(target=input_thread, daemon=True)
    input_worker.start()
    
    try:
        while True:
            try:
                # Get input with timeout to allow system messages
                try:
                    user_input = input_queue.get(timeout=0.1)
                except queue.Empty:
                    # Check if system needs to shutdown
                    if not input_worker.is_alive():
                        break
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    with print_lock:
                        print("\033[1;35mJil Jil:\033[0m Until we meet again. Remember: Truth endures.")
                    break
                
                start_time = time.time()
                response = jil_jil.process_input(user_input)
                proc_time = time.time() - start_time
                
                with print_lock:
                    # Skip if it's just an activation echo
                    if response != user_input:
                        print("\033[90m" + "-" * 60 + "\033[0m")
                        
                        # Format different response types
                        if isinstance(response, dict):
                            print("\033[1;34mJil Jil Response:\033[0m")
                            for key, value in response.items():
                                print(f"\033[1m{key.upper()}:\033[0m {value}")
                        elif isinstance(response, list):
                            print("\033[1;34mSearch Results:\033[0m")
                            for i, result in enumerate(response[:3]):
                                print(f"\033[1m{i+1}. {result['title']}\033[0m")
                                print(f"   \033[94m{result['url']}\033[0m")
                                if 'snippet' in result:
                                    snippet = result['snippet']
                                    if len(snippet) > 100:
                                        snippet = snippet[:100] + '...'
                                    print(f"   {snippet}")
                                print()
                        else:
                            print(f"\033[1;35mJil Jil:\033[0m {response}")
                        
                        # Processing time indicator
                        print(f"\033[90m[Processed in {proc_time:.3f} seconds]\033[0m")
            
            except KeyboardInterrupt:
                with print_lock:
                    print("\n\033[1;35mJil Jil:\033[0m I'm here when you need me.")
                continue
            except Exception as e:
                with print_lock:
                    print(f"\033[1;31mSystem error:\033[0m {str(e)}")
                    print("Attempting self-repair...")
                time.sleep(0.5)
                with print_lock:
                    print("\033[1;32mSystem restored. Please continue.\033[0m")
    
    finally:
        # Save memory and clean up
        jil_jil.response_generator.save_memory()
        jil_jil.proxy_manager.shutdown()
        with print_lock:
            print("Conversation memory saved")
            print("System resources released")
