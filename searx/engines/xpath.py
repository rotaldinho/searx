from lxml import html
from urllib.parse import urlencode
from searx.utils import extract_text, extract_url, eval_xpath

search_url = None
url_xpath = None
content_xpath = None
title_xpath = None
thumbnail_xpath = False
paging = False
suggestion_xpath = ''
results_xpath = ''

# parameters for engines with paging support
#
# number of results on each page
# (only needed if the site requires not a page number, but an offset)
page_size = 1
# number of the first page (usually 0 or 1)
first_page_num = 1


def request(query, params):
    query = urlencode({'q': query})[2:]

    fp = {'query': query}
    if paging and search_url.find('{pageno}') >= 0:
        fp['pageno'] = (params['pageno'] - 1) * page_size + first_page_num

    params['url'] = search_url.format(**fp)
    params['query'] = query

    return params


def response(resp):
    results = []
    dom = html.fromstring(resp.text)
    if results_xpath:
        for result in eval_xpath(dom, results_xpath):
            url = extract_url(eval_xpath(result, url_xpath), search_url)
            title = extract_text(eval_xpath(result, title_xpath))
            content = extract_text(eval_xpath(result, content_xpath))
            tmp_result = {'url': url, 'title': title, 'content': content}

            # add thumbnail if available
            if thumbnail_xpath:
                thumbnail_xpath_result = eval_xpath(result, thumbnail_xpath)
                if len(thumbnail_xpath_result) > 0:
                    tmp_result['img_src'] = extract_url(thumbnail_xpath_result, search_url)

            results.append(tmp_result)
    else:
        for url, title, content in zip(
            (extract_url(x, search_url) for
             x in eval_xpath(dom, url_xpath)),
            map(extract_text, eval_xpath(dom, title_xpath)),
            map(extract_text, eval_xpath(dom, content_xpath))
        ):
            results.append({'url': url, 'title': title, 'content': content})

    if not suggestion_xpath:
        return results
    for suggestion in eval_xpath(dom, suggestion_xpath):
        results.append({'suggestion': extract_text(suggestion)})
    return results
