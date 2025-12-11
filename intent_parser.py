import re
from typing import Dict, List, Optional, Union
import yaml

class IntentParser:
    """
    Converts natural language intents into structured YAML network policies.
    """
    
    # Service to port mappings
    SERVICE_PORTS = {
        # Web services
        'http': [80],
        'https': [443],
        'web': [80, 443],  # Web implies both HTTP and HTTPS
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
        'dns': [53, 853],  # DNS over TLS on 853
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
    }
    
    # Common service aliases and categories
    SERVICE_ALIASES = {
        # Database aliases
        'database': ['mysql', 'postgres', 'mongodb', 'redis'],
        'db': ['mysql', 'postgres', 'mongodb', 'redis'],
        'sql': ['mysql', 'postgres'],
        'nosql': ['mongodb', 'redis'],
        
        # Web and API
        'api': ['https'],
        'rest': ['https'],
        'graphql': ['https'],
        
        # Email and communication
        'email': ['smtp', 'imap', 'pop3'],
        'mail': ['smtp', 'imap', 'pop3'],
        'sendmail': ['smtp'],
        
        # Network services
        'internet': ['http', 'https', 'dns'],
        'browsing': ['http', 'https', 'dns'],
        'network': ['dns', 'ntp'],
        
        # Cloud services
        'aws': ['https'],
        'azure': ['https'],
        'gcp': ['https'],
    }
    
    # Common domains that should get .com appended if no TLD specified
    COMMON_DOMAINS = {
        'google', 'youtube', 'facebook', 'twitter', 'instagram', 'linkedin',
        'github', 'stackoverflow', 'reddit', 'amazon', 'netflix', 'spotify',
        'stripe', 'paypal', 'slack', 'zoom', 'microsoft', 'apple'
    }
    
    def __init__(self):
        # Compiled patterns for performance
        self.service_patterns = [
            # L7 Domains with TLD (e.g., google.com, api.stripe.com)
            (re.compile(r'(?:access|connect to|reach|use)\s+(?:to\s+)?([a-zA-Z0-9-]+\.[a-zA-Z0-9-]+\.[a-zA-Z]{2,}|[a-zA-Z0-9-]+\.[a-zA-Z]{2,})', re.IGNORECASE),
             lambda m, i: self._add_domain(m.group(1).lower(), i)),
            
            # Simple domain names without TLD (e.g., "access google", "access youtube")
            (re.compile(r'(?:access|connect to|reach|use)\s+(?:to\s+)?([a-zA-Z0-9-]+)(?:\s|$)', re.IGNORECASE),
             lambda m, i: self._add_domain_smart(m.group(1).lower(), i)),

            # Web/HTTP
            (re.compile(r'(?:access|use|connect to|enable|allow|need|require)s?\s+(?:the\s+)?(?:web|internet|http|https)(?:\s+services?)?', re.IGNORECASE), 
             lambda s, i: self._add_service('web', i)),
            
            # Databases
            (re.compile(r'(?:connect to|access|use|enable|allow|need|require)s?\s+(?:the\s+)?(database|postgres|postgresql|mysql|mongodb|redis)', re.IGNORECASE), 
             lambda m, i: self._add_service(m.group(1).lower(), i)),
            
            # Email
            (re.compile(r'(?:send|receive|access|use|enable|allow|need|require)s?\s+(?:to\s+)?(email|mail|smtp)', re.IGNORECASE), 
             lambda m, i: self._add_service(m.group(1).lower(), i)),
            
            # DNS
            (re.compile(r'(?:enable|allow|need|require)s?\s+(?:to\s+)?(?:use\s+)?(dns|domain name resolution)', re.IGNORECASE), 
             lambda m, i: self._add_service('dns', i)),
            
            # Generic catch-all
            (re.compile(r'(?:allow|enable|need|require)s?\s+(?:to\s+)?(?:access\s+(?:to\s+)?)?(\w+)(?:\s+services?)?', re.IGNORECASE), 
             self._parse_service_access),
             
            (re.compile(r'(?:needs?|requires?|wants?|should)\s+(?:to\s+)?(?:talk|connect)(?:\s+to)?(?:\s+the)?\s+(\w+)(?:\s+service)?', re.IGNORECASE), 
             self._parse_service_access),
             
            (re.compile(r'(?:allow|enable|need|require)s?\s+(?:to\s+)?(\w+)(?:\s+access)?', re.IGNORECASE), 
             self._parse_service_access),
        ]
        
    DANGEROUS_PORTS = {
        21: "FTP (Plain text credentials)",
        23: "Telnet (Plain text traffic)",
        25: "SMTP (Unencrypted mail)",
        3389: "RDP (Remote Desktop)",
        22: "SSH (Sensitive administrative access)",
    }

    def parse(self, text: str, container_name: str = "my-container") -> Dict:
        """Parses inputs into K8s-style NetworkPolicy entities."""
        intent = {
            'apiVersion': 'v1',
            'kind': 'ContainerIntent',
            'metadata': {
                'name': container_name,
                'annotations': {}
            },
            'spec': { 'egress': [] }
        }
        
        alerts = []
        
        # Split by sentence boundaries to handle complex multi-part intents
        sentences = re.split(r'[.!?](?:\s+|$)', text)
        
        for line in sentences:
            line = line.strip()
            if not line: continue
            
            matched = False
            for pattern, handler in self.service_patterns:
                match = pattern.search(line)
                if match:
                    # Invoke specific handler for the match
                    if handler == self._parse_service_access:
                        if match.lastindex and match.lastindex > 0:
                            handler(match.group(1).lower(), intent)
                    elif handler == self._add_domain:
                        if match.lastindex and match.lastindex > 0:
                            handler(match.group(1).lower(), intent)
                    else:
                        handler(match, intent)
                    
                    matched = True
                    # Don't break; allow multiple keywords per sentence
            
            if not matched:
                # Fallback logging could go here
                pass
    
        # Scan for policy violations
        for rule in intent['spec']['egress']:
            for port_info in rule.get('ports', []):
                p = port_info.get('number')
                if p in self.DANGEROUS_PORTS:
                    msg = f"Port {p} ({self.DANGEROUS_PORTS[p]}) is considered dangerous."
                    if msg not in alerts: alerts.append(msg)
                    
        if alerts:
            intent['metadata']['annotations']['warnings'] = "; ".join(alerts)
            intent['metadata']['annotations']['security_risk'] = "High"

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
    
    def _add_domain_smart(self, name: str, intent: Dict) -> None:
        """
        Intelligently handles domain names - appends .com to common domains.
        Examples: 'google' -> 'google.com', 'youtube' -> 'youtube.com'
        """
        # Ignore if it's a known service keyword (avoid false positives)
        if name in self.SERVICE_PORTS or name in self.SERVICE_ALIASES:
            return
        
        # If it's in our common domains list, append .com
        if name in self.COMMON_DOMAINS:
            full_domain = f"{name}.com"
            self._add_domain(full_domain, intent)
        # If it already has a dot, treat it as a full domain
        elif '.' in name:
            self._add_domain(name, intent)
        # Otherwise, assume it's a domain and append .com
        else:
            # For unknown single-word domains, append .com as well
            full_domain = f"{name}.com"
            self._add_domain(full_domain, intent)
            
    def _add_domain(self, domain: str, intent: Dict) -> None:
        """Whitelists a domain and enables required DNS/Web ports."""
        self._add_service('web', intent)
        
        # Attach domain to the first available rule (simplification for prototype)
        target_rule = next((r for r in intent['spec']['egress'] if any(p['number'] == 443 for p in r.get('ports', []))), None)
        
        if not target_rule and intent['spec']['egress']:
             target_rule = intent['spec']['egress'][0]
             
        if target_rule:
            if 'domains' not in target_rule: target_rule['domains'] = []
            if domain not in target_rule['domains']: target_rule['domains'].append(domain)
    
    def _add_service(self, service: str, intent: Dict) -> None:
        if service in self.SERVICE_ALIASES:
            for alias in self.SERVICE_ALIASES[service]:
                self._add_single_service(alias, intent)
            return
        self._add_single_service(service, intent)
    
    def _add_single_service(self, service: str, intent: Dict) -> None:
        """Add a single service to the intent"""
        if service not in self.SERVICE_PORTS:
            return
            
        # SPECIAL HANDLING: If 'web' or 'internet' is requested, usually we need DNS too
        if service in ['web', 'internet', 'browsing']:
            self._add_single_service('dns', intent)

        # Get all existing ports
        existing_ports = set()
        for rule in intent['spec']['egress']:
            for port in rule.get('ports', []):
                existing_ports.add((port['number'], port.get('protocol', 'TCP')))
        
        # Add ports that aren't already in the rules
        new_ports = [
            (port, 'TCP') if isinstance(port, int) else port
            for port in self.SERVICE_PORTS[service]
            if (port if isinstance(port, tuple) else (port, 'TCP')) not in existing_ports
        ]
        
        if new_ports:
            # Group by protocol
            ports_by_protocol = {}
            for port in new_ports:
                if isinstance(port, tuple):
                    port_num, protocol = port
                else:
                    port_num, protocol = port, 'TCP'
                    
                if protocol not in ports_by_protocol:
                    ports_by_protocol[protocol] = []
                ports_by_protocol[protocol].append(port_num)
            
            # Add a rule for each protocol
            for protocol, ports in ports_by_protocol.items():
                intent['spec']['egress'].append({
                    'ports': [
                        {'number': port, 'protocol': protocol.upper()}
                        for port in sorted(ports)
                    ]
                })
    
    def to_yaml(self, intent: Dict) -> str:
        """Convert intent dictionary to YAML string"""
        return yaml.dump(intent, default_flow_style=False, sort_keys=False)


def parse_intent(text: str, container_name: str = "my-container") -> str:
    """Parse natural language intent and return YAML string."""
    parser = IntentParser()
    intent = parser.parse(text, container_name)
    return parser.to_yaml(intent)


if __name__ == "__main__":
    test_intent = """
    My container needs to access google.com.
    """
    
    print("Parsing intent:")
    print(test_intent)
    print("\nGenerated YAML:")
    print(parse_intent(test_intent, "example-app"))
