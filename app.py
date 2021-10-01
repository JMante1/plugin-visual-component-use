from flask import Flask, request, abort
import sys
import traceback
from Functions.input_data import input_data
from Functions.find_role_name import find_role_name
from Functions.sankey import sankey
from Functions.sankey_graph import sankey_graph
from Functions.retrieve_html import retrieve_html

from Functions.most_used_bar import most_used_bar
from Functions.bar_plot import bar_plot
from Functions.most_used_by_type_bar import most_used_by_type_bar
from Functions.toggle_bars import toggle_bars

import tempfile
import os


app = Flask(__name__)


@app.route("/sankey/status")
def Sankey_Status():
    return("The sankey plugin is up and running")


@app.route("/sankey/evaluate", methods=["POST"])
def Sankey_Evaluate():
    data = request.get_json(force=True)
    rdf_type = data['type']

    # ~~~~~~~~~~~~ REPLACE THIS SECTION WITH OWN RUN CODE ~~~~~~~~~~~~~~~~~~~
    # uses rdf types
    accepted_types = {'Component'}

    acceptable = rdf_type in accepted_types
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~ END SECTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    if acceptable:
        return f'The type sent ({rdf_type}) is an accepted type', 200
    else:
        return f'The type sent ({rdf_type}) is NOT an accepted type', 415


@app.route("/bar/run", methods=["POST"])
def Sankey_Run():
    data = request.get_json(force=True)

    top_level_url = data['top_level']
    complete_sbol = data['complete_sbol']
    instance_url = data['instanceUrl']

    url = complete_sbol.replace('/sbol', '')

    try:
        # retrieve information about the part of interest
        self_df, display_id, title, role, count = input_data(top_level_url,
                                                             instance_url)

        # Find the role name in the ontology of the part of interest
        role_link = find_role_name(role, plural=False)

        # create data for the sankey diagram and format it correctly
        df_sankey = sankey(url, top_level_url, title, instance_url)

        sankey_title = f'Parts Co-Located with {title} (a {role_link}'

        # create a temporary directory
        temp_dir = tempfile.TemporaryDirectory()

        # name file
        filename = os.path.join(temp_dir.name, "Sankey.html")

        # create the sankey diagram
        sankey_graph(filename, df_sankey, 'Node, Label',
                     'Link', 'Color', 'Source', 'Target', 'Value',
                     'Link Color', sankey_title, url_not_name=False)

        # obtain the html from the sankey diagram
        result = retrieve_html(filename)

        return result

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        lnum = exc_tb.tb_lineno
        abort(400, f'Exception is: {e}, exc_type: {exc_type}, exc_obj: {exc_obj}, fname: {fname}, line_number: {lnum}, traceback: {traceback.format_exc()}')


@app.route("/bar/status")
def Bar_Status():
    return("The bar plugin is up and running")


@app.route("/bar/evaluate", methods=["POST"])
def Bar_Evaluate():
    data = request.get_json(force=True)
    rdf_type = data['type']

    # ~~~~~~~~~~~~ REPLACE THIS SECTION WITH OWN RUN CODE ~~~~~~~~~~~~~~~~~~~
    # uses rdf types
    accepted_types = {'Component'}

    acceptable = rdf_type in accepted_types
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~ END SECTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    if acceptable:
        return f'The type sent ({rdf_type}) is an accepted type', 200
    else:
        return f'The type sent ({rdf_type}) is NOT an accepted type', 415


@app.route("/bar/run", methods=["POST"])
def Bar_Run():
    data = request.get_json(force=True)

    top_level_url = data['top_level']
    complete_sbol = data['complete_sbol']
    instance_url = data['instanceUrl']

    url = complete_sbol.replace('/sbol', '')

    try:
        # create input data
        self_df, display_id, title, role, count = input_data(top_level_url,
                                                             instance_url)

        # create and format data for the most_used barchart
        bar_df = most_used_bar(top_level_url, instance_url, display_id, title,
                               role, count)

        # graph title for most used barchart
        graph_title = f'Top Ten Parts by Number of Uses Compared to <a href="{url}" target="_blank">{title}</a>'

        # create a temporary directory
        temp_dir = tempfile.TemporaryDirectory()

        # name file
        filename1 = os.path.join(temp_dir.name, "Most_Used.html")

        # create the most used barchart
        bar_plot('title', 'count', 'color', bar_df, graph_title, filename1,
                 'deff')

        # retrieve html
        most_used = retrieve_html(filename1)

        # find poi role ontology link
        role_link = find_role_name(role, plural=False)

        bar_df = most_used_by_type_bar(top_level_url, instance_url, display_id,
                                       title, role, count)

        # graph title for most used barchart
        graph_title = f'Top Ten {role_link} by Number of Uses Compared to <a href="{url}" target="_blank">{title}</a>'

        # name file
        filename2 = os.path.join(temp_dir.name, "Most_Used_Type.html")

        # create the most used barchart
        bar_plot('title', 'count', 'color', bar_df, graph_title, filename2,
                 'deff')

        # retrieve html
        by_role = retrieve_html(filename2)

        # create bar toggle html
        toggle_display = toggle_bars(most_used, by_role)

        return toggle_display

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        lnum = exc_tb.tb_lineno
        abort(400, f'Exception is: {e}, exc_type: {exc_type}, exc_obj: {exc_obj}, fname: {fname}, line_number: {lnum}, traceback: {traceback.format_exc()}')
