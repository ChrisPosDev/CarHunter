from typing import AsyncIterator
from urllib.parse import urljoin
from selectolax.lexbor import LexborHTMLParser
from ...core.models import Listing
from ...core.exceptions import StrategyError
from ...config.schema import StrategyConfig
from ...extraction.field_mapper import apply_transforms
from ..base import FetchStrategy, register_strategy

@register_strategy("html_css")
class HtmlCssStrategy(FetchStrategy):
    async def extract(self, html: str, config: StrategyConfig, portal_name: str) -> AsyncIterator[Listing]:
        if not config.item_selector:
            raise StrategyError("html_css strategy requires item_selector")

        tree = LexborHTMLParser(html)
        nodes = tree.css(config.item_selector)
        
        if not nodes:
            raise StrategyError(f"No elements found for selector: {config.item_selector}")

        for node in nodes:
            try:
                extracted = {}
                for field_name, dsl in config.fields.items():
                    selector, _, transforms = dsl.partition('|')
                    selector = selector.strip()
                    
                    val = None
                    if selector.startswith('@'):
                        # Attribute on the root item node, e.g., @data-id
                        attr_name = selector[1:]
                        val = node.attributes.get(attr_name)
                    else:
                        # Parse things like "h1 a::text" or "img::attr(src)"
                        target_selector, _, action = selector.partition('::')
                        target_selector = target_selector.strip()
                        action = action.strip()
                        
                        target_node = node.css_first(target_selector) if target_selector else node
                        if target_node:
                            if action == 'text':
                                val = target_node.text(strip=True)
                            elif action.startswith('attr('):
                                attr_name = action[5:-1]
                                val = target_node.attributes.get(attr_name)
                            else:
                                val = target_node.text(strip=True)

                
                    extracted[field_name] = apply_transforms(val, transforms)

                if not extracted.get('id'):
                    continue

                yield Listing(
                    id=str(extracted['id']),
                    portal=portal_name,
                    title=str(extracted.get('title', '')),
                    price=extracted.get('price', 0),
                    url=extracted.get('url', ''),
                    image=extracted.get('image')
                )
            except Exception as e:
                continue
