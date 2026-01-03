#!/usr/bin/env python3
"""
DEEPSEE Google Meet Bot
Optimized for Colab - Fast Execution
"""

import asyncio
import random
import time
from typing import Optional
from playwright.async_api import async_playwright, Page, Browser

class DeepSeeBot:
    """Main bot class for Google Meet automation"""
    
    def __init__(self, user_name: str):
        self.user_name = user_name
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.is_joined = False
        
    async def setup_browser(self):
        """Setup browser with optimized settings"""
        browser_args = [
            '--disable-blink-features=AutomationControlled',
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--mute-audio',
            '--use-fake-ui-for-media-stream',
            '--use-fake-device-for-media-stream',
            '--disable-web-security',
            '--disable-features=IsolateOrigins,site-per-process',
            '--disable-background-timer-throttling',
            '--disable-renderer-backgrounding',
            '--disable-backgrounding-occluded-windows',
            '--disable-component-update',
            '--disable-default-apps',
            '--disable-extensions',
            '--disable-sync',
            '--disable-translate',
            '--no-default-browser-check',
            '--no-first-run',
            '--disable-dev-shm-usage',
        ]
        
        p = await async_playwright().start()
        
        self.browser = await p.chromium.launch(
            headless=True,  # True for Colab (faster)
            args=browser_args,
            ignore_default_args=[
                '--enable-automation',
                '--enable-blink-features'
            ]
        )
        
        # Create context with realistic settings
        context = await self.browser.new_context(
            viewport={'width': 1366, 'height': 768},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            permissions=['microphone', 'camera'],
            locale='en-US',
            timezone_id='Asia/Kolkata'
        )
        
        self.page = await context.new_page()
        
        # Set timeouts
        self.page.set_default_timeout(30000)
        self.page.set_default_navigation_timeout(30000)
        
        # Random mouse movements to appear human
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
    
    async def join_meeting(self, meeting_code: str, passcode: str = ""):
        """Join Google Meet meeting"""
        try:
            print(f"👤 [{self.user_name}] Joining meeting: {meeting_code}")
            
            # Navigate to Google Meet
            url = f"https://meet.google.com/{meeting_code}"
            await self.page.goto(url, wait_until="domcontentloaded")
            await asyncio.sleep(2)
            
            # Enter passcode if provided
            if passcode:
                try:
                    passcode_input = await self.page.wait_for_selector(
                        'input[type="password"]', 
                        timeout=5000
                    )
                    if passcode_input:
                        await passcode_input.fill(passcode)
                        await self.page.keyboard.press('Enter')
                        await asyncio.sleep(2)
                        print(f"   [{self.user_name}] Passcode entered")
                except:
                    pass
            
            # Try multiple join button selectors
            join_selectors = [
                'div[role="button"][aria-label*="join" i]',
                'button:has-text("Ask to join")',
                'button:has-text("Join now")',
                'div[jsname="Qx7uuf"]',
                'button[data-initial-active="false"]',
                'button[aria-label*="request to join" i]',
                'button:has-text("طلب الانضمام")',  # Arabic
                'button:has-text("参加をリクエスト")',  # Japanese
            ]
            
            joined = False
            for selector in join_selectors:
                try:
                    join_button = await self.page.wait_for_selector(
                        selector, 
                        timeout=3000
                    )
                    if join_button:
                        await join_button.click()
                        await asyncio.sleep(2)
                        print(f"   [{self.user_name}] Clicked join button")
                        joined = True
                        break
                except:
                    continue
            
            if not joined:
                # Try clicking by coordinates as fallback
                try:
                    await self.page.mouse.click(600, 500)
                    await asyncio.sleep(1)
                except:
                    pass
            
            # Turn off microphone and camera for faster performance
            try:
                mic_button = await self.page.wait_for_selector(
                    'button[aria-label*="microphone" i]',
                    timeout=3000
                )
                if mic_button:
                    await mic_button.click()
                    await asyncio.sleep(0.5)
                    print(f"   [{self.user_name}] Microphone muted")
            except:
                pass
            
            try:
                cam_button = await self.page.wait_for_selector(
                    'button[aria-label*="camera" i]',
                    timeout=3000
                )
                if cam_button:
                    await cam_button.click()
                    await asyncio.sleep(0.5)
                    print(f"   [{self.user_name}] Camera turned off")
            except:
                pass
            
            self.is_joined = True
            print(f"✅ [{self.user_name}] Successfully joined meeting!")
            return True
            
        except Exception as e:
            print(f"❌ [{self.user_name}] Failed to join: {str(e)}")
            return False
    
    async def stay_in_meeting(self, minutes: int):
        """Stay in meeting for specified minutes"""
        if not self.is_joined:
            return
        
        seconds = minutes * 60
        print(f"⏳ [{self.user_name}] Staying for {minutes} minutes...")
        
        # Check periodically if still in meeting
        check_interval = 30  # Check every 30 seconds
        
        for i in range(0, seconds, check_interval):
            if not self.is_joined:
                break
            
            # Random small activities to appear active
            if random.random() < 0.1:  # 10% chance
                try:
                    # Move mouse randomly
                    x = random.randint(100, 1200)
                    y = random.randint(100, 600)
                    await self.page.mouse.move(x, y)
                except:
                    pass
            
            remaining = (seconds - i) // 60
            if i > 0 and i % 300 == 0:  # Every 5 minutes
                print(f"   [{self.user_name}] Still in meeting ({remaining} min remaining)")
            
            await asyncio.sleep(check_interval)
    
    async def leave_meeting(self):
        """Leave the meeting"""
        if not self.is_joined:
            return
        
        try:
            # Try to find leave button
            leave_selectors = [
                'button[aria-label*="leave" i]',
                'button[aria-label*="خروج" i]',  # Arabic
                'button[aria-label*="退席" i]',  # Japanese
                'button:has-text("Leave call")',
                'button:has-text("خروج من المكالمة")',
            ]
            
            for selector in leave_selectors:
                try:
                    leave_button = await self.page.wait_for_selector(
                        selector, 
                        timeout=3000
                    )
                    if leave_button:
                        await leave_button.click()
                        await asyncio.sleep(2)
                        break
                except:
                    continue
            
            print(f"👋 [{self.user_name}] Left the meeting")
            
        except Exception as e:
            print(f"⚠️ [{self.user_name}] Error leaving: {str(e)}")
        finally:
            self.is_joined = False
    
    async def close(self):
        """Close browser and cleanup"""
        try:
            if self.browser:
                await self.browser.close()
                print(f"🔒 [{self.user_name}] Browser closed")
        except:
            pass

