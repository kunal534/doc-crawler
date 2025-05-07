import re
from typing import List, Dict

class OutputCleaner:
    def clean_output(self, modules: List[Dict]) -> List[Dict]:
        """Clean and deduplicate module data"""
        cleaned_modules = []
        seen_modules = set()
        seen_submodules = {}

        for module in modules:
            module_name = module["module"]
            if module_name in seen_modules:
                continue
            seen_modules.add(module_name)

            # Clean module description
            description = re.sub(r'\s+', ' ', module["Description"].strip())
            description = re.sub(r'[^\x00-\x7F]+', '', description)  # Remove non-ASCII

            # Clean and deduplicate submodules
            cleaned_submodules = {}
            for sub_name, sub_desc in module["Submodule"].items():
                # Clean submodule name
                sub_name = re.sub(r'[^\x00-\x7F]+', '', sub_name)  # Remove soft hyphens
                sub_name = re.sub(r'\s+', ' ', sub_name.strip())
                if not sub_name or sub_name.lower() in ["untitled", "manage apps", ""]:
                    continue

                # Split concatenated titles
                if len(sub_name) > 30 or any(x in sub_name for x in ["Windows", "MacOS", "Contracts", "Agent"]):
                    # Split on camel case or common separators
                    parts = re.split(r'(?<!\s)([A-Z][a-z]+)|[\/\-\s]+', sub_name)
                    sub_name = next((part.strip() for part in parts if part and len(part.strip()) > 2), sub_name)
                    if not sub_name:
                        continue

                # Clean submodule description
                sub_desc = re.sub(r'\s+', ' ', sub_desc.strip())
                sub_desc = re.sub(r'[^\x00-\x7F]+', '', sub_desc)
                if not sub_desc or sub_desc == sub_name:
                    sub_desc = f"Details for {sub_name}"

                # Deduplicate submodules
                sub_key = f"{module_name}:{sub_name}"
                if sub_key not in seen_submodules:
                    seen_submodules[sub_key] = sub_desc
                    cleaned_submodules[sub_name] = sub_desc
                elif len(sub_desc) > len(seen_submodules[sub_key]):
                    # Update with more detailed description if available
                    seen_submodules[sub_key] = sub_desc
                    cleaned_submodules[sub_name] = sub_desc

            # Add cleaned module
            cleaned_module = {
                "module": module_name,
                "Description": description[:100] + "..." if len(description) > 100 else description,
                "Submodule": cleaned_submodules
            }
            cleaned_modules.append(cleaned_module)

        return cleaned_modules