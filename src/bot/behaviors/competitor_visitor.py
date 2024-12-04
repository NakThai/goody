"""Competitor site visiting behavior."""
import random
import logging
from typing import Any

class CompetitorVisitor:
    def __init__(self, page: Any, logger: logging.Logger):
        self.page = page
        self.logger = logger
        self.keyword = ""  # Will be set during visit

    def visit_competitors(self, count: int):
        """Visit competitor sites before target site."""
        try:
            # Attendre que les résultats soient chargés
            self.page.wait_for_selector('div#search', state="visible", timeout=10000)
            self.page.wait_for_timeout(random.randint(1000, 2000))

            # Trouver tous les résultats organiques
            organic_results = self.page.locator('div#search div.g:not([data-hveid*="CAA"]) a[href^="http"]')
            visited_count = 0
            
            for i in range(organic_results.count()):
                if visited_count >= count:
                    break
                    
                link = organic_results.nth(i)
                href = link.get_attribute("href")
                
                if href:
                    self.logger.info(f"Visite du concurrent {visited_count + 1}: {href}")
                    self._visit_competitor_site(link)
                    visited_count += 1
                    
            self.logger.info(f"Visite de {visited_count} sites concurrents terminée")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la visite des concurrents: {str(e)}")

    def _visit_competitor_site(self, link: Any):
        """Visit a single competitor site with natural behavior."""
        try:
            # Scroll to link
            link.scroll_into_view_if_needed()
            self.page.wait_for_timeout(random.randint(800, 1500))
            
            # Click and wait for load
            link.click()
            self.page.wait_for_load_state("networkidle", timeout=10000)
            
            # Handle cookie popups after page load
            self._handle_cookie_popup()
            
            # Natural scrolling behavior
            visit_time = random.randint(8000, 15000)
            start_time = self.page.evaluate("() => Date.now()")
            elapsed = 0
            viewport_height = self.page.viewport_size["height"]
            total_height = self.page.evaluate("() => document.body.scrollHeight")
            current_position = 0
            
            while elapsed < visit_time:
                # Calculer la position de défilement actuelle
                current_position = self.page.evaluate("() => window.scrollY")
                
                # Parfois remonter un peu
                if random.random() < 0.2 and current_position > viewport_height:
                    scroll_up = random.randint(100, 300)
                    self.page.mouse.wheel(0, -scroll_up)
                    self.page.wait_for_timeout(random.randint(500, 1000))
                
                # Défilement normal
                scroll_amount = random.randint(100, 300)
                self.page.mouse.wheel(0, scroll_amount)
                self.page.wait_for_timeout(random.randint(200, 400))
                
                # Parfois déplacer la souris
                if random.random() < 0.3:
                    self.page.mouse.move(
                        random.randint(0, self.page.viewport_size["width"]),
                        random.randint(0, viewport_height)
                    )
                    self.page.wait_for_timeout(random.randint(200, 500))
                
                # Pauses aléatoires plus longues
                if random.random() < 0.2:
                    self.page.wait_for_timeout(random.randint(800, 1500))
                
                elapsed = self.page.evaluate("() => Date.now()") - start_time
                
                # Si on atteint le bas de la page, remonter un peu
                if current_position + viewport_height >= total_height:
                    self.page.mouse.wheel(0, -random.randint(300, 500))
                    self.page.wait_for_timeout(random.randint(500, 1000))
                
            # Return to search results using browser back
            self.page.go_back()
            self.page.wait_for_load_state("networkidle", timeout=10000)
            self.page.wait_for_timeout(random.randint(2000, 4000))
            
        except Exception as e:
            self.logger.warning(f"Erreur pendant la visite: {str(e)}")
            # Retry going back
            try:
                self.page.go_back()
                self.page.wait_for_load_state("networkidle", timeout=10000)
            except Exception:
                self.logger.error("Failed to go back, trying history navigation")
                self.page.evaluate("() => window.history.back()")
            
            self.page.wait_for_timeout(random.randint(1000, 2000))
            
    def _handle_cookie_popup(self):
        """Handle cookie popups on competitor sites."""
        try:
            # Common cookie popup selectors
            selectors = [
                'button:has-text("Accepter")',
                'button:has-text("Accept")',
                'button:has-text("Agree")',
                'button:has-text("Accept all")',
                'button:has-text("Accepter tout")',
                'button:has-text("J\'accepte")',
                '#didomi-notice-agree-button',
                '#onetrust-accept-btn-handler',
                '.cc-accept',
                '[aria-label*="cookie" i]',
                'button[id*="cookie" i]',
                'button[class*="cookie" i]',
                '[id*="cookie-accept" i]',
                '[class*="cookie-accept" i]'
            ]
            
            self.page.wait_for_timeout(random.randint(2000, 3000))
            
            for selector in selectors:
                try:
                    button = self.page.locator(selector).first
                    if button.is_visible(timeout=1000):
                        self.logger.info(f"Found cookie button: {selector}")
                        button.click(delay=random.randint(200, 500))
                        self.page.wait_for_timeout(random.randint(1000, 2000))
                        return
                except Exception:
                    continue
                    
            self.logger.info("No cookie popup found or already handled")
            
        except Exception as e:
            self.logger.debug(f"Cookie popup handling error: {str(e)}")
            # Continue even if cookie handling fails