import httpx

origins = [
    "https://dicer.unvisitor.site/store/plugins.json",
    "https://unvisitor.gitee.io/dicer/store/plugins.json",
]


async def get_plugins():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://dicer.unvisitor.site/store/plugins.json")
        result = response.json()

        official = result["official"] if "official" in result.keys() else {}
        community = result["community"] if "community" in result.keys() else {}
        return official, community


async def get_plugins_mixed():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://dicer.unvisitor.site/store/plugins.json")
        result = response.json()

        official = result["official"] if "official" in result.keys() else {}
        community = result["community"] if "community" in result.keys() else {}
        official.update(community)
        return official


async def get_official_plugins():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://dicer.unvisitor.site/store/plugins.json")
        result = response.json()

        return result["official"] if "official" in result.keys() else {}


async def get_community_plugins():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://dicer.unvisitor.site/store/plugins.json")
        result = response.json()

        return result["community"] if "community" in result.keys() else {}


if __name__ == "__main__":
    import asyncio

    print(asyncio.run(get_plugins()))
