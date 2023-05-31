import json
temp = {
    "title": "AI评论生成",
    "paramsArr": [
        {
            "key": "name",
            "title": "店名",
            "type": "mpc",
        },
        {
            "key": "products",
            "title": "产品",
            "type": "moc",
        },
        {
            "key": "word_count",
            "title": "字数",
            "type": "mpc",
        }
    ],
    "choices": {
        "name": [],
        "products": [],
        "word_count": [
            {"label": "100", "value": 100},
            {"label": "200", "value": 200},
            {"label": "300", "value": 300},
        ]
    },
    "args": {
        "industry": "",
        "name": "",
        "products": "",
        "word_count": 200,
    },
    "prompt": "你是一名专业的点评家，今天你光顾的这家店是[industry]行业的，名字叫[name]。你体验了他们的[products]。请根据你今天的体验写一份[word_count]字的点评。"
}

print(json.dumps(temp))
