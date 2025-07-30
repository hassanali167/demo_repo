#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re
import sys

def detect_technologies(url):
    # Ensure URL format
    if not url.startswith("http"):
        url = "http://" + url

    print(f"[*] Analyzing {url} ...")

    try:
        response = requests.get(url, timeout=10)
        headers = response.headers
        content = response.text
    except Exception as e:
        print(f"[!] Error fetching URL: {e}")
        return

    tech_stack = {
        "Web Server": None,
        "Backend Language": None,
        "CMS": None,
        "JavaScript Frameworks": [],
        "Database": None
    }

    # Detect Web Server
    if "Server" in headers:
        tech_stack["Web Server"] = headers["Server"]

    # Detect Backend Language
    if "X-Powered-By" in headers:
        powered_by = headers["X-Powered-By"].lower()
        if "php" in powered_by:
            tech_stack["Backend Language"] = "PHP"
        elif "asp" in powered_by or ".net" in powered_by:
            tech_stack["Backend Language"] = "ASP.NET"
        elif "python" in powered_by:
            tech_stack["Backend Language"] = "Python"
        elif "java" in powered_by:
            tech_stack["Backend Language"] = "Java"

    # CMS Detection (from meta tags and HTML content)
    if re.search(r'wp-content|wordpress', content, re.I):
        tech_stack["CMS"] = "WordPress"
    elif re.search(r'joomla', content, re.I):
        tech_stack["CMS"] = "Joomla"
    elif re.search(r'drupal', content, re.I):
        tech_stack["CMS"] = "Drupal"

    # Detect JavaScript frameworks
    js_frameworks = {
        "React": r'react',
        "Angular": r'angular',
        "Vue.js": r'vue(\.js)?',
        "jQuery": r'jquery'
    }
    for name, pattern in js_frameworks.items():
        if re.search(pattern, content, re.I):
            tech_stack["JavaScript Frameworks"].append(name)

    # Database guess (based on hints in HTML or powered-by)
    if re.search(r'mysql|mariadb', content, re.I):
        tech_stack["Database"] = "MySQL/MariaDB"
    elif re.search(r'postgresql|pgsql', content, re.I):
        tech_stack["Database"] = "PostgreSQL"
    elif re.search(r'mongodb', content, re.I):
        tech_stack["Database"] = "MongoDB"

    # Parse meta tags for generator info
    soup = BeautifulSoup(content, "html.parser")
    for meta in soup.find_all("meta"):
        if meta.get("name", "").lower() == "generator":
            tech_stack["CMS"] = meta.get("content")

    print("\n[+] Technology Stack Detected:")
    for key, value in tech_stack.items():
        print(f"- {key}: {value if value else 'Not Detected'}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <domain>")
        sys.exit(1)
    
    domain = sys.argv[1]
    detect_technologies(domain)
