from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from .models import Artifacts, ArchiveManager, SearchCriteria, CriteriaManager
from django.views.decorators.http import require_http_methods
from urllib.request import urlopen
import os, shutil


"""
def index(request):
    return render(request, "form.html")


@require_http_methods(["GET", "POST"])
def search(request):
    if request.method == 'POST':
        a_id = request.POST.get('textfield', None)

        return render(view_artifact(request, a_id), "form.html")

    # else:
        # return render(request, 'form.html')

"""


# i.e. test home page
def start_session(request, search_criteria_id):
    execute_session(search_criteria_id)
    return HttpResponse("created session: " + str(search_criteria_id))


def delete_session(request, session_id):
    ArchiveManager.delete_session(session_id)
    return HttpResponse("deleted session: " + str(session_id))

# Redirected page of artifact
@require_http_methods(["GET", "POST"])
def view_artifact(request, artifact_id):
    try:
        artifact = ArchiveManager.get_artifact(artifact_id)
        webpage = artifact.artifact_url

        # remove "https://" when real urls are stored
        return HttpResponseRedirect("https://" + webpage)

    except Artifacts.DoesNotExist:
        raise Http404("Website does not exist")


# Page that returns artifacts of a particular session
@require_http_methods(["GET", "POST"])
def get_session(request, session_id):
    try:
        artifact_list = ArchiveManager.get_session(session_id)
        # output = ',\n'.join([a.artifact_url for a in artifact_list])
        output = {}
        i = 0

        for a in artifact_list:
            output[i] = a.artifact_url
            i += 1

        return JsonResponse(output)

    except Artifacts.DoesNotExist:
        raise Http404("Session does not exit")


# Page that returns search criteria list
@require_http_methods(["GET", "POST"])
def get_search_criteria(request):
    try:
        criteria_list = CriteriaManager.get_criteria()
        # output = ',\n'.join([c.criterion for c in criteria_list])
        output = {}
        i = 0

        for c in criteria_list:
            output[i] = c.criterion
            i += 1

        return JsonResponse(output)

    except SearchCriteria.DoesNotExist:
        raise Http404("Search Criteria does not exit")


# Page that allows user to edit search criteria list & returns updated search criteria list
@require_http_methods(["GET", "POST"])
def edit_search_criteria(request):
    # criteria_list = CriteriaManager.get_criteria()

    # GUI interaction to create criterion or delete criterion
    # user selects option to add or delete criterion | i.e True = add, False = delete

    edit_action = True

    try:
        if edit_action:
            # user enters criterion to be added
            criterion = "criterion here"
            CriteriaManager.create_criterion(criterion)
        else:
            # user selects criterion to delete | example criterion_id = 1 = criterion_list[0]
            criterion_id = 0
            CriteriaManager.delete_criterion(criterion_id)

        return get_search_criteria(request)

    except SearchCriteria.DoesNotExist:
        raise Http404("Search Criteria does not exit")


# Function to start a session, receive artifact url list from scrapy, and store the url's in the DB
def execute_session(search_criteria_id):
    try:
        # get sesearch_criteria_id through user I/O from frontend

        # CriteriaManager.reset_criterion_to_use()
        CriteriaManager.set_criterion_to_use(search_criteria_id)
        run_crawler()

    except OSError:
        # display error message
        return False
    else:
        return True


# Function to save artifact HTML file to local file reserve directory
def save_artifact_to_file(filename, artifact_url):

    # prompt tagging options

    try:
        # extract HTML file via url
        url = artifact_url
        response = urlopen(url)  # change to urllib2
        web_content = response.read()

        # write webpage content to file & save
        f = open(filename + ".html", "w")
        f.write(web_content)
        f.close()

    except IOError:
        # display error message
        return False
    else:
        return True


