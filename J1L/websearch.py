# websearch.py
import requests
import time
import random
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import re
import logging

class WebSearch:
    def __init__(self, proxy_manager):
        self.proxy_manager = proxy_manager
        self.ua = UserAgent()  # Using updated fake-useragent
        self.search_engines = [
            "https://www.google.com/search?q={}&num=7",
            "https://www.bing.com/search?q={}&count=7",
            "https://search.yahoo.com/search?p={}&n=7",
            "https://duckduckgo.com/html/?q={}"
        ]
        self.last_search_time = 0
        self.search_counter = 0
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        logger = logging.getLogger('WebSearch')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
        
    def search(self, query, max_results=5):
        """Perform an evasive web search with enhanced anonymity"""
        # Apply search patterns to avoid detection
        self._apply_evasion_tactics()
        
        # Select a random search engine
        engine_url = random.choice(self.search_engines)
        search_url = engine_url.format(requests.utils.quote(query))
        
        # Get proxy and headers
        proxy = self.proxy_manager.get_random_proxy()
        if not proxy:
            return "Proxy system not ready. Please try again later."
        
        proxies = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
        headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.google.com/'
        }
        
        try:
            self.logger.info(f"Searching: {query[:20]}... via {proxy}")
            start_time = time.time()
            
            response = requests.get(
                search_url,
                headers=headers,
                proxies=proxies,
                timeout=10
            )
            
            latency = time.time() - start_time
            self.logger.info(f"Search completed in {latency:.2f}s")
            
            if response.status_code == 200:
                return self._parse_results(response.text, max_results, engine_url)
            return f"Search failed with status: {response.status_code}"
        except Exception as e:
            self.logger.error(f"Search error: {str(e)}")
            return f"Search error: {str(e)}"
    
    def _apply_evasion_tactics(self):
        """Apply techniques to avoid bot detection"""
        current_time = time.time()
        time_since_last = current_time - self.last_search_time
        
        # Random delay based on search frequency
        if self.search_counter > 0:
            min_delay = max(0.5, 3 - self.search_counter)  # More searches = shorter delays
            max_delay = min(3, 5 - self.search_counter/2)
            delay = random.uniform(min_delay, max_delay)
            time.sleep(delay)
        
        # Reset counter every 4-6 searches
        if self.search_counter >= random.randint(4, 6):
            self.search_counter = 0
            # Longer pause with random duration
            time.sleep(random.uniform(5, 10))
        
        self.last_search_time = time.time()
        self.search_counter += 1
    
    def _parse_results(self, html, max_results, engine_url):
        """Parse search results from HTML with multiple engine support"""
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        # Google
        if "google.com" in engine_url:
            for g in soup.select('div.g'):
                title = g.select_one('h3')
                link = g.select_one('a[href]')
                snippet = g.select_one('div.IsZvec, .VwiC3b')
                
                if title and link:
                    result = {
                        'title': title.get_text(),
                        'url': link['href'],
                        'snippet': snippet.get_text() if snippet else ''
                    }
                    results.append(result)
                    if len(results) >= max_results:
                        return results
        
        # Bing
        elif "bing.com" in engine_url:
            for b in soup.select('li.b_algo'):
                title = b.select_one('h2')
                link = b.select_one('a[href]')
                snippet = b.select_one('div.b_caption > p')
                
                if title and link:
                    result = {
                        'title': title.get_text(),
                        'url': link['href'],
                        'snippet': snippet.get_text() if snippet else ''
                    }
                    results.append(result)
                    if len(results) >= max_results:
                        return results
        
        # Yahoo
        elif "yahoo.com" in engine_url:
            for y in soup.select('div.algo-sr'):
                title = y.select_one('h3.title')
                link = y.select_one('a[href]')
                snippet = y.select_one('div.compText')
                
                if title and link:
                    result = {
                        'title': title.get_text(),
                        'url': link['href'],
                        'snippet': snippet.get_text() if snippet else ''
                    }
                    results.append(result)
                    if len(results) >= max_results:
                        return results
        
        # DuckDuckGo
        elif "duckduckgo.com" in engine_url:
            for d in soup.select('div.result'):
                title = d.select_one('h2.result__title')
                link = d.select_one('a.result__a[href]')
                snippet = d.select_one('a.result__snippet')
                
                if title and link:
                    result = {
                        'title': title.get_text(),
                        'url': link['href'],
                        'snippet': snippet.get_text() if snippet else ''
                    }
                    results.append(result)
                    if len(results) >= max_results:
                        return results
        
        # Fallback to generic parsing
        if not results:
            links = soup.select('a[href]')
            for link in links:
                url = link.get('href')
                title = link.get_text().strip()
                
                # Basic URL validation
                if url and url.startswith('http') and title:
                    # Find snippet - look for adjacent divs
                    snippet = ""
                    next_sib = link.find_next_sibling()
                    if next_sib and next_sib.name == 'div':
                        snippet = next_sib.get_text()
                    
                    results.append({
                        'title': title,
                        'url': url,
                        'snippet': snippet
                    })
                    if len(results) >= max_results:
                        break
        
        return results if results else "No results found"
