"""
Reconnaissance Service Package
================================

Servicio modular para reconocimiento y OSINT.
"""

from .base import BaseReconnaissanceService
from .subdomain_enumeration import SubdomainEnumerationService
from .dns_enumeration import DNSEnumerationService
from .email_harvesting import EmailHarvestingService
from .web_crawling import WebCrawlingService
from .osint_tools import OSINTToolsService
from .secrets_detection import SecretsDetectionService
from .google_dorks import GoogleDorksService
from .complete_recon import CompleteReconService
from .parsers import ResultParsersService


class ReconnaissanceService:
    """
    Servicio completo de reconnaissance y OSINT.
    
    Orquesta todos los submódulos especializados.
    """
    
    def __init__(self, scan_repository=None):
        """Inicializa el servicio y todos los submódulos."""
        self.scan_repo = scan_repository or __import__('repositories', fromlist=['ScanRepository']).ScanRepository()
        
        # Inicializar submódulos
        self.subdomain_service = SubdomainEnumerationService(self.scan_repo)
        self.dns_service = DNSEnumerationService(self.scan_repo)
        self.email_service = EmailHarvestingService(self.scan_repo)
        self.web_crawl_service = WebCrawlingService(self.scan_repo)
        self.osint_service = OSINTToolsService(self.scan_repo)
        self.secrets_service = SecretsDetectionService(self.scan_repo)
        self.google_dorks_service = GoogleDorksService(self.scan_repo)
        self.complete_recon_service = CompleteReconService(self.scan_repo)
        self.parsers_service = ResultParsersService(self.scan_repo)
    
    # ============================================
    # SUBDOMAIN ENUMERATION
    # ============================================
    
    def start_subdomain_enum(self, *args, **kwargs):
        """Delega a SubdomainEnumerationService."""
        return self.subdomain_service.start_subdomain_enum(*args, **kwargs)
    
    def start_findomain_enum(self, *args, **kwargs):
        """Delega a SubdomainEnumerationService."""
        return self.subdomain_service.start_findomain_enum(*args, **kwargs)
    
    def start_crtsh_lookup(self, *args, **kwargs):
        """Delega a SubdomainEnumerationService."""
        return self.subdomain_service.start_crtsh_lookup(*args, **kwargs)
    
    def preview_subdomain_enum(self, *args, **kwargs):
        """Preview de enumeración de subdominios."""
        return self.subdomain_service.preview_subdomain_enum(*args, **kwargs)
    
    def preview_findomain_enum(self, *args, **kwargs):
        """Preview de Findomain."""
        return self.subdomain_service.preview_findomain_enum(*args, **kwargs)
    
    def preview_crtsh_lookup(self, *args, **kwargs):
        """Preview de crt.sh."""
        return self.subdomain_service.preview_crtsh_lookup(*args, **kwargs)
    
    def preview_whois_lookup(self, *args, **kwargs):
        """Preview de consulta WHOIS."""
        return self.complete_recon_service.preview_whois_lookup(*args, **kwargs)
    
    # ============================================
    # DNS ENUMERATION
    # ============================================
    
    def start_dns_recon(self, *args, **kwargs):
        """Delega a DNSEnumerationService."""
        return self.dns_service.start_dns_recon(*args, **kwargs)
    
    def start_dns_lookup(self, *args, **kwargs):
        """Delega a DNSEnumerationService."""
        return self.dns_service.start_dns_lookup(*args, **kwargs)
    
    def start_traceroute(self, *args, **kwargs):
        """Delega a DNSEnumerationService."""
        return self.dns_service.start_traceroute(*args, **kwargs)
    
    def start_dns_enum_alt(self, *args, **kwargs):
        """Delega a DNSEnumerationService."""
        return self.dns_service.start_dns_enum_alt(*args, **kwargs)
    
    def preview_dns_recon(self, *args, **kwargs):
        """Preview de reconocimiento DNS."""
        return self.dns_service.preview_dns_recon(*args, **kwargs)
    
    def preview_dns_lookup(self, *args, **kwargs):
        """Preview de consulta DNS lookup."""
        return self.dns_service.preview_dns_lookup(*args, **kwargs)
    
    def preview_dns_enum_alt(self, *args, **kwargs):
        """Preview de DNS enum alt."""
        return self.dns_service.preview_dns_enum_alt(*args, **kwargs)
    
    def preview_traceroute(self, *args, **kwargs):
        """Preview de traceroute."""
        return self.dns_service.preview_traceroute(*args, **kwargs)
    
    # ============================================
    # EMAIL HARVESTING
    # ============================================
    
    def start_email_harvest(self, *args, **kwargs):
        """Delega a EmailHarvestingService."""
        return self.email_service.start_email_harvest(*args, **kwargs)
    
    def preview_hunter_io_search(self, *args, **kwargs):
        """Preview de Hunter.io."""
        return self.email_service.preview_hunter_io_search(*args, **kwargs)
    
    def start_hunter_io_search(self, *args, **kwargs):
        """Delega a EmailHarvestingService."""
        return self.email_service.start_hunter_io_search(*args, **kwargs)
    
    def preview_linkedin_enum(self, *args, **kwargs):
        """Preview de LinkedIn enum."""
        return self.email_service.preview_linkedin_enum(*args, **kwargs)
    
    def start_linkedin_enum(self, *args, **kwargs):
        """Delega a EmailHarvestingService."""
        return self.email_service.start_linkedin_enum(*args, **kwargs)
    
    # ============================================
    # WEB CRAWLING
    # ============================================
    
    def start_web_crawl(self, *args, **kwargs):
        """Delega a WebCrawlingService."""
        return self.web_crawl_service.start_web_crawl(*args, **kwargs)
    
    # ============================================
    # OSINT TOOLS
    # ============================================
    
    def start_shodan_search(self, *args, **kwargs):
        """Delega a OSINTToolsService."""
        return self.osint_service.start_shodan_search(*args, **kwargs)
    
    def start_censys_search(self, *args, **kwargs):
        """Delega a OSINTToolsService."""
        return self.osint_service.start_censys_search(*args, **kwargs)
    
    def start_wayback_urls(self, *args, **kwargs):
        """Delega a OSINTToolsService."""
        return self.osint_service.start_wayback_urls(*args, **kwargs)
    
    # ============================================
    # SECRETS DETECTION
    # ============================================
    
    def start_secrets_scan(self, *args, **kwargs):
        """Delega a SecretsDetectionService."""
        return self.secrets_service.start_secrets_scan(*args, **kwargs)
    
    # ============================================
    # GOOGLE DORKS
    # ============================================
    
    def start_google_dorks(self, *args, **kwargs):
        """Delega a GoogleDorksService."""
        return self.google_dorks_service.start_google_dorks(*args, **kwargs)
    
    def preview_email_harvest(self, *args, **kwargs):
        """Preview de email harvest."""
        return self.email_service.preview_email_harvest(*args, **kwargs)
    
    def preview_web_crawl(self, *args, **kwargs):
        """Preview de web crawl."""
        return self.web_crawl_service.preview_web_crawl(*args, **kwargs)
    
    def preview_shodan_search(self, *args, **kwargs):
        """Preview de Shodan search."""
        return self.osint_service.preview_shodan_search(*args, **kwargs)
    
    def preview_censys_search(self, *args, **kwargs):
        """Preview de Censys search."""
        return self.osint_service.preview_censys_search(*args, **kwargs)
    
    def preview_wayback_urls(self, *args, **kwargs):
        """Preview de Wayback URLs."""
        return self.osint_service.preview_wayback_urls(*args, **kwargs)
    
    def preview_secrets_scan(self, *args, **kwargs):
        """Preview de secrets scan."""
        return self.secrets_service.preview_secrets_scan(*args, **kwargs)
    
    def preview_google_dorks(self, *args, **kwargs):
        """Preview de Google Dorks."""
        return self.google_dorks_service.preview_google_dorks(*args, **kwargs)
    
    # ============================================
    # COMPLETE RECONNAISSANCE
    # ============================================
    
    def start_whois_lookup(self, *args, **kwargs):
        """Delega a CompleteReconService."""
        return self.complete_recon_service.start_whois_lookup(*args, **kwargs)
    
    def start_complete_recon(self, *args, **kwargs):
        """Delega a CompleteReconService con servicios inyectados."""
        return self.complete_recon_service.start_complete_recon(
            *args,
            subdomain_service=self.subdomain_service,
            dns_service=self.dns_service,
            email_service=self.email_service,
            osint_service=self.osint_service,
            **kwargs
        )
    
    # ============================================
    # PARSERS
    # ============================================
    
    def get_scan_results(self, *args, **kwargs):
        """Delega a ResultParsersService."""
        return self.parsers_service.get_scan_results(*args, **kwargs)
