import backoff
import requests

def abstract_from_oa_response(data):
    inv_abst = data['abstract_inverted_index']
    if inv_abst:
        total = max(max(inv_abst[word]) for word in inv_abst)
        lst_abst = [''] * (total + 10)
        # loop through the dictionary and place each word in their position
        for word in inv_abst:
            for position in inv_abst[word]:
                
                try:
                    lst_abst[position] = word
                except:
#                     print(position,word, len(lst_abst))
                    # assert 1==2
                    pass

        # convert the list of words into a string and there you go!
        abstract = " ".join(lst_abst)
        return abstract


def check_response(r):
    if r.status_code!=200:
        return True
    if r.elapsed.seconds>3:
        return True
    return False

@backoff.on_predicate(
    backoff.expo,
    predicate=lambda r: check_response(r),
    )
@backoff.on_exception(backoff.expo,(requests.exceptions.Timeout,
                                    requests.exceptions.ConnectionError),
                      max_tries=8,
                      max_time=60
                     )
def openalex_issn_query(issn,cursor,email):
    url = f'https://api.openalex.org/works?filter=host_venue.issn:{issn}&per-page=100&cursor={cursor}&mailto={email}'
    return requests.get(url)
    

def openalex_from_issn(issn, email):
    ## to prevent the fn from running in an endless loop, set a max # of iterations.
    ## note that doing so might mean we lose results
    ## we are getting 100 rows at a time, so 1000 iterations will stop at 100,000 results etc
    max_iter = 2000
    
    cursor = '*'
    count = 1
    results_count = 0
    iter_count = 0
    last3lens = []
    while results_count < count and iter_count<max_iter:
        r = openalex_issn_query(issn,cursor,email)
        data = r.json()
        results = data['results']
        results_count+=len(results)
        cursor = data['meta']['next_cursor']
        count = data['meta']['count']
        yield results
        last3lens = last3lens.append(len(results))[:3]
        if sum(last3lens)==0:
            print('Last 3 requests returned nothing. Breaking request loop!')
            break
        iter_count+=1
        if iter_count>=max_iter:
            print('Maximum iterations reached for this journal. Breaking request loop.')
        
            