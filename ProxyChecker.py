import asyncio
import aiohttp
import os
from colorama import Fore, Style, init


init(autoreset=True)

working_proxies = []
file_lock = asyncio.Lock()

async def main():

    url = input("e.g. https://Http,Https,Socks4,Socks5.txt : ")
    proxy_type = input("Proxy type (e.g. http, https, socks4, socks5): ")


    output_file_name = f"{proxy_type}.txt"
    output_file_path = os.path.join(os.getcwd(), output_file_name)

    proxies = await get_proxies_from_url(url)

    print(f"Retrieved {len(proxies)} proxies from the URL.")

    tasks = [check_proxy(proxy, proxy_type, output_file_path) for proxy in proxies]
    await asyncio.gather(*tasks)

    print("All checks completed.")
    print(f"{len(working_proxies)} proxies work! Saved as: {output_file_path}")

async def get_proxies_from_url(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                content = await response.text()
                return content.splitlines()
    except Exception as ex:
        print(f"Error retrieving proxies: {ex}")
        return []

async def check_proxy(proxy, proxy_type, file_name):
    try:
        if ':' not in proxy:
            print(f"Invalid proxy format: {proxy}")
            return

        proxy_url = f"{proxy_type}://{proxy}"

        async with aiohttp.ClientSession() as session:
            async with session.get("https://ipwho.is/", proxy=proxy_url) as response:
                if response.status == 200:
                    data = await response.json()
                    country_code = data['country_code']
                    country = data['country']
                    city = data['city']

             
                    print(f"{Fore.GREEN}{proxy}{Style.RESET_ALL} - {Fore.BLUE}{country_code}{Style.RESET_ALL} - {Fore.YELLOW}{country}, {city}{Style.RESET_ALL}")

                    async with file_lock:
                        with open(file_name, 'a') as f:
                            f.write(proxy + '\n')

                    working_proxies.append(proxy)
                else:
                    print(f"Proxy failed: {proxy} - Status Code: {response.status}")
    except Exception as ex:
        pass  
       

if __name__ == "__main__":
    asyncio.run(main())
