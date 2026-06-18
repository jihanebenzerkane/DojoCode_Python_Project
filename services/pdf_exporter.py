from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

class ProgressExporter:
    """Exporte le rapport de progression en PDF."""
    
    def __init__(self, user_data: dict, challenges_data: list):
        self.user = user_data
        self.challenges = challenges_data
    
    def generate(self, filepath: str):
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Titre
        title = Paragraph(f"Rapport CodeDojo - {self.user['username']}", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Stats
        stats = f"""
        <b>Niveau:</b> {self.user['level']}<<br/>
        <b>Points:</b> {self.user['points']}<<br/>
        <b>Défis complétés:</b> {len([c for c in self.challenges if c['completed']])}/{len(self.challenges)}<<br/>
        <b>Temps total:</b> {self.user['total_time']} minutes
        """
        story.append(Paragraph(stats, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Tableau des défis
        data = [["Défi", "Statut", "Tentatives", "Temps"]]
        for c in self.challenges:
            status = "✅" if c['completed'] else "❌"
            data.append([c['title'], status, str(c['attempts']), f"{c['time']}min"])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        doc.build(story)