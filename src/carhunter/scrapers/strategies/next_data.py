import json
import re
from typing import AsyncIterator
from urllib.parse import urljoin
from ...core.models import Listing
from ...core.exceptions import StrategyError
from ...config.schema import StrategyConfig
from ...extraction.field_mapper import extract_json_path, apply_transforms
from ..base import FetchStrategy, register_strategy

@register_strategy("next_data")
class NextDataStrategy(FetchStrategy):
    async def extract(self, html: str, config: StrategyConfig, portal_name: str) -> AsyncIterator[Listing]:
        if not config.items_path:
            raise StrategyError("next_data strategy requires items_path")

        m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
        if not m:
            raise StrategyError("__NEXT_DATA__ script not found in HTML")
        
        try:
            data = json.loads(m.group(1))
        except json.JSONDecodeError as e:
            raise StrategyError(f"Failed to parse __NEXT_DATA__ JSON: {e}")

        # Items path might have multiple steps. 
        # For otomoto we know some parts are strings that need json.loads (like urqlState data).
        # We need a custom extraction to handle this specific nested structure, 
        # or we can do it specifically in a robust way.
        # Let's write a targeted robust extractor for the items_path format.
        
        items = extract_json_path(data, config.items_path)
        
        # If the path extraction returned a string instead of dict/list (like urql data), try parsing it
        if isinstance(items, list):
            # Otomoto specific: urqlState has stringified 'data'
            parsed_items = []
            for item in items:
                if isinstance(item, dict) and 'data' in item and isinstance(item['data'], str):
                    try:
                        parsed_data = json.loads(item['data'])
                        # Now we need to find advertSearch.edges inside parsed_data
                        if 'advertSearch' in parsed_data and 'edges' in parsed_data['advertSearch']:
                            parsed_items.extend(parsed_data['advertSearch']['edges'])
                    except:
                        pass
                else:
                    parsed_items.append(item)
            items = parsed_items
        elif items is None:
             raise StrategyError(f"Could not find items at path: {config.items_path}")
        
        if not items:
            return
            
        for item in items:
            try:
                extracted = {}
                for field_name, dsl in config.fields.items():
                    path, _, transforms = dsl.partition('|')
                    path = path.strip()
                    val = extract_json_path(item, path)
                    extracted[field_name] = apply_transforms(val, transforms)

                # Ensure URL is absolute (though Otomoto graphql usually returns absolute)
                url = extracted.get('url', '')

                yield Listing(
                    id=str(extracted['id']),
                    portal=portal_name,
                    title=str(extracted.get('title', '')),
                    price=extracted.get('price', 0),
                    url=url,
                    image=extracted.get('image'),
                    location=extracted.get('location'),
                    mileage=extracted.get('mileage'),
                    year=extracted.get('year')
                )
            except Exception as e:
                # Log error for a specific item but continue
                continue

