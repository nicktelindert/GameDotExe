import requests
import os
import json
import datetime
from PySide6.QtCore import QCoreApplication

class MetadataProvider:
    def fetch_metadata(self, game_name):
        raise NotImplementedError

    def search_matches(self, game_name):
        raise NotImplementedError

class PCGamingWikiProvider(MetadataProvider):
    BASE_URL = "https://www.pcgamingwiki.com/w/api.php"

    def __init__(self, log_path=None, cache_dir=None):
        self.log_path = log_path
        self.headers = {'User-Agent': 'GameDotExe/1.0 (MS-DOS Launcher; +https://github.com/nick/GameDotExe)'}
        self.cache_file = os.path.join(cache_dir, "pcgw_cache.json") if cache_dir else None
        self.cache = {"search": {}, "metadata": {}}
        self._load_cache()

    def _load_cache(self):
        if self.cache_file and os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r") as f:
                    self.cache = json.load(f)
            except Exception: pass

    def _save_cache(self):
        if self.cache_file:
            try:
                with open(self.cache_file, "w") as f:
                    json.dump(self.cache, f)
            except Exception: pass

    def _log(self, message, data):
        if not self.log_path:
            return
        try:
            with open(self.log_path, "a") as f:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] {message}:\n")
                if isinstance(data, (dict, list)):
                    f.write(json.dumps(data, indent=2))
                else:
                    f.write(str(data))
                f.write("\n" + "="*50 + "\n")
        except Exception as e:
            print(f"Logging error: {e}")

    def search_matches(self, game_name):
        """Geeft een lijst met mogelijke pagina-titels terug."""
        if game_name in self.cache["search"]:
            return self.cache["search"][game_name]

        try:
            search_params = {
                "action": "query",
                "list": "search",
                "srsearch": f"{game_name}",
                "format": "json"
            }
            res = requests.get(self.BASE_URL, params=search_params, timeout=5, headers=self.headers)
            self._log(f"Search request URL for '{game_name}'", res.url)
            
            if res.status_code != 200:
                self._log(f"API Error: HTTP {res.status_code}", res.text)
                return []
                
            response = res.json()
            self._log(f"Search matches for '{game_name}'", response)
            
            search_results = response.get("query", {}).get("search", [])
            titles = [result["title"] for result in search_results]
            self.cache["search"][game_name] = titles
            self._save_cache()
            return titles
        except Exception as e:
            print(f"Search error: {e}")
            return []

    def fetch_metadata(self, page_title):
        """Haalt de specifieke metadata op voor een geselecteerde titel."""
        if page_title in self.cache["metadata"]:
            return self.cache["metadata"][page_title]

        # Use translate for standard statuses
        unknown_str = QCoreApplication.translate("MetadataProvider", "Unknown")
        playable_str = QCoreApplication.translate("MetadataProvider", "Playable (PCGW)")
        metadata = {"icon_url": None, "compatibility": unknown_str, "release_date": unknown_str}
        try:
            # Haal release datum en de bestandsnaam van de afbeelding op via Cargo
            cargo_params = {
                "action": "cargoquery",
                "tables": "Infobox_game",
                "fields": "Released, Cover",
                "where": f'_pageName="{page_title}"',
                "format": "json"
            }
            res = requests.get(self.BASE_URL, params=cargo_params, timeout=5, headers=self.headers)
            self._log(f"Cargo request URL for '{page_title}'", res.url)
            
            if res.status_code != 200:
                self._log(f"Cargo API Error: HTTP {res.status_code}", res.text)
                return metadata
                
            cargo_res = res.json()
            self._log(f"Cargo response for '{page_title}'", cargo_res)
            
            cargo_data = cargo_res.get("cargoquery", [])
            if cargo_data:
                title_data = cargo_data[0].get("title", {})
                metadata["release_date"] = title_data.get("Released") or unknown_str
                # Als er meerdere releasedata zijn (gescheiden door ';'), pak de eerste
                if isinstance(metadata["release_date"], str) and ';' in metadata["release_date"]:
                    metadata["release_date"] = metadata["release_date"].split(';')[0].strip()
                image_file = title_data.get("Cover")
                
                if image_file:
                    # Resolve de bestandsnaam naar een publieke URL (thumbnail van 256px breed)
                    img_info_params = {
                        "action": "query",
                        "titles": f"File:{image_file}",
                        "prop": "imageinfo",
                        "iiprop": "url",
                        "iiurlwidth": "256",
                        "format": "json"
                    }
                    res = requests.get(self.BASE_URL, params=img_info_params, timeout=5, headers=self.headers)
                    self._log(f"Image info request URL for '{image_file}'", res.url)
                    
                    if res.status_code != 200:
                        self._log(f"Image Info API Error: HTTP {res.status_code}", res.text)
                        return metadata
                        
                    img_info_data = res.json()
                    self._log(f"Image info response", img_info_data)
                    
                    pages = img_info_data.get("query", {}).get("pages", {})
                    for p in pages.values():
                        if "imageinfo" in p:
                            # Gebruik thumburl (de gegenereerde thumbnail) indien beschikbaar
                            metadata["icon_url"] = p["imageinfo"][0].get("thumburl", p["imageinfo"][0].get("url"))

            metadata["compatibility"] = playable_str
            self.cache["metadata"][page_title] = metadata
            self._save_cache()
        except Exception as e:
            print(f"Metadata error: {e}")
        return metadata