async def start(user_name: str, stay_minutes: int, meeting_code: str, passcode: str = ""):
    """
    Main function to start bot - This is called from Colab
    
    Args:
        user_name: Name to display
        stay_minutes: Minutes to stay in meeting
        meeting_code: Google Meet code
        passcode: Meeting passcode (optional)
    """
    bot = DeepSeeBot(user_name)
    
    try:
        # Setup browser
        await bot.setup_browser()
        
        # Join meeting
        success = await bot.join_meeting(meeting_code, passcode)
        
        if success:
            # Stay for specified time
            await bot.stay_in_meeting(stay_minutes)
            
            # Leave meeting
            await bot.leave_meeting()
        else:
            print(f"⚠️ [{user_name}] Skipping stay time due to join failure")
        
    except Exception as e:
        print(f"🚨 [{user_name}] Critical error: {str(e)}")
    
    finally:
        # Always cleanup
        await bot.close()

# For testing locally
async def local_test():
    """Test function for local testing"""
    print("🧪 Local test mode")
    
    meeting_code = input("Enter meeting code: ").strip()
    passcode = input("Enter passcode (if any): ").strip()
    
    test_user = "Test User"
    stay_time = 2  # 2 minutes for testing
    
    await start(test_user, stay_time, meeting_code, passcode)

if __name__ == "__main__":
    # Run local test if file executed directly
    asyncio.run(local_test())
