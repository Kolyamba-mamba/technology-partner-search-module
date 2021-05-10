from django.shortcuts import render
import os
import sys
sys.path.append(os.path.abspath('..'))
from modules.analyzer.psComparator import get_patents
from modules.helpers.dbHelper import create_connection
from modules.dbActions.getTables import get_entities_by_condition


def index(request):
    if request.method == "POST":
        query = request.POST.get("input_text")
        matches = get_patents(str(query)) #reducing capacity
        return render(request, 'searchPartners/homepage.html', {'partners': matches, 'input_text': query})
    else:
        return render(request, 'searchPartners/homepage.html')

def patent(request, id):
    abstr = ""
    descr = ""
    claims = ""
    con = create_connection("diplom", "postgres", "postgres", "localhost", "5432")
    patent = get_entities_by_condition(con, "patents", f"id = '{str(id)}'")[0]
    if patent[6]:
        if os.path.isfile(patent[6]):
            with open(str(patent[6]), 'r', encoding='utf8') as f:
                abstr = f.read()
    if patent[7]:
        if os.path.isfile(patent[7]):
            with open(str(patent[7]), 'r', encoding='utf8') as f:
                descr = f.read()
    if patent[8]:
        if os.path.isfile(patent[8]):
            with open(str(patent[8]), 'r', encoding='utf8') as f:
                claims = f.read()
    return render(request, 'searchPartners/patentpage.html', {'patent': patent, 'abstr': abstr, 'descr': descr, 'claims': claims})