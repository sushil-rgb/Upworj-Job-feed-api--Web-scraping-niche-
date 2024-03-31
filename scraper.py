from tool import Response, filter, flat
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import asyncio


async def rss_url_lists():
    urls = []
    for page in range(0, 20, 10):
        rss_urls = [
        f"https://www.upwork.com/ab/feed/jobs/rss?paging={page}%3B10&q=web+scraping&sort=recency&subcategory2_uid=531770282593251331&api_params=1&securityToken=9036a5d7ac251defd2cbbdb953be6517dccc8dc88a16442dbe27b213db19c07588315c71fa8e894087e88e44384a7743bf0a75944eecda66f0909750157b2e4d&userUid=1368080374926864384&orgUid=1368080374926864385",
        f"https://www.upwork.com/ab/feed/jobs/rss?paging={page}%3B10&q=web+scraping&sort=recency&api_params=1&securityToken=9036a5d7ac251defd2cbbdb953be6517dccc8dc88a16442dbe27b213db19c07588315c71fa8e894087e88e44384a7743bf0a75944eecda66f0909750157b2e4d&userUid=1368080374926864384&orgUid=1368080374926864385",
        f"https://www.upwork.com/ab/feed/jobs/rss?paging={page}%3B10&q=data+extraction&sort=recency&api_params=1&securityToken=9036a5d7ac251defd2cbbdb953be6517dccc8dc88a16442dbe27b213db19c07588315c71fa8e894087e88e44384a7743bf0a75944eecda66f0909750157b2e4d&userUid=1368080374926864384&orgUid=1368080374926864385",
        f"https://www.upwork.com/ab/feed/jobs/rss?paging={page}%3B10&q=data+scraping&sort=recency&api_params=1&securityToken=9036a5d7ac251defd2cbbdb953be6517dccc8dc88a16442dbe27b213db19c07588315c71fa8e894087e88e44384a7743bf0a75944eecda66f0909750157b2e4d&userUid=1368080374926864384&orgUid=1368080374926864385",
        f"https://www.upwork.com/ab/feed/jobs/rss?q=web+scraping&sort=recency&paging={page}%3B10&api_params=1&securityToken=9036a5d7ac251defd2cbbdb953be6517dccc8dc88a16442dbe27b213db19c07588315c71fa8e894087e88e44384a7743bf0a75944eecda66f0909750157b2e4d&userUid=1368080374926864384&orgUid=1368080374926864385",
        ]
        urls.append(rss_urls)
    return flat(urls)



async def job_alerts(rss_url):
    # source_timezone = pytz.utc
    # target_timezone = pytz.timezone('Asia/Kathmandu')

    job_datas = []
    cont = await Response(rss_url).content()
    soup = BeautifulSoup(cont, 'xml')
    jobs = soup.select('channel')
    for job in jobs:
        for idx in range(10):
            datas = {
                'title': [j.text.strip() for j in job.select('title')[2:]][idx],
                'link': [j.text.strip() for j in job.select('link')[2:]][idx],
                'post_date': [' '.join(j.text.strip().split()[:-2]) for j in job.select('pubDate')][idx],
                # 'post_time': [(source_timezone.localize(datetime.strptime(j.text.strip().split()[-2], "%H:%M:%S"))).astimezone(target_timezone).strftime("%H:%M:%S") for j in job.select('pubDate')][idx],

            }
            job_datas.append(datas)

    return job_datas


async def concurrency():
    urls = await rss_url_lists()
    dfs = []
    coroutines = [job_alerts(url) for url in urls]
    results = await asyncio.gather(*coroutines)

    res = [pd.DataFrame(result) for result in results]
    dff = pd.concat(res)

    length_example = len(dff['title'].values.tolist())

    for idx in range(length_example):
        try:
            datas = {
                "title": (filter(dff['title'].values.tolist()))[idx],
                "link": (filter(dff['link'].values.tolist()))[idx],
                'post_date': (dff['post_date'].values.tolist())[idx],
                # 'post_time': (dff['post_time'].values.tolist())[idx],
            }
            dfs.append(datas)
        except IndexError:
            continue
    return dfs


