# trail.py में ये modifications करें:

import asyncio
from playwright.async_api import async_playwright
import time

async def start(user, stay_time, meetingcode, passcode):
    """Optimized version of start function"""
    
    # OPTIMIZATION 1: Use faster browser context settings
    browser_args = [
        '--disable-blink-features=AutomationControlled',
        '--disable-dev-shm-usage',
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-accelerated-2d-canvas',
        '--disable-gpu',
        '--disable-features=IsolateOrigins,site-per-process',
        '--disable-web-security',
        '--disable-features=VizDisplayCompositor',
        '--disable-background-timer-throttling',
        '--disable-backgrounding-occluded-windows',
        '--disable-renderer-backgrounding',
        '--disable-background-networking',
        '--disable-component-update',
        '--disable-default-apps',
        '--disable-extensions',
        '--disable-sync',
        '--disable-translate',
        '--mute-audio',
        '--no-default-browser-check',
        '--no-first-run',
        '--use-fake-ui-for-media-stream',
        '--use-fake-device-for-media-stream',
    ]
    
    async with async_playwright() as p:
        # OPTIMIZATION 2: Launch browser with headless for speed
        browser = await p.chromium.launch(
            headless=True,  # Headless is faster
            args=browser_args,
            ignore_default_args=[
                '--enable-automation',
                '--enable-blink-features'
            ]
        )
        
        # OPTIMIZATION 3: Create context with reduced resources
        context = await browser.new_context(
            viewport={'width': 1366, 'height': 768},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            permissions=['microphone', 'camera'],
            # Reduce timeouts for faster navigation
            default_timeout=30000
        )
        
        page = await context.new_page()
        
        try:
            # OPTIMIZATION 4: Set faster navigation timeouts
            page.set_default_timeout(30000)
            page.set_default_navigation_timeout(30000)
            
            print(f"👉 {user} joining...")
            
            # Navigate to Google Meet
            await page.goto(f"https://meet.google.com/{meetingcode}", wait_until="domcontentloaded")
            
            # Wait for page to load (reduced time)
            await page.wait_for_timeout(2000)
            
            # OPTIMIZATION 5: Combine multiple actions
            # Enter passcode if required
            if passcode:
                try:
                    await page.fill('input[type="password"]', passcode, timeout=5000)
                    await page.keyboard.press('Enter')
                    await page.wait_for_timeout(1000)
                except:
                    pass
            
            # Click on "Ask to join" or similar button
            join_selectors = [
                'div[role="button"][aria-label*="join" i]',
                'button:has-text("Ask to join")',
                'button:has-text("Join now")',
                'div[jsname="Qx7uuf"]',
                'button[aria-label*="join" i]'
            ]
            
            for selector in join_selectors:
                try:
                    await page.click(selector, timeout=2000)
                    break
                except:
                    continue
            
            # Turn off mic and camera for faster join
            try:
                await page.click('button[aria-label*="microphone" i]', timeout=2000)
                await page.wait_for_timeout(500)
                await page.click('button[aria-label*="camera" i]', timeout=2000)
            except:
                pass
            
            print(f"✅ {user} joined successfully")
            
            # Wait for specified time
            await asyncio.sleep(stay_time)
            
            # Leave meeting
            await page.click('button[aria-label*="leave" i]', timeout=5000)
            print(f"👋 {user} left after {stay_time//60} minutes")
            
        except Exception as e:
            print(f"❌ {user} error: {str(e)}")
        finally:
            # OPTIMIZATION 6: Faster cleanup
            await browser.close()
