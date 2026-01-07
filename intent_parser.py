import re
from typing import Dict, List, Optional, Union
import yaml
import requests
import json
import sys
import ipaddress

class IntentParser:
    """
    Converts natural language intents into structured YAML network policies.
    Supports both RegEx (Deterministic) and LLM (Probabilistic) parsing.
    """
    
    # Service to port mappings (Used for Regex Mode and as fallback)
    SERVICE_PORTS = {
        # Web services
        'http': [80],
        'https': [443],
        'web': [80, 443],
        'www': [80, 443],
        
        # Database services
        'mysql': [3306],
        'postgres': [5432],
        'postgresql': [5432],
        'mongodb': [27017],
        'redis': [6379],
        
        # Messaging
        'rabbitmq': [5672],
        'amqp': [5672],
        
        # Email
        'smtp': [25, 587, 465],
        'email': [25, 587, 465, 993, 995],
        'imap': [143, 993],
        'pop3': [110, 995],
        
        # Network services
        'dns': [53, 853],
        'ldap': [389, 636],
        'ntp': [123],
        
        # Remote access
        'ssh': [22],
        'ftp': [21],
        'sftp': [22],
        'telnet': [23], 
        
        # Common protocols
        'rdp': [3389],
        'vnc': [5900, 5901],
        
        # Microservices & Gateways
        'api-gateway': [8080],
        'gateway': [8080],
    }
    
    # Common service aliases and categories
    SERVICE_ALIASES = {
        'database': ['mysql', 'postgres', 'mongodb', 'redis'],
        'db': ['mysql', 'postgres', 'mongodb', 'redis'],
        'sql': ['mysql', 'postgres'],
        'nosql': ['mongodb', 'redis'],
        'api': ['https'],
        'rest': ['https'],
        'graphql': ['https'],
        'email': ['smtp'], # Default to send
        'mail': ['smtp'],
        'sendmail': ['smtp'],
        'send-email': ['smtp'],
        'receive-email': ['imap', 'pop3'],
        'inbox': ['imap', 'pop3'],
        'internet': ['http', 'https', 'dns'],
        'browsing': ['http', 'https', 'dns'],
        'network': ['dns', 'ntp'],
        'aws': ['https'],
        'azure': ['https'],
        'gcp': ['https'],
    }
    
    COMMON_DOMAINS = {
        'google', 'youtube', 'facebook', 'twitter', 'instagram', 'linkedin',
        'github', 'stackoverflow', 'reddit', 'amazon', 'netflix', 'spotify',
        'stripe', 'paypal', 'slack', 'zoom', 'microsoft', 'apple'
    }
    
    STOP_WORDS = {
        'the', 'a', 'an', 'on', 'to', 'for', 'with', 'using', 'through', 
        'access', 'connect', 'reach', 'talk', 'needs', 'require', 'needed',
        'legacy', 'mainframe', 'server', 'service', 'app', 'application'
    }
    
    DANGEROUS_PORTS = {
        21: "FTP (Plain text credentials)",
        23: "Telnet (Plain text traffic)",
        25: "SMTP (Unencrypted mail)",
        3389: "RDP (Remote Desktop)",
        22: "SSH (Sensitive administrative access)",
    }
    
    def __init__(self):
        # Compiled patterns for Regex Mode
        self.service_patterns = [
            (re.compile(r'(?:access|connect to|reach|use)\s+(?:to\s+)?([a-zA-Z0-9-]+\.[a-zA-Z0-9-]+\.[a-zA-Z]{2,}|[a-zA-Z0-9-]+\.[a-zA-Z]{2,})', re.IGNORECASE),
             lambda m, i: self._add_domain(m.group(1).lower(), i)),
             
            (re.compile(r'(?:access|connect to|reach|use)\s+(?:to\s+)?([a-zA-Z0-9-]+)(?:\s|$)', re.IGNORECASE),
             lambda m, i: self._add_domain_smart(m.group(1).lower(), i)),

            (re.compile(r'(?:access|use|connect to|enable|allow|need|require)s?\s+(?:the\s+)?(?:web|internet|http|https)(?:\s+services?)?', re.IGNORECASE), 
             lambda s, i: self._add_service('web', i)),
            
            (re.compile(r'(?:connect to|access|use|enable|allow|need|require)s?\s+(?:the\s+)?(database|postgres|postgresql|mysql|mongodb|redis)', re.IGNORECASE), 
             lambda m, i: self._add_service(m.group(1).lower(), i)),
            
            (re.compile(r'(?:send|receive|access|use|enable|allow|need|require)s?\s+(?:to\s+)?(email|mail|smtp)', re.IGNORECASE), 
             lambda m, i: self._add_service(m.group(1).lower(), i)),
            
            (re.compile(r'(?:enable|allow|need|require)s?\s+(?:to\s+)?(?:use\s+)?(dns|domain name resolution)', re.IGNORECASE), 
             lambda m, i: self._add_service('dns', i)),
            
            (re.compile(r'(?:allow|enable|need|require)s?\s+(?:to\s+)?(?:access\s+(?:to\s+)?)?(\w+)(?:\s+services?)?', re.IGNORECASE), 
             self._parse_service_access),
             
            (re.compile(r'(?:needs?|requires?|wants?|should)\s+(?:to\s+)?(?:talk|connect|communicate)(?:\s+to)?(?:\s+the)?\s+([a-zA-Z0-9-]+)(?:\s+service)?', re.IGNORECASE), 
             self._parse_service_access),
             
            (re.compile(r'(?:allow|enable|need|require)s?\s+(?:to\s+)?([a-zA-Z0-9-]+)(?:\s+access)?', re.IGNORECASE), 
             self._parse_service_access),
             
            # Microservices specific pattern: "A talks to B"
            (re.compile(r'([a-zA-Z0-9-]+)\s+(?:talks?|connects?|communicates?)\s+to\s+([a-zA-Z0-9-]+)', re.IGNORECASE),
             self._parse_microservice_interaction),
             
            # IP address support
            (re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
             lambda m, i: self._add_domain(m.group(0), i)),
             
            # Contextual domain pattern: "via SendGrid", "on 1.2.3.4"
            (re.compile(r'(?:via|through|on|at)\s+([a-zA-Z0-9.-]+)', re.IGNORECASE),
             lambda m, i: self._add_domain_smart(m.group(1).lower(), i)),
             
            # Fallback for bare service names
            (re.compile(r'\b(postgres|postgresql|mysql|mongodb|redis|http|https|ssh|telnet|dns|ftp|smtp|imap|pop3|api-gateway|gateway|email|mail|web|rdp|vnc|rabbitmq)\b', re.IGNORECASE),
             lambda m, i: self._add_service(m.group(1).lower(), i)),
        ]

    def parse(self, text: str, container_name: str = "my-container") -> Dict:
        """
        Parses inputs into K8s-style NetworkPolicy entities.
        
        TOGGLE MODE HERE:
        Uncomment the one you want to use.
        """
        
        # --- MODE 1: REGEX (Deterministic, Fast, Offline) ---
        return self._parse_with_regex(text, container_name)
        
        # --- MODE 2: LLM (Smart, Context-Aware, Requires Ollama) ---
        # If Ollama fails, it will fallback to Regex automatically.
        # return self._parse_with_llm(text, container_name)

    def _parse_with_llm(self, text: str, container_name: str, model: str = "llama3") -> Dict:
        """Uses a local LLM (Ollama) to parse intents with few-shot prompting."""
        print(f"[INFO] Parsing with local LLM ({model})...")
        
        prompt = f"""
        You are a network security expert. Extract technical requirements from the user's intent.
        Return ONLY a JSON object.

        {{
            "services": ["service_name_1", "service_name_2"],
            "domains": ["domain1.com", "domain2.com"]
        }}

        Known services keys: 
        web, http, https, dns, ssh, telnet, ftp, smtp, imap, pop3, mysql, postgres, mongodb, redis, rabbitmq, rdp, vnc.

        If the user mentions a specific port (e.g. "port 8080"), add it as a service named "port-8080".
        If the intent is vague, assume reasonable defaults (e.g. "ping" -> "icmp" or "network").

        Examples:
        User Intent: "I need Telnet access to the legacy mainframe on 10.0.50.10"
        JSON:
        {{
            "services": ["telnet"],
            "domains": ["10.0.50.10"]
        }}

        User Intent: "frontend talks to api-gateway and redis cache in the local servers, backend connects to postgres and sends emails via SendGrid"
        JSON:
        {{
            "services": ["api-gateway", "redis", "postgres", "email"],
            "domains": ["servers.local", "sendgrid.com"]
        }}

        User Intent: "{text}"
        JSON:
        """
        
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model, 
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": 0.1 # Keep it deterministic
                    }
                },
                timeout=10 # Increased timeout for LLM inference
            )
            
            if response.status_code == 200:
                result = response.json()
                raw_response = result.get('response', '{}')
                data = json.loads(raw_response)
                
                # Convert LLM JSON to Policy Dict
                intent = self._create_base_intent(container_name)
                
                # Apply Services
                for svc in data.get('services', []):
                    svc = svc.lower().strip()
                    # Handle raw ports "port-8080"
                    if svc.startswith("port-"):
                        try:
                            port = int(svc.split("-")[1])
                            intent['spec']['egress'].append({
                                'ports': [{'number': port, 'protocol': 'TCP'}]
                            })
                        except: pass
                    else:
                        self._add_service(svc, intent)
                
                # Apply Domains
                for dom in data.get('domains', []):
                    self._add_domain(dom.lower().strip(), intent)
                
                # Ensure we have at least some rules if the LLM returned services but no ports were found
                if not intent['spec']['egress'] and (data.get('services') or data.get('domains')):
                    print("[WARN] LLM returned data but no egress rules were generated. Checking fallbacks.")
                
                self._enrich_security_risks(intent)
                return intent
                
            else:
                print(f"[WARN] LLM Error {response.status_code}, falling back to Regex.")
                return self._parse_with_regex(text, container_name)
                
        except Exception as e:
            print(f"[WARN] LLM unavailable or error ({str(e)}), falling back to Regex.")
            return self._parse_with_regex(text, container_name)

    def _create_base_intent(self, container_name: str) -> Dict:
        return {
            'apiVersion': 'v1',
            'kind': 'ContainerIntent',
            'metadata': {
                'name': container_name,
                'annotations': {}
            },
            'spec': { 'egress': [] }
        }

    def _enrich_security_risks(self, intent: Dict):
        """Scans the generated intent for high-risk ports."""
        alerts = []
        for rule in intent['spec']['egress']:
            for port_info in rule.get('ports', []):
                p = port_info.get('number')
                if p in self.DANGEROUS_PORTS:
                    msg = f"Port {p} ({self.DANGEROUS_PORTS[p]}) is considered dangerous."
                    if msg not in alerts: alerts.append(msg)
                    
        if alerts:
            intent['metadata']['annotations']['warnings'] = "; ".join(alerts)
            intent['metadata']['annotations']['security_risk'] = "High"

    def _parse_with_regex(self, text: str, container_name: str) -> Dict:
        """Original Regex Logic (Refactored)"""
        print("[INFO] Parsing with regex engine...")
        intent = self._create_base_intent(container_name)
        
        # Split by sentence boundaries, commas, and conjunctions
        # Use a lookahead to ensure dots are only splitters if they end a sentence
        # Also handle "and" more broadly but avoid breaking domain names
        sentences = re.split(r'(?:[.!?](?:\s+|$))|[;,]|\s+(?:and|also|plus|with)\s+', text)
        
        for line in sentences:
            line = line.strip()
            if not line: continue
            
            matched = False
            for pattern, handler in self.service_patterns:
                matches = pattern.finditer(line)
                for match in matches:
                    if handler == self._parse_service_access:
                        if match.lastindex and match.lastindex > 0:
                            handler(match.group(1).lower(), intent)
                    elif handler == self._add_domain:
                        if match.lastindex and match.lastindex > 0:
                            handler(match.group(1).lower(), intent)
                    elif handler == self._parse_microservice_interaction:
                        handler(match.group(1).lower(), match.group(2).lower(), intent)
                    else:
                        handler(match, intent)
                    matched = True
            
        self._enrich_security_risks(intent)
        return intent

    def _parse_service_access(self, service: str, intent: Dict) -> None:
        """Resolves service names/aliases to port rules."""
        if service in self.SERVICE_ALIASES:
            for actual_service in self.SERVICE_ALIASES[service]:
                self._add_service(actual_service, intent)
        elif service in self.SERVICE_PORTS:
            self._add_service(service, intent)
        elif '.' in service and not service.endswith('.'):
             self._add_domain(service, intent)
             
    def _parse_microservice_interaction(self, source: str, target: str, intent: Dict) -> None:
        """Handles patterns like 'frontend talks to redis'."""
        if source not in self.STOP_WORDS:
            # We could use source to filter/tag, but for now we just parse the target
            self._parse_service_access(target, intent)
        else:
            # If source is a stop word, maybe target is actually the service
            self._parse_service_access(source, intent)
            self._parse_service_access(target, intent)

    def _add_domain_smart(self, name: str, intent: Dict) -> None:
        if name in self.STOP_WORDS or len(name) < 2 or name.isdigit():
            return
            
        if name in self.SERVICE_PORTS or name in self.SERVICE_ALIASES: 
            self._add_service(name, intent)
            return
        
        # Check if it's an IP highlight
        if self._is_ip(name):
            self._add_domain(name, intent)
            return

        if name in self.COMMON_DOMAINS:
            self._add_domain(f"{name}.com", intent)
        elif '.' in name:
            self._add_domain(name, intent)
        else:
            self._add_domain(f"{name}.com", intent)

    def _is_ip(self, val: str) -> bool:
        try:
            ipaddress.ip_address(val)
            return True
        except ValueError:
            return False
            
    def _add_domain(self, domain: str, intent: Dict) -> None:
        # Only add web ports if it's NOT an IP address
        if not self._is_ip(domain):
            self._add_service('web', intent)
            
        target_rule = next((r for r in intent['spec']['egress'] if any(p['number'] == 443 for p in r.get('ports', []))), None)
        
        if not target_rule and intent['spec']['egress']:
             target_rule = intent['spec']['egress'][0]
             
        if not target_rule:
            intent['spec']['egress'].append({'ports': []})
            target_rule = intent['spec']['egress'][-1]

        if 'domains' not in target_rule: target_rule['domains'] = []
        if domain not in target_rule['domains']: target_rule['domains'].append(domain)
    
    def _add_service(self, service: str, intent: Dict) -> None:
        if service in self.SERVICE_ALIASES:
            for alias in self.SERVICE_ALIASES[service]:
                self._add_single_service(alias, intent)
            return
        self._add_single_service(service, intent)
    
    def _add_single_service(self, service: str, intent: Dict) -> None:
        if service not in self.SERVICE_PORTS: return
        if service in ['web', 'internet', 'browsing']: self._add_single_service('dns', intent)

        existing_ports = set()
        for rule in intent['spec']['egress']:
            for port in rule.get('ports', []):
                existing_ports.add((port['number'], port.get('protocol', 'TCP')))
        
        new_ports = [
            (port, 'TCP') if isinstance(port, int) else port
            for port in self.SERVICE_PORTS[service]
            if (port if isinstance(port, tuple) else (port, 'TCP')) not in existing_ports
        ]
        
        if new_ports:
            ports_by_protocol = {}
            for port in new_ports:
                if isinstance(port, tuple): port_num, protocol = port
                else: port_num, protocol = port, 'TCP'
                    
                if protocol not in ports_by_protocol: ports_by_protocol[protocol] = []
                ports_by_protocol[protocol].append(port_num)
            
            for protocol, ports in ports_by_protocol.items():
                intent['spec']['egress'].append({
                    'ports': [{'number': port, 'protocol': protocol.upper()} for port in sorted(ports)]
                })
    
    def to_yaml(self, intent: Dict) -> str:
        return yaml.dump(intent, default_flow_style=False, sort_keys=False)


def parse_intent(text: str, container_name: str = "my-container") -> str:
    parser = IntentParser()
    intent = parser.parse(text, container_name)
    return parser.to_yaml(intent)


if __name__ == "__main__":
    test_intent = "My container needs to access google.com."
    print(parse_intent(test_intent, "example-app"))
