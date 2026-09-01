import os
import asyncio
from playwright.async_api import async_playwright
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TELEGRAM_BOT_TOKEN = "8705942752:AAE2kk91ODRJbqKNqvJUg6PipiLsiGWkPvI"
MOBILE_NUMBER = "9381827477" 
USER_NAME = "imran"
SELFIE_PATH = "image1783085563d387c7da850b3fee.jpg"" 
TARGET_SCORE = 4300
SPEED_FACTOR = 2.0  

async def play_game_automation():
    if not os.path.exists(SELFIE_PATH):
        print(f"[!] Image not found: {SELFIE_PATH}")
        return False

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--use-fake-ui-for-media-stream",
                "--use-fake-device-for-media-stream",
                "--disable-dev-shm-usage"
            ]
        )

        context = await browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
            viewport={"width": 375, "height": 812},
            is_mobile=True,
            permissions=["camera"],
        )

        page = await context.new_page()

        try:
            await page.add_init_script(f\"\"\"
                window._forceShot = 0.12;
                Math.random = () => window._forceShot !== undefined ? window._forceShot : Math.random();

                const speedFactor = {SPEED_FACTOR};
                let baseReal = performance.now();
                let baseFake = baseReal;
                const origNow = performance.now.bind(performance);
                performance.now = () => {{
                    const real = origNow();
                    baseFake += (real - baseReal) * speedFactor;
                    baseReal = real;
                    return baseFake;
                }};

                const origDate = Date.now;
                let offset = 0;
                Date.now = () => origDate() + offset;
                setInterval(() => offset += 16 * (speedFactor - 1), 16);

                const origSetTimeout = window.setTimeout;
                const origSetInterval = window.setInterval;
                window.setTimeout = (fn, delay = 0, ...args) => origSetTimeout(fn, delay / speedFactor, ...args);
                window.setInterval = (fn, delay = 0, ...args) => origSetInterval(fn, delay / speedFactor, ...args);
            \"\"\")

            await page.goto("https://bounce.makear.org/")
            await page.wait_for_load_state("domcontentloaded")
            await asyncio.sleep(1.2)

            selectors = [
                "#checkbox", "#acceptButton", "#playGameButton",
                "#parentalOkButton", "#instructionOkButton",
                "button:has-text('Accept')", "button:has-text('Ok')", "button:has-text('Play')"
            ]
            for sel in selectors:
                try:
                    await page.locator(sel).first.click(timeout=1800)
                    await asyncio.sleep(0.3)
                except:
                    pass

            await page.evaluate(f\"\"\"
                () => new Promise(resolve => {{
                    const id = setInterval(() => {{
                        const el = document.querySelector('#score') || document.querySelector('.score') || document.getElementById('currentScore') || document.getElementById('scoreNumber');
                        const score = el ? parseInt(el.innerText.replace(/\\\\D/g,'')) || 0 : 0;
                        if (score >= {TARGET_SCORE}) {{
                            clearInterval(id);
                            window._forceShot = 0.9;
                            resolve();
                        }}
                    }}, 40);
                }})
            \"\"\")

            await page.wait_for_selector("#formScreen", state="visible", timeout=30000)
            await asyncio.sleep(1)

            await page.fill('input[name="name"], #name', USER_NAME)
            await page.fill('input[name="mobile"], #phoneNumber, input[type="tel"]', str(MOBILE_NUMBER))

            try:
                await page.click('input[name="gender"][value="male"]', timeout=2000)
            except:
                await page.locator('text=Male').first.click()

            await page.set_input_files("#galleryInput", SELFIE_PATH)
            await asyncio.sleep(1)

            await page.evaluate(\"\"\"() => {
                const input = document.getElementById('galleryInput');
                if (!input || !input.files || input.files.length === 0) return false;
                const file = input.files[0];
                const event = new Event('change', { bubbles: true });
                input.dispatchEvent(event);
                if (typeof handleFileSelect === 'function') handleFileSelect(file);
                if (window.userData) window.userData.photo = file;
            }\"\"\")
            
            await asyncio.sleep(1.2)
            await page.locator('button[type="submit"]').first.click()
            
            await page.wait_for_selector("#avatarSelectionScreen", state="visible", timeout=25000)
            await page.click("#generateButton")
            await page.wait_for_selector("#userCardScreen", state="visible", timeout=15000)
            await asyncio.sleep(1.5)
            await page.click("#leaderboardButton")
            
            await browser.close()
            return True

        except Exception as e:
            await page.screenshot(path="error_debug.png")
            await browser.close()
            return False

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is online! Send /run to execute.")

async def run_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Starting game automation task...")
    success = await play_game_automation()
    if success:
        await update.message.reply_text("✅ Automation finished successfully!")
    else:
        await update.message.reply_text("❌ Automation failed.")

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("run", run_command))
    app.run_polling()

if __name__ == "__main__":
    main()
