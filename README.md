kafka-streaming
===

## Prerequites
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- Create python virtual env:
```bash
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

## Development guides
- Edit config file `config/app-config.yaml` to update configurations for tasks and kafka.
- Run the program:
```bash
$ make docker-compose-up
$ python3 main.py
2025-05-10 10:01:57+0700 | INFO | task.py:51 | Welcome to kafka-streaming project
2025-05-10 10:01:57+0700 | INFO | task.py:21 | created kafka consumer on localhost:9092, group: test-echo-1
2025-05-10 10:01:57+0700 | INFO | task.py:24 | subscribed for topic my-topic-1
2025-05-10 10:01:57+0700 | INFO | task.py:21 | created kafka consumer on localhost:9092, group: test-echo-2
2025-05-10 10:01:57+0700 | INFO | task.py:24 | subscribed for topic my-topic-2
2025-05-10 10:01:58+0700 | INFO | task.py:51 | Welcome to kafka-streaming project
2025-05-10 10:02:00+0700 | INFO | task.py:51 | Welcome to kafka-streaming project
2025-05-10 10:02:01+0700 | INFO | kafka_utils.py:116 | partitions assigned: {TopicPartition(topic='my-topic-1', partition=0)}
2025-05-10 10:02:01+0700 | INFO | kafka_utils.py:116 | partitions assigned: {TopicPartition(topic='my-topic-2', partition=0)}
2025-05-10 10:02:03+0700 | INFO | task.py:51 | Welcome to kafka-streaming project
2025-05-10 10:02:07+0700 | INFO | task.py:51 | Welcome to kafka-streaming project
2025-05-10 10:02:11+0700 | WARNING | kafka_utils.py:69 | stop iteration because data consumption limit reached
2025-05-10 10:02:11+0700 | INFO | task.py:43 | inserted 120 bytes to db
2025-05-10 10:02:12+0700 | WARNING | kafka_utils.py:69 | stop iteration because data consumption limit reached
2025-05-10 10:02:12+0700 | INFO | task.py:43 | inserted 120 bytes to db
```
