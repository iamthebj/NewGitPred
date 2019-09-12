'''api module'''
import subprocess
import urllib
import os

import flask
import logging

import requests
from flask import json, Flask
import json
from flask import request as rq
from flask import Response
from fetching_data.test_data import TestData
from web_git_prediction.app import app
from fetching_file_data.fetching_file_data import Fetch_file
from fetching_file_data.test_data import TestData1
from fetching_data.fetching_data import Fetch
from search.search import Search
from comments.comment import Comment

from store_model.store_model import StoreModel
import fetching_file_data.helper
from fetching_data import commit_api
from web_git_prediction import object_file_predict
from web_git_prediction.linter import lint

log = logging.getLogger(__name__)


@app.route('/', methods=['GET', 'POST', 'HEAD'])
def index():
    """Index page"""
    return 'Welcome'


@app.route('/github/', methods=['GET', 'POST', 'HEAD'])
def api_github_message():
    """api for sending comments"""
    if rq.headers['Content-Type'] == 'application/json':
        my_info = json.dumps(rq.json)
        payload = json.loads(my_info)
        if not payload['action'] == 'closed':
            comment_url = payload['pull_request']['comments_url']
            linter_returned = lint(payload)

            if linter_returned == 1:
                model = StoreModel().loadData()
                tdf = TestData()
                tdf1 = TestData1()
                parameter_dict = tdf.fetcher(my_info)
                extension_file = tdf1.file_fetcher(my_info)
                feature_dict = parameter_dict['feature_dict']
                comment_url = parameter_dict['comment_url']
                comment_body = tdf.test_feeder(feature_dict, model)
                file_comment_body = tdf1.file_test_feeder(extension_file[0], extension_file[1])
                Comment.post_comment(comment_url, comment_body)
                Comment.post_comment(comment_url, str(file_comment_body))
                app.logger.info(comment_body)
                prediction_response = json.dumps({"state": comment_body})
                app.logger.info(comment_body)
                res = Response(prediction_response, status=200, mimetype='application.json')
                return res
            else:
                comment_body = linter_returned
                headers = {'Content-Type': 'application/json'}
                myurl = '%s' % comment_url
                post_comment_data = '{\"body\":\"%s\"}' % comment_body
                post_comment_json = json.loads(post_comment_data)
                response = requests.post(myurl, auth=("GithubPrediction", "password4gp"), headers=headers,
                                         json=post_comment_json)
                if response.status_code == 201:
                    print("Successfully posted a comment")
                else:
                    print("Failed to post a response with http status code : ", response.status_code)
                return "done"
        else:
            print ("Closed pull request")

"""         
        prediction_response = json.dumps({"state": "closed pull request"})
        app.logger.info("closed pull request")
        res = Response(prediction_response, status=200, mimetype='application.json')
        return res"""


@app.route('/api/connection/', methods=['GET', 'POST', 'HEAD'])
def api_getconnection():
    """api for creating connection"""
    if rq.method == 'POST':
        user_id = rq.form['user_id']
        password = rq.form['password']
        search_keyword = rq.form['search_keyword']
        response = requests.get('https://api.github.com', auth=(user_id, password))
        status = response.headers['Status']
        if status == '401 Unauthorized' or status == 'Forbidden':
            app.logger.info('failed to log in.... Please try again')
            msg = json.dumps({"status": 401, "authorization": "False"})
            res = Response(msg, status=201, mimetype='application.json')
            return res
        else:
            owner_repositories = Search.search(search_keyword)
            owner_repositories_dict = {}
            owner_repositories_dict = owner_repositories
            connection_response = json.dumps({"status": 200, "authorization": "True",
                                              "owner_repositories_list": owner_repositories_dict})
            app.logger.info('logged in successfully')
            res = Response(connection_response, status=201, mimetype='application.json')
            return res


@app.route('/api/pulls_extract/', methods=['POST', 'GET'])
def result():
    """api for pull level features"""
    if rq.method == 'POST':
        search_keyword = rq.form['search_keyword']
        FETCH_OBJ = Fetch()
        owner_repositories = Search.search(search_keyword)
        for i in owner_repositories:
            owner_name = i["owner_name"]
            repository_name = i["repository_name"]
            FETCH_OBJ.json_to_csv_conversion(owner_name, repository_name)
        msg = json.dumps({"status": 200, "state": "pulls level Csv is being Constructed"})
        res = Response(msg, status=201, mimetype='application/json')
        return res


@app.route('/api/files_extract/', methods=['POST', 'GET'])
def fileresult():
    """api for file level features"""
    if rq.method == 'POST':
        search_keyword = rq.form['search_keyword']
        FETCH_OBJ = Fetch_file()
        owner_repositories = Search.search(search_keyword)
        for i in owner_repositories:
            owner_name = i["owner_name"]
            repository_name = i["repository_name"]
            FETCH_OBJ.json_to_csv(owner_name, repository_name)
        msg = json.dumps({"status": 200, "state": "files level Csv is being Constructed"})
        res = Response(msg, status=201, mimetype='application/json')
        return res
