@@ .. @@
                 if links.count() > 0:
                     self.logger.info(f"Site cible trouvé sur la page {current_page}: {self.target_site}")
                     links.first.scroll_into_view_if_needed()
                     page.wait_for_timeout(random.randint(1000, 2000))
-                    links.first.click()
-                    page.wait_for_load_state("networkidle")
+                    try:
+                        with page.expect_navigation(wait_until="domcontentloaded", timeout=30000):
+                            links.first.click()
+                        # Additional wait for network stability
+                        page.wait_for_load_state("networkidle", timeout=30000)
+                    except Exception as e:
+                        self.logger.warning(f"Navigation error, retrying: {str(e)}")
+                        # Fallback: try direct navigation
+                        href = links.first.get_attribute("href")
+                        if href:
+                            page.goto(href, wait_until="domcontentloaded")
+                            page.wait_for_load_state("networkidle", timeout=30000)
+                            
                     site_found = True
                     
                     if not self.running:
@@ .. @@
                     # Passer à la page suivante si disponible
                     next_button = page.locator('a#pnnext')
                     if next_button.count() > 0:
-                        next_button.first.click()
-                        page.wait_for_load_state("networkidle")
+                        try:
+                            with page.expect_navigation(wait_until="domcontentloaded", timeout=30000):
+                                next_button.first.click()
+                            page.wait_for_load_state("networkidle", timeout=30000)
+                        except Exception as e:
+                            self.logger.warning(f"Next page navigation error: {str(e)}")
+                            break
                         page.wait_for_timeout(random.randint(2000, 4000))
                         current_page += 1
                     else: