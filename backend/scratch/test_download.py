import httpx
import hashlib

def try_download():
    attachment_id = 275
    directory_name = "site_1/0xxx/ef036a7eb94c0b004bf50409053455f2/"
    directory_hash = hashlib.md5(directory_name.encode()).hexdigest()
    
    url = f"http://172.16.1.40/paradigmitindia/index.php?m=attachments&a=getAttachment&id={attachment_id}&directoryNameHash={directory_hash}"
    print(f"Trying to download from: {url}")
    
    try:
        response = httpx.get(url, timeout=10.0)
        print(f"Status Code: {response.status_code}")
        print(f"Content Type: {response.headers.get('Content-Type')}")
        if response.status_code == 200 and "application/pdf" in response.headers.get("Content-Type", ""):
            print("Success! Downloaded PDF.")
            with open("test_download.pdf", "wb") as f:
                f.write(response.content)
        else:
            print("Failed to download or not a PDF.")
            # print(f"Content: {response.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    try_download()
