import yaml
import re

class IntentValidator:
    def validate(self, intent_data):
        """Validate intent structure and content"""
        errors = []
        
        # Check required fields
        if not intent_data.get('apiVersion'):
            errors.append("Missing 'apiVersion' field")
        
        if intent_data.get('kind') != 'ContainerIntent':
            errors.append("Kind must be 'ContainerIntent'")
        
        # Validate metadata
        metadata = intent_data.get('metadata', {})
        if not metadata.get('name'):
            errors.append("Missing 'metadata.name'")
        elif not re.match(r'^[a-z0-9-]+$', metadata.get('name', '')):
            errors.append("Name must be lowercase alphanumeric with hyphens")
        
        # Validate spec and egress rules
        spec = intent_data.get('spec', {})
        egress_rules = spec.get('egress', [])
        
        if not egress_rules:
            errors.append("No egress rules defined")
        
        for i, rule in enumerate(egress_rules):
            # Check if rule has either domains or ports
            if not rule.get('domains') and not rule.get('ports'):
                errors.append(f"Rule {i}: Must have either domains or ports")
            
            # Validate ports
            for port_spec in rule.get('ports', []):
                port = port_spec.get('number')
                if port is None:
                    errors.append(f"Rule {i}: Port number is required")
                elif not (1 <= port <= 65535):
                    errors.append(f"Rule {i}: Port {port} must be between 1-65535")
                
                protocol = port_spec.get('protocol', 'TCP')
                if protocol not in ['TCP', 'UDP']:
                    errors.append(f"Rule {i}: Protocol must be TCP or UDP")
        
        return errors
    
    def semantic_analysis(self, intent_data):
        """Analyze security patterns and provide recommendations"""
        warnings = []
        suggestions = []
        
        egress_rules = intent_data.get('spec', {}).get('egress', [])
        
        for i, rule in enumerate(egress_rules):
            ports = [p['number'] for p in rule.get('ports', [])]
            domains = rule.get('domains', [])
            
            # Detect overly permissive rules
            if not domains and len(ports) > 5:
                warnings.append(f"Rule {i}: Overly permissive - many ports without domain restrictions")
                suggestions.append("Consider restricting to specific domains")
            
            # Flag dangerous port combinations
            dangerous_ports = {22, 23, 3389, 1433, 3306}  # SSH, Telnet, RDP, SQL
            found_dangerous = dangerous_ports.intersection(ports)
            if found_dangerous and not domains:
                warnings.append(f"Rule {i}: Security risk - administrative ports {found_dangerous} without domain restrictions")
                suggestions.append("Restrict administrative ports to specific internal domains")
            
            # Check for HTTP without HTTPS
            has_http = 80 in ports
            has_https = 443 in ports
            if has_http and not has_https:
                warnings.append(f"Rule {i}: HTTP allowed without HTTPS - potential security risk")
                suggestions.append("Consider requiring HTTPS for web traffic")
            
            # Detect external database exposure
            db_ports = {1433, 3306, 5432, 27017}  # SQL Server, MySQL, PostgreSQL, MongoDB
            external_db_ports = db_ports.intersection(ports)
            if external_db_ports and any('.' in domain for domain in domains):
                warnings.append(f"Rule {i}: Database ports {external_db_ports} exposed to external domains")
                suggestions.append("Consider if database should be exposed externally")
        
        return warnings, suggestions