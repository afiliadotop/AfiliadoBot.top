"""
Introspect Shopee GraphQL schema to find correct field structure
"""

import sys
import os
import asyncio

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "afiliadohub"))

from dotenv import load_dotenv
load_dotenv()

from api.utils.shopee_client import ShopeeAffiliateClient
import os

async def introspect():
    """Introspects schema to find BrandOffer fields"""
    client = ShopeeAffiliateClient(
        os.getenv("SHOPEE_APP_ID"),
        os.getenv("SHOPEE_SECRET")
    )
    
    try:
        await client.connect()
        
        # Get brandOffer type fields
        print("\n=== Introspecting brandOffer ===")
        query = """
        {
            __type(name: "Query") {
                fields {
                    name
                    type {
                        name
                        kind
                        ofType {
                            name
                            kind
                        }
                    }
                }
            }
        }
        """
        
        result = await client.graphql_query(query)
        if "data" in result:
            fields = result["data"]["__type"]["fields"]
            
            # Find brandOffer
            brand_offer_field = next((f for f in fields if f["name"] == "brandOffer"), None)
            if brand_offer_field:
                print(f"\nbrandOffer type: {brand_offer_field['type']['name']}")
                
                # Get BrandOfferConnection fields
                conn_query = f"""
                {{
                    __type(name: "{brand_offer_field['type']['name']}") {{
                        fields {{
                            name
                            type {{
                                name
                                kind
                                ofType {{
                                    name
                                }}
                            }}
                        }}
                    }}
                }}
                """
                
                conn_result = await client.graphql_query(conn_query)
                if "data" in conn_result and conn_result["data"]["__type"]:
                    print("\nAvailable fields in BrandOfferConnection:")
                    for field in conn_result["data"]["__type"]["fields"]:
                        print(f"  - {field['name']}: {field['type']['name'] or field['type']['ofType']['name']}")
        
        # Try simple brandOffer query
        print("\n=== Testing brandOffer query ===")
        test = """
        {
            brandOffer {
                totalCount
            }
        }
        """
        result = await client.graphql_query(test)
        print(f"Result: {result}")
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(introspect())
