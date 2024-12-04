"""Browser fingerprint masking utilities."""
from typing import Any
import random

class FingerprintMasker:
    def __init__(self, page: Any):
        self.page = page
        
    def apply_masks(self):
        """Apply all fingerprint masks randomly."""
        self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            window.chrome = { runtime: {} };
        """)
        
        masks = [
            self._mask_webgl,
            self._mask_canvas,
            self._mask_audio,
            self._mask_hardware,
            self._mask_navigator
        ]
        
        for mask in masks:
            if random.choice([True, False]):
                mask()
                
    def _mask_webgl(self):
        """Mask WebGL fingerprint."""
        self.page.evaluate("""() => {
            try {
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) {
                        return 'Google Inc. (NVIDIA)';
                    }
                    if (parameter === 37446) {
                        return 'ANGLE (NVIDIA, NVIDIA GeForce GTX 1070 Direct3D11 vs_5_0 ps_5_0)';
                    }
                    return getParameter.apply(this, arguments);
                };
            } catch (e) {
                console.debug('WebGL masking failed:', e);
            }
        }""")
        
        self.page.evaluate("""() => {
            try {
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => false
                });
            } catch (e) {
                console.debug('Webdriver masking failed:', e);
            }
        }""")
        
        self.page.evaluate("""() => {
            try {
                window.chrome = {
                    runtime: {},
                    loadTimes: function() {},
                    csi: function() {},
                    app: {}
                };
            } catch (e) {
                console.debug('Chrome API masking failed:', e);
            }
        }""")
        
    def _mask_canvas(self):
        """Mask Canvas fingerprint."""
        self.page.evaluate("""() => {
            const original = HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL = function(type) {
                if (type === 'image/png' && this.width === 220 && this.height === 30) {
                    return 'data:image/png;base64,';
                }
                return original.apply(this, arguments);
            };
        }""")
        
    def _mask_audio(self):
        """Mask AudioContext fingerprint."""
        self.page.evaluate("""() => {
            const audioContext = window.AudioContext || window.webkitAudioContext;
            if (audioContext) {
                const original = audioContext.prototype.createOscillator;
                audioContext.prototype.createOscillator = function() {
                    const result = original.apply(this, arguments);
                    result.frequency.value = Math.random() * 1000;
                    return result;
                };
            }
        }""")
        
    def _mask_hardware(self):
        """Mask hardware information."""
        self.page.evaluate("""() => {
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                value: 8
            });
            Object.defineProperty(navigator, 'deviceMemory', {
                value: 8
            });
        }""")
        
    def _mask_navigator(self):
        """Mask navigator properties."""
        self.page.evaluate("""() => {
            Object.defineProperty(navigator, 'platform', {
                value: 'Win32'
            });
            Object.defineProperty(navigator, 'language', {
                value: 'fr-FR'
            });
        }""")