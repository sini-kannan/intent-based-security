import unittest
import sys
import os
import json
from intent_parser import IntentParser

class TestIntentBasedSecurity(unittest.TestCase):
    
    def setUp(self):
        self.parser = IntentParser()

    # --- 1. Dangerous Port Handling Tests ---
    def test_dangerous_port_detection(self):
        print("\n[TEST] Dangerous Port Detection (Telnet)")
        intent = self.parser.parse("Allow access to telnet")
        
        # Check if port 23 is in the rules
        has_port_23 = False
        for rule in intent['spec']['egress']:
            for port in rule['ports']:
                if port['number'] == 23:
                    has_port_23 = True
        self.assertTrue(has_port_23, "Telnet port 23 should be added")
        
        # Check for warning
        self.assertIn('annotations', intent['metadata'])
        self.assertIn('warnings', intent['metadata']['annotations'])
        self.assertIn('Telnet', intent['metadata']['annotations']['warnings'])
        print("✅ PASS: Detected Telnet and issued warning.")

    # --- 2. HTTP / HTTPS Support Tests ---
    def test_web_inference(self):
        print("\n[TEST] HTTP/HTTPS Inference")
        intent = self.parser.parse("Allow access to web services")
        
        ports = set()
        for rule in intent['spec']['egress']:
            for port in rule['ports']:
                ports.add(port['number'])
                
        self.assertIn(80, ports, "Port 80 (HTTP) should be inferred")
        self.assertIn(443, ports, "Port 443 (HTTPS) should be inferred")
        self.assertIn(53, ports, "Port 53 (DNS) should be inferred")
        print("✅ PASS: Inferred HTTP, HTTPS, and DNS from 'web'.")

    # --- 5. Automatic Inference Tests ---
    def test_complex_inference(self):
        print("\n[TEST] Complex Multi-Service Inference")
        intent = self.parser.parse("My app needs database. It also needs email.")
        
        ports = set()
        for rule in intent['spec']['egress']:
            for port in rule['ports']:
                ports.add(port['number'])
        
        # DB (MySQL/Postgres/etc - depends on alias mapping, 'database' maps to multiple)
        # Email (SMTP/IMAP/POP3)
        self.assertTrue(any(p in ports for p in [3306, 5432]), "Database ports should be present")
        self.assertTrue(any(p in ports for p in [25, 587]), "Email ports should be present")
        print("✅ PASS: Inferred Database and Email ports correctly.")

    # --- 6. DNS + Web Traffic Logic (L7) ---
    def test_l7_domain_filtering(self):
        print("\n[TEST] L7 Domain Filtering")
        domain = "api.stripe.com"
        intent = self.parser.parse(f"Allow access to {domain}")
        
        # Check for domain in spec
        found_domain = False
        for rule in intent['spec']['egress']:
            if 'domains' in rule and domain in rule['domains']:
                found_domain = True
                
        self.assertTrue(found_domain, f"Domain '{domain}' should be in the spec")
        
        # Check that DNS is also allowed
        ports = set()
        for rule in intent['spec']['egress']:
            for port in rule['ports']:
                ports.add(port['number'])
        self.assertIn(53, ports, "DNS (Port 53) must be auto-enabled for domains")
        print(f"✅ PASS: Captured domain '{domain}' and enabled DNS.")

if __name__ == '__main__':
    unittest.main(verbosity=0)
