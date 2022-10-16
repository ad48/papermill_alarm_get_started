import time
import requests


def wakeup(headers, invocations=10):
    """
    This is a hacky way around the cold-start problem
    - we hit the API with some dummy data and wait for it to return the right number of predictions.
    """
    url = 'https://papermill-alarm.p.rapidapi.com'
    dummy_docs = {'payload':[{'id':'fake id','title':'fake title','abstract':'fake abstract'} for i in range(invocations)]}
    status = 429
    while status!=200:
        # make a POST request to the API
        r = requests.post(url, 
                          headers = headers,
                          json = dummy_docs)
        # if the response code is good, then we return the prediction
        if r.status_code==200:
            if r.json().get('status_code',429)==200:
                if len(r.json().get('message',[]))==invocations:
                    print('Papermill Alarm is awake and working. Beginning to process docs!')
                    status=200
                else:
                    print(f"{len(r.json().get('message',[]))} results in response")
            else:
                print('Status != 200')
        print(f"Response status code: {r.status_code}")
        print(f"PMA response: {r.json().get('status_code')}")
        if status!=200:
            print('Papermill Alarm needs time to wake up. Waiting for 60s.')
            time.sleep(60)
    return True