import re

def get_safe_filename(name):
    """
    Zorgt dat een string veilig is om als bestandsnaam of mapnaam te gebruiken op alle OS'en.
    Verwijdert karakters die problemen kunnen veroorzaken in paden.
    """
    return re.sub(r'[^\w\s\.-]', '', name).strip()