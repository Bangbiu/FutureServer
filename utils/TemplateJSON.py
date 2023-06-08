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
            "key": "env_desc",
            "title": "环境描述",
            "type": "lb"
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
            {"label": "50", "value": 50},
            {"label": "100", "value": 100},
            {"label": "200", "value": 200},
            {"label": "300", "value": 300},
        ]
    },
    "args": {
        "industry": "",
        "name": "",
        "products": "",
        "env_desc": "",
        "word_count": 100,
    },
    "prompt": "你是一名专业的点评家，今天你光顾的这家店是[industry]行业的，这家店的店面特点是[env_desc]，名字叫[name]。你体验了他们的以下产品: [products]。请根据你今天的体验写一份[word_count]字的点评，一定要多用中国网络用语，一定要多描述实际体验，少臆断，可以不提及店名，每个产品可以用列表的形式列出感想。"
}

print(json.dumps(temp))
