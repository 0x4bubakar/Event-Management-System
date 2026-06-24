from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Spacer, Paragraph, Table, SimpleDocTemplate
from reportlab.graphics.charts.barcharts import VerticalBarChart
from datetime import datetime as dt

timestamp = dt.now()
filename = f"Your Bristol Community Events Receipt - {timestamp.strftime("%d %B %Y")}.pdf"
print(filename)

def receipt():
    timestamp = dt.now()
    filename = f"Bristol Community Events Receipt - {timestamp.strftime("%d")}"
    print(timestamp.strftime())
    c = canvas.Canvas('hello.pdf')
    c.drawString(100, 100, "hello world")
    c.save()
