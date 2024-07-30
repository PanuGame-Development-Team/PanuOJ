from markdown import markdown
from settings import *
def bs4_render_table(table_ori):
    html = ""
    table = table_ori[:]
    head = table.pop(0)
    
    html += "<table class=\"table table-striped\">"
    html += "<thead><tr>"
    for i in head:
        html += f"<th>{i}</th>"
    html += "</tr></thead>"
    html += "<tbody>"
    for line in table:
        html += "<tr>"
        for i in line:
            html += f"<td>{i}</td>"
        html += "</tr>"
    html += "</table>"
    return html
def render_markdown(md):
    return markdown(md,extensions=mdmodules,extension_configs=mdconfigs)