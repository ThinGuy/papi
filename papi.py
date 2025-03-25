#!/usr/bin/env python3
# Ubuntu Project and Package Information (PAPI)
# Revision: 1.0.0

from flask import Flask, request, jsonify, render_template
import requests
import gzip
import io
import concurrent.futures
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def parse_packages_file(content):
    """Parse a Packages file content and extract package information"""
    packages = []
    current_package = {}
    
    for line in content.splitlines():
        if not line.strip():
            if current_package:
                packages.append(current_package)
                current_package = {}
            continue
            
        if ":" in line:
            key, value = line.split(":", 1)
            current_package[key.strip()] = value.strip()
    
    # Add the last package if exists
    if current_package:
        packages.append(current_package)
        
    return packages

def map_entitlement_to_repo_path(entitlement_name):
    """Map API entitlement names to actual repository paths"""
    # Strip "esm-" prefix if present
    if entitlement_name.startswith("esm-"):
        return entitlement_name[4:]
    return entitlement_name

def get_repo_url(repo_type, entitlement, release, pocket, component, arch):
    """Build the repository URL based on the parameters"""
    if repo_type == "esm":
        # Map entitlement if needed
        repo_path = map_entitlement_to_repo_path(entitlement)
        
        # Build URL with the correct suite format
        if pocket:
            if pocket == "release":
                suite = release
            else:
                suite = f"{release}-{entitlement}-{pocket}"
        else:
            suite = release
            
        url = f"https://esm.ubuntu.com/{repo_path}/ubuntu/dists/{suite}/{component}/{arch}"
        
    elif repo_type == "archive":
        # Build URL for archive.ubuntu.com
        if pocket and pocket != "release":
            suite = f"{release}-{pocket}"
        else:
            suite = release
            
        url = f"https://archive.ubuntu.com/ubuntu/dists/{suite}/{component}/{arch}"
        
    elif repo_type == "ports":
        # Build URL for ports.ubuntu.com
        if pocket and pocket != "release":
            suite = f"{release}-{pocket}"
        else:
            suite = release
            
        url = f"https://ports.ubuntu.com/ubuntu-ports/dists/{suite}/{component}/{arch}"
        
    elif repo_type == "cloud":
        # Determine cloud archive format
        if pocket:
            suite = f"{release}-updates/{pocket}"
        else:
            suite = release
            
        url = f"https://ubuntu-cloud.archive.canonical.com/ubuntu/dists/{suite}/{component}/{arch}"
        
    else:
        # Custom repository URL
        if pocket and pocket != "release":
            suite = f"{release}-{pocket}"
        else:
            suite = release
            
        url = f"{repo_type}/dists/{suite}/{component}/{arch}"
    
    return url

def fetch_packages_file(url, token=None):
    """Fetch a Packages.gz file from the repository"""
    headers = {}
    auth = None
    
    # Add authentication for ESM repositories
    if token and "esm.ubuntu.com" in url:
        auth = ("bearer", token)
    
    try:
        # First try Packages.gz
        packages_url = f"{url}/Packages.gz"
        response = requests.get(packages_url, headers=headers, auth=auth, timeout=10)
        
        if response.status_code == 200:
            # Decompress gzip content
            with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as f:
                content = f.read().decode('utf-8')
            return content
        
        # If gzip fails, try uncompressed Packages
        packages_url = f"{url}/Packages"
        response = requests.get(packages_url, headers=headers, auth=auth, timeout=10)
        
        if response.status_code == 200:
            return response.text
            
        # If direct attempts fail, try a directory listing to verify the URL exists
        dir_response = requests.get(url, headers=headers, auth=auth, timeout=10)
        
        if dir_response.status_code == 200:
            return None  # Directory exists but no Packages file
            
        # Log the failed response
        logging.warning(f"Failed to fetch {url}: {response.status_code}")
        return None
        
    except Exception as e:
        logging.error(f"Error fetching {url}: {str(e)}")
        return None

