sc_private_miner server impl

URL: -

# doc

- GET /random_private_url
  query params: - is_small: int (0, 1)
- GET /urls
  query params: - page_size: int - cursor: str? - is_small: int (0, 1)
- POST /url
  body: - { url: str, sender_name: str, follower_count: int, artist_name: str, title: str? }
- POST /small_url
  body: - { url: str, sender_name: str, follower_count: int, artist_name: str, title: str? }

# self-hosting

example:

```
gcloud run deploy sc-private-miner --source . --project sc-private-miner --region asia-northeast1
```
