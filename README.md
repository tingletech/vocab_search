# vocab_search
search controlled vocabularies for URLs to "link" into descriptive records

work in progress

Right now, this is an experiment using `vocab.getty.edu`.

## grab latest getty vocabs
checks for file changes
```
./sync.sh
```

## parse the getty vocabs
```
./parse_getty_rdf.py
```

## write out framed json-ld
```
./create_getty_resource_json.py
```

## put files into elasticsearch
TODO

## cloud formation / AWS setup
TODO