def fetch_sources_file(url, token=None):
    """Fetch a Sources.gz file from the repository"""
    headers = {}
    auth = None
    
    # Add authentication for ESM repositories
    if token and "esm.ubuntu.com" in url:
        auth = ("bearer", token)
    
    try:
        # First try Sources.gz
        sources_url = f"{url}/Sources.gz"
        response = requests.get(sources_url, headers=headers, auth=auth, timeout=10)
        
        if response.status_code == 200:
            # Decompress gzip content
            with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as f:
                content = f.read().decode('utf-8')
            return content
        
        # If gzip fails, try uncompressed Sources
        sources_url = f"{url}/Sources"
        response = requests.get(sources_url, headers=headers, auth=auth, timeout=10)
        
        if response.status_code == 200:
            return response.text
            
        return None
        
    except Exception as e:
        logging.error(f"Error fetching {url}: {str(e)}")
        return None

def calculate_repo_size(repo_type, entitlement, release, pocket, component, arch, token=None):
    """Calculate repository size for a specific combination"""
    url = get_repo_url(repo_type, entitlement, release, pocket, component, arch)
    
    if arch == "source":
        content = fetch_sources_file(url, token)
        index_type = "Sources"
    else:
        content = fetch_packages_file(url, token)
        index_type = "Packages"
    
    if not content:
        return {
            "url": url,
            "exists": False,
            "package_count": 0,
            "total_size_bytes": 0,
            "index_type": index_type
        }
    
    # Parse packages/sources file
    packages = parse_packages_file(content)
    
    # Calculate total size
    if arch == "source":
        # For source packages, we need to sum the size of all files
        total_size = 0
        for pkg in packages:
            files_str = pkg.get("Files", "")
            for file_line in files_str.strip().split("\n"):
                parts = file_line.strip().split()
                if len(parts) >= 3:
                    try:
                        size = int(parts[1])
                        total_size += size
                    except (ValueError, IndexError):
                        pass
    else:
        # For binary packages, use the Size field
        total_size = sum(int(pkg.get("Size", 0)) for pkg in packages)
    
    return {
        "url": url,
        "exists": True,
        "package_count": len(packages),
        "total_size_bytes": total_size,
        "index_type": index_type
    }

def format_size(size_bytes):
    """Format size in bytes to human readable format"""
    if size_bytes == 0:
        return "0 B"
        
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    i = 0
    while size_bytes >= 1024.0 and i < len(units) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.2f} {units[i]}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/estimate', methods=['POST'])
def estimate_size():
    data = request.json
    
    repo_type = data.get('repo_type')
    entitlement = data.get('entitlement')
    release = data.get('release')
    pockets = data.get('pockets', [])
    components = data.get('components', [])
    architectures = data.get('architectures', [])
    token = data.get('token')  # Optional token for ESM repositories
    
    results = []
    total_packages = 0
    total_size = 0
    
    # Use concurrent.futures to parallelize requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_params = {}
        
        # Submit tasks for each combination
        for pocket in pockets:
            for component in components:
                for arch in architectures:
                    future = executor.submit(
                        calculate_repo_size,
                        repo_type, entitlement, release, pocket, component, arch, token
                    )
                    future_to_params[future] = (pocket, component, arch)
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_params):
            pocket, component, arch = future_to_params[future]
            try:
                result = future.result()
                
                if result["exists"]:
                    formatted_size = format_size(result["total_size_bytes"])
                    
                    results.append({
                        "pocket": pocket,
                        "component": component,
                        "architecture": arch,
                        "package_count": result["package_count"],
                        "size": formatted_size,
                        "url": result["url"],
                        "index_type": result["index_type"]
                    })
                    
                    total_packages += result["package_count"]
                    total_size += result["total_size_bytes"]
            except Exception as e:
                logging.error(f"Error processing {pocket}/{component}/{arch}: {str(e)}")
    
    # Sort results by size (largest first)
    results.sort(key=lambda x: x.get("package_count", 0), reverse=True)
    
    return jsonify({
        "config": {
            "repo_type": repo_type,
            "entitlement": entitlement,
            "release": release,
            "pockets": pockets,
            "components": components,
            "architectures": architectures
        },
        "results": results,
        "summary": {
            "total_packages": total_packages,
            "total_size": format_size(total_size),
            "estimated_disk_space": format_size(total_size * 1.2)  # 20% overhead
        }
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
