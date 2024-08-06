import subprocess
import time

pip_install_strings = ['playwright']

def substrate_function(func):
    func.is_substrate_function = True
    return func

@substrate_function
def test_playwright(url: str):
    from playwright.sync_api import sync_playwright
    
    # Record the start time before installation
    start_time = time.time()
    
    # Install Playwright browser binaries using subprocess
    # Suppress the output of installing dependencies
    subprocess.run(["playwright", "install-deps"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Suppress the output of installing Chromium
    subprocess.run(["playwright", "install", "chromium"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # return("worked")
    # Record the end time after installation
    end_time = time.time()
    # return("works?")
    installation_time = end_time - start_time

    stdout = f"Installation time: {installation_time:.2f} seconds\n"
    stderr = ""

    try:
        with sync_playwright() as p:
            return("works?")
            try:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.goto(url)
                content = page.content()
                browser.close()
                stdout += f"Playwright ran successfully. First 1000 characters of content:\n{content[:1000]}"
            except Exception as e:
                stderr = f"Failed to launch browser or navigate to the URL: {str(e)}"
    except Exception as e:
        stderr = f"Error running Playwright: {str(e)}"

    return stdout, stderr
