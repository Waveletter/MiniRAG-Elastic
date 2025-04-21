
import elasticsearch

from info import ES_Info
import logging
import requests

def main():

    #logging.basicConfig(level=logging.DEBUG)

    print(ES_Info.host.value, ES_Info.credentials.value, ES_Info.api_key.value)
    es = elasticsearch.Elasticsearch(
        ES_Info.host.value,
        verify_certs=False,
        ssl_show_warn=False,
        api_key=ES_Info.api_key.value
    )

    if es.ping():
        print("Connection successful")
    else:
        print("No connection")

    print(es.info())

    url = f"{ES_Info.host.value}/test_index"
    headers = {
        "Authorization": f"ApiKey {ES_Info.api_key.value}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers, verify=False)
    print(response.status_code, response.text)


if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        print(ex)