"""
Servizio per la generazione di certificati PDF
"""

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from datetime import datetime
import os
from pathlib import Path


class CertificateService:
    """
    Servizio per generare certificati PDF per eventi e corsi completati.
    """
    
    def __init__(self, output_dir: str = "./certificates"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_event_certificate(
        self,
        participant_name: str,
        event_title: str,
        event_date: datetime,
        certificate_id: str
    ) -> str:
        """
        Genera un certificato per la partecipazione a un evento.
        
        Args:
            participant_name: Nome del partecipante
            event_title: Titolo dell'evento
            event_date: Data dell'evento
            certificate_id: ID univoco del certificato
        
        Returns:
            Path del file PDF generato
        """
        filename = f"certificate_event_{certificate_id}.pdf"
        filepath = self.output_dir / filename
        
        # Crea PDF in formato landscape
        c = canvas.Canvas(str(filepath), pagesize=landscape(A4))
        width, height = landscape(A4)
        
        # Sfondo e bordo
        c.setFillColor(colors.HexColor('#F8F9FA'))
        c.rect(0, 0, width, height, fill=True, stroke=False)
        
        c.setStrokeColor(colors.HexColor('#0066CC'))
        c.setLineWidth(3)
        c.rect(30, 30, width-60, height-60, fill=False, stroke=True)
        
        # Logo/Header
        c.setFillColor(colors.HexColor('#0066CC'))
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(width/2, height-80, "AFRICA BUSINESS BRIDGE")
        
        # Titolo Certificato
        c.setFillColor(colors.HexColor('#333333'))
        c.setFont("Helvetica-Bold", 36)
        c.drawCentredString(width/2, height-150, "CERTIFICATO DI PARTECIPAZIONE")
        
        # Linea decorativa
        c.setStrokeColor(colors.HexColor('#FF8C42'))
        c.setLineWidth(2)
        c.line(width/2-150, height-165, width/2+150, height-165)
        
        # Testo principale
        c.setFillColor(colors.HexColor('#333333'))
        c.setFont("Helvetica", 16)
        c.drawCentredString(width/2, height-220, "Si certifica che")
        
        # Nome partecipante
        c.setFont("Helvetica-Bold", 28)
        c.setFillColor(colors.HexColor('#0066CC'))
        c.drawCentredString(width/2, height-270, participant_name.upper())
        
        # Dettagli evento
        c.setFont("Helvetica", 16)
        c.setFillColor(colors.HexColor('#333333'))
        c.drawCentredString(width/2, height-320, "ha partecipato con successo all'evento")
        
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(width/2, height-360, f'"{event_title}"')
        
        # Data
        event_date_str = event_date.strftime("%d %B %Y")
        c.setFont("Helvetica", 14)
        c.drawCentredString(width/2, height-400, f"tenutosi il {event_date_str}")
        
        # Footer
        c.setFont("Helvetica-Oblique", 10)
        c.setFillColor(colors.HexColor('#666666'))
        c.drawCentredString(width/2, 80, f"Certificato ID: {certificate_id}")
        c.drawCentredString(width/2, 60, "Africa Business Bridge - Connecting Italian SMEs with African Markets")
        
        # Firma (placeholder)
        c.setFont("Helvetica", 12)
        c.drawString(100, 150, "_" * 30)
        c.drawString(100, 130, "Direttore IBP")
        
        c.drawString(width-250, 150, "_" * 30)
        c.drawString(width-250, 130, "Responsabile Formazione")
        
        c.save()
        
        return str(filepath)
    
    def generate_course_certificate(
        self,
        participant_name: str,
        course_title: str,
        completion_date: datetime,
        duration_hours: int,
        certificate_id: str
    ) -> str:
        """
        Genera un certificato per il completamento di un corso.
        
        Args:
            participant_name: Nome del partecipante
            course_title: Titolo del corso
            completion_date: Data di completamento
            duration_hours: Durata del corso in ore
            certificate_id: ID univoco del certificato
        
        Returns:
            Path del file PDF generato
        """
        filename = f"certificate_course_{certificate_id}.pdf"
        filepath = self.output_dir / filename
        
        # Crea PDF in formato landscape
        c = canvas.Canvas(str(filepath), pagesize=landscape(A4))
        width, height = landscape(A4)
        
        # Sfondo e bordo
        c.setFillColor(colors.HexColor('#F8F9FA'))
        c.rect(0, 0, width, height, fill=True, stroke=False)
        
        c.setStrokeColor(colors.HexColor('#0066CC'))
        c.setLineWidth(3)
        c.rect(30, 30, width-60, height-60, fill=False, stroke=True)
        
        # Logo/Header
        c.setFillColor(colors.HexColor('#0066CC'))
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(width/2, height-80, "AFRICA BUSINESS BRIDGE")
        
        # Titolo Certificato
        c.setFillColor(colors.HexColor('#333333'))
        c.setFont("Helvetica-Bold", 36)
        c.drawCentredString(width/2, height-150, "CERTIFICATO DI COMPLETAMENTO")
        
        # Linea decorativa
        c.setStrokeColor(colors.HexColor('#FF8C42'))
        c.setLineWidth(2)
        c.line(width/2-150, height-165, width/2+150, height-165)
        
        # Testo principale
        c.setFillColor(colors.HexColor('#333333'))
        c.setFont("Helvetica", 16)
        c.drawCentredString(width/2, height-220, "Si certifica che")
        
        # Nome partecipante
        c.setFont("Helvetica-Bold", 28)
        c.setFillColor(colors.HexColor('#0066CC'))
        c.drawCentredString(width/2, height-270, participant_name.upper())
        
        # Dettagli corso
        c.setFont("Helvetica", 16)
        c.setFillColor(colors.HexColor('#333333'))
        c.drawCentredString(width/2, height-320, "ha completato con successo il corso")
        
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(width/2, height-360, f'"{course_title}"')
        
        # Durata e data
        c.setFont("Helvetica", 14)
        c.drawCentredString(width/2, height-400, f"Durata: {duration_hours} ore")
        
        completion_date_str = completion_date.strftime("%d %B %Y")
        c.drawCentredString(width/2, height-430, f"Completato il {completion_date_str}")
        
        # Footer
        c.setFont("Helvetica-Oblique", 10)
        c.setFillColor(colors.HexColor('#666666'))
        c.drawCentredString(width/2, 80, f"Certificato ID: {certificate_id}")
        c.drawCentredString(width/2, 60, "Africa Business Bridge - Connecting Italian SMEs with African Markets")
        
        # Firma (placeholder)
        c.setFont("Helvetica", 12)
        c.drawString(100, 150, "_" * 30)
        c.drawString(100, 130, "Direttore IBP")
        
        c.drawString(width-250, 150, "_" * 30)
        c.drawString(width-250, 130, "Responsabile Formazione")
        
        c.save()
        
        return str(filepath)
    
    def get_certificate_url(self, certificate_path: str) -> str:
        """
        Converte il path del certificato in URL pubblico.
        
        Args:
            certificate_path: Path del file certificato
        
        Returns:
            URL pubblico del certificato
        """
        filename = Path(certificate_path).name
        return f"/certificates/{filename}"


# Funzione helper per uso standalone
def generate_certificate(
    participant_name: str,
    title: str,
    date: datetime,
    certificate_type: str = "event",
    duration_hours: int = None
) -> str:
    """
    Funzione helper per generazione rapida certificati.
    """
    service = CertificateService()
    certificate_id = f"{certificate_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    if certificate_type == "event":
        return service.generate_event_certificate(
            participant_name, title, date, certificate_id
        )
    elif certificate_type == "course":
        return service.generate_course_certificate(
            participant_name, title, date, duration_hours or 10, certificate_id
        )
    else:
        raise ValueError(f"Tipo certificato non valido: {certificate_type}")

