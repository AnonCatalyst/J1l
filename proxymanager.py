# proxymanager.py
import requests
import random
import threading
import time
from fake_useragent import UserAgent
import concurrent.futures
import re
import multiprocessing
import datetime
from collections import defaultdict
import queue

class ProxyManager:
    PROXY_SOURCES = [
        "https://www.sslproxies.org/",
        "https://free-proxy-list.net/",
        "https://www.us-proxy.org/",
        "https://proxyscrape.com/free-proxy-list",
        "https://hidemy.name/en/proxy-list/"
    ]
    
    def __init__(self, min_stock=100, refresh_threshold=50, max_scrape=200, debug=False):
        """
        Initialize the Proxy Manager with configuration settings.
        
        Parameters:
        min_stock (int): Minimum number of proxies to maintain
        refresh_threshold (int): Proxy count threshold to trigger refresh
        max_scrape (int): Maximum proxies to scrape per source
        debug (bool): Enable debug output
        """
        self.proxies = []
        self.min_stock = min_stock
        self.refresh_threshold = refresh_threshold
        self.max_scrape = max_scrape
        self.debug = debug
        self.last_refresh = 0
        self.lock = threading.Lock()
        self.ua = UserAgent()
        self.running = True
        self.proxy_pattern = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}:\d{2,5}\b')
        self.initialized = False
        self.stats = {
            'total_scraped': 0,
            'valid_proxies': 0,
            'last_refresh_duration': 0,
            'source_stats': defaultdict(int),
            'health_check_stats': {'success': 0, 'failure': 0}
        }
        self.status_queue = multiprocessing.Queue()
        
        # Start maintenance thread
        self.maintenance_thread = threading.Thread(target=self._maintenance_loop)
        self.maintenance_thread.daemon = True
        self.maintenance_thread.start()

        # Start status monitor thread
        self.status_thread = threading.Thread(target=self._status_monitor)
        self.status_thread.daemon = True
        self.status_thread.start()
        
    def _extract_proxies(self, text):
        """Extract proxies using regex pattern"""
        return self.proxy_pattern.findall(text)
    
    def _fetch_proxies_from_source(self, source):
        """
        Scrape proxies from a single source with OPSEC measures
        
        Parameters:
        source (str): URL of the proxy list source
        
        Returns:
        list: List of proxies scraped from the source
        """
        try:
            headers = {
                'User-Agent': self.ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://www.google.com/',
                'DNT': '1'
            }
            
            # OPSEC: Add random delays between requests
            time.sleep(random.uniform(0.5, 2.0))
            
            response = requests.get(
                source,
                headers=headers,
                timeout=10,
                allow_redirects=True
            )
            
            proxies = self._extract_proxies(response.text)
            return proxies[:self.max_scrape//len(self.PROXY_SOURCES)]
        except Exception as e:
            if self.debug:
                print(f"Error scraping {source}: {str(e)}")
            return []
    
    def _scrape_proxies_concurrently(self):
        """
        Scrape all proxy sources concurrently using thread pool
        
        Returns:
        tuple: (list of scraped proxies, scraping duration)
        """
        if self.debug:
            print("Starting concurrent proxy scraping...")
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.PROXY_SOURCES)) as executor:
            future_to_source = {executor.submit(self._fetch_proxies_from_source, source): source 
                               for source in self.PROXY_SOURCES}
            
            new_proxies = []
            for future in concurrent.futures.as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    proxies = future.result()
                    new_proxies.extend(proxies)
                    self.status_queue.put(('SCRAPED', source, len(proxies)))
                    if self.debug:
                        print(f"Scraped {len(proxies)} proxies from {source}")
                except Exception as e:
                    if self.debug:
                        print(f"Error processing {source}: {str(e)}")
        
        # Remove duplicates
        new_proxies = list(set(new_proxies))
        if self.debug:
            print(f"Total scraped: {len(new_proxies)}. Starting health checks...")
        self.stats['total_scraped'] = len(new_proxies)
        self.status_queue.put(('TOTAL_SCRAPED', len(new_proxies)))
        
        return new_proxies, time.time() - start_time
    
    def _batch_health_check(self, proxies, batch_size=50):
        """
        Perform health checks on proxies in batches with progress reporting
        
        Parameters:
        proxies (list): Proxies to check
        batch_size (int): Number of proxies per batch
        
        Returns:
        list: Valid proxies that passed health checks
        """
        if self.debug:
            print(f"Starting health checks for {len(proxies)} proxies...")
        valid_proxies = []
        total = len(proxies)
        checked = 0
        
        # Split into batches
        batches = [proxies[i:i + batch_size] for i in range(0, len(proxies), batch_size)]
        
        for batch in batches:
            with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                future_to_proxy = {executor.submit(self._check_proxy_health, proxy): proxy for proxy in batch}
                
                for future in concurrent.futures.as_completed(future_to_proxy):
                    proxy = future_to_proxy[future]
                    checked += 1
                    try:
                        if future.result():
                            valid_proxies.append(proxy)
                            self.status_queue.put(('VALID_PROXY', proxy))
                            self.stats['health_check_stats']['success'] += 1
                        else:
                            self.stats['health_check_stats']['failure'] += 1
                    except:
                        self.stats['health_check_stats']['failure'] += 1
                    
                    # Update progress every 10% or 10 proxies
                    if self.debug and checked % max(10, total//10) == 0:
                        progress = (checked / total) * 100
                        self.status_queue.put(('PROGRESS', progress, checked, total))
        
        if self.debug:
            print(f"Health checks complete. Valid proxies: {len(valid_proxies)}/{total}")
        return valid_proxies
    
    def _refresh_proxies(self):
        """Refresh proxy list with concurrent scraping and batch health checks"""
        start_time = time.time()
        if self.debug:
            print("Refreshing proxy list...")
        self.status_queue.put(('REFRESH_START',))
        
        # Scrape proxies concurrently
        new_proxies, scrape_time = self._scrape_proxies_concurrently()
        self.status_queue.put(('SCRAPE_TIME', scrape_time))
        
        # Perform health checks in batches
        valid_proxies = self._batch_health_check(new_proxies)
        health_check_time = time.time() - start_time - scrape_time
        
        with self.lock:
            # Combine existing and new valid proxies
            combined = list(set(self.proxies + valid_proxies))
            
            # Prioritize newer proxies but keep some old ones
            self.proxies = combined[:self.min_stock]
            
            # Update stats
            self.stats['valid_proxies'] = len(self.proxies)
            self.stats['last_refresh_duration'] = time.time() - start_time
            self.last_refresh = time.time()
            self.initialized = True
            
            if self.debug:
                print(f"Proxy refresh complete. Total proxies: {len(self.proxies)}")
            self.status_queue.put(('REFRESH_COMPLETE', len(self.proxies), time.time() - start_time))
    
    def _check_proxy_health(self, proxy):
        """
        Check if a proxy is functional by testing with multiple sites
        
        Parameters:
        proxy (str): Proxy address in IP:PORT format
        
        Returns:
        bool: True if proxy is functional, False otherwise
        """
        try:
            test_sites = [
                "https://www.google.com",
                "https://www.cloudflare.com",
                "https://www.github.com"
            ]
            
            headers = {'User-Agent': self.ua.random}
            proxies_config = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
            
            # Test with multiple sites
            for site in test_sites:
                response = requests.get(
                    site, 
                    headers=headers, 
                    proxies=proxies_config, 
                    timeout=5
                )
                if response.status_code != 200:
                    return False
            
            return True
        except Exception:
            return False
    
    def _status_monitor(self):
        """Display live statistics and progress updates only in debug mode"""
        while self.running:
            try:
                # Non-blocking check of the queue
                try:
                    message = self.status_queue.get_nowait()
                except queue.Empty:
                    time.sleep(0.1)
                    continue
                
                if not self.debug:
                    continue
                
                if message[0] == 'SCRAPED':
                    _, source, count = message
                    print(f"🔎 Scraped {count} proxies from {source}")
                elif message[0] == 'TOTAL_SCRAPED':
                    _, count = message
                    print(f"📊 Total proxies scraped: {count}")
                elif message[0] == 'PROGRESS':
                    _, progress, checked, total = message
                    bar_length = 30
                    filled_length = int(bar_length * checked // total)
                    bar = '█' * filled_length + '-' * (bar_length - filled_length)
                    print(f"🔄 Health checks: [{bar}] {progress:.1f}% ({checked}/{total})")
                elif message[0] == 'VALID_PROXY':
                    _, proxy = message
                    print(f"✅ Valid proxy: {proxy}")
                elif message[0] == 'REFRESH_START':
                    print("\n🚀 Starting proxy refresh...")
                elif message[0] == 'SCRAPE_TIME':
                    _, duration = message
                    print(f"⏱️ Scraping completed in {duration:.2f} seconds")
                elif message[0] == 'REFRESH_COMPLETE':
                    _, count, duration = message
                    print(f"\n🎉 Proxy refresh completed!")
                    print(f"🕒 Total duration: {duration:.2f} seconds")
                    print(f"🛡️ Active proxies: {count}\n")
                
            except Exception as e:
                if self.debug:
                    print(f"Status monitor error: {str(e)}")
    
    def _maintenance_loop(self):
        """Background thread for proxy maintenance"""
        # Initial refresh
        self._refresh_proxies()
        
        # Periodic maintenance
        while self.running:
            time.sleep(60)  # Check every minute
            
            with self.lock:
                proxy_count = len(self.proxies)
                
                # Only refresh if below threshold
                if proxy_count < self.refresh_threshold:
                    if self.debug:
                        print(f"Low proxy count ({proxy_count} < {self.refresh_threshold}), refreshing...")
                    self._refresh_proxies()
    
    def get_random_proxy(self):
        """Get a random proxy from the pool (thread-safe)"""
        with self.lock:
            if not self.proxies:
                return None
            return random.choice(self.proxies)
    
    def get_stats(self):
        """Get current statistics (thread-safe)"""
        with self.lock:
            stats = self.stats.copy()
            stats['current_proxies'] = len(self.proxies)
            stats['last_refresh'] = datetime.datetime.fromtimestamp(
                self.last_refresh).strftime('%Y-%m-%d %H:%M:%S')
            stats['source_distribution'] = dict(self.stats['source_stats'])
            return stats
    
    def is_ready(self):
        """Check if proxy system is initialized"""
        return self.initialized
    
    def shutdown(self):
        """Clean shutdown of the proxy manager"""
        self.running = False
        if self.maintenance_thread.is_alive():
            self.maintenance_thread.join(timeout=5)
        if self.status_thread.is_alive():
            self.status_thread.join(timeout=2)
