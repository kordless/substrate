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
    subprocess.run(["playwright", "install-deps"], check=True)
    subprocess.run(["playwright", "install", "chromium"], check=True)
    # return("worked")
    # Record the end time after installation
    end_time = time.time()
    return("huh, getting the error before this")
    installation_time = end_time - start_time

    return("doesn't work either")

    stdout = f"Installation time: {installation_time:.2f} seconds\n"
    stderr = ""
    return stdout
    try:
        with sync_playwright() as p:
            try:
                browser = p.webkit.launch()
                page = browser.new_page()
                page.goto(url)
                content = page.content()
                browser.close()
                stdout += f"Playwright ran successfully. First 1000 characters of content:\n{content[:1000]}"
            except Exception as e:
                stderr = f"Failed to launch browser or navigate to the URL: {str(e)}"
    except Exception as e:
        stderr = f"Error running Playwright: {str(e)}"

    # Ensure to return the o
