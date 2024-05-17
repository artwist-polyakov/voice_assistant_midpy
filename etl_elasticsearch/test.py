from configs.settings import ElasticSettings, settings
from elasticsearch import Elasticsearch


def get_all_documents():
    """
    Получает все документы из индекса Elasticsearch.

    Returns:
    list: Список всех документов из индекса.
    """
    elastic_settings = ElasticSettings()
    index_name = settings.elastic_movies_index
    query = {
        "query": {
            "match_all": {}
        }
    }
    url = (f"{elastic_settings.hosts[0].scheme}://"
           f"{elastic_settings.hosts[0].host}:{elastic_settings.hosts[0].port}")

    es = Elasticsearch(
        [url],
        request_timeout=elastic_settings.timeout,
        max_retries=elastic_settings.max_retries,
        retry_on_timeout=elastic_settings.retry_on_timeout
    )

    result = es.search(index=index_name, body=query, scroll='1m', size=1000)

    all_documents = []
    hits = result['hits']['hits']
    scroll_id = result['_scroll_id']
    all_documents.extend(hits)
    while hits:
        result = es.scroll(scroll_id=scroll_id, scroll='1m')
        hits = result['hits']['hits']
        all_documents.extend(hits)
    return all_documents


if __name__ == "__main__":
    all_documents = get_all_documents()
    print(f"Total documents retrieved: {len(all_documents)}")
    for doc in all_documents:
        print(doc)